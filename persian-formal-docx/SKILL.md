---
name: persian-formal-docx
description: Convert any Markdown file into a formal Persian (Farsi, RTL) Word .docx deliverable in the "سند شناخت توانیر" house format — identification table in the header of every page (page number, project, doc ID, consultant/مشاور و مجری, client/کارفرما, date, doc title), title page, sign-off + revision-history page (تهیه کننده / تایید کننده / تاریخچه سند), real Word table of contents (فهرست), Vazirmatn typography (Light body, bold headings), right-to-left tables that render correctly in Word, LibreOffice and OnlyOffice. Use this whenever the user wants a Persian/Farsi .md turned into Word/docx, asks for a گزارش/سند/deliverable "in our format", "like the Tavanir document", "با قالب سند", or wants a client-ready Word version of a Farsi markdown report — even if they only say "make this a Word file" about a Persian document.
---

# Persian formal DOCX from Markdown

`scripts/md2docx.py` does the whole conversion deterministically. pandoc turns the
Markdown into a raw docx. python-docx then restyles it into the house format.
Finally, headless LibreOffice fills in the TOC page numbers and can export a PDF
preview. Your job is to collect the document metadata, run the script, and check
the result.

The Markdown can be anything: reports, specs, assessments, manuals. The body is
converted as written, and the house format is wrapped around it.

## Workflow

1. **Read the Markdown** to learn its title, its structure, and whether it
   already has YAML front matter.

2. **Collect metadata.** The format has fixed slots (see the table below). Fill
   them from, in order: the front matter, a `meta.yaml` from an earlier document
   in the same folder or project (the same client and contractor usually repeat,
   so reuse it), then what the user told you. Ask the user **once, in one message**,
   for whatever is still missing and matters (typically client, contractor, doc ID,
   date, and signatories). Tell them that any field left blank will appear as an
   empty slot. Don't invent names, IDs or dates: an empty cell is fine, a wrong
   name on a sign-off table is not.

3. **Write a `meta.yaml`** next to the output rather than editing the user's
   Markdown, so the source stays clean and the metadata can be reused. If the
   user prefers front matter in the `.md`, that works too, and `--meta` values
   win on conflicts.

4. **Convert:**
   ```bash
   python3 <skill-dir>/scripts/md2docx.py input.md -o output.docx --meta meta.yaml --pdf
   ```
   `--pdf` writes `output.pdf` beside the docx. `--no-lo` skips LibreOffice
   entirely; Word then fills the TOC page numbers when the file is opened.

5. **Look at the result before reporting.** Render a few pages
   (`pdftoppm -r 60 -png -f 1 -l 6 output.pdf pg`) and view them. Check the
   title page, the sign-off page, the TOC, one body page, and any wide table.
   Delete the PDF afterwards unless the user wanted one.

6. **Report** the output path, the metadata you used, any slots left empty, and
   the Word note below.

## Metadata fields

| key | appears as | default |
|---|---|---|
| `title` | title page line 1; header row 3 | first `# H1` of the Markdown (then removed from the body) |
| `subtitle` | title page line 2 (e.g. full system name) | empty |
| `project` | header row 1 | `subtitle`, else `title` |
| `client` | «کارفرما: …» on the title page and in the header | empty |
| `contractor` | «طراحی و اجرا: …» on the title page; «مشاور و مجری: …» in the header | empty |
| `doc_id` | «شناسه سند» | empty |
| `revision` | «شماره اصلاحیه» | `0` |
| `date` | «تاریخ تهیه» in the header, «تاریخ انتشار», sign-off dates | empty |
| `date_text` | date line on the title page, e.g. `اردیبهشت ماه ۱۴۰۵` | omitted |
| `prepared_by` / `approved_by` | sign-off table rows: `{name, role, date}` or a list of them | one empty row each |
| `history` | revision table: list of `{revision, date, description}` | one row: `revision`, `date`, «نسخه اولیه» |
| `toc_title` / `toc_levels` | TOC heading and depth | `فهرست` / `3` |
| `font_fa` / `font_latin` | body text (Persian / Latin) | `Vazirmatn Light` / `Vazirmatn Light` |
| `font_heading` / `font_heading_latin` | headings, title lines, and every bold run | `Vazirmatn` / `Vazirmatn` |
| `font_code` | code blocks and inline code | `Consolas` |

Keep dates in the Jalali form the user gives, e.g. `09/02/1405`. Don't convert
them. ASCII digits are drawn as Persian digits automatically (see below), so
`09/02/1405` and `۰۹/۰۲/۱۴۰۵` come out the same.

```yaml
# meta.yaml example
subtitle: سامانه صدور مجوز نیروگاه‌های تولید پراکنده مقیاس کوچک
client: شرکت توانیر
contractor: شرکت آرین نوین رایانه
doc_id: GT54-0400
revision: 0
date: 09/02/1405
date_text: اردیبهشت ماه ۱۴۰۵
prepared_by: {name: سپیده امانلو, role: تحلیلگر}
approved_by: {name: وحید محمدیاری, role: مدیر فنی}
```

## How Markdown maps to the format

- `#`, `##`, `###` … become real Word **Heading 1/2/3…** styles: Vazirmatn bold,
  16/13/12pt, black, right-aligned. These feed the TOC and Word's navigation
  pane. Heading numbers such as «۱.۲» are kept exactly as written; the script
  does not auto-number. If the user wants numbered headings and the Markdown
  has none, add the numbers to the Markdown text (in a copy) before converting.
- The first `# H1` is used as the document title when `title` isn't given, and
  it's removed from the body so it doesn't appear twice. If a document has
  several H1 chapters and no title H1, pass `title` explicitly.
- Tables read **right to left**. The first Markdown column becomes the rightmost
  column, so write Markdown tables in the order a Persian reader reads them;
  don't reverse them yourself. Word's RTL-table flag (`bidiVisual`) is ignored
  by OnlyOffice, so the script doesn't rely on it: it stores every table's cells
  physically reversed. The result looks the same in Word, LibreOffice and
  OnlyOffice. This applies to every table: body tables, the sign-off and history
  tables, and the page-header ID table, whose narrow page/ID/date column is
  therefore on the right.
- Tables get a bold, centred header row that repeats across pages. Column widths
  are sized to the content. Tables with 5 or more columns drop to 10pt, and 7 or
  more to 9pt, so words aren't broken.
- Code blocks become LTR monospace blocks. Inline code, links, footnotes,
  images (paths relative to the `.md`) with captions, block quotes, and nested
  and task lists all work.
- Horizontal rules (`---`) are dropped, because the house format doesn't use
  divider lines.
- Mixed Persian/English text is split into RTL and LTR runs, the way Word does
  it, so English stays left-to-right inside Persian sentences.
- **Typography:** everything is Vazirmatn, which covers Persian and Latin. Body
  text is Vazirmatn Light at 11pt (Vazirmatn runs larger than B Nazanin). Headings,
  the title-page lines and every bold run use the regular-weight `Vazirmatn`
  family. A light face has no real bold, so Word would otherwise fake one. Code
  stays monospace (`font_code`) because code in a proportional face is hard to
  read.
- **Digits:** Vazirmatn draws ASCII digits as Latin digits, so a number that
  isn't attached to Latin text is converted to Persian digits: `550 کاربر` gives
  `۵۵۰ کاربر`, and dates and table figures convert too. Numbers glued to Latin
  text (`k6`, `PostgreSQL 16`) and anything in code are left alone. To keep
  digits Latin, such as an IP address or a version string, put them in backticks.

## Things to tell the user

- **When opened in Word**, a prompt asks to update fields. Answering *Yes*
  refreshes the TOC page numbers for Word's own layout. The LibreOffice-computed
  numbers are already filled in and are usually right.
- The document uses **Vazirmatn** (free, from github.com/rastikerdar/vazirmatn).
  Readers need the static fonts installed, at least **Vazirmatn Light**,
  Regular and Bold. Otherwise the viewer substitutes another font and page breaks
  shift. Mention this if the file will go outside the organisation.
- **Page numbers** (the header «شماره صفحه» and the footer) are computed by the
  viewer when the file is opened, so they show in whatever digits the viewer
  uses, usually Latin. That is the one place the digit conversion can't reach.

## Requirements

`pandoc` (2.x or 3.x), `python3` with `python-docx` and `pyyaml`. LibreOffice
with its Python `uno` module is optional; it's used for TOC page numbers and the
PDF. If something is missing, the script says so. Install what's needed with
`pip install python-docx pyyaml` and the system package manager for pandoc and
LibreOffice.
