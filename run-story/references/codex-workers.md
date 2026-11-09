# Running a phase step with Codex instead of a subagent

A build, test or explainer step can run in the Codex CLI in non-interactive mode instead of a `story-worker-*` Claude subagent. The prompt is the same (prompt A, B or C from `SKILL.md`). Only the launcher changes. State still moves through the handoff files, so a Codex step and a Claude step are interchangeable round to round.

Checked with `codex-cli 0.167.0` on Linux (Fedora, Podman).

## The command

```bash
codex exec \
  -m gpt-6-luna -c model_reasoning_effort="high" \
  -C <absolute worktree path> \
  -s workspace-write \
  -c sandbox_workspace_write.network_access=true \
  -c 'sandbox_workspace_write.writable_roots=["/home/<user>/.nuget","/home/<user>/.dotnet","/tmp"]' \
  --ephemeral \
  -o <scratchpad>/pXX-<step>-last.txt \
  - < <scratchpad>/pXX-<step>-prompt.md
```

What each part does:

- `codex exec` runs one task with no TUI and exits when the agent finishes.
- `-m` and `-c model_reasoning_effort=...` pin the model and effort, like the `story-worker-<model>-<effort>` agent types do. List the models the account has with `jq -r '.models[].slug' ~/.codex/models_cache.json`. Each model lists its effort levels under `supported_reasoning_levels`.
- `-C` sets the working directory to the phase worktree. The sandbox makes that directory writable.
- `-s workspace-write` lets the agent write only inside the worktree, plus the writable roots below.
- `network_access=true` is needed for Testcontainers. Without it the sandbox blocks the Podman/Docker unix socket, so no Postgres container can start.
- `writable_roots` adds the folders a .NET build writes outside the repo. Without `~/.nuget` the build fails on a read-only file system. `/tmp` is for test runner and container temporary files. Other stacks need their own caches here (`~/.cache/uv`, `~/.npm`, `~/.cargo`, …).
- `--ephemeral` saves no Codex session to disk.
- `-o` writes the agent's last message to a file. The orchestrator reads only that file, which holds the one status line (`BUILD:`, `VERDICT:` or `LEARN:`).
- `- < prompt.md` reads the prompt from stdin, so a long prompt needs no shell quoting.

All settings are `-c` overrides on this one call. `~/.codex/config.toml` stays unchanged, so interactive Codex keeps its own defaults.

## Quota: what a Codex builder runs

A Codex step re-sends its whole context on every shell call, so a builder that loops on full builds empties a small plan quickly. Story 002 of integra (2 phases, 13 `terra` medium runs, 2026-11-09) used about 53M input tokens and 150k output, most of a $20 plan's 5-hour window. The details and the general rules are in `delegate-codex/SKILL.md`, "Keep the quota down". For run-story:

- **The Codex builder runs only the narrow checks**: the one or two projects it changed, with a `--filter` for its tests. It does **not** run `verify_phase.py` or the solution build. Replace the "Check your work with verify_phase.py" bullet of prompt A with those narrow commands.
- **The tester runs `verify_phase.py` once** (a Claude `story-worker-haiku-*`, which bills Claude, not Codex). A mechanical failure there comes back as a numbered fix, as usual.
- **One Codex builder per phase, in sequence.** Don't split a phase into parallel workers to save time unless the user asks for it. Every worker re-reads the same guides, and the shared files (`<M>Module.cs`, csproj files, Build-Notes) need extra rounds to merge.
- **Prompts name what is allowed, not only what is forbidden.** For example: "no new NuGet package; a ProjectReference that follows the module rules is fine". An ambiguous ban made two workers stop as BLOCKED.
- **No log polling.** Any long command runs in the foreground with output to a file, and the worker reads only the summary lines.

## How the orchestrator runs it

1. Fill the prompt exactly as for a subagent and write it to a scratchpad file.
2. Start the command with Bash `run_in_background: true`. The completion notification arrives when Codex exits.
3. Read the `-o` file for the status line. Never read Codex's full output: it would flood the orchestrator's context.
4. Go on with the loop as for a subagent: a fresh `codex exec` per round, never `codex exec resume`.

Keep the memory rules in the prompt as for any agent (`MSBUILDDISABLENODEREUSE=1`, `-nodeReuse:false`, `dotnet build-server shutdown`). Count a Codex step against `Max parallel` like any other.

## Check the sandbox first, without a model

`codex sandbox` runs a plain command inside the same sandbox and calls no model, so it costs no quota. Use it once per machine or stack before the first real run:

```bash
cd <worktree>
codex sandbox -c sandbox_mode=\"workspace-write\" \
  -c sandbox_workspace_write.network_access=true \
  -c 'sandbox_workspace_write.writable_roots=["/home/<user>/.nuget","/home/<user>/.dotnet","/tmp"]' \
  -- sh -c 'curl -s --unix-socket /run/user/1000/podman/podman.sock http://d/_ping; echo; dotnet test tests/<a Postgres test project> --filter "Category=Postgres" -nodeReuse:false | tail -3'
```

Results on the reference machine:

| Check inside the sandbox | Result |
|---|---|
| Podman socket, default settings | blocked (curl exit 7) |
| Podman socket, `network_access=true` | `OK` |
| Write to `~/.nuget` without `writable_roots` | read-only file system |
| `dotnet build Integra.slnx` with the roots | 0 errors |
| Postgres tests (`Integra.Data.Schema.Tests`) | 8 passed, 26 s |

## Limits

- `network_access=true` opens the whole network, not only the container socket. Codex has no setting to allow only one socket. The tester prompt still forbids tests that reach the network.
- Avoid `--dangerously-bypass-approvals-and-sandbox`. It removes the sandbox entirely, and the settings above are enough.
- The `-o` file holds only the last message. If Codex stops early (quota, crash), the file may be missing or hold no status line. Treat that as a failed step and check the handoff files before you start another round.
- Goal mode (`/goal`, feature `goals`, on by default since 0.133) is an interactive TUI feature. In `codex exec`, a prompt starting with `/goal` is plain text: the `--json` event stream shows one ordinary `turn.started` / `turn.completed` and no goal events, and `codex exec --help` has no goal or budget flag (checked on 0.167.0). So a build step can't run in goal mode through `exec`. Guard against an early stop the way the loop already does: the prompt demands a `BUILD:` status line only after `verify_phase.py` prints `MECHANICAL: PASS`, and a missing status line, or a Build-Notes file without the round's block, counts as a failed step. The next step is a fresh `codex exec`, which picks up the partial work from the worktree.
- Before the first real run, check that the account can reach the chosen model. Codex's default model in `config.toml` may differ from it.
