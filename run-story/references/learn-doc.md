# Learning docs

After each wave, a fresh **explainer** agent writes a document that teaches the developer what the wave built and why. The developer often vibe-codes: the agents did the work, so without this doc they can't explain their own system. The doc is a study note: short sentences, the decisions taken with the reason and what each one changes later, and the key ideas. It borrows VibeWise's way of teaching a concept and tying it to this project, without quizzes.

**What decides a good doc is understanding, not length:** after one read the developer knows what happened, how it works and why it was built this way. There is no size target: many short sentences are fine, but each must carry a fact, a decision or a reason. Never pad and never cut what the reader needs. Nothing is left bare: every code block, command, table or diagram comes with its explanation.

## Files

All in `<story folder>/Learn/`:

| File | Written | Content |
|---|---|---|
| `Wave-<N>.md` | after every wave is merged and checked | what that wave built, how and why |
| `Overview.md` | after the last wave, only for stories with two or more waves | the whole story as one system: the end-to-end flow, how the waves fit, the main concepts |

Settings come from `docs/stories/settings.md`: `Docs language` (`fa` or `en`), `Level` (default `Intermediate-Advanced`), and the `Explained concepts` list. `scripts/learn_doc.py` wraps the body in the house style (Mikhak font for Persian and English, colours, callouts; [style-header.html](style-header.html)), so the explainer never reads or writes CSS. `check_story.py` ignores `Learn/`.

## Prompt C — explainer agent

Run it with `subagent_type: "story-worker-sonnet-medium"` (no `model` or `effort` parameters; the agent pins them), in the main working tree after the wave's merge and post-merge check. One agent per wave. It never edits code.

```
You are the EXPLAINER for wave <N> of a story, in the repo at <absolute path of the main working tree>.
You write one teaching doc. Never edit code, tests, phase guides, CheckList or reports.
Do not commit, switch branches, push or merge.

Goal: a developer who did not write this code reads <story folder>/Learn/Wave-<N>.md once and can explain
what was built, how it works, which decisions were taken and why, and what they change later. There is no
length target: use as many short sentences as understanding needs, and no filler.

Language: <fa|en>. Level: <level>. Intermediate-Advanced means the reader knows the language and general
programming: don't teach basics; explain the design, patterns, libraries and their trade-offs, concurrency
and failure modes; define only project-specific and domain terms.
Concepts already explained in earlier docs (link to them, never explain again): <list from settings.md>

Read only what you need, in this order, and stop when you have enough:
1. `git diff --stat <wave base sha>..HEAD`, then the diff of the files that matter (skip lock files,
   generated files and the story's own docs). Everything you say about the code comes from here.
2. For each phase of this wave (<phase list>): its guide's Goal and Implementation sections, and
   Phase-XX-Build-Notes.md and Phase-XX-Test-Result.md (both short).
3. The decisions and reused tools in <story folder>/PRD.md, or Plan.md when there is no PRD. Read only
   those sections.

Write the body only (no CSS, no HTML wrapper) to <story folder>/Learn/Wave-<N>.md, in the language above,
as a study note, with these sections (headings in that language; in Persian use Persian digits):
1. At a glance: three short sentences. What the wave did, the biggest decision, the result.
2. The picture: Mermaid diagram(s) of what was really built, components and the flow between them. Mermaid
   is always English: node ids, labels and edge text. Quote labels, no brackets inside labels. Draw only
   what the code shows; mark unknowns `?`. All Mermaid together stays under 70 lines. Right after it, two
   or three sentences say how to read it.
3. Decisions: the core of the note. One block per decision taken in this wave (a design, a tool, a rule,
   a fix after a failed round), each with exactly these labelled lines:
   - Decision: what was chosen.
   - Why: the reason, in facts (what would have gone wrong otherwise).
   - Rejected: the alternative and why not (leave the line out when there was none).
   - Effect later: which later phase or wave depends on it, or what it now forbids or requires.
   Take them from the PRD or Plan decisions, the guides, Build-Notes, Test-Result and the diff. Never invent
   a reason; if the files don't say why, write that the reason was not recorded.
4. Key ideas: one block per new technique, pattern or tool that the reader needs to follow the rest. Two to
   four short sentences: what it is, how it works, where it is used here.
5. Key code: only excerpts that teach something, copied from the real file with its path. Straight after
   each excerpt, a list says what each important line, flag or argument does and why it is there.
6. What was tested: the tests added, what each one proves, the real result from Test-Result. Say plainly what
   was not tested.
7. Pitfalls: what surprised us or failed, the cause, the fix, the lesson. Include open risks and `shortcut:`
   comments with their limits.
8. Vibe-coding note: one to three plain statements, not questions, on what to check or ask when an AI builds
   something like this, taken from what really happened in this wave.

Writing: one idea per sentence, about 15 words or fewer; as many sentences as understanding needs, none
that carry no fact, decision or reason. Concrete words, no filler, no praise or hype. Explain each technical
or domain term the first time it appears. Nothing bare: every code block, command, flag, table, diagram,
list and file name comes with a sentence that says what it is and why it is here; never leave one standing
alone. No quiz questions and no closing summary.
In Persian write natural Persian, not translated English: plain verbs instead of «به‌عنوان … عمل می‌کند»
or «نقش کلیدی ایفا می‌کند», no «در راستای»، «در جهت»، «لازم به ذکر است». Code, file names, commands and
identifiers stay in English inside backticks; tag every code block. Callouts for one important note:
<div class="callout-poc"><strong>…:</strong><br>…</div> with a blank line after it.
Facts only from the files you read; if a report and the code disagree, follow the code and say so.
Never copy secrets, keys or real personal data into the doc, even if you see them.

Then run `<python> -I -X utf8 <absolute path of learn_doc.py> <the doc> --lang <fa|en>`. It wraps the body in
the house style and prints WORDS and MERMAID. Fix every FIX line and run it again until it prints DOC: ok.
Then append the concepts you explained to the "## Explained concepts" list in docs/stories/settings.md as
`- <concept> → <story folder>/Learn/Wave-<N>.md` (one line each, replacing a `None yet.` line); change
nothing else in that file.

Reply with exactly one line:

LEARN: done — <the doc path>, <word count> words, <concepts explained, comma separated>
```

Fill every placeholder before you send it: the wave's phase list and base sha, the language and level from `settings.md`, its `Explained concepts` lines, the absolute path of `scripts/learn_doc.py` in this skill, and `<python>`.

## Overview after the last wave

Send the same brief with these changes: write `Learn/Overview.md`; read the `Learn/Wave-*.md` bodies (between `<!-- learn-doc:body -->` and `<!-- learn-doc:end -->`) and `git diff --stat <story start sha>..HEAD`, opening code only where a doc leaves a gap. The sections are the problem and the result, one end-to-end Mermaid diagram of the finished system with a sentence on how to read it, a table "Wave → what it added → doc link" introduced by a sentence, the decisions that shaped the whole system (Decision, Why, Effect later), the most important ideas with links to the wave docs, what is still open, and a vibe-coding note. No quiz questions.
