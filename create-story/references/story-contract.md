# Story contract

`create-story` writes stories in this shape, `run-story` executes them, and `scripts/check_story.py` enforces it. Change all three together.

## Folder

`docs/stories/Story-NNN-Title-In-Kebab-Case/`

- `NNN` is the highest existing story number plus one (`001` for the first). Never reuse a number.
- English, Markdown, no `<div dir="rtl">` wrappers. Every diagram is a fenced `mermaid` block with quoted labels and no brackets or parentheses inside labels (use `·` and `<br/>`).

## Tiers

| Tier | When | Files |
|---|---|---|
| small | One module, no new schema or cutover, about 1–3 phases | `Prompt.md`, `Plan.md`, `CheckList.md`, phase guides |
| large | New module, data or schema migration, cross-module contract changes, a cutover, or more than 4 phases | the above plus `PRD.md`; Phase 00 is a discovery/decisions phase (`Mode: interactive`); the last phase is a cutover/cleanup/docs phase (`Mode: interactive`, `Attended: yes`) |

`Prompt.md` declares the tier on its own line right under the H1: `Tier: small` or `Tier: large`.

## Files

### `Prompt.md`

```
# Story NNN — Title

Tier: small | large

## How to run
<one paragraph: what exists today, what the story changes>
Read these first:
1. `AGENTS.md` or `CLAUDE.md` … (numbered; story docs; module docs; last item is always every `Phase-XX-Execution-Report.md` in this folder)
<run-one-phase rule; "follow the code, note the difference" rule>
<report rule: what goes into Phase-XX-Execution-Report.md, then tick the CheckList>

## Fixed rules
- bullet list of hard rules (migrations, module boundaries, contracts, branches)
- the "How we build" rules from the template: reuse before you build, right-sized design, smallest complete change, and the AI and secrets lines
```

### `PRD.md` (large only)

Sections: `## Problem`, `## Goals`, `## Non-goals`, `## Decisions` (table `Topic | Decision`), `## Reused tools` (table `Capability | Tool | Use as is / customize / built here | Why`), a scope or ownership table, the behaviour spec of anything new, `## Acceptance criteria`.

### `Plan.md`

1. Optional `## Target shape` with a Mermaid diagram.
2. `## Phase order`: numbered list of links, one per phase: `1. [Phase 00 — Title](Phase-00-Title.md)`.
3. A Mermaid `flowchart` of phase dependencies. Nodes are `P00`, `P01`, … and every edge `PXX --> PYY` means "YY depends on XX". The edges equal the phase headers' `Depends on` exactly.
4. The waves table:

   ```
   | Wave | Phases | Start when |
   |---|---|---|
   | 1 | 00 | Now |
   | 2 | 01, 02 | Phase 00 is merged |
   ```

   A wave lists phases that may run **in parallel**. Sequential phases go in separate waves. Every phase is in exactly one wave, and a wave comes after the waves of all its dependencies.
5. The session start line: `> Read \`docs/stories/<folder>/Prompt.md\` and run Phase NN.`
6. If any wave has more than one phase: the shared files parallel phases touch, and "only append, keep both sides on conflict".
7. Shared recipes, guardrails, stop conditions (as needed).

### `CheckList.md`

```
# CheckList — Story NNN: Title

Nothing is assumed done. Next to each tick, note the test or file that proves it.

## Phase NN — <short name>
- [ ] <provable outcome>

## Every phase
- [ ] build, tests and lint green · migrations listed in the report · …
```

One `## Phase NN` section per phase, then `## Every phase`.

### `Phase-NN-Title-In-Kebab-Case.md`

```
# Story NNN / Phase NN — Title

Mode: worker
Depends on: none
Attended: no
Builder: sonnet/low
Tester: haiku/medium

## Goal
## Implementation
## Tests
## Verification
## Exit criteria
## Phase prompt

> Run only Phase NN of Story NNN. <one or two sentences>. Write the phase report.
```

| Field | Values | Meaning |
|---|---|---|
| `Mode` | `worker`, `interactive` | `interactive`: the orchestrator runs it itself with the user (decisions, design, runbooks). `worker`: a worker agent runs it |
| `Depends on` | `none` or `02, 03` | Phases that must be merged first |
| `Attended` | `no`, `yes` | `yes`: never start without the user's go-ahead (production steps, maintainer work) |
| `Builder` | `haiku/low`, `haiku/medium`, `haiku/high`, `sonnet/low`, `sonnet/medium`, `none` | Model and effort of the build agent, which writes the code and tests (also for the code part of an interactive phase); `none` only for an interactive phase with no code |
| `Tester` | same values | Model and effort of the test agent, which checks the build read-only; `none` exactly when `Builder` is `none` |

Older stories have a single `Worker:` line instead of `Builder:` / `Tester:`. `run-story` reads it as the builder, with a `haiku/medium` tester, and the checker only warns about it. New stories always use the two lines.

### Who reads which section

A worker phase runs as a loop of two fresh agents (see `run-story`): a **build** agent writes code and tests, then a **test** agent verifies read-only and returns PASS or a fix list; on FAIL a new build agent fixes it. Neither agent carries memory between rounds and neither knows the design discussion, so each section must stand on its own:

| Section | Read by | Write it as |
|---|---|---|
| `Goal` | both | One or two sentences on the end state |
| `Implementation` | builder | Numbered, concrete steps: which file, which type, which library and API to use, which pattern to apply and what goes where, which decision applies. A `sonnet/low` builder must be able to follow it without design judgement |
| `Tests` | builder | The tests to write: project, class, the behaviours each test proves |
| `Verification` | tester | The exact commands, one per line as `` `<build|test|lint> <dir>: <command>` `` with the project folder and commands from `docs/stories/settings.md`, then 2–6 review points the tester can check from the diff alone, e.g. "a duplicate insert raises `OrderExists`", "nothing in `app/billing` imports `app.auth`", "no new dependency in the manifest" |
| `Exit criteria` | tester | What must be true for PASS |

Guides point at real files ("roughly where"), not line numbers. They never contain run output. `run-story` writes these files next to each guide:

| File | Written by | Content |
|---|---|---|
| `Phase-NN-Build-Notes.md` | build agent, one `## Round N` block appended per round | files changed, what was done, what the builder was unsure of |
| `Phase-NN-Test-Result.md` | test agent, overwritten each round | `VERDICT: PASS`, `FAIL` or `BLOCKED`, the `verify_phase.py` summary, a numbered fix list |
| `Phase-NN-Execution-Report.md` | test agent on PASS (the orchestrator for interactive phases) | the phase report described in `Prompt.md` |
| `Learn/Wave-N.md`, `Learn/Overview.md` | explainer agent after each wave / the last wave | learning docs for the developer, in the settings' docs language; outside the contract, `check_story.py` ignores `Learn/` |

`docs/stories/settings.md` (shared by all stories) holds the docs language, the developer's level, `Learning mode: on|off`, the projects with their build/test/lint commands, and the concepts the learning docs already explained.
