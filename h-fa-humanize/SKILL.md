---
name: h-fa-humanize
description: Humanizes Persian (Farsi) text so it reads like a skilled native writer, not AI or machine translation — removes AI-writing tells (Wikipedia "Signs of AI writing"), ترجمه‌زدگی, banned filler phrases and empty buzzwords, while keeping every fact, number and the document's formatting. Works on pasted text, text from the conversation, or files (.docx .xlsx .pptx .html .md .txt .csv; PDF as text). Use when the user asks to humanize / naturalize / de-AI / «انسانی کن» / «طبیعی کن» / «بوی هوش مصنوعی نده» / «ترجمه‌زدگی را بگیر» / «ویرایش کن که ماشینی نباشد», or says "h-fa-humanize".
---

# h-fa-humanize

Rewrite Persian text so it sounds like an experienced native writer, without changing what it says.
General purpose: any domain, any document type.

## Files

- `references/patterns-fa.md` — **read fully before rewriting.** The rules: AI tells, translation-ese, banned phrases, empty words, punctuation, what must never change, tone definitions.
- `scripts/fa_io.py` — extract text segments from a file and apply rewrites back with formatting intact; writes the before/after report.
- `scripts/fa_lint.py` — flags known patterns (use before rewriting, and again as the audit).

Run scripts with `python <skill-dir>/scripts/...` (Python 3, standard library only).

## Step 1: what to humanize

The input can be: text pasted in the message, text earlier in the conversation ("the text above", "section 2 of that doc"), or one or more file paths. If it is unclear which text, ask. If the user named a part (one section, one sheet), only change that part.

## Step 2: ask before rewriting (every time)

Ask these two questions together, in one short message (use the question tool if available). Skip a question only if the user already answered it in the request.

1. **لحن:** حفظ لحن متن / رسمی حرفه‌ای / نیمه‌رسمی / محاوره (definitions in `patterns-fa.md` §7).
2. **خروجی:**
   - for files: «فایل جدید کنار فایل اصلی با پسوند ‎-humanized» / «جایگزینی فایل اصلی (یک نسخه‌ی ‎.bak نگه داشته می‌شود)» / «مسیر دیگر»;
   - for pasted text: «نمایش در چت» / «ذخیره در فایل (md یا docx)».

Optionally ask for a short sample of the user's own writing to match their voice; do not insist.

## Step 3: load the text

| Input | How |
|---|---|
| `.docx .xlsx .pptx .html .htm .md .txt .csv` | `python fa_io.py extract <file> <work>/segments.json` |
| `.doc .xls .ppt .rtf .odt` | ask the user to Save As .docx/.xlsx/.pptx (the script stops with that message) |
| `.pdf` | read it with the Read tool; output as `.md` or `.docx` text (say that PDF layout can't be kept) |
| pasted / conversation text | work on it directly (split into paragraphs yourself) |

Keep work files (segments, rewrites) in a scratch/temp folder, not next to the user's document.

**Markers in segments — keep them exactly, in the same order:**
- `⟦#k⟧` fixed item (tab, line break, image, field, HTML tag). Never delete or move it past another marker.
- `⟦k⟧…⟦/k⟧` text with its own formatting (bold, link, another font). Rewrite the words inside, keep the pair.
In `.md` segments, keep markdown/HTML markup (`**`, `` ` ``, `[]()`, `|`, tags) as it is.

## Step 4: find the problems

Run `python fa_lint.py <work>/segments.json` (or on a text file). Read the hits **and** read the whole text yourself: the linter only knows fixed patterns; most problems (ترجمه‌زدگی in sentence structure, made-up idioms, mixed metaphors, monotone rhythm, inflated claims) need judgement against `patterns-fa.md`.

## Step 5: rewrite

For each segment that needs it, write the new text following `patterns-fa.md` and the chosen tone:
- short sentences with a clear subject and verb; vary length; drop filler;
- active voice when the actor is known; plain verbs («است»، «دارد») instead of «به‌عنوان … عمل می‌کند»؛
- replace empty words with the concrete action/result **from the text**; if the text gives none, shorten and flag it;
- keep every fact, number, name, date, quote, term, URL and the segment's structure (one paragraph/cell in → one out);
- do not add facts, examples, opinions or emphasis that are not in the source; do not fake "human" errors.

Write `<work>/rewrite.json`: `{"segments": [{"id": "...", "text": "...", "why": "…"}]}` — only changed segments; `why` is a short Persian reason naming the sign fixed (e.g. «مجهول با توسط → معلوم؛ حذف می‌باشد»). For big files, split into several rewrite files (`rewrite-1.json`, `rewrite-2.json`, …).

## Step 6: audit

1. `python fa_lint.py <work>/rewrite.json` — every remaining hit must be a deliberate keep (e.g. «توسط» inside a quote or legal term). Fix the rest.
2. Re-read each changed segment against the original: same meaning, same claims, nothing dropped or added, tone as chosen, reads naturally aloud.

## Step 7: write the output

- Files: `python fa_io.py apply <original> <output> <work>/rewrite.json [more.json] --report <report.md>`
  - output path from Step 2 (new file `name-humanized.ext` by default; for overwrite, first copy the original to `name.ext.bak`, then apply onto a temp file and move it over the original).
  - `ERROR` (marker problems) → nothing is written: fix those segments and re-run.
  - `WARN numbers differ` → a number changed: fix unless it was only a format change you meant (Persian/Latin digits).
- Pasted text: show the rewritten text (or save it where the user asked).

## Step 8: report (detailed before/after)

- Files: the script writes the table (`#`, قبل، بعد، دلیل) to the report file (styled with h-md-style when that skill is installed). Save it next to the output as `name-humanize-report.md`.
- In chat: up to ~15 rows → show the full table; more → give the report path and show the most important rows.
- Always add, in 2–4 lines: how many segments changed out of how many, the most frequent signs fixed, and **anything you were unsure about or left unchanged on purpose** (vague claims you could not make concrete, terms you kept, numbers flagged).

## Rules

- Meaning first: when in doubt, keep the original wording and mention it in the report.
- Never touch: quotes in «» from people or documents, legal/contract wording unless asked, code, formulas, URLs, names, numbers.
- Respect the requested scope and tone; formal documents never become colloquial unless the user picked «محاوره».
- Persian orthography: «»، ،، ؟، نیم‌فاصله، ی/ک فارسی — but don't convert digits or rewrite technical English terms unless they are inconsistent within the document.
