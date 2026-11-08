---
name: delegate-codex
description: Delegate a self-contained piece of work to a Codex CLI worker (`codex exec`) instead of a Claude subagent, picking the Codex tier by difficulty (luna for what Haiku could do, terra for Sonnet-level work, sol for hard jobs), always on the newest model version available. Use when the user says "delegate to codex", "run this in codex", "use codex as a subagent/worker", "offload to luna/terra/sol", or wants to save Claude quota by farming out builds, tests, refactors, reviews or research to Codex, even if they don't name the CLI.
argument-hint: <task> [luna|terra|sol] [effort]
---

# Delegate to Codex

Run a bounded task in `codex exec` (non-interactive, no TUI) and read back only its final message. Codex acts like a subagent: you write a self-contained prompt, it works in a directory, and you get a short result. The worker never sees this conversation, so everything it needs must be in the prompt or in files it can read.

## Pick the tier

Match the Claude tier you would otherwise have used:

| Work | Claude equivalent | Codex tier | Default effort |
|---|---|---|---|
| Mechanical, well-specified: rename, boilerplate, simple tests, lookups, formatting | Haiku | **luna** | medium |
| Normal implementation, bug fixes, test writing, moderate refactors, code review | Sonnet | **terra** | medium–high |
| Hard: design-heavy changes, tricky debugging, cross-module refactors, security-sensitive review | Opus-level | **sol** | high |

If a luna result is wrong or thin, retry one tier up rather than looping at the same tier. The user can force a tier or effort via the arguments.

## Always use the latest version

Tier names stay stable while the version number moves (`gpt-6-luna`, `gpt-6.1-terra`, `gpt-6.1-sol`, ...). Never hardcode a slug; resolve it at call time, because the newest version differs per tier:

```bash
MODEL=$(bash ~/.claude/skills/delegate-codex/scripts/latest_model.sh terra)   # luna | terra | sol
```

The script reads `~/.codex/models_cache.json` and sorts versions numerically. Check that the effort you want is listed for that model (`jq -r '.models[]|select(.slug=="'$MODEL'")|.supported_reasoning_levels[].effort' ~/.codex/models_cache.json`); luna tops out at `max`, terra and sol also have `ultra`. Use `xhigh` or above only when the user asks, since they burn quota.

## Run it

1. Write the prompt to a scratchpad file (see "Writing the prompt").
2. Launch in the background so you can keep working; you get a notification when Codex exits:

```bash
codex exec \
  -m "$MODEL" -c model_reasoning_effort="medium" \
  -C <absolute working dir> \
  -s workspace-write \
  --json -o <scratchpad>/<name>-last.txt \
  - < <scratchpad>/<name>-prompt.md > <scratchpad>/<name>-events.jsonl 2>&1
```

Drop `--ephemeral` for any task you might pause or continue: it is what keeps the session on disk. Use `--ephemeral` only for throwaway one-shots.

Use Bash with `run_in_background: true`. Independent tasks can run as parallel `codex exec` calls, each with its own `-o` file; give parallel workers separate directories (git worktrees) or disjoint files so they don't overwrite each other.

3. Read **only** the `-o` file. Codex's streamed output is long and would flood your context.
4. Verify before trusting: check `git diff`/`git status` in the working dir and run the project's tests or linters yourself. Codex reporting success is a claim, not proof.

What the flags do:

- `-C` sets the worker's directory; `workspace-write` lets it write only there (plus the roots below).
- `-s read-only` for pure review/research tasks, so it cannot change anything.
- `--json` streams events to stdout as JSONL; the first line is `{"type":"thread.started","thread_id":"<uuid>"}`. Redirect it to a file and never read it whole.
- `-o` captures the final message; `-` reads the prompt from stdin so no shell quoting is needed.
- All settings are `-c` overrides on this call, so `~/.codex/config.toml` and interactive Codex stay untouched.

### When the task needs more than the working dir

The sandbox blocks things many builds need. Add only what the task requires:

- Network (package installs, Testcontainers/Docker socket): `-c sandbox_workspace_write.network_access=true`. This opens the whole network; tell the worker in the prompt not to reach out beyond what's needed.
- Caches outside the repo (build fails with "read-only file system"): `-c 'sandbox_workspace_write.writable_roots=["/home/<user>/.nuget","/tmp"]'`, adding the stack's cache (`~/.cache/uv`, `~/.npm`, `~/.cargo`, `~/.nuget`, ...).
- To test a sandbox setup without spending model quota: `codex sandbox -c sandbox_mode=\"workspace-write\" <same -c flags> -- sh -c '<command>'`.

Avoid `--dangerously-bypass-approvals-and-sandbox`; the settings above are normally enough. For details and a worked .NET/Podman example, see `run-story/references/codex-workers.md` in this repo.

## Pause and resume

Codex has no pause command, but a stopped session can be continued, so pause = interrupt, resume = `codex exec resume`. Verified on codex-cli 0.167.0: an interrupted worker resumed with its context intact (it remembered a word given before the interrupt and finished the task).

**Capture the id** right after launch: `grep -o '"thread_id":"[^"]*"' <name>-events.jsonl | head -1 | cut -d'"' -f4`. Save it somewhere durable (a handoff file) next to the task name.

**Pause**: send SIGINT to the PID of the background `codex exec` you started (`kill -INT <pid>`, falling back to `-TERM` after a few seconds). Kill only that PID; never `pkill -f codex`, which can hit the user's other Codex sessions. Whatever tool call was in flight is lost, and files already written stay in the working dir.

**Resume**:

```bash
cd <same working dir>          # resume has no -C
codex exec resume \
  -m "$MODEL" -c model_reasoning_effort="medium" \
  -c sandbox_mode=\"workspace-write\" \
  --json -o <scratchpad>/<name>-last2.txt \
  <thread_id> "You were interrupted. Continue where you left off; <new instructions>" \
  > <scratchpad>/<name>-events2.jsonl 2>&1
```

- `resume` does not accept `-s` or `-C`; set the sandbox with `-c sandbox_mode=...`, add the same `network_access`/`writable_roots` `-c` flags as the first run, and `cd` into the original directory first. Settings are not inherited from the first run.
- `--last` picks the newest session for the cwd but is racy with parallel workers; always pass the explicit id.
- The model can be changed on resume with `-m` (e.g. move a stuck luna session to terra) and the session keeps its history.
- Tell the worker what was interrupted; an in-flight command is gone, so it should re-check state (`git status`, files) before continuing.
- `codex exec resume` can also add follow-up instructions to a *finished* session, which is cheaper than a cold start when the next step builds on the last. For an independent task, start fresh.
- Sessions live under `~/.codex/sessions/`. `codex archive <id>` / `codex delete <id>` clean them up. (`codex queue --thread <id> --message ...` queues a message for a session, but it is meant for a running app-server/TUI, not for `exec`.)

## Writing the prompt

The worker starts cold, so include:

- **Goal** in one or two sentences, and why it matters (so it can make sensible calls on edge cases).
- **Scope**: which files/dirs it may touch and which it must not.
- **Context it can't infer**: conventions, relevant file paths, the command that runs the tests.
- **A concrete first action**: "before anything else, create `<file>` with `<skeleton>`, then build outward." This matters more than any other line. Without it the worker reads 40k tokens of guides, has no obvious next move, and ends its turn (see "Why workers quit"). Name the file or command to start with.
- **Done criteria**: e.g. "tests X pass", "no new lint warnings".
- **Result contract**: end with exactly one status line, and allow only two outcomes: `DONE: <summary>` or `BLOCKED: <the specific question only the user can answer>`. Do not add "incomplete" or similar, because a worker that is not allowed to claim done or blocked will invent a third word and quit through it.

Keep the prompt mostly instructions to do, not a wall of prohibitions, and don't say "finish everything in this one run". A big, high-stakes ask with no start point makes the worker plan instead of act.

## Size the task

One call should be a chunk the worker can start without further planning: one module, one aggregate, one bug. If the job spans several of those (for example "three aggregates plus a transactional writer"), split it into sequential calls, each ending with a verify step, and let the next call build on the files the last one wrote. Check dependencies between chunks before launching them in parallel: a task that needs another task's output will end in a `BLOCKED:` question.

## Why workers quit

A real failure from a past session: four `terra` builds each read about 36-46k tokens of guides across 6-9 shell calls, posted one line like "I'm checking the available paths...", ran the cleanup command from the prompt (`dotnet build-server shutdown`), and reported `incomplete` with zero edits. The sandbox was fine (all commands exited 0). The model chose to end its turn. Likely drivers: no concrete first step, a large phase attempted in one go, a status contract with a loophole, low or medium effort for a hard job, and a "when done, run cleanup" rule that works as an exit ritual.

Guard against it:

- Apply the prompt and sizing rules above.
- Run cleanup commands only if the worker actually built something.
- Treat zero edits as failure. After the run, check `git status` or `git diff --stat` in the working dir. A run with a status line but no file changes did not do the work, whatever the line says.
- Match the tier to difficulty (see the table), and move up a tier before repeating the same prompt at the same tier.

## Handling failures

- **Quit without editing** (status like `incomplete`, or no changes in `git status`): do not just rerun the same prompt. `resume` the session (drop `--ephemeral` so it exists) with a direct nudge, "You stopped before editing. Create `<file>` now," which skips re-reading the context. If that stalls too, shrink the task or move up a tier.

- `-o` file missing or without a status line: the worker stopped early (quota, crash, timeout). Treat as failed and inspect the working dir. Resume it by thread id if the context matters; start fresh if the partial work is bad.
- `/goal` is an interactive-only feature; it does nothing in `codex exec`. Guard against early stopping by making the status line conditional on verification passing.
- Quota or model-access errors: confirm the account can reach the model (`codex exec -m "$MODEL" "say ok"` in a throwaway dir), then fall back one tier or to a Claude subagent.
- Keep `--json` output in a file so you can see which commands ran and with what `exit_code` (`grep '"exit_code":[1-9]'`) when diagnosing a stall; the plain log does not show tool results reliably.
- Never delegate secrets or tasks the user wouldn't want sent to a third-party model; Codex sends the prompt and the files it reads to its provider.
