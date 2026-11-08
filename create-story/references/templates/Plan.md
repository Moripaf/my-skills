# Plan — Story {{NNN}}: {{Title}}

## Target shape

{{Optional, large stories. A Mermaid diagram of modules and the contracts between them, then 2–4 bullets.}}

## Phase order

1. [Phase 00 — {{Title}}](Phase-00-{{Title-In-Kebab-Case}}.md)
2. [Phase 01 — {{Title}}](Phase-01-{{Title-In-Kebab-Case}}.md)

```mermaid
flowchart LR
  P00["Phase 00<br/>{{short}}"] --> P01["Phase 01<br/>{{short}}"]
```

| Wave | Phases | Start when |
|---|---|---|
| 1 | 00 | Now |
| 2 | 01 | Phase 00 is merged |

## Dependency schedule

`run-story` can run by the waves above, or start each phase as soon as the phases it depends on are merged. The second way doesn't wait for a whole wave. Each row lists one or more phases and the phases they need merged first (`Now` means none).

| Phase | Starts when merged |
|---|---|
| 00 | Now |
| 01 | 00 |

Critical path: {{the longest dependency chain, e.g. 00 → 01 → 03 → 05}}. When more phases are ready than may run at once, phases on the critical path go first, then phases that unblock the most others.

Start each phase in a fresh session from a clean tree:

> Read `docs/stories/{{Story-NNN-Folder}}/Prompt.md` and run Phase NN.

{{If any two phases can run at the same time, in a wave or in the dependency schedule: "Parallel phases touch the same shared spots: <files>. Only append your own lines there; on a conflict, keep both sides."}}

## {{Shared recipe: <name>}}

1. {{Steps every phase of this kind follows, with the existing code to copy.}}

## Guardrails

- {{Rules that apply across phases.}}

## Stop conditions

Stop and ask the maintainer if:

- {{situations where the worker must not guess}}
