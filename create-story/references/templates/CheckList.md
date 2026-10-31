# CheckList — Story {{NNN}}: {{Title}}

Nothing is assumed done. Next to each tick, note the test or file that proves it.

## Phase 00 — {{short name}}

- [ ] {{Outcome a reviewer can prove with a test name or a file.}}

## Every phase

- [ ] The phase's build, test and lint commands (Verification) are green.
- [ ] `Phase-XX-Test-Result.md` says `VERDICT: PASS` and `verify_phase.py` printed `MECHANICAL: PASS` (worker phases).
- [ ] Model changes that need a migration are listed in the phase report.
- [ ] No new dependency, unless the phase guide names it; nothing hand-written that a named library already does.
- [ ] No real model API or network call in tests; no keys, `.env`, model weights or large files committed.
- [ ] {{Story-wide rule, e.g. public API unchanged, docs updated.}}
