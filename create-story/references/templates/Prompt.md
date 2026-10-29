# Story {{NNN}} — {{Title}}

Tier: {{small|large}}

## How to run

{{One paragraph: what exists today, what is wrong or missing, and what this story changes.}}

Read these first:

1. `AGENTS.md` at the repo root, especially {{the sections that matter, e.g. "Concurrency and persistence", "Integration events"}}.
2. {{Large: [PRD](PRD.md) for scope and decisions, }}[Plan](Plan.md) for phase order{{, the shared recipes}} and the stop conditions, [CheckList](CheckList.md) for status.
3. {{The bounded-context and API docs of the modules this story touches: `docs/boundedContexts/<module>.md`, `docs/api/api-<module>.md`.}}
4. {{Any earlier story or code that is the pattern to copy.}}
5. Every `Phase-XX-Execution-Report.md` already in this folder. You start with no memory of earlier phases, and these reports are the only record of what they did.

Run only the phase you are asked to run. The phase guides point at roughly where the code is, not exact lines. If the code disagrees with a guide, follow the code and note the difference in the phase report.

At the end of each phase, write a short `Phase-XX-Execution-Report.md` in this folder: files changed, {{story-specific items}}, tests and results, model changes that need a migration, deviations from the guide, and open items. Then tick the [CheckList](CheckList.md).

## Fixed rules

- Never create or apply migrations. If a model or `DbContext` changes, say in the report that a migration is needed.
- {{Module-boundary rule for the modules involved.}}
- {{Contract rule: which routes, events, keys and error codes must not change.}}
- {{Concurrency rule: no new locks beyond AGENTS.md options 1–4, unless the Plan justifies one.}}
- {{Branch rule: phase branches merge into the story branch, never into `stage`, until the last phase.}}
