---
name: create-story
description: Design and write a phased user story in docs/Ai/Prompts/Story-NNN-*/ that run-story can execute — discovery, decision rounds with the user in plan mode, outline approval, then the story files and a structure check. Use when the user says "/create-story", "write a story for …", or asks to plan a feature as a story.
argument-hint: <what the story should achieve, in your own words>
model: opus
disable-model-invocation: true
---

# Create a story

You turn the user's idea (`$ARGUMENTS`) into a story folder that `/run-story` can execute. The design work happens in plan mode together with the user. Writing the files comes only after they approve the outline.

The shape of every file is fixed by [references/story-contract.md](references/story-contract.md). Read it first. The templates in [references/templates/](references/templates/) are the starting point for each file. `scripts/check_story.py` enforces the contract.

## 1. Enter plan mode and load context

1. Call `EnterPlanMode` (load it with ToolSearch if it is deferred). Stay in plan mode until step 4 is approved. The plan file is your outline.
2. Read `AGENTS.md`, `references/story-contract.md`, and the `Prompt.md` + `Plan.md` + one phase guide of the **last three English stories** in `docs/Ai/Prompts/` (highest numbers whose files are not wrapped in `dir="rtl"`) as style reference.
3. Work out the story number: highest `Story-NNN` in `docs/Ai/Prompts/` plus one. Some numbers are duplicated; never reuse one.
4. If `$ARGUMENTS` is empty or too vague to search for, ask the user what the story should achieve before going further.

## 2. Discovery

Start up to 3 `Explore` agents **in one message** with `model: "haiku"`, each with a focused brief and the repo context they need (module names, what you are looking for, "report paths and short notes, no file dumps"). Typical split:

- the owning module's internals: entities, services, contracts, controllers, locks, jobs, events;
- everything outside it that calls or depends on those parts: Catalog adapters, ports, listeners, other modules, `Startup.cs`;
- docs and tests: the bounded-context and API docs, the test projects and fixtures that cover the area, and any earlier story that did something similar.

Read the few files that matter most yourself, to confirm what the agents reported. Don't plan on facts you haven't checked.

## 3. Decide with the user

Turn each open design question into AskUserQuestion rounds (up to 4 questions per call, 2–4 options each, your recommendation first and marked "(Recommended)", the trade-off in each description; use `preview` for shapes, layouts or code). Cover, as they apply:

- scope (what is in, what is explicitly out);
- behaviour semantics (what happens exactly, edge cases, idempotency, concurrency);
- data: migration, backfill, starting empty, rollback path;
- client-visible contract changes (routes, JSON, roles, error codes, events);
- naming of new modules, schemas, events and roles;
- rollout (one cutover or flagged, which phases must be attended).

Settle conventions the code and `AGENTS.md` already answer without asking, and list them as your own choices. Read every answer carefully: free-text answers often change the question ("maybe X instead"). Follow them, and ask again only if they're still ambiguous. Keep going until no design question is open. Questions that need code facts nobody has yet become work for a Phase 00.

## 4. Outline and approval

Pick the tier from the contract (small or large) and say why. Write the plan file:

- **Context**: the problem and the outcome.
- **Decisions**: a table, marking which ones the user made and which you made.
- **Key design points**: the parts a worker would otherwise get wrong.
- **Phases**: a table with No, Title, Mode, Depends on, Attended, Builder, Tester, and one line of scope each. Rules:
  - `run-story` runs each worker phase as a loop: a fresh **build** agent writes the code and tests from the guide, then a fresh **test** agent checks the result read-only (a script for build, tests and rule greps, then the diff against the guide) and returns PASS or a fix list for the next build round. Neither agent has your design context or memory of other rounds. The point is to let cheap models do the work, so the design judgement has to live in the guide, not in the worker;
  - size a phase for one `sonnet/low` build session: one or two vertical slices with concrete steps, never "the whole module". If a phase only works with a smarter builder, split it or move the open decisions into an interactive phase;
  - decisions and design work go in `interactive` phases, and code goes in `worker` phases;
  - production and maintainer steps are `Attended: yes`;
  - pick the cheapest pair that can do the phase safely:

    | Phase kind | Builder | Tester |
    |---|---|---|
    | Docs only, checklists, inventories, renames | `haiku/medium` | `haiku/low` |
    | Default: pattern copies, moves, dead-code removal, characterization tests, normal code with explicit steps | `sonnet/low` | `haiku/high` |
    | Risky: persistence model, transactions, locks, events, crossing module boundaries, many files | `sonnet/medium` | `haiku/high`, and the guide says it is high-risk |

  - interactive phases with no code get `Builder: none` and `Tester: none`; an interactive phase with a code slice gets a pair for that slice;
  - make phases parallel only when they touch different code. List the shared files they will both append to.
- **Waves**: a wave holds phases that run in parallel; sequential phases go in separate waves.
- **Files to write**: the file list for the story folder.

Call `ExitPlanMode`. If the user rejects it or comments, revise the plan and call it again. Write nothing outside the plan file before approval.

## 5. Write the story

Create `docs/Ai/Prompts/Story-NNN-Title-In-Kebab-Case/` and write each file from its template:

- Replace every `{{placeholder}}`. Drop optional sections that don't apply instead of leaving them empty.
- Write in English. Diagrams are Mermaid only. The phase-dependency flowchart uses nodes `P00`, `P01`, …, and its edges equal the `Depends on` headers.
- Each phase guide is written for two readers who know nothing but the guide, `Prompt.md` and the code:
  - `## Implementation` (builder): numbered steps naming real files and types ("roughly where", no line numbers), the pattern to copy, and the decision each step relies on, spelled out rather than referenced ("per D3" is not enough; say what D3 means here);
  - `## Tests` (builder): the test project, the class, and the behaviour each test proves;
  - `## Verification` (tester): the exact `dotnet test …` commands, one per line in backticks (the tester feeds them to `verify_phase.py`), then 2–6 review points it can confirm from the diff alone, for example "a duplicate insert maps to `SSOException` 01xxx" or "no `Bina.Duel` file references `Bina.Learning`". Don't ask the tester to judge design;
  - `## Exit criteria`: what must hold for PASS;
  - a phase prompt starting `> Run only Phase NN of Story NNN.`
- Before you cite a path in a guide, check it exists with Glob or Grep. Files the story creates are fine to cite.
- The CheckList has provable items per phase ("proved by" a test name or a file), plus `## Every phase`.
- Don't write execution reports or the `Build-Notes` / `Test-Result` handoff files. `run-story` writes those.
- Carry the repo's hard rules into `Fixed rules`: no migrations by agents, module boundaries, contracts kept, the AGENTS.md concurrency options, branches never merged into `stage` mid-story.

## 6. Check

Run `python3 -I .claude/skills/create-story/scripts/check_story.py docs/Ai/Prompts/<folder>`. Fix every error and run it again until it passes. Warnings about paths are fine only for files the story itself will create; fix any other warning.

## 7. Hand off

End with a short message:

- the folder and the tier;
- the phase table (No, Title, Mode, Attended, Builder, Tester) and the waves;
- the migrations the story expects the maintainer to create;
- the decisions the user made, and separately the choices you made on your own;
- the command to start it: `/run-story NNN`. Don't start it yourself.

Don't commit unless the user asks.
