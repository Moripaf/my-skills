# Story {{NNN}} — {{Title}}

Tier: {{small|large}}

## How to run

{{One paragraph: what exists today, what is wrong or missing, and what this story changes.}}

Read these first:

1. `{{AGENTS.md|CLAUDE.md}}` at the repo root, especially {{the sections that matter}}.
2. {{Large: [PRD](PRD.md) for scope and decisions, }}[Plan](Plan.md) for phase order{{, the shared recipes}} and the stop conditions, [CheckList](CheckList.md) for status.
3. {{The docs and the main modules this story touches, e.g. `docs/api.md`, `src/<pkg>/<module>.py`.}}
4. {{Any earlier story or code that is the pattern to copy.}}
5. Every `Phase-XX-Execution-Report.md` already in this folder. You start with no memory of earlier phases, and these reports are the only record of what they did.

Run only the phase you are asked to run. The phase guides point at roughly where the code is, not exact lines. If the code disagrees with a guide, follow the code and note the difference in the phase report.

At the end of each phase, write a short `Phase-XX-Execution-Report.md` in this folder: files changed, {{story-specific items}}, tests and results, model changes that need a migration, deviations from the guide, and open items. Then tick the [CheckList](CheckList.md).

## Fixed rules

- Never create or apply migrations (Alembic, Django or any other). If a model changes, say in the report that a migration is needed.
- {{Module-boundary rule for the packages involved, e.g. "`app/billing` never imports `app.auth`".}}
- {{Contract rule: which public functions, routes, CLI flags, settings and exceptions must not change.}}
- Phase branches merge into the story branch, never into `{{default branch}}`, until the last phase.

How we build (every phase):

- Reuse before you build: the library or tool the guide names, then a helper already in this repo, then the standard library, then an installed package. Never hand-write what a named library does, and never add a dependency the guide doesn't name.
- Right-sized design: follow the repo's architecture and the structure and pattern the guide names. One responsibility per module, function and class; external services ({{model APIs, vector stores, …}}) only through their adapter ({{e.g. `app/llm/client.py`}}). No layer, interface, base class, option or config with a single use or nobody asking for it, and no business logic in route handlers or scripts.
- Finish everything the step needs, including the callers, tests and fixtures it breaks. Nothing more.
- A shortcut with a known limit gets a comment: `# shortcut: <the limit>, <when to upgrade>`.
- New non-trivial logic (a branch, a loop, a parser, money or security) gets at least one small test.
- Never cut validation at trust boundaries, error handling that prevents data loss, or security.
- Tests never call a real model API, the network or a paid service; they use {{the repo's fakes / mocks / recorded responses}}. Evals against real models run only in an attended phase.
- Model output is validated before use ({{e.g. a Pydantic model}}); every model call has a timeout and a bounded retry.
- Never commit keys, tokens, `.env` files, model weights or large data files.
- Comment only the why the code can't show.
