# Flow of the story skills

Two skills: `create-story` plans, `run-story` executes. Colors: Opus = orchestrator, Sonnet = builder, Haiku = tester and fact-finder.

## 1. Big picture

The user starts both skills. They share only files in `docs/stories/` and git, so a chat can be cleared between them.

```mermaid
flowchart LR
  U(["User"]) -->|"/create-story idea"| CS["create-story<br/>Opus · plan mode"]
  CS --> F[("docs/stories/Story-NNN/<br/>Prompt · Plan · CheckList · Phase guides<br/>+ settings.md")]
  F --> RS["run-story<br/>Opus · orchestrator"]
  U -->|"/run-story NNN"| RS
  RS --> G[("git: story branch<br/>one commit per phase")]
  RS --> L[("Learn/Wave-N.md<br/>Learn/Overview.md")]
  RS -->|"brief + questions"| U
```

## 2. create-story: who does what

Discovery runs in parallel with cheap agents. Every design choice goes to the user. Nothing is written before the outline is approved.

```mermaid
flowchart TD
  A["Opus: enter plan mode<br/>read AGENTS.md, contract, last 3 stories"] --> S{"settings.md<br/>exists?"}
  S -->|"no"| D["detect_project.py<br/>(script, no agent)"]
  D -->|"gaps"| X0["Explore · haiku<br/>find build/test commands"]
  D --> Q0["AskUserQuestion<br/>docs language + projects"]
  X0 --> Q0
  S -->|"yes"| P
  Q0 --> P["Discovery: all in one message"]
  P --> X1["Explore · haiku<br/>package internals"]
  P --> X2["Explore · haiku<br/>callers and entry points"]
  P --> X3["Explore · haiku<br/>docs, tests, fixtures"]
  P --> W["general-purpose · sonnet<br/>web search: existing libraries"]
  X1 --> M["Opus: confirm key files itself"]
  X2 --> M
  X3 --> M
  W --> M
  M --> Q["AskUserQuestion rounds<br/>scope · semantics · data · contract<br/>reuse or build · design · rollout"]
  Q --> O["Opus: outline in plan file<br/>decisions · reused tools · phases · waves"]
  O --> AP{"User approves<br/>(ExitPlanMode)?"}
  AP -->|"no"| O
  AP -->|"yes"| WR["Opus: write story files<br/>from templates"]
  WR --> CK["check_story.py<br/>(script)"]
  CK -->|"errors"| WR
  CK -->|"ok"| H["Hand-off message<br/>+ command /run-story NNN"]
```

## 3. run-story: the whole run

Each wave holds phases that may run in parallel. After each wave an explainer writes the study note. The user is asked only on problems, attended phases, or when learning mode is on.

```mermaid
flowchart TD
  L0["Opus: load story<br/>check_story.py · read settings.md"] --> RP["Run plan + AskUserQuestion<br/>branch · pause policy"]
  RP --> CM["Commit story folder<br/>'story NNN: plan'"]
  CM --> WV{"Next wave?"}
  WV -->|"yes"| BASE["Record wave base sha"]
  BASE --> MODE{"Phase mode"}
  MODE -->|"interactive"| IP["Opus runs it itself<br/>Explore haiku fact-finders<br/>AskUserQuestion decisions"]
  MODE -->|"worker"| LOOP["Build → Test loop<br/>(diagram 4)"]
  IP -->|"has code slice"| LOOP
  IP --> CMT
  LOOP --> CMT["Opus: light check + commit<br/>'story NNN phase XX'"]
  CMT --> MG{"Parallel<br/>wave?"}
  MG -->|"yes"| MRG["merge phase branches --no-ff<br/>post-merge verify_phase.py"]
  MG -->|"no"| EX
  MRG --> EX["Explainer agent · Prompt C<br/>writes Learn/Wave-N.md"]
  EX --> BR["Brief to user"]
  BR --> PB{"Problem, attended phase<br/>or learning mode?"}
  PB -->|"yes"| ASK["AskUserQuestion"]
  ASK --> WV
  PB -->|"no"| WV
  WV -->|"no more"| OV["Explainer agent<br/>Learn/Overview.md"]
  OV --> FIN["Final brief<br/>migrations · open items · branch"]
```

## 4. The build → test loop (one worker phase)

Every agent is fresh. State moves only through files and git, so no agent carries a long context.

```mermaid
flowchart TD
  S["Opus: git rev-parse HEAD<br/>= base sha"] --> B1["BUILD agent · fresh<br/>sonnet/low (or per guide)<br/>reads Prompt + guide<br/>runs verify_phase.py until MECHANICAL PASS"]
  B1 -->|"appends"| BN[("Phase-XX-Build-Notes.md")]
  B1 -->|"BUILD: blocked"| UQ["Ask the user"]
  B1 -->|"BUILD: done"| T1["TEST agent · fresh<br/>haiku/high · read-only on code<br/>runs verify_phase.py<br/>reads diff vs guide"]
  BN --> T1
  T1 -->|"overwrites"| TR[("Phase-XX-Test-Result.md")]
  T1 -->|"PASS"| REP["writes Execution-Report<br/>ticks CheckList"]
  REP --> LC["Opus: light check + commit"]
  T1 -->|"FAIL, round 1"| B2["BUILD agent · fresh<br/>round 2: only the numbered Fixes"]
  TR --> B2
  B2 --> T2["TEST agent · fresh<br/>round 2"]
  T2 -->|"PASS"| REP
  T2 -->|"FAIL"| UQ
  T1 -->|"BLOCKED"| UQ
  UQ -->|"one step up / Opus takes over / stop"| B1
```

## 5. Parallel wave with worktrees

Used only when every project builds from the worktree's own files. Otherwise phases run one after another in the main tree.

```mermaid
flowchart LR
  SB[("story branch")] --> W1["worktree s001-p02<br/>branch story/001-p02"]
  SB --> W2["worktree s001-p03<br/>branch story/001-p03"]
  W1 --> L1["Build → Test loop"]
  W2 --> L2["Build → Test loop"]
  L1 --> M1["merge --no-ff"]
  L2 --> M2["merge --no-ff"]
  M1 --> M2
  M2 --> PV["post-merge verify_phase.py<br/>(Opus runs it once)"]
  PV -->|"fails"| FX["fix round: Build → Test<br/>on the story branch"]
  PV -->|"ok"| NX["explainer · next wave"]
```

## Agent roster

| Agent | Model | Started by | Count | Reads | Writes |
|---|---|---|---|---|---|
| Orchestrator | Opus | user | 1 per run | story folder, statuses only | commits, briefs |
| Explore (facts) | haiku | either skill | up to 3 per discovery, more in interactive phases | repo | nothing (report in reply) |
| Library search | sonnet | create-story | 1 | web, manifests | nothing |
| Build | per guide (sonnet/low default) | run-story | 1 per round, max 2 before asking | Prompt, guide, Test-Result | code, tests, Build-Notes |
| Test | per guide (haiku/high default) | run-story | 1 per round | diff, guide, Build-Notes | Test-Result, report, CheckList |
| Explainer | per Prompt C | run-story | 1 per wave + 1 Overview | wave diff, guides | Learn/Wave-N.md |

No agent starts another agent. Only the orchestrator spawns, so nesting depth is 1.
