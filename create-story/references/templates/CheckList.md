# CheckList — Story {{NNN}}: {{Title}}

Nothing is assumed done. Next to each tick, note the test or file that proves it.

## Phase 00 — {{short name}}

- [ ] {{Outcome a reviewer can prove with a test name or a file.}}

## Every phase

- [ ] `dotnet build arena-backend.slnx` and the changed modules' tests are green.
- [ ] `Phase-XX-Test-Result.md` says `VERDICT: PASS` and `verify_phase.py` printed `MECHANICAL: PASS` (worker phases).
- [ ] Model changes that need a migration are listed in the phase report.
- [ ] {{Story-wide rule, e.g. no new locks, docs updated.}}
