# Experiment plan: cheaper runs, same or better quality

Goal: lower the tokens per story without lowering quality. Each experiment changes one thing and is judged on the same scorecard, so we can keep or drop the change.

## Scorecard (measured per story, from the session transcripts)

| Metric | What it says | Source |
|---|---|---|
| Cost-equivalent tokens (cache-read ×0.1, cache-write ×1.25, output ×5) | money | transcript `usage` of the chat and of every subagent file |
| First-round PASS rate | quality of guides and builder | `Phase-XX-Test-Result.md` of round 1 |
| Rounds per phase | rework | count `## Round` in Build-Notes |
| Fixes per FAIL | how much the tester finds | numbered Fixes lists |
| Escalations to the user | where cheap agents give up | BLOCKED or second FAIL |
| Diff size vs the guide | over-building | `git diff --stat <base>` |
| Post-merge failures | hidden breakage | the post-merge `verify_phase.py` |
| Study-note check | doc quality | `learn_doc.py` + a manual read |

A change is accepted only if cost drops and first-round PASS rate, rounds and escalations do not get worse.

## Experiments

| # | Question | How | Status |
|---|---|---|---|
| E1 | Where do the tokens go per role? | Script over the transcript: tokens per agent (orchestrator, build, test, explainer) | Done for Story-001 earlier: story is about 5% of the old chat; chat length dominates |
| E2 | Can a subagent start a subagent (needed for `context: fork`)? | One haiku agent tries to spawn another | Done: a haiku subagent started a child and got `CHILD-RAN`. Nesting works here (depth 2). The CLI output has a `refused.depth_limit` counter, so a deeper limit exists. Not yet tested: a real `context: fork` skill |
| E3 | Does `claude -p "/run-story NNN"` work (skills, permissions, questions)? | Needs `claude` CLI login in a terminal; run in a throwaway repo with `--max-turns` and `--output-format json` | Done (partly), haiku, scratch repo: `claude -p "/probe"` does NOT run the skill (treated as plain text). `-p "Use the Skill tool to run probe"` works, but only without `disable-model-invocation: true`. A `context: fork` skill ran and started a child (`max_depth` 2, `CHILD-RAN`). Not yet tested: AskUserQuestion, file-write permissions and git in `-p`, and the real run-story |
| E4 | Does a lower auto-compact window (100k) hurt the run? | Run the same small story twice, with and without the setting | Not started |
| E5 | Is a fresh chat per wave cheaper and equal in quality? | Same story: one chat vs `/clear` between waves; compare the scorecard | Not started |
| E6 | Can the tester drop from `haiku/high` to `haiku/medium`? | Re-run the test step of finished phases at both efforts; compare verdicts and fix lists | Not started |
| E7 | Is the explainer worth `sonnet`, or does `haiku` write an equal note? | Same wave diff, two models, compare by `learn_doc.py` and a read | Not started |
| E8 | How much do shorter prompts A/B save? | Cut text that agents never use; compare first-round PASS rate | Not started |
| E9 | Do fewer plugins cut the subagent floor? | First-turn `cache_creation` of a subagent before (about 54K) and after the plugin removal | Needs a new chat |

## Results: tiny one-phase story (slugify, 4 tests), headless driver, 2026-10-31

| Run | Orchestrator | Builder | Tester | Explainer | Cost-eq tokens | $ | Quality |
|---|---|---|---|---|---|---|---|
| 1 | sonnet-5/medium (unpinned) | sonnet-5/medium (asked low) | haiku-4.5 (asked high) | sonnet-5/medium | 1,497K | 1.39 | PASS round 1 |
| 2 pinned agents | opus-5.5/medium 660K | sonnet-5.5/low 169K | haiku-5.5/high 515K | 2 docs 237K | 1,580K | 1.52 | PASS round 1, Wave + Overview |
| 3 cost fixes | opus-5.5/medium 280K | sonnet-5.5/low 75K | haiku-5.5/medium 198K | 1 doc 48K | 601K | 0.74 | PASS round 1, Wave doc |

Run 3 changes: worker agents limited to 6 tools, `--strict-mcp-config` (no MCP), tester without design judgement and default `haiku/medium`, no Overview for one-wave stories, fewer orchestrator turns, `--auto` in the skill. Found on the way: the `haiku` / `sonnet` aliases resolve to Haiku 4.5 / Sonnet 5 and `effort` on Agent calls was ignored; the `story-worker-*` agents pin both, `check_models.py` checks every wave. One small story only: confirm on a real multi-phase story before trusting the numbers.

## Results: real story (kb-pipeline Story-001, copy), wave 3 = Phase 04 scanner adapters

| Wave | Cost | Turns | Models | Outcome |
|---|---|---|---|---|
| 3 | $1.08 | 11 | MODELS: PASS (opus/medium, sonnet/medium ×2, haiku/high ×2) | 2 rounds, then BLOCKED; questions in NEEDS-USER.md, driver stopped as designed |

Found: the story's docker test commands mount a fixed path (`-v E:/Project-Arian/kb-pipeline:/w`), so testers in worktrees or copies test the main tree. Fix to make in the skill: a `{repo}` placeholder that `verify_phase.py` fills with the current tree, and a create-story warning on absolute repo paths.

## Order

1. E2 now (done below). E9 and E1 need no extra runs.
2. E3 after the user runs `claude` once in a terminal and logs in. It decides whether a per-wave driver is possible.
3. E5 and E4 on a small real story, such as Wave 2 of Story-001 as the test case.
4. E6, E7, E8 after that, one at a time, only for the roles that cost the most.

## Rules for every run

- Throwaway repo or a story branch. Nothing is pushed.
- Record the scorecard in `results/<experiment>.md` next to the story.
- Keep a change only if the scorecard rule above holds. Otherwise revert it.
