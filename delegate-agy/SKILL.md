---
name: delegate-agy
description: Delegate a self-contained piece of work to an Antigravity CLI worker (`agy -p`) instead of a Claude subagent, using Gemini Flash for Haiku-level work and the Claude models inside Antigravity for harder jobs, always on the newest version available. Use when the user says "delegate to agy", "use antigravity/gemini as a worker", "offload to flash", "run this in agy", or wants to save Claude quota on reading, analysis, summarising, research or simple edits, even if they don't name the CLI.
argument-hint: <task> [flash|sonnet|opus] [effort]
---

# Delegate to Antigravity (`agy`)

Run a bounded task in `agy -p` (print mode: one prompt, no TUI, exits when done) and read back one JSON result. The worker never sees this conversation, so the prompt must be self-contained. Facts here were tested on agy 1.5.3.

## What agy is good for here

Edits inside the workspace and reading work headless with no setup. **Shell commands are denied by default** in print mode, because nothing can prompt for approval. So agy suits reading, analysis, summarising, review, research, and file edits. It does not suit "build and run the tests" unless you grant a scoped command allowlist (see below). If the task needs to run builds, tests or git, say so to the user and consider `delegate-codex` or a Claude subagent instead.

## Pick the tier

| Work | Claude equivalent | agy model | Notes |
|---|---|---|---|
| Mechanical or well-specified: lookups, summaries, simple edits, boilerplate | Haiku | **flash** (`low`/`medium`/`high`) | Effort is part of the slug |
| Normal implementation, review, moderate reasoning | Sonnet | **sonnet** (`claude-sonnet-*`) | Runs inside Antigravity, uses its quota |
| Hard reasoning | Opus | **opus** (`claude-opus-*-thinking`) | |

Resolve the slug at call time, never hardcode it:

```bash
MODEL=$(bash ~/.claude/skills/delegate-agy/scripts/agy_model.sh flash medium)   # or: sonnet | opus
```

`--effort` conflicts with the flash slugs (agy errors with "conflicts with --effort"). Choose the effort through the slug for flash, and use `--effort low|medium|high|xhigh|max` only with the non-flash models. If a flash result is thin, retry one tier up instead of repeating it. `gpt-oss-120b-medium` also exists but is not part of the tiers.

## Run it

```bash
cd <working dir>      # agy has no -C; it works in the current directory
agy -p "$(cat <scratchpad>/<name>-prompt.md)" \
  --model "$MODEL" --output-format json \
  > <scratchpad>/<name>-result.json 2><scratchpad>/<name>-err.txt
```

Run it with Bash `run_in_background: true` to keep working; add `--print-timeout 20m` (any duration) to bound a stuck run. Use `--add-dir <dir>` to give the worker more directories. Parallel workers should use separate directories or disjoint files.

The result JSON has `conversation_id`, `status`, `response`, `duration_seconds`, `num_turns`, `usage`, and `denied_actions` when something was blocked. Read it with `jq`, for example `jq '{status, response, denied_actions}'`. For live progress use `--output-format stream-json` (events carry the `conversation_id` from the first `init` line), but never read that stream whole.

### Check the result honestly

`status: "SUCCESS"` only means the process ran. A worker blocked on a command still reports SUCCESS with an empty `response`. Treat the run as failed if **any** of these hold:

- `denied_actions` is non-empty, or `response` is empty;
- stderr has `no output produced`;
- the expected files did not change (`git status` / `git diff --stat`).

Verify real work yourself (run the tests, read the diff) rather than trusting the reply.

## Letting the worker run commands (restricted)

Never pass `--dangerously-skip-permissions` to a delegated worker. It removes all containment and was only used to learn how agy behaves. Default print mode already allows edits inside the workspace and auto-denies everything else, so grant exactly the commands the task needs through a per-run `--settings` allowlist.

### Per-project permissions file (don't rebuild the rules each time)

Keep the allowlist in the project, in `.delegate-agy/permissions.json`, and let a script assemble the `--settings` JSON. Commit the file so the user can review what workers are allowed to run.

```bash
S=~/.claude/skills/delegate-agy/scripts/agy_settings.py
python3 $S init                      # once per project: read-only git + ls base, plus build/test/lint profiles detected from the stack
python3 $S show                      # see what is saved
S_JSON=$(python3 $S emit --profile test --extra 'command(dotnet test tests/Foo.Tests)')
agy -p "..." --model "$MODEL" --settings "$S_JSON" --output-format json
python3 $S add 'command(dotnet format --verify-no-changes)' --profile lint   # keep a task rule for next time
```

- **base** rules go into every run (read-only: `git status|diff|log|show`, `ls`). **profiles** (`build`, `test`, `lint`, ...) are added with `--profile`. **`--extra`** rules apply to this run only; use `add` to save one if it will recur.
- The script refuses anything unsafe, so a bad rule cannot slip into the file: only `command(<words>)` prefix rules; no `regex:` or `*`; no shell syntax (`; && | > $( \`` `#`); no shells, interpreters, `rm/cp/mv/touch`, `curl/wget/ssh`, `cat/rg/grep/sed/find` (they read any path), or state-changing git subcommands. If a task genuinely needs one of those, do not work around the script; ask the user.
- `init` never overwrites an existing file (use `--force`). Review the generated profiles once: they are detected from marker files (`.sln`/`.csproj`, `package.json`, `Cargo.toml`, `go.mod`, `pyproject.toml`) and scoped to the plain build/test commands. Prefer a narrow `--extra` (e.g. one test project) over widening a profile.
- Without a permissions file the script exits with a pointer to `init`; run it rather than hand-writing JSON.

### How the rules behave (tested on agy 1.5.3)

- **Use prefix rules, `command(<words>)`.** The command must start with those words; extra arguments are fine (`command(ls)` allowed `ls -la .`). Prefix rules are strict about shell syntax: chains with a command that isn't allowed (`ls . ; rm -f c.txt`, `echo a && ls .`) and redirects (`echo ran > b.txt`) were denied. That strictness is what keeps the worker contained.
- **Never use `regex:` allow rules for commands.** They match the whole raw line, so `command(regex:echo .*)` let `echo a; rm -f c.txt` run and delete a file, and let a redirect write into `$HOME`.
- **Path arguments are not restricted.** An allowed command can touch any path: with `command(touch)` allowed, `touch ~/x` created a file in `$HOME`. So allow only commands that are safe on any path or that only read: build and test runners, `git status/diff/log`, `ls`. (`cat`, `rg`, `grep` read any path, so they are excluded; agy's own file-read and search tools stay inside the workspace.) Do not allow shells or interpreters (`sh`, `bash`, `python`, `node`), `touch`, `cp`, `mv`, `rm`, `chmod`, `curl`, `wget`, `git push/checkout/reset`, or anything that runs arbitrary input.
- **Deny rules do not contain commands.** `command(regex:...)` and `command(touch /home)` deny entries had no effect on an allowed `touch /home/...`. A `write_file(<path>)` deny did block a shell redirect to that path, but redirects are already refused by prefix rules. Don't rely on deny rules as a boundary.
- **`--sandbox` gives nothing here.** It does not enable commands, and with it an allowed command still wrote outside the workspace (`bwrap` exists on this machine, so it is not simply missing). Don't pass it expecting containment.
- Rules apply to this run only; pass them again on resume. Don't put `#` comments in rule strings. Allow, ask and deny are evaluated deny first.

Residual risk: a build or test command runs the project's own code, which can do anything the user can. So give such tasks to projects the user trusts, work in a throwaway git worktree or copy, say "only touch files under the current directory, use relative paths" in the prompt, and check `git status` and the diff afterwards. If the task truly needs arbitrary commands, ask the user before going further instead of widening the rules yourself.

Other flags, tested:

- `--mode auto` is **not available on this account**: agy warns "not available for this account" and falls back to the default mode, so it is not an option here.
- `--mode accept-edits` behaves like the default for headless runs: edits yes, commands no.
- `--mode plan` writes a plan and waits for approval; it creates no files, so it is useless for headless work.
- Writing a file **outside** the workspace with the file tool is denied by default, so the workspace boundary holds for edits. It does not hold for allowed commands (above).

## Pause and resume

A conversation can be continued by id; context is kept (verified):

```bash
ID=$(jq -r .conversation_id <scratchpad>/<name>-result.json)
agy -p "<follow-up or 'You were interrupted; continue, check state first'>" \
  --conversation "$ID" --model "$MODEL" --output-format json > <scratchpad>/<name>-result2.json
```

`-c` continues the most recent conversation, but with parallel workers always pass the explicit id. Resume is also the cheap way to add a follow-up to a finished task. To pause a run, send `kill -INT <pid>` to the PID of the background `agy` you started (never `pkill -f agy`, which can hit the user's own sessions). Resuming after an interrupt works (verified: SIGINT mid-`sleep`, then `--conversation <id>` finished the task and still remembered an earlier instruction). The id comes from the first `init` line of `--output-format stream-json`, so use stream-json if you may need to pause a run before it finishes. The in-flight command is lost, so check `git status` and tell the worker what was interrupted before continuing. Settings from `--settings` are per-run, so pass them again on resume.

## Writing the prompt

Include: the **goal** and why; the **scope** (files it may touch, files it must not); context it can't infer (paths, conventions); a **concrete first action** (name the file or step to start with, so it acts instead of planning); **done criteria**; and a **result contract**: end with one line, `DONE: <summary>` or `BLOCKED: <specific question only the user can answer>`, and no third outcome. If commands are not allowed, say "you cannot run shell commands; edit files only" so it doesn't waste turns trying.

Size the task to something the worker can start without more planning (one file, one module, one question). Split bigger jobs into sequential calls and check dependencies before running chunks in parallel.

## Handling failures

- Empty response / `denied_actions`: a permission block. Add the missing prefix allow rule if it is safe (see the rules above), or move the task to a tool that can run commands.
- Quit without editing: don't rerun the same prompt. Resume the conversation with a direct nudge ("Create `<file>` now"), or shrink the task or move up a tier.
- `invalid model selection`: you passed `--effort` with a flash slug, or the slug no longer exists; rerun `agy_model.sh` and `agy models`.
- Never delegate secrets or content the user wouldn't want sent to a third-party model; agy sends the prompt and the files it reads to Google (or the chosen provider).
