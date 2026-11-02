#!/usr/bin/env python3
"""Convert any Markdown file into a formal Persian (RTL) Word document.

Layout (modelled on the "سند شناخت" deliverable format):
  * a 3-row identification table in the header of every page
    (page number, project, doc id, consultant, client, date, doc title)
  * page number centred in the footer
  * page 1  - title page (title, subtitle, client, contractor, date, doc id block)
  * page 2  - sign-off table (prepared by / approved by) + revision history table
  * page 3  - table of contents (real Word TOC field over Heading 1..N)
  * page 4+ - the Markdown body, RTL, with real Heading styles

Pipeline: pandoc (Markdown -> raw docx)  ->  python-docx post-processing
          ->  optional LibreOffice pass that computes TOC page numbers / PDF.

Usage:
  md2docx.py input.md -o output.docx [--meta meta.yaml] [--pdf] [--no-lo]

Metadata comes from YAML front matter in the Markdown and/or --meta (the --meta
file wins on conflicts). See SKILL.md for the field list.
"""
import argparse
import copy
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

import yaml
from lxml import etree
from docx import Document
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.text.run import Run

# ---------------------------------------------------------------- constants
PAGE_W, PAGE_H = 12240, 15840                       # US Letter, twips
MARGINS = dict(top=284, right=1440, bottom=709, left=1440, header=294, footer=89)
TEXT_W = PAGE_W - MARGINS["left"] - MARGINS["right"]  # 9360

DEFAULT_META = {
    "title": None,            # title page line 1 + header row 3 (default: first H1)
    "subtitle": "",           # title page line 2 (e.g. system / project full name)
    "project": "",            # header row 1 (default: subtitle, else title)
    "client": "",             # کارفرما
    "contractor": "",         # مشاور و مجری / طراحی و اجرا
    "doc_id": "",             # شناسه سند
    "revision": "0",          # شماره اصلاحیه
    "date": "",               # تاریخ تهیه / انتشار, e.g. 09/02/1405
    "date_text": "",          # title page date line, e.g. اردیبهشت ماه ۱۴۰۵
    "prepared_by": [],        # {name, role, date} or list of them
    "approved_by": [],
    "history": None,          # list of {revision, date, description}
    "toc_title": "فهرست",
    "toc_levels": 3,
    # Vazirmatn covers Persian and Latin, so one family serves both scripts.
    # Static Vazirmatn installs expose the light weight as its own family name.
    "font_fa": "Vazirmatn Light",       # body, Persian
    "font_latin": "Vazirmatn Light",    # body, Latin
    "font_heading": "Vazirmatn",        # headings, title lines and every bold run
    "font_heading_latin": "Vazirmatn",
    "font_code": "Consolas",
}

ARABIC = "؀-ۿݐ-ݿࢠ-ࣿﭐ-﷿ﹰ-﻿"
# An RTL span starts and ends with an Arabic-script character and may contain
# anything except Latin letters / ASCII digits in between. Everything else is
# written as an LTR run - the same split Word itself produces when typing.
RTL_SPAN = re.compile(f"[{ARABIC}](?:[^A-Za-z0-9À-ɏ]*[{ARABIC}])?")
# Vazirmatn draws ASCII digits as Latin digits, so numbers that are not glued to
# Latin text (dates, counts, table figures) are written with Persian digits.
FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
LATIN_LETTER = re.compile("[A-Za-zÀ-ɏ]")
BODY_PT = 22  # half-points: Vazirmatn Light at 11pt reads like B Nazanin at 12pt


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


# ---------------------------------------------------------------- markdown prep
def split_front_matter(text):
    m = re.match(r"^﻿?---[ \t]*\n(.*?)\n(?:---|\.\.\.)[ \t]*\n", text, re.S)
    if not m:
        return {}, text
    data = yaml.safe_load(m.group(1)) or {}
    if not isinstance(data, dict):
        return {}, text
    return data, text[m.end():]


def pop_title_h1(body, title):
    """Return (title, body). The first ATX H1 becomes the document title when no
    title is given, and is removed from the body when it duplicates the title."""
    in_fence = False
    lines = body.split("\n")
    for i, line in enumerate(lines):
        if re.match(r"^\s*(```|~~~)", line):
            in_fence = not in_fence
        if in_fence:
            continue
        m = re.match(r"^#\s+(.+?)\s*#*\s*$", line)
        if m:
            h1 = m.group(1).strip()
            if title is None or h1 == str(title).strip():
                del lines[i]
                return h1, "\n".join(lines)
            break
    return title, body


def run_pandoc(md_text, resource_dir, out_path):
    src = out_path + ".md"
    with open(src, "w", encoding="utf-8") as f:
        f.write(md_text)
    cmd = ["pandoc", src, "-o", out_path, "-t", "docx",
           "-f", "markdown+lists_without_preceding_blankline-yaml_metadata_block",
           f"--resource-path={resource_dir}"]
    subprocess.run(cmd, check=True)


# ---------------------------------------------------------------- xml helpers
PPR_ORDER = ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl",
             "numPr", "suppressLineNumbers", "pBdr", "shd", "tabs", "suppressAutoHyphens",
             "kinsoku", "wordWrap", "overflowPunct", "topLinePunct", "autoSpaceDE",
             "autoSpaceDN", "bidi", "adjustRightInd", "snapToGrid", "spacing", "ind",
             "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc", "textDirection",
             "textAlignment", "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr",
             "sectPr", "pPrChange"]
TBLPR_ORDER = ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize",
               "tblStyleColBandSize", "tblW", "jc", "tblCellSpacing", "tblInd", "tblBorders",
               "shd", "tblLayout", "tblCellMar", "tblLook"]


def set_child(parent, xml, order):
    """Insert/replace a child element of `parent`, keeping schema order."""
    el = parse_xml(xml) if isinstance(xml, str) else xml
    name = el.tag.split("}")[1]
    for old in parent.findall(qn("w:" + name)):
        parent.remove(old)
    idx = order.index(name)
    for i, child in enumerate(parent):
        cname = child.tag.split("}")[1]
        if cname in order and order.index(cname) > idx:
            child.addprevious(el)
            return el
    parent.append(el)
    return el


def ppr(p):
    pPr = p.find(qn("w:pPr"))
    if pPr is None:
        pPr = parse_xml(f"<w:pPr {nsdecls('w')}/>")
        p.insert(0, pPr)
    return pPr


def W(tag_and_attrs):
    return f"<w:{tag_and_attrs} {nsdecls('w')}/>"


def fonts_xml(latin, cs):
    return (f'<w:rFonts {nsdecls("w")} w:ascii="{esc(latin)}" w:hAnsi="{esc(latin)}" '
            f'w:eastAsia="{esc(latin)}" w:cs="{esc(cs)}"/>')


def run_xml(text, bold=False, size=None, font=None):
    rpr = ""
    if font:
        rpr += f'<w:rFonts w:ascii="{esc(font)}" w:hAnsi="{esc(font)}" w:cs="{esc(font)}"/>'
    if bold:
        rpr += "<w:b/><w:bCs/>"
    if size:
        rpr += f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
    rpr = f"<w:rPr>{rpr}</w:rPr>" if rpr else ""
    return f'<w:r>{rpr}<w:t xml:space="preserve">{esc(text)}</w:t></w:r>'


def field_xml(instr, cached="", bold=False, size=None):
    rpr = ("<w:b/><w:bCs/>" if bold else "") + (
        f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>' if size else "")
    rpr = f"<w:rPr>{rpr}</w:rPr>" if rpr else ""
    return (f'<w:r>{rpr}<w:fldChar w:fldCharType="begin"/></w:r>'
            f'<w:r>{rpr}<w:instrText xml:space="preserve"> {instr} </w:instrText></w:r>'
            f'<w:r>{rpr}<w:fldChar w:fldCharType="separate"/></w:r>'
            f'<w:r>{rpr}<w:t>{esc(cached)}</w:t></w:r>'
            f'<w:r>{rpr}<w:fldChar w:fldCharType="end"/></w:r>')


def para_xml(inner="", jc=None, before=None, after=None, keep_next=False, page_break=False,
             style=None):
    p = ""
    if style:
        p += f'<w:pStyle w:val="{style}"/>'
    if keep_next:
        p += "<w:keepNext/>"
    if before is not None or after is not None:
        p += "<w:spacing" + (f' w:before="{before}"' if before is not None else "") + (
            f' w:after="{after}"' if after is not None else "") + "/>"
    if jc:
        p += f'<w:jc w:val="{jc}"/>'
    br = '<w:r><w:br w:type="page"/></w:r>' if page_break else ""
    return f'<w:p {nsdecls("w")}><w:pPr>{p}</w:pPr>{inner}{br}</w:p>'


# ---------------------------------------------------------------- styles
def restyle(doc, m):
    fa, lat, hlat, code = m["font_fa"], m["font_latin"], m["font_heading_latin"], m["font_code"]
    styles_el = doc.styles.element

    # document defaults: Persian complex-script font, 12pt, fa-IR, 1.16 line spacing
    rpr_def = styles_el.find(qn("w:docDefaults")).find(qn("w:rPrDefault")).find(qn("w:rPr"))
    for child in list(rpr_def):
        rpr_def.remove(child)
    for x in (fonts_xml(lat, fa), W(f'sz w:val="{BODY_PT}"'), W(f'szCs w:val="{BODY_PT}"'),
              W('lang w:val="en-US" w:eastAsia="en-US" w:bidi="fa-IR"')):
        rpr_def.append(parse_xml(x))
    ppr_def = styles_el.find(qn("w:docDefaults")).find(qn("w:pPrDefault"))
    if ppr_def is None:
        ppr_def = parse_xml(f"<w:pPrDefault {nsdecls('w')}><w:pPr/></w:pPrDefault>")
        styles_el.find(qn("w:docDefaults")).append(ppr_def)
    set_child(ppr_def.find(qn("w:pPr")), W('spacing w:after="160" w:line="278" w:lineRule="auto"'),
              PPR_ORDER)

    def define(style_id, name, based_on="Normal", ptype="paragraph", ppr_x="", rpr_x=""):
        el = styles_el.find(f'{qn("w:style")}[@{qn("w:styleId")}="{style_id}"]')
        if el is None:
            el = parse_xml(f'<w:style {nsdecls("w")} w:type="{ptype}" w:styleId="{style_id}">'
                           f'<w:name w:val="{name}"/></w:style>')
            if based_on:
                el.append(parse_xml(f'<w:basedOn {nsdecls("w")} w:val="{based_on}"/>'))
            el.append(parse_xml(f'<w:uiPriority {nsdecls("w")} w:val="39"/>'))
            styles_el.append(el)
        for tag in ("w:pPr", "w:rPr"):
            for old in el.findall(qn(tag)):
                el.remove(old)
        anchor = el.find(qn("w:tblPr"))
        for x in (f"<w:pPr {nsdecls('w')}>{ppr_x}</w:pPr>" if ptype != "character" else None,
                  f"<w:rPr {nsdecls('w')}>{rpr_x}</w:rPr>"):
            if x is None:
                continue
            node = parse_xml(x)
            if anchor is not None:
                anchor.addprevious(node)
            else:
                el.append(node)
        return el

    f_body = (f'<w:rFonts w:ascii="{esc(lat)}" w:hAnsi="{esc(lat)}" w:eastAsia="{esc(lat)}" '
              f'w:cs="{esc(fa)}"/>')
    f_head = (f'<w:rFonts w:ascii="{esc(hlat)}" w:hAnsi="{esc(hlat)}" w:eastAsia="{esc(hlat)}" '
              f'w:cs="{esc(m["font_heading"])}"/>')
    f_code = (f'<w:rFonts w:ascii="{esc(code)}" w:hAnsi="{esc(code)}" w:eastAsia="{esc(code)}" '
              f'w:cs="{esc(code)}"/>')
    black = '<w:color w:val="000000"/>'

    define("Normal", "Normal", based_on=None,
           ppr_x='<w:bidi/><w:spacing w:after="160" w:line="278" w:lineRule="auto"/><w:jc w:val="both"/>',
           rpr_x=f'{f_body}<w:sz w:val="{BODY_PT}"/><w:szCs w:val="{BODY_PT}"/><w:lang w:bidi="fa-IR"/>')
    for sid, name in (("BodyText", "Body Text"), ("FirstParagraph", "First Paragraph")):
        define(sid, name, ppr_x='<w:spacing w:before="0" w:after="160"/>')
    define("Compact", "Compact", ppr_x='<w:spacing w:before="0" w:after="0"/>')

    # Headings: bold, black, in the heading (regular-weight) family
    head_specs = {1: (32, 240, 80), 2: (26, 160, 80), 3: (24, 120, 60),
                  4: (24, 120, 40), 5: (24, 80, 40), 6: (24, 80, 40)}
    for lvl, (sz, before, after) in head_specs.items():
        define(f"Heading{lvl}", f"heading {lvl}",
               ppr_x=(f'<w:keepNext/><w:keepLines/><w:spacing w:before="{before}" w:after="{after}"/>'
                      f'<w:jc w:val="left"/><w:outlineLvl w:val="{lvl - 1}"/>'),
               rpr_x=(f'{f_head}<w:b/><w:bCs/>{black}<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>'))
    # note: in a bidi paragraph jc="left" is the logical start, i.e. visually right

    define("BlockText", "Block Text",
           ppr_x=('<w:shd w:val="clear" w:color="auto" w:fill="F2F2F2"/>'
                  '<w:spacing w:before="60" w:after="120"/><w:ind w:left="567" w:right="567"/>'),
           rpr_x="")
    define("SourceCode", "Source Code",
           ppr_x=('<w:shd w:val="clear" w:color="auto" w:fill="F5F5F5"/><w:bidi w:val="0"/>'
                  '<w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>'
                  '<w:jc w:val="left"/>'),
           rpr_x=f'{f_code}<w:sz w:val="20"/><w:szCs w:val="20"/>')
    define("VerbatimChar", "Verbatim Char", based_on="DefaultParagraphFont", ptype="character",
           rpr_x=f'{f_code}<w:sz w:val="20"/><w:szCs w:val="20"/>')
    for sid, name in (("Figure", "Figure"), ("CaptionedFigure", "Captioned Figure")):
        define(sid, name, ppr_x='<w:keepNext/><w:spacing w:before="120" w:after="60"/><w:jc w:val="center"/>')
    for sid, name in (("ImageCaption", "Image Caption"), ("TableCaption", "Table Caption"),
                      ("Caption", "caption")):
        define(sid, name, ppr_x='<w:spacing w:before="60" w:after="160"/><w:jc w:val="center"/>',
               rpr_x='<w:sz w:val="20"/><w:szCs w:val="20"/>')
    define("FootnoteText", "footnote text", ppr_x='<w:spacing w:after="0"/>',
           rpr_x='<w:sz w:val="20"/><w:szCs w:val="20"/>')

    # TOC entry styles (tab = end-aligned dotted leader, as in the reference)
    toc_tab = f'<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="{TEXT_W - 10}"/></w:tabs>'
    for lvl in range(1, 10):
        ind = f'<w:ind w:left="{(lvl - 1) * 240}"/>' if lvl > 1 else ""
        bold = f"{f_head}<w:b/><w:bCs/>" if lvl <= 2 else ""
        define(f"TOC{lvl}", f"toc {lvl}",
               ppr_x=f'{toc_tab}<w:spacing w:after="100"/>{ind}<w:jc w:val="left"/>',
               rpr_x=bold)

    define("TableGrid", "Table Grid", based_on=None, ptype="table",
           ppr_x='<w:spacing w:after="0" w:line="240" w:lineRule="auto"/>')
    tg = styles_el.find(f'{qn("w:style")}[@{qn("w:styleId")}="TableGrid"]')
    if tg.find(qn("w:tblPr")) is None:
        b = "".join(f'<w:{s} w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
                    for s in ("top", "left", "bottom", "right", "insideH", "insideV"))
        tg.append(parse_xml(f"<w:tblPr {nsdecls('w')}><w:tblBorders>{b}</w:tblBorders>"
                            '<w:tblCellMar><w:left w:w="108" w:type="dxa"/>'
                            '<w:right w:w="108" w:type="dxa"/></w:tblCellMar></w:tblPr>'))


# ---------------------------------------------------------------- body clean-up
def clean_body(doc):
    body = doc.element.body
    # horizontal rules: the reference format has none; drop them
    for p in body.findall(qn("w:p")):
        if p.xpath(".//*[local-name()='rect'][@*[local-name()='hr']='t']"):
            body.remove(p)

    # pandoc bookmark names are derived from heading text (Persian, long) - Word
    # limits names to 40 chars; rename to safe ids and repoint internal links.
    rename = {}
    for i, bm in enumerate(body.iter(qn("w:bookmarkStart"))):
        old = bm.get(qn("w:name"))
        if old and not old.startswith("_"):
            rename[old] = f"_Ref{i + 1:06d}"
            bm.set(qn("w:name"), rename[old])
    for h in body.iter(qn("w:hyperlink")):
        a = h.get(qn("w:anchor"))
        if a in rename:
            h.set(qn("w:anchor"), rename[a])


def format_tables(doc):
    for tbl in doc.element.body.iter(qn("w:tbl")):
        tblPr = tbl.find(qn("w:tblPr"))
        set_child(tblPr, W('tblStyle w:val="TableGrid"'), TBLPR_ORDER)
        set_child(tblPr, W('tblW w:w="5000" w:type="pct"'), TBLPR_ORDER)
        set_child(tblPr, W('jc w:val="center"'), TBLPR_ORDER)
        set_child(tblPr, W('tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" '
                           'w:lastColumn="0" w:noHBand="0" w:noVBand="1"'), TBLPR_ORDER)
        rows = tbl.findall(qn("w:tr"))
        grid = tbl.find(qn("w:tblGrid"))
        cols = grid.findall(qn("w:gridCol")) if grid is not None else []
        n = len(cols)
        # many columns -> smaller type so words are not broken mid-word
        size = 18 if n >= 7 else 20 if n >= 5 else None
        texts = [["".join(t.text or "" for t in tc.iter(qn("w:t"))) for tc in tr.findall(qn("w:tc"))]
                 for tr in rows]
        simple = n and all(len(r) == n for r in texts)  # no merged cells
        widths = column_widths(texts, n, size or BODY_PT) if simple else None
        if widths:
            set_child(tblPr, W('tblLayout w:type="fixed"'), TBLPR_ORDER)
            for c, w in zip(cols, widths):
                c.set(qn("w:w"), str(w))
        # short columns read best centred (as in the reference); long text starts at the right
        centred = [max((len(r[i]) for r in texts), default=0) <= 25 for i in range(n)] if simple else []
        for tr in rows:
            trPr = tr.find(qn("w:trPr"))
            is_header = trPr is not None and trPr.find(qn("w:tblHeader")) is not None
            for ci, tc in enumerate(tr.findall(qn("w:tc"))):
                tcPr = tc.find(qn("w:tcPr"))
                if tcPr is None:
                    tcPr = parse_xml(f"<w:tcPr {nsdecls('w')}/>")
                    tc.insert(0, tcPr)
                for tag in ("w:tcW", "w:vAlign"):
                    for old in tcPr.findall(qn(tag)):
                        tcPr.remove(old)
                if widths:
                    tcPr.insert(0, parse_xml(W(f'tcW w:w="{widths[ci]}" w:type="dxa"')))
                tcPr.append(parse_xml(W('vAlign w:val="center"')))
                jc = "center" if is_header or (centred and centred[ci]) else "left"  # left = start in RTL
                for p in tc.findall(qn("w:p")):
                    set_child(ppr(p), W(f'jc w:val="{jc}"'), PPR_ORDER)
                    for r in p.iter(qn("w:r")):
                        f = Run(r, None).font
                        if is_header:
                            f.bold = True
                            f.cs_bold = True
                        if size:
                            set_run_size(r, size)


def mirror_table_columns(container):
    """Make every table read right to left in any viewer.

    Tables are built in logical order (first column = rightmost). Word and
    LibreOffice can show that via <w:bidiVisual/>, but other editors (OnlyOffice)
    ignore the flag and draw the first column on the left. So instead of the flag,
    store the cells physically reversed: the result looks the same everywhere."""
    for tbl in container.iter(qn("w:tbl")):
        tblPr = tbl.find(qn("w:tblPr"))
        if tblPr is not None:
            for el in tblPr.findall(qn("w:bidiVisual")):
                tblPr.remove(el)
        for parent, tag in [(tbl.find(qn("w:tblGrid")), "w:gridCol")] + \
                [(tr, "w:tc") for tr in tbl.findall(qn("w:tr"))]:
            if parent is None:
                continue
            kids = parent.findall(qn(tag))
            if len(kids) < 2:
                continue
            anchor = kids[-1].getnext()  # keep any trailing siblings (e.g. w:trPrChange) in place
            for k in kids:
                parent.remove(k)
            for k in reversed(kids):
                if anchor is not None:
                    anchor.addprevious(k)
                else:
                    parent.append(k)


def bold_runs_use_heading_font(container, font):
    """A light body face has no bold of its own (Word would fake one); bold runs
    switch to the regular-weight heading family, which has a real bold."""
    off = {"0", "false", "off"}
    for r in container.iter(qn("w:r")):
        rPr = r.find(qn("w:rPr"))
        if rPr is None:
            continue
        b = rPr.find(qn("w:b"))
        if b is None or b.get(qn("w:val"), "true") in off:
            continue
        if rPr.find(qn("w:rStyle")) is not None and \
                rPr.find(qn("w:rStyle")).get(qn("w:val")) == "VerbatimChar":
            continue  # bold inline code stays monospace
        Run(r, None).font.name = font  # ascii / hAnsi / eastAsia
        rPr.find(qn("w:rFonts")).set(qn("w:cs"), font)


def set_run_size(r, half_pts):
    """Set both Latin (sz) and complex-script (szCs) size on a run."""
    Run(r, None).font.size = half_pts * 6350  # half-points -> EMU
    rPr = r.find(qn("w:rPr"))
    for old in rPr.findall(qn("w:szCs")):
        rPr.remove(old)
    rPr.find(qn("w:sz")).addnext(parse_xml(W(f'szCs w:val="{half_pts}"')))


def column_widths(texts, n, half_pts):
    """Content-based column widths (twips) summing to the text width: every column
    gets room for its longest word, the rest is shared by how much text it holds."""
    char_tw = 12 * half_pts / 2 + 5         # rough Vazirmatn glyph width in twips (bold headers included)
    pad = 2 * 108 + 40                      # cell margins + slack
    mins, wants = [], []
    for i in range(n):
        cells = [r[i] for r in texts]
        longest_word = max((len(w) for c in cells for w in c.split()), default=1)
        longest_cell = max((len(c) for c in cells), default=1)
        mins.append(min(longest_word, 30) * char_tw + pad)
        wants.append(min(longest_cell, 60) * char_tw + pad)
    extra = TEXT_W - sum(mins)
    if extra <= 0:
        return [int(m * TEXT_W / sum(mins)) for m in mins]
    grow = [max(w - m, 0) for w, m in zip(wants, mins)]
    if not sum(grow):
        grow = mins
    return [int(m + extra * g / sum(grow)) for m, g in zip(mins, grow)]


# ---------------------------------------------------------------- front matter
def people(v):
    if not v:
        return [{}]
    return v if isinstance(v, list) else [v]


def simple_table(rows, widths, bold_first_col=False):
    """rows[0] is the header row. Logical order; mirror_table_columns puts the
    first column on the right."""
    grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in widths)
    trs = ""
    for ri, row in enumerate(rows):
        tcs = ""
        for ci, text in enumerate(row):
            bold = ri == 0 or (bold_first_col and ci == 0)
            tcs += (f'<w:tc><w:tcPr><w:tcW w:w="{widths[ci]}" w:type="dxa"/><w:vAlign w:val="center"/></w:tcPr>'
                    f'<w:p><w:pPr><w:spacing w:before="40" w:after="40"/><w:jc w:val="center"/></w:pPr>'
                    f'{run_xml(text, bold=bold) if text else ""}</w:p></w:tc>')
        trpr = "<w:trPr><w:tblHeader/></w:trPr>" if ri == 0 else ""
        trs += f"<w:tr>{trpr}{tcs}</w:tr>"
    return (f'<w:tbl {nsdecls("w")}><w:tblPr><w:tblStyle w:val="TableGrid"/>'
            f'<w:tblW w:w="{sum(widths)}" w:type="dxa"/><w:jc w:val="center"/>'
            f'<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" w:lastColumn="0" '
            f'w:noHBand="0" w:noVBand="1"/></w:tblPr><w:tblGrid>{grid}</w:tblGrid>{trs}</w:tbl>')


def front_matter(m):
    """XML elements for title page, sign-off page and TOC heading (TOC added later)."""
    out = []
    # --- page 1: title page
    hf = m["font_heading"]
    out.append(para_xml(run_xml(m["title"], size=44, font=hf), jc="center", before=2600, after=120))
    if m["subtitle"]:
        out.append(para_xml(run_xml(m["subtitle"], size=40, font=hf), jc="center", before=120, after=120))
    if m["client"]:
        out.append(para_xml(run_xml(f"کارفرما: {m['client']}", bold=True, size=28),
                            jc="center", before=900, after=0))
    if m["contractor"]:
        out.append(para_xml(run_xml(f"طراحی و اجرا: {m['contractor']}", bold=True, size=28),
                            jc="center", before=500, after=0))
    if m["date_text"]:
        out.append(para_xml(run_xml(m["date_text"], bold=True), jc="center", before=1700, after=0))
    first = True
    for label, key in (("شناسه سند", "doc_id"), ("شماره اصلاحیه", "revision"),
                       ("تاریخ انتشار", "date")):
        if str(m[key]).strip():
            out.append(para_xml(run_xml(f"{label}: {m[key]}"), jc="left",
                                before=1500 if first else 0, after=120))
            first = False
    out.append(para_xml(page_break=True, after=0))

    # --- page 2: sign-off + revision history
    rows = [["", "نام و نام خانوادگی", "سمت", "تاریخ"]]
    for label, key in (("تهیه کننده", "prepared_by"), ("تایید کننده", "approved_by")):
        for person in people(m[key]):
            rows.append([label, str(person.get("name", "")), str(person.get("role", "")),
                         str(person.get("date", m["date"]) if person else "")])
    out.append(para_xml(before=600, after=0))
    out.append(simple_table(rows, [1600, 3000, 2600, 2160], bold_first_col=True))
    out.append(para_xml(run_xml("تاریخچه سند", bold=True), jc="center", before=1100, after=160))
    hist = m["history"]
    if not hist:
        hist = [{"revision": m["revision"], "date": m["date"],
                 "description": "نسخه اولیه" if str(m["revision"]) in ("0", "۰") else ""}]
    rows = [["شماره اصلاحیه", "تاریخ انتشار", "توضیحات"]] + [
        [str(h.get("revision", "")), str(h.get("date", "")), str(h.get("description", ""))]
        for h in hist]
    out.append(simple_table(rows, [2000, 2400, 4960]))
    out.append(para_xml(page_break=True, after=0))

    # --- page 3: TOC title (plain paragraph, so it is not itself listed in the TOC)
    out.append(para_xml(run_xml(m["toc_title"], bold=True, size=28), jc="left", before=240, after=160))
    return [parse_xml(x) for x in out]


def heading_level(p):
    ps = p.find(qn("w:pPr"))
    ps = ps.find(qn("w:pStyle")) if ps is not None else None
    if ps is None:
        return None
    mt = re.fullmatch(r"Heading(\d)", ps.get(qn("w:val")))
    return int(mt.group(1)) if mt else None


def build_toc(doc, levels):
    """Bookmark each heading and write a TOC field whose cached result already
    lists the entries (page numbers filled in later by LibreOffice or by Word)."""
    entries = []
    for p in doc.element.body.findall(qn("w:p")):
        lvl = heading_level(p)
        if lvl is None or lvl > levels:
            continue
        text = "".join(t.text or "" for t in p.iter(qn("w:t"))).strip()
        if not text:
            continue
        name = f"_Toc{len(entries) + 1:06d}"
        bid = str(900000 + len(entries))
        start = parse_xml(f'<w:bookmarkStart {nsdecls("w")} w:id="{bid}" w:name="{name}"/>')
        end = parse_xml(f'<w:bookmarkEnd {nsdecls("w")} w:id="{bid}"/>')
        ppr(p).addnext(start)
        p.append(end)
        entries.append((lvl, text, name))

    paras = []
    instr = f'TOC \\o "1-{levels}" \\h \\z \\u'
    for i, (lvl, text, name) in enumerate(entries):
        head = ""
        if i == 0:
            head = (f'<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
                    f'<w:r><w:instrText xml:space="preserve"> {instr} </w:instrText></w:r>'
                    f'<w:r><w:fldChar w:fldCharType="separate"/></w:r>')
        tail = '<w:r><w:fldChar w:fldCharType="end"/></w:r>' if i == len(entries) - 1 else ""
        link = (f'<w:hyperlink w:anchor="{name}" w:history="1">{run_xml(text)}'
                f'<w:r><w:tab/></w:r>{field_xml(f"PAGEREF {name} " + chr(92) + "h", "")}</w:hyperlink>')
        paras.append(parse_xml(f'<w:p {nsdecls("w")}><w:pPr><w:pStyle w:val="TOC{lvl}"/></w:pPr>'
                               f'{head}{link}{tail}</w:p>'))
    if not entries:  # still leave a working field for Word to fill
        paras.append(parse_xml(para_xml(
            f'<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> '
            f'{instr} </w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r>'
            f'<w:r><w:fldChar w:fldCharType="end"/></w:r>')))
    paras.append(parse_xml(para_xml(page_break=True, after=0)))
    return paras, entries


# ---------------------------------------------------------------- header / footer
def build_header_footer(doc, m):
    sec = doc.sections[0]
    sec.page_width, sec.page_height = PAGE_W * 635, PAGE_H * 635  # twips -> EMU
    sec.top_margin, sec.bottom_margin = MARGINS["top"] * 635, MARGINS["bottom"] * 635
    sec.left_margin, sec.right_margin = MARGINS["left"] * 635, MARGINS["right"] * 635
    sec.header_distance, sec.footer_distance = MARGINS["header"] * 635, MARGINS["footer"] * 635
    sec.gutter = 0
    sec.different_first_page_header_footer = False

    def cell(width, inner, span=1, center=False):
        gs = f'<w:gridSpan w:val="{span}"/>' if span > 1 else ""
        jc = f'<w:jc w:val="{"center" if center else "left"}"/>'  # left = start in RTL
        return (f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>{gs}<w:vAlign w:val="center"/></w:tcPr>'
                f'<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>'
                f'{jc}</w:pPr>{inner}</w:p></w:tc>')

    project = m["project"] or m["subtitle"] or m["title"]
    sz = 20  # 10pt keeps the narrow info column on one line

    def txt(t):
        return run_xml(t, size=sz)

    # logical order like every table: the narrow info column ends up on the right
    row1 = cell(2600, txt("شماره صفحه: ") + field_xml("PAGE \\* MERGEFORMAT", "1", size=sz)) + \
        cell(6618, txt(project), span=2)
    row2 = cell(2600, txt(f"شناسه سند: {m['doc_id']}")) + \
        cell(3100, txt(f"مشاور و مجری: {m['contractor']}")) + \
        cell(3518, txt(f"کارفرما: {m['client']}"))
    row3 = cell(2600, txt(f"تاریخ تهیه: {m['date']}")) + cell(6618, txt(m["title"]), span=2)
    tbl = (f'<w:tbl {nsdecls("w")}><w:tblPr><w:tblStyle w:val="TableGrid"/>'
           f'<w:tblW w:w="9218" w:type="dxa"/><w:jc w:val="center"/>'
           f'<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" w:lastColumn="0" '
           f'w:noHBand="0" w:noVBand="1"/></w:tblPr>'
           f'<w:tblGrid><w:gridCol w:w="2600"/><w:gridCol w:w="3100"/><w:gridCol w:w="3518"/></w:tblGrid>'
           f'<w:tr><w:trPr><w:jc w:val="center"/></w:trPr>{row1}</w:tr>'
           f'<w:tr><w:trPr><w:jc w:val="center"/></w:trPr>{row2}</w:tr>'
           f'<w:tr><w:trPr><w:jc w:val="center"/></w:trPr>{row3}</w:tr></w:tbl>')

    hdr = sec.header
    hdr.is_linked_to_previous = False
    h_el = hdr._element
    for child in list(h_el):
        h_el.remove(child)
    h_el.append(parse_xml(tbl))
    h_el.append(parse_xml(para_xml(after=0)))

    ftr = sec.footer
    ftr.is_linked_to_previous = False
    f_el = ftr._element
    for child in list(f_el):
        f_el.remove(child)
    f_el.append(parse_xml(para_xml(field_xml("PAGE \\* MERGEFORMAT", "1"), jc="center", after=0)))


# ---------------------------------------------------------------- run direction
def merge_runs(container):
    """Merge adjacent plain-text runs with identical formatting (pandoc emits one
    run per word), so the script split below yields Word-like runs."""
    for parent in list(container.iter(qn("w:p"))) + list(container.iter(qn("w:hyperlink"))):
        prev = None
        for r in list(parent):
            if r.tag != qn("w:r") or not _plain(r):
                prev = None
                continue
            if prev is not None and _rpr_key(prev) == _rpr_key(r):
                pt, rt = prev.find(qn("w:t")), r.find(qn("w:t"))
                pt.text = (pt.text or "") + (rt.text or "")
                pt.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
                parent.remove(r)
            else:
                prev = r


def _plain(r):
    kids = [c for c in r if c.tag != qn("w:rPr")]
    return len(kids) == 1 and kids[0].tag == qn("w:t")


def _rpr_key(r):
    rp = r.find(qn("w:rPr"))
    return b"" if rp is None else etree.tostring(rp)


def _is_code(r):
    rs = r.find(qn("w:rPr"))
    rs = rs.find(qn("w:rStyle")) if rs is not None else None
    if rs is not None and rs.get(qn("w:val")) == "VerbatimChar":
        return True
    p = next((a for a in r.iterancestors(qn("w:p"))), None)
    ps = p.find(qn("w:pPr")) if p is not None else None
    ps = ps.find(qn("w:pStyle")) if ps is not None else None
    return ps is not None and ps.get(qn("w:val")) == "SourceCode"


def split_runs_by_script(container):
    for r in list(container.iter(qn("w:r"))):
        if not _plain(r):
            continue
        t = r.find(qn("w:t"))
        text = t.text or ""
        if not text:  # keep empty runs (e.g. cached field results waiting to be filled)
            continue
        code = _is_code(r)
        segs, pos = [], 0
        for mt in RTL_SPAN.finditer(text):
            if mt.start() > pos:
                segs.append((text[pos:mt.start()], False))
            segs.append((mt.group(), True))
            pos = mt.end()
        if pos < len(text):
            segs.append((text[pos:], False))
        if not code:  # bare numbers ("12/07/1405", "۳ of 200") become Persian digits
            segs = [(s.translate(FA_DIGITS), True)
                    if not rtl and not LATIN_LETTER.search(s) and re.search("[0-9]", s)
                    else (s, rtl) for s, rtl in segs]
            # rejoin neighbours that are now all RTL so a sentence stays one run
            merged = []
            for s, rtl in segs:
                if merged and rtl and merged[-1][1]:
                    merged[-1] = (merged[-1][0] + s, True)
                else:
                    merged.append((s, rtl))
            segs = merged
        if len(segs) == 1 and segs[0][0] != text:
            t.text = segs[0][0]
        if len(segs) == 1:
            Run(r, None).font.rtl = True if segs[0][1] else None
            continue
        for seg, rtl in segs:
            nr = copy.deepcopy(r)
            nt = nr.find(qn("w:t"))
            nt.text = seg
            nt.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            Run(nr, None).font.rtl = True if rtl else None
            r.addprevious(nr)
        r.getparent().remove(r)


def mirror_cs_formatting(container):
    """pandoc sets b/i; make sure complex-script bold/italic follow."""
    for rpr in container.iter(qn("w:rPr")):
        f = Run(rpr.getparent(), None).font if rpr.getparent().tag == qn("w:r") else None
        if f is None:
            continue
        if rpr.find(qn("w:b")) is not None and rpr.find(qn("w:bCs")) is None:
            f.cs_bold = True
        if rpr.find(qn("w:i")) is not None and rpr.find(qn("w:iCs")) is None:
            f.cs_italic = True


# ---------------------------------------------------------------- LibreOffice pass
def libreoffice_toc_pages(docx_path, pdf_path=None, timeout=90):
    """Open the docx in headless LibreOffice, update the TOC, return its page
    numbers (list of str, in entry order). Optionally export a PDF."""
    try:
        import uno
        from com.sun.star.beans import PropertyValue
    except ImportError:
        return None
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        return None
    profile = tempfile.mkdtemp(prefix="md2docx_lo_")
    pipe = f"md2docx_{os.getpid()}"
    proc = subprocess.Popen([soffice, f"-env:UserInstallation=file://{profile}", "--headless",
                             "--invisible", "--nologo", "--norestore", "--nodefault",
                             f"--accept=pipe,name={pipe};urp;"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def pv(name, value):
        p = PropertyValue()
        p.Name, p.Value = name, value
        return p

    try:
        local = uno.getComponentContext()
        resolver = local.ServiceManager.createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver", local)
        ctx, deadline = None, time.time() + timeout
        while ctx is None:
            try:
                ctx = resolver.resolve(f"uno:pipe,name={pipe};urp;StarOffice.ComponentContext")
            except Exception:
                if time.time() > deadline or proc.poll() is not None:
                    return None
                time.sleep(0.5)
        desktop = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
        doc = desktop.loadComponentFromURL(uno.systemPathToFileUrl(os.path.abspath(docx_path)),
                                           "_blank", 0, (pv("Hidden", True),))
        pages = []
        idxs = doc.getDocumentIndexes()
        for i in range(idxs.getCount()):
            idx = idxs.getByIndex(i)
            idx.update()
            if not pages:
                for line in idx.getAnchor().getString().splitlines():
                    mt = re.search(r"\t\s*(\d+)\s*$", line)
                    if mt:
                        pages.append(mt.group(1))
        if pdf_path:
            doc.storeToURL(uno.systemPathToFileUrl(os.path.abspath(pdf_path)),
                           (pv("FilterName", "writer_pdf_Export"),))
        doc.close(True)
        try:
            desktop.terminate()
        except Exception:
            pass
        return pages
    finally:
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(profile, ignore_errors=True)


def fill_toc_pages(docx_path, pages):
    doc = Document(docx_path)
    # cached result of each PAGEREF field = the run after its 'separate' fldChar
    targets = []
    for instr in doc.element.body.iter(qn("w:instrText")):
        if (instr.text or "").strip().startswith("PAGEREF _Toc"):
            cached = instr.getparent().getnext().getnext()  # run after 'separate'
            t = cached.find(qn("w:t")) if cached is not None else None
            targets.append(t)
    if len(targets) != len(pages) or any(t is None for t in targets):
        return False
    for t, pg in zip(targets, pages):
        t.text = pg
    doc.save(docx_path)
    return True


def set_update_fields(doc):
    settings = doc.settings.element
    for old in settings.findall(qn("w:updateFields")):
        settings.remove(old)
    el = parse_xml(W('updateFields w:val="true"'))
    # schema order: updateFields must precede these siblings
    after = {"hdrShapeDefaults", "footnotePr", "endnotePr", "compat", "docVars", "rsids", "mathPr",
             "attachedSchema", "themeFontLang", "clrSchemeMapping", "doNotIncludeSubdocsInStats",
             "doNotAutoCompressPictures", "forceUpgrade", "captions", "readModeInkLockDown",
             "smartTagType", "schemaLibrary", "shapeDefaults", "doNotEmbedSmartTags",
             "decimalSymbol", "listSeparator"}
    for child in settings:
        if etree.QName(child).localname in after:
            child.addprevious(el)
            return
    settings.append(el)


# ---------------------------------------------------------------- main
def convert(md_path, out_path, meta_path=None, pdf=False, use_lo=True):
    with open(md_path, encoding="utf-8") as f:
        fm, body = split_front_matter(f.read())
    meta = dict(DEFAULT_META)
    meta.update({k: v for k, v in fm.items() if v is not None})
    if meta_path:
        with open(meta_path, encoding="utf-8") as f:
            meta.update({k: v for k, v in (yaml.safe_load(f) or {}).items() if v is not None})
    meta["title"], body = pop_title_h1(body, meta["title"])
    if not meta["title"]:
        meta["title"] = os.path.splitext(os.path.basename(md_path))[0]
    for k in ("title", "subtitle", "project", "client", "contractor", "doc_id", "revision",
              "date", "date_text", "toc_title"):
        meta[k] = "" if meta[k] is None else str(meta[k])
    levels = int(meta["toc_levels"])

    work = tempfile.mkdtemp(prefix="md2docx_")
    try:
        raw = os.path.join(work, "raw.docx")
        run_pandoc(body, os.path.dirname(os.path.abspath(md_path)), raw)
        doc = Document(raw)
        restyle(doc, meta)
        clean_body(doc)
        format_tables(doc)
        toc_paras, entries = build_toc(doc, levels)
        body_el = doc.element.body
        first = body_el[0]
        for el in front_matter(meta) + toc_paras:
            first.addprevious(el)
        build_header_footer(doc, meta)
        for part in (doc.element.body, doc.sections[0].header._element,
                     doc.sections[0].footer._element):
            mirror_cs_formatting(part)
            bold_runs_use_heading_font(part, meta["font_heading"])
            mirror_table_columns(part)
            merge_runs(part)
            split_runs_by_script(part)
        set_update_fields(doc)
        doc.save(out_path)
    finally:
        shutil.rmtree(work, ignore_errors=True)

    pdf_path = os.path.splitext(out_path)[0] + ".pdf" if pdf else None
    status = "TOC page numbers: left for Word to fill on open"
    if use_lo and entries:
        pages = libreoffice_toc_pages(out_path)
        if pages and fill_toc_pages(out_path, pages):
            status = "TOC page numbers: filled via LibreOffice (Word refreshes them on open)"
    if pdf_path:
        if use_lo and libreoffice_toc_pages(out_path, pdf_path=pdf_path) is not None:
            status += f"\nPDF: {pdf_path}"
        else:
            status += "\nPDF: not produced (LibreOffice/uno unavailable)"
    print(f"Wrote {out_path}  ({len(entries)} TOC entries)\n{status}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("markdown")
    ap.add_argument("-o", "--output", help="output .docx (default: next to the input)")
    ap.add_argument("--meta", help="YAML file with document metadata (overrides front matter)")
    ap.add_argument("--pdf", action="store_true", help="also export a PDF preview via LibreOffice")
    ap.add_argument("--no-lo", action="store_true", help="skip the LibreOffice TOC page-number pass")
    a = ap.parse_args()
    out = a.output or os.path.splitext(a.markdown)[0] + ".docx"
    if not shutil.which("pandoc"):
        sys.exit("pandoc is required (https://pandoc.org/installing.html)")
    convert(a.markdown, out, a.meta, pdf=a.pdf, use_lo=not a.no_lo)


if __name__ == "__main__":
    main()
