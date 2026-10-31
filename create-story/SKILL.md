---
name: create-story
description: Design and write a phased user story for any project (Python, .NET, JS/TS, Go, Java, PHP, Rust, …) in docs/stories/Story-NNN-*/ that run-story can execute — discovery, decision rounds with the user in plan mode, outline approval, then the story files and a structure check. Use when the user says "/create-story", "write a story for …", or asks to plan a feature as a story.
argument-hint: <what the story should achieve, in your own words>
model: opus
disable-model-invocation: true
---

# Create a story

You turn the user's idea (`$ARGUMENTS`) into a story folder that `/run-story` can execute. The design work happens in plan mode together with the user. Writing the files comes only after they approve the outline.

The shape of every file is fixed by [references/story-contract.md](references/story-contract.md). Read it first. The templates in [references/templates/](references/templates/) are the starting point for each file. `scripts/check_story.py` (in this skill's folder) enforces the contract.

Three principles shape every story. Apply them in the design, not just in the rules, because the cheap workers that run the phases can't make these calls:

1. **Reuse before you build.** Most features already exist somewhere: in this repo, in the standard library, in an installed package, or as a mature open-source library or tool. Find it first and use it as is or customize it. Writing it ourselves is the last option and needs a stated reason. This avoids repeated work and saves tokens in every later phase.
2. **Right-sized design.** Follow normal software-engineering practice and the architecture the repo already has: one responsibility per module, function and class; clear boundaries; dependencies pointing inward; external services (model APIs, vector stores, queues) behind one thin adapter. Use a design pattern when it solves a problem the story really has (an Adapter around a vendor SDK, a Strategy once two real variants exist, a Factory where the configuration picks the implementation), never for a variant that might come later. Neither over-built (layers, interfaces or base classes with a single use, config nobody sets) nor under-built (business logic in route handlers, one function doing several jobs, copy-pasted near-duplicates).
3. **Smallest complete change.** Each phase builds the smallest version that fully does its job, including the callers, tests and fixtures it touches, and nothing nobody asked for.

## 1. Enter plan mode and load context

1. Call `EnterPlanMode` (load it with ToolSearch if it is deferred). Stay in plan mode until step 4 is approved. The plan file is your outline.
2. Read `AGENTS.md` and/or `CLAUDE.md` (whichever exist), `references/story-contract.md`, and the `Prompt.md` + `Plan.md` + one phase guide of the **last three stories** in `docs/stories/` as style reference. With no earlier stories, the templates are the reference.
3. Load `docs/stories/settings.md`, shared by all stories. If it exists, use it and ask nothing. If it doesn't, set it up once, as cheaply as possible:
   - Run `<python> -I <this skill's folder>/scripts/detect_project.py --repo <repo root>`. It reads only manifest files (`pyproject.toml`, `package.json`, `*.sln`, `go.mod`, `pom.xml`, `composer.json`, `Cargo.toml`, …) at the root and two folders down, and prints a table of projects with their build, test and lint commands. `<python>` is `python`, else `python3`, else `py -3` (on Windows `python3` is often only the Microsoft Store stub).
   - Only if it prints `none detected` or a row lacks a test command: start one `Explore` agent with `model: "haiku"` and a narrow brief ("find the build, test and lint commands and the folders they run in, from README, CI config, Makefile, scripts; report a table, no file dumps").
   - Ask one AskUserQuestion call with two questions: **Docs language** (header `Docs`): فارسی / English, for the learning docs `run-story` writes after each wave; and **Projects** (header `Projects`), with the table in the option's preview: Looks right / I'll correct it (then take the corrections in chat).
   - Note the result in the plan and write the file in step 5 with the story (plan mode allows no other writes):

   ```markdown
   # Story settings

   Docs language: fa
   Level: Intermediate-Advanced
   Learning mode: off

   ## Projects
   | Dir | Stack | Build | Test | Lint |
   |---|---|---|---|---|
   | `Code` | python | - | `uv run pytest -q` | `uv run ruff check .` |

   ## Explained concepts
   None yet.
   ```

   Several commands in one cell are separated by ` ; ` and run one by one. `Intermediate-Advanced`: the reader knows the language and the basics; the learning docs explain the design, patterns, trade-offs and failure modes, and define only project or domain terms. `Learning mode: on` makes you ask for the user's approach on consequential design questions (below) and makes `run-story` pause after each wave; off, the docs are still written and nothing pauses. Never overwrite an existing settings file; the user changes it by hand.
4. Work out the story number: highest `Story-NNN` in `docs/stories/` plus one (`001` if none). Never reuse one.
5. If `$ARGUMENTS` is empty or too vague to search for, ask the user what the story should achieve before going further.

## 2. Discovery

Start up to 3 `Explore` agents **in one message** with `model: "haiku"`, each with a focused brief and the repo context they need (module names, what you are looking for, "report paths and short notes, no file dumps"). Typical split:

- the owning package's internals: models, services, functions, classes, routes or CLI commands, settings, background jobs;
- everything outside it that imports or calls those parts, and the entry points (app factory, `__main__`, CLI, settings, dependency injection);
- docs and tests: README and `docs/`, the test files and fixtures that cover the area (and how they fake model APIs and the network), helpers in the repo that a phase can reuse, and any earlier story in `docs/stories/` that did something similar.

In the same message, start one more `general-purpose` agent with `model: "sonnet"` for **existing solutions**. Brief it with each capability the story needs, in plain words ("retry LLM calls with backoff", "structured output into Pydantic models", "chunk and embed PDFs"), the stack and its version, and the packages already installed (from the manifest and lock file of each project in settings). It uses WebSearch and WebFetch and reports, per capability, up to three candidates: the package or tool, what part of the need it covers, maturity (latest release date, maintenance, adoption), license, how it fits the installed stack, and roughly how much of our own code it would replace. It also says when an installed package already covers the need. Report only, no file dumps, no installs.

Read the few files that matter most yourself, to confirm what the agents reported. Don't plan on facts you haven't checked.

## 3. Decide with the user

With `Learning mode: on`, open each consequential design question (structure, pattern, reuse or build, data shape) as a learning step first, the way VibeWise does: explain an unfamiliar concept in two or three plain sentences in the user's language, ask in chat how they would approach it, and wait. Give feedback on their actual reasoning, then ask the AskUserQuestion round with their idea among the options when it is viable. Don't do this for conventions or small choices. Then, in both modes, turn each open design question into AskUserQuestion rounds (up to 4 questions per call, 2–4 options each, your recommendation first and marked "(Recommended)", the trade-off in each description; use `preview` for shapes, layouts or code). Cover, as they apply:

- scope (what is in, what is explicitly out);
- behaviour semantics (what happens exactly, edge cases, idempotency, concurrency);
- data: migration, backfill, starting empty, rollback path;
- public contract changes (functions, routes, JSON, CLI flags, settings, exceptions);
- naming of new packages, modules, tables and settings;
- **reuse or build**, one question per capability where a real candidate exists: use the library as is, use it and customize it (a thin adapter or subclass in our code), or build it ourselves. Put the candidate's maturity and license in the description. Building ourselves needs a stated reason (no mature option, license, size of the dependency against what we use, a hard constraint);
- the design shape where the code doesn't already decide it: where each responsibility lives, and the pattern for it, with the reason;
- AI-specific behaviour, as it applies: which model or provider, prompts and where they live, structured-output validation, retries, timeouts and cost limits, and how tests fake the model (no real API calls in tests; evals against real models go in an attended phase);
- rollout (one cutover or flagged, which phases must be attended).

Settle conventions the code, `AGENTS.md` and `CLAUDE.md` already answer without asking, and list them as your own choices. Read every answer carefully: free-text answers often change the question ("maybe X instead"). Follow them, and ask again only if they're still ambiguous. Keep going until no design question is open. Questions that need code facts nobody has yet become work for a Phase 00.

## 4. Outline and approval

Pick the tier from the contract (small or large) and say why. Write the plan file:

- **Context**: the problem and the outcome.
- **Decisions**: a table, marking which ones the user made and which you made.
- **Reused tools**: per capability, the library or tool chosen (or "built here" with the reason), the version range, and whether it is already installed.
- **Key design points**: the parts a worker would otherwise get wrong, including the structure and the design pattern for each new part and why it is the right size.
- **Skipped on purpose**: features, options and flexibility left out to keep the story the smallest version that does the core job, one line each.
- **Phases**: a table with No, Title, Mode, Depends on, Attended, Builder, Tester, and one line of scope each. Rules:
  - `run-story` runs each worker phase as a loop: a fresh **build** agent writes the code and tests from the guide, then a fresh **test** agent checks the result read-only (a script for build, tests and rule greps, then the diff against the guide) and returns PASS or a fix list for the next build round. Neither agent has your design context or memory of other rounds. The point is to let cheap models do the work, so the design judgement has to live in the guide, not in the worker;
  - size a phase for one `sonnet/low` build session: one or two vertical slices with concrete steps, never "the whole module". If a phase only works with a smarter builder, split it or move the open decisions into an interactive phase;
  - decisions and design work go in `interactive` phases, and code goes in `worker` phases;
  - production and maintainer steps are `Attended: yes`;
  - pick the cheapest pair that can do the phase safely:

    | Phase kind | Builder | Tester |
    |---|---|---|
    | Docs only, checklists, inventories, renames | `haiku/medium` | `haiku/low` |
    | Default: pattern copies, moves, dead-code removal, characterization tests, normal code with explicit steps | `sonnet/low` | `haiku/medium` |
    | Risky: persistence model, transactions, concurrency, async, crossing package boundaries, many files | `sonnet/medium` | `haiku/high`, and the guide says it is high-risk |

  - interactive phases with no code get `Builder: none` and `Tester: none`; an interactive phase with a code slice gets a pair for that slice;
  - make phases parallel only when they touch different code. List the shared files they will both append to.
- **Waves**: a wave holds phases that run in parallel; sequential phases go in separate waves.
- **Files to write**: the file list for the story folder.

Call `ExitPlanMode`. If the user rejects it or comments, revise the plan and call it again. Write nothing outside the plan file before approval.

## 5. Write the story

Create `docs/stories/Story-NNN-Title-In-Kebab-Case/` and write each file from its template. Write `docs/stories/settings.md` too if step 1 set it up:

- Replace every `{{placeholder}}`. Drop optional sections that don't apply instead of leaving them empty.
- Write in English. Diagrams are Mermaid only. The phase-dependency flowchart uses nodes `P00`, `P01`, …, and its edges equal the `Depends on` headers.
- Each phase guide is written for two readers who know nothing but the guide, `Prompt.md` and the code:
  - `## Implementation` (builder): numbered steps naming real files, functions and classes ("roughly where", no line numbers), the existing helper, library or pattern to reuse, and the decision each step relies on, spelled out rather than referenced ("per D3" is not enough; say what D3 means here). When a step uses a library, name the package, the exact API to call, and the dependency line to add if it is new; the builder adds no dependency the guide doesn't name. When a step introduces a pattern, name it and say what goes where ("`LLMClient` in `app/llm/client.py` is the only module that imports `anthropic`"). Write the smallest steps that fully do the job;
  - `## Tests` (builder): the test file, the test functions or class, the fixtures to reuse, how model APIs and the network are faked, and the behaviour each test proves;
  - `## Verification` (tester): the exact commands, one per line (split a settings cell at ` ; `: `verify_phase.py` refuses `;`, `&`, `|`, `<`, `>`, `` ` `` and `$`), each as `` `<kind> <dir>: <command>` `` where kind is `build` (must pass, every error counts), `test` or `lint` (only issues on changed lines count) and dir is the project folder from settings (`.` for the root). The tester feeds them to `verify_phase.py`. Narrow the test command to this phase's tests where the runner allows it (`test Code: uv run pytest tests/test_orders.py`, `test .: dotnet test tests/Orders.Tests`, `test web: npm test -- orders`). Then 2–6 review points it can confirm from the diff alone, for example "a duplicate insert raises `OrderExists`", "nothing in `app/billing` imports `app.auth`" or "no new dependency in the manifest". Don't ask the tester to judge design;
  - `## Exit criteria`: what must hold for PASS;
  - a phase prompt starting `> Run only Phase NN of Story NNN.`
- Before you cite a path in a guide, check it exists with Glob or Grep. Files the story creates are fine to cite.
- The CheckList has provable items per phase ("proved by" a test name or a file), plus `## Every phase`.
- Don't write execution reports or the `Build-Notes` / `Test-Result` handoff files. `run-story` writes those.
- Carry the repo's hard rules into `Fixed rules`: no migrations by agents, package boundaries, contracts kept, any rule from `AGENTS.md` / `CLAUDE.md`, branches never merged into the default branch mid-story. Keep the template's "How we build" block as is, and fill its AI lines when the story touches model calls.

## 6. Check

Run `<python> -I <this skill's folder>/scripts/check_story.py docs/stories/<folder>`. Fix every error and run it again until it passes. Warnings about paths are fine only for files the story itself will create; fix any other warning.

## 7. Hand off

End with a short message:

- the folder and the tier;
- the phase table (No, Title, Mode, Attended, Builder, Tester) and the waves;
- the migrations the story expects the maintainer to create;
- the decisions the user made, and separately the choices you made on your own;
- the reused tools per capability, and what was built here and why;
- what was skipped on purpose, and any risk the user must know;
- that `run-story` writes a learning doc per wave and an Overview in `Learn/`, in the docs language (and pauses for it when learning mode is on);
- the command to start it: `/run-story NNN`, best in a fresh chat (`/clear` or a new one): it needs nothing from this chat, and a long chat is re-read on every turn. Don't start it yourself.

Don't commit unless the user asks.
