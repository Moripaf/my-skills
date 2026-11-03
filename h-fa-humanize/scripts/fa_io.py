"""h-fa-humanize I/O: pull text segments out of a document and put rewritten text back,
keeping every bit of formatting. Standard library only (no python-docx / openpyxl needed).

  python fa_io.py extract <input> <segments.json>
  python fa_io.py apply   <input> <output> <rewrite.json> [<rewrite2.json> ...] [--report report.md]

Formats: .docx .pptx .xlsx (text inside the XML only: styles, tables, images, charts untouched),
         .html/.htm, .md/.markdown/.txt, .csv

Segment text may contain markers that MUST be kept, in the same order:
  ⟦#k⟧          fixed item (tab, line break, image, field, HTML tag). Never remove or move across other markers.
  ⟦k⟧ … ⟦/k⟧    text with different formatting (bold, link, other font). Rewrite the words inside freely,
                but keep the pair, and keep the markers in the original order.

rewrite.json: {"segments": [{"id": "...", "text": "new text", "why": "short reason (Persian)"}]}
Only changed segments need to be listed.
"""
import csv, html, io, json, os, re, sys, zipfile

MARK = re.compile(r"⟦(#?)(\d+)⟧|⟦/(\d+)⟧")
PERSIAN = re.compile(r"[\u0600-\u06FF]")
DIG = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def xml_unesc(s):
    return html.unescape(s)


def xml_esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ----------------------------------------------------------------------------- OOXML
class OOXML:
    """Paragraph-level text model over raw XML strings (regex, so nothing else in the XML changes)."""

    def __init__(self, fmt):
        self.fmt = fmt
        if fmt == "docx":
            self.parts = re.compile(r"word/(document|header\d*|footer\d*|footnotes|endnotes)\.xml$")
            self.para = re.compile(r"<w:p[\s>](?:(?!<w:p[\s>]).)*?</w:p>", re.S)
            self.tok = re.compile(r"<w:r[\s>].*?</w:r>|<w:r/>", re.S)
            self.rpr = re.compile(r"<w:rPr\b[^>]*/>|<w:rPr\b.*?</w:rPr>", re.S)
            self.t = re.compile(r"(<w:t\b[^>]*>)(.*?)(</w:t>)|<w:t\b[^>]*/>", re.S)
            self.cont = re.compile(r"<(w:hyperlink|w:ins|w:smartTag|w:fldSimple)\b.*?</\1>", re.S)
            self.allowed = re.compile(r"<w:rPr\b[^>]*/>|<w:rPr\b.*?</w:rPr>|<w:t\b[^>]*/>|<w:t\b[^>]*>.*?</w:t>|<w:lastRenderedPageBreak/>", re.S)
            self.inner = re.compile(r"<w:r\b[^>]*>(.*)</w:r>", re.S)
            self.tag = "w:"
        elif fmt == "pptx":
            self.parts = re.compile(r"ppt/(slides/slide\d+|notesSlides/notesSlide\d+)\.xml$")
            self.para = re.compile(r"<a:p[\s>](?:(?!<a:p[\s>]).)*?</a:p>", re.S)
            self.tok = re.compile(r"<a:r>.*?</a:r>|<a:br\b[^>]*/>|<a:br\b.*?</a:br>|<a:fld\b.*?</a:fld>", re.S)
            self.rpr = re.compile(r"<a:rPr\b[^>]*/>|<a:rPr\b.*?</a:rPr>", re.S)
            self.t = re.compile(r"(<a:t\b[^>]*>)(.*?)(</a:t>)|<a:t\b[^>]*/>", re.S)
            self.cont = None
            self.allowed = re.compile(r"<a:rPr\b[^>]*/>|<a:rPr\b.*?</a:rPr>|<a:t\b[^>]*/>|<a:t\b[^>]*>.*?</a:t>", re.S)
            self.inner = re.compile(r"<a:r>(.*)</a:r>", re.S)
            self.tag = "a:"
        else:  # xlsx shared strings
            self.parts = re.compile(r"xl/sharedStrings\.xml$")
            self.para = re.compile(r"<(?:x:)?si>.*?</(?:x:)?si>", re.S)
            self.tok = re.compile(r"<(?:x:)?r>.*?</(?:x:)?r>|<(?:x:)?t\b[^>]*>.*?</(?:x:)?t>|<(?:x:)?t\b[^>]*/>|<(?:x:)?rPh\b.*?</(?:x:)?rPh>|<(?:x:)?phoneticPr\b[^>]*/>", re.S)
            self.rpr = re.compile(r"<(?:x:)?rPr\b.*?</(?:x:)?rPr>|<(?:x:)?rPr\b[^>]*/>", re.S)
            self.t = re.compile(r"(<(?:x:)?t\b[^>]*>)(.*?)(</(?:x:)?t>)|<(?:x:)?t\b[^>]*/>", re.S)
            self.cont = None
            self.allowed = re.compile(r"<(?:x:)?rPr\b.*?</(?:x:)?rPr>|<(?:x:)?rPr\b[^>]*/>|<(?:x:)?t\b[^>]*>.*?</(?:x:)?t>|<(?:x:)?t\b[^>]*/>", re.S)
            self.inner = re.compile(r"<(?:x:)?r>(.*)</(?:x:)?r>|(<(?:x:)?t\b.*)", re.S)
            self.tag = ""

    def spans(self, p):
        """Split one paragraph string into spans: text spans (runs with the same formatting) and fixed tokens."""
        conts = [(m.start(), m.end()) for m in self.cont.finditer(p)] if self.cont else []
        out = []
        for m in self.tok.finditer(p):
            s = m.group(0)
            if re.match(r"<(?:x:)?rPh\b|<(?:x:)?phoneticPr\b", s):
                continue
            inner = self.inner.match(s)
            body = (inner.group(1) or inner.group(2) or "") if inner else ""
            fixed = (not inner) or bool(re.search(r"<\w", self.allowed.sub("", body)))
            c = next((i for i, (a, b) in enumerate(conts) if a <= m.start() < b), -1)
            if fixed:
                out.append({"fixed": True, "toks": [(m.start(), m.end())]})
                continue
            r = self.rpr.search(body)
            key = ((r.group(0) if r else ""), c)
            txt = "".join(xml_unesc(t.group(2) or "") for t in self.t.finditer(body))
            if out and not out[-1]["fixed"] and out[-1]["key"] == key:
                out[-1]["toks"].append((m.start(), m.end())); out[-1]["text"] += txt
            else:
                out.append({"fixed": False, "key": key, "toks": [(m.start(), m.end())], "text": txt})
        return out

    def render(self, sp):
        """Segment text with markers, or None if the paragraph has no visible text."""
        texts = [s for s in sp if not s["fixed"]]
        if not texts or not "".join(s["text"] for s in texts).strip():
            return None, None
        lens = {}
        for s in texts: lens[s["key"]] = lens.get(s["key"], 0) + len(s["text"])
        dom = max(lens, key=lens.get)
        parts = []
        for k, s in enumerate(sp, 1):
            if s["fixed"]: parts.append(f"⟦#{k}⟧")
            elif s["key"] == dom: parts.append(s["text"])
            else: parts.append(f"⟦{k}⟧{s['text']}⟦/{k}⟧")
        return "".join(parts), dom

    def write_span(self, p, s, new):
        """Return list of (start, end, replacement) putting `new` into the span's first <t>, emptying the rest."""
        reps, first = [], True
        for a, b in s["toks"]:
            run = p[a:b]
            def sub(m):
                nonlocal first
                val = new if first else ""
                first = False
                if self.tag == "w:":
                    return f'<w:t xml:space="preserve">{xml_esc(val)}</w:t>'
                if m.group(1) is None:  # self-closing <t/>
                    name = re.match(r"<([\w:]+)", m.group(0)).group(1)
                    return f"<{name}>{xml_esc(val)}</{name}>"
                op = m.group(1)
                if self.tag == "" and "xml:space" not in op:
                    op = op[:-1] + ' xml:space="preserve">'
                return op + xml_esc(val) + m.group(3)
            reps.append((a, b, self.t.sub(sub, run)))
        if first and new:  # span had no text element at all: add one to its first run
            a, b = s["toks"][0]
            run = p[a:b]; close = run.rindex("</")
            t = '<w:t xml:space="preserve">' if self.tag == "w:" else f"<{self.tag}t>"
            reps[0] = (a, b, run[:close] + t + xml_esc(new) + f"</{self.tag}t>" + run[close:])
        return reps


def assign(sp, dom, new):
    """Map rewritten marker text back onto spans. Returns {span_index: text} or raises ValueError."""
    items, pos, cur = [], 0, None
    for m in MARK.finditer(new):
        chunk = new[pos:m.start()]
        if m.group(3):  # closing ⟦/k⟧
            k = int(m.group(3))
            if cur != k: raise ValueError(f"marker ⟦/{k}⟧ does not close the open marker")
            items.append(("m", k, chunk)); cur = None
        else:
            if cur is not None: raise ValueError(f"marker ⟦{cur}⟧ not closed")
            items.append(("u", None, chunk))
            k = int(m.group(2))
            if m.group(1): items.append(("f", k, ""))
            else: cur = k
        pos = m.end()
    if cur is not None: raise ValueError(f"marker ⟦{cur}⟧ not closed")
    items.append(("u", None, new[pos:]))
    want = [(("f" if s["fixed"] else "m"), k) for k, s in enumerate(sp, 1) if s["fixed"] or s["key"] != dom]
    got = [(t, k) for t, k, _ in items if t != "u"]
    if want != got:
        raise ValueError(f"markers changed: expected {fmt_marks(want)} got {fmt_marks(got)}")
    # gaps of dominant spans between markers
    gaps, g = [], []
    for k, s in enumerate(sp, 1):
        if not s["fixed"] and s["key"] == dom: g.append(k)
        else: gaps.append(g); g = []
    gaps.append(g)
    res, gi, last = {}, 0, None
    for t, k, chunk in items:
        if t == "u":
            grp = gaps[gi]; gi += 1
            if grp:
                res[grp[0]] = chunk
                for x in grp[1:]: res[x] = ""
                last = grp[0]
            elif chunk:
                if last is not None and not sp[last - 1]["fixed"]: res[last] = res.get(last, "") + chunk
                else: res.setdefault("_pending", ""); res["_pending"] += chunk
        elif t == "m":
            res[k] = res.pop("_pending", "") + chunk; last = k
        else:
            last = k
    if "_pending" in res:
        tail = res.pop("_pending")
        tgt = max((k for k in res), default=None)
        if tgt is None: raise ValueError("text has nowhere to go")
        res[tgt] += tail
    return res


def fmt_marks(ms):
    return " ".join(("⟦#%d⟧" if t == "f" else "⟦%d⟧") % k for t, k in ms)


def ooxml_extract(path, fmt):
    M, segs = OOXML(fmt), []
    with zipfile.ZipFile(path) as z:
        for name in sorted(z.namelist(), key=part_order):
            if not M.parts.search(name): continue
            x = z.read(name).decode("utf-8")
            for i, pm in enumerate(M.para.finditer(x)):
                text, _ = M.render(M.spans(pm.group(0)))
                if text is not None and PERSIAN.search(text):
                    segs.append({"id": f"{name}#{i}", "text": text})
    return segs


def part_order(n):
    m = re.search(r"(\d+)\.xml$", n)
    main = n.startswith(("word/document", "ppt/slides/", "xl/"))
    return (0 if main else 1, re.sub(r"\d+\.xml$", "", n), int(m.group(1)) if m else 0)


def ooxml_apply(path, out, fmt, rw, errors):
    M = OOXML(fmt)
    by_part = {}
    for sid, v in rw.items():
        part, i = sid.rsplit("#", 1); by_part.setdefault(part, {})[int(i)] = (sid, v)
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(out + ".tmp", "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename in by_part:
                x = data.decode("utf-8")
                reps = []
                for i, pm in enumerate(M.para.finditer(x)):
                    if i not in by_part[info.filename]: continue
                    sid, new = by_part[info.filename][i]
                    p = pm.group(0); sp = M.spans(p); _, dom = M.render(sp)
                    try:
                        res = assign(sp, dom, new)
                    except ValueError as e:
                        errors.append(f"{sid}: {e}"); continue
                    preps = []
                    for k, txt in res.items(): preps += M.write_span(p, sp[k - 1], txt)
                    for a, b, r in sorted(preps, reverse=True): p = p[:a] + r + p[b:]
                    reps.append((pm.start(), pm.end(), p))
                for a, b, r in sorted(reps, reverse=True): x = x[:a] + r + x[b:]
                data = x.encode("utf-8")
            zout.writestr(info, data)
    return out + ".tmp"


# ----------------------------------------------------------------------------- HTML
BLOCK = set("p li h1 h2 h3 h4 h5 h6 td th dt dd blockquote figcaption caption summary label button title div section article header footer nav aside main ul ol table tr thead tbody tfoot dl body head html br hr option legend details figure form".split())
SKIP = {"script", "style", "pre", "code", "svg", "textarea", "math", "kbd", "samp"}
TAG = re.compile(r"(<!--.*?-->|<[^>]+>)", re.S)


def html_tokens(src):
    toks, skip = TAG.split(src), None
    segs, cur = [], []   # cur: list of token indices in the current block

    def flush():
        if any(not toks[j].startswith("<") and PERSIAN.search(toks[j]) for j in cur):
            segs.append(list(cur))
        cur.clear()
    for j, t in enumerate(toks):
        if j % 2 == 1:  # tag
            m = re.match(r"<\s*(/?)\s*([a-zA-Z0-9]+)", t)
            name = m.group(2).lower() if m else ""
            if skip:
                if m and m.group(1) and name == skip: skip = None
                continue
            if name in SKIP and m and not m.group(1) and not t.endswith("/>"):
                flush(); skip = name; continue
            if name in BLOCK or not m:
                flush(); continue
            cur.append(j)
        else:
            if skip: continue
            cur.append(j)
    flush()
    return toks, segs


def html_render(toks, seg):
    out, k = [], 0
    for j in seg:
        if toks[j].startswith("<"):
            k += 1; out.append(f"⟦#{k}⟧")
        else:
            out.append(html.unescape(toks[j]))
    return "".join(out)


def html_apply_seg(toks, seg, new):
    tags = [j for j in seg if toks[j].startswith("<")]
    pieces = MARK.split(new)
    # MARK.split yields text, g1, g2, g3, text, ...
    texts, marks = [pieces[0]], []
    for i in range(1, len(pieces), 4):
        if pieces[i] != "#" or pieces[i + 2] is not None: raise ValueError("only ⟦#k⟧ markers exist in HTML segments")
        marks.append(int(pieces[i + 1])); texts.append(pieces[i + 3])
    if marks != list(range(1, len(tags) + 1)):
        raise ValueError(f"tag markers changed: expected 1..{len(tags)} in order, got {marks}")
    textslots = []  # text token positions in each gap
    gap = []
    for j in seg:
        if toks[j].startswith("<"): textslots.append(gap); gap = []
        else: gap.append(j)
    textslots.append(gap)
    for slots, t in zip(textslots, texts):
        esc = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if slots:
            toks[slots[0]] = esc
            for s in slots[1:]: toks[s] = ""
        elif t.strip():
            raise ValueError("text was moved into a position that had no text (between two adjacent tags)")


# ----------------------------------------------------------------------------- text formats
def md_blocks(src):
    lines = src.split("\n")
    blocks, cur, fence, raw = [], [], False, None
    def flush():
        if cur and any(PERSIAN.search(lines[i]) for i in cur): blocks.append(list(cur))
        cur.clear()
    for i, l in enumerate(lines):
        s = l.strip()
        if s.startswith("```") or s.startswith("~~~"):
            flush(); fence = not fence; continue
        if fence: continue
        if raw:
            if re.search(rf"</{raw}>", s, re.I): raw = None
            continue
        m = re.match(r"<(style|script)\b", s, re.I)
        if m:
            flush()
            if not re.search(rf"</{m.group(1)}>", s, re.I): raw = m.group(1)
            continue
        if not s or re.match(r"^(---+|\*\*\*+|___+)$", s) or (s.startswith("<") and s.endswith(">") and not PERSIAN.search(s)):
            flush(); continue
        if re.match(r"^(#{1,6}\s|\s*[-*+]\s|\s*\d+[.)]\s|\|)", l) and cur:
            flush()
        cur.append(i)
        if re.match(r"^(#{1,6}\s|\|)", l): flush()
    flush()
    return lines, blocks


# ----------------------------------------------------------------------------- driver
def kind(path):
    e = os.path.splitext(path)[1].lower()
    if e in (".docx", ".docm"): return "docx"
    if e in (".pptx",): return "pptx"
    if e in (".xlsx", ".xlsm"): return "xlsx"
    if e in (".html", ".htm"): return "html"
    if e in (".md", ".markdown", ".txt", ".text"): return "md"
    if e == ".csv": return "csv"
    if e in (".doc", ".xls", ".ppt", ".rtf", ".odt"):
        sys.exit(f"{e} is a legacy/other format: open it in Word/Excel/PowerPoint and Save As .docx/.xlsx/.pptx first.")
    sys.exit(f"unsupported format {e}")


def read_text(path):
    raw = open(path, "rb").read()
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw[3:].decode("utf-8"), "utf-8-sig"
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return raw.decode("utf-16"), "utf-16"
    for enc in ("utf-8", "cp1256"):
        try: return raw.decode(enc), enc
        except UnicodeDecodeError: pass
    sys.exit("cannot decode text file")


def extract(path):
    k = kind(path)
    if k in ("docx", "pptx", "xlsx"): return ooxml_extract(path, k)
    src, _ = read_text(path)
    if k == "html":
        toks, segs = html_tokens(src)
        return [{"id": f"h{i}", "text": html_render(toks, s)} for i, s in enumerate(segs)]
    if k == "md":
        lines, blocks = md_blocks(src)
        return [{"id": f"L{b[0] + 1}-{b[-1] + 1}", "text": "\n".join(lines[i] for i in b)} for b in blocks]
    rows = list(csv.reader(io.StringIO(src)))
    return [{"id": f"r{r}c{c}", "text": v} for r, row in enumerate(rows) for c, v in enumerate(row) if PERSIAN.search(v)]


def numbers(s):
    return sorted(re.findall(r"\d+(?:[.,/٫]\d+)*", MARK.sub("", s).translate(DIG)))


def apply(path, out, rw, errors):
    k = kind(path)
    if k in ("docx", "pptx", "xlsx"):
        tmp = ooxml_apply(path, out, k, rw, errors); return tmp
    src, enc = read_text(path)
    if k == "html":
        toks, segs = html_tokens(src)
        for i, s in enumerate(segs):
            sid = f"h{i}"
            if sid in rw:
                try: html_apply_seg(toks, s, rw[sid])
                except ValueError as e: errors.append(f"{sid}: {e}")
        res = "".join(toks)
    elif k == "md":
        lines, blocks = md_blocks(src)
        for b in reversed(blocks):
            sid = f"L{b[0] + 1}-{b[-1] + 1}"
            if sid in rw: lines[b[0]:b[-1] + 1] = rw[sid].split("\n")
        res = "\n".join(lines)
    else:
        rows = list(csv.reader(io.StringIO(src)))
        for sid, v in rw.items():
            r, c = map(int, re.match(r"r(\d+)c(\d+)", sid).groups()); rows[r][c] = v
        buf = io.StringIO(); csv.writer(buf, lineterminator="\n").writerows(rows); res = buf.getvalue()
    tmp = out + ".tmp"
    open(tmp, "w", encoding="utf-8-sig" if enc == "utf-8-sig" else "utf-8", newline="").write(res)
    return tmp


def main():
    a = sys.argv[1:]
    if len(a) >= 3 and a[0] == "extract":
        segs = extract(a[1])
        json.dump({"file": os.path.abspath(a[1]), "segments": segs}, open(a[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        marked = sum(1 for s in segs if "⟦" in s["text"])
        print(f"OK  {len(segs)} segments ({marked} with markers, {sum(len(s['text']) for s in segs)} chars) -> {a[2]}")
        return
    if len(a) >= 4 and a[0] == "apply":
        report = None
        if "--report" in a:
            i = a.index("--report"); report = a[i + 1]; a = a[:i] + a[i + 2:]
        src, out, files = a[1], a[2], a[3:]
        orig = {s["id"]: s["text"] for s in extract(src)}
        rw, why = {}, {}
        for f in files:
            for s in json.load(open(f, encoding="utf-8"))["segments"]:
                if s["id"] not in orig: sys.exit(f"ERROR unknown segment id {s['id']} (re-run extract on the same input file)")
                if s["text"] != orig[s["id"]]:
                    rw[s["id"]] = s["text"]; why[s["id"]] = s.get("why", "")
        errors, warns = [], []
        for sid, t in rw.items():
            if numbers(t) != numbers(orig[sid]): warns.append(f"{sid}: numbers differ: {numbers(orig[sid])} -> {numbers(t)}")
            if kind(src) == "md":
                for sym in ("**", "`", "](", "|", "<"):
                    if orig[sid].count(sym) != t.count(sym): warns.append(f"{sid}: count of '{sym}' changed (markdown/HTML markup?)")
        tmp = apply(src, out, rw, errors)
        for w in warns: print("WARN ", w)
        if errors:
            os.remove(tmp)
            for e in errors: print("ERROR", e)
            sys.exit("nothing written: fix the segments above and re-run apply")
        os.replace(tmp, out)
        bad = []
        if kind(src) in ("docx", "pptx", "xlsx", "html"):
            check = {s["id"]: s["text"] for s in extract(out)}
            bad = [sid for sid, t in rw.items() if MARK.sub("", check.get(sid, "")).strip() != MARK.sub("", t).strip()]
        for sid in bad: print("WARN ", f"{sid}: re-extracted text differs from the rewrite, check this paragraph in the output")
        print(f"OK  {len(rw)} of {len(orig)} segments changed -> {out}")
        if report:
            clean = lambda s: MARK.sub(lambda m: " " if m.group(1) else "", s).replace("|", "\\|").replace("\n", "<br>")
            rows = [f"| {i} | {clean(orig[sid])} | {clean(rw[sid])} | {why[sid].replace('|', '/')} |" for i, sid in enumerate(rw, 1)]
            hdr = f"# گزارش انسانی‌سازی متن\n\n**فایل:** `{os.path.basename(src)}` → `{os.path.basename(out)}`  \n**بخش‌های تغییرکرده:** {len(rw)} از {len(orig)}\n\n| # | قبل | بعد | دلیل |\n|---|---|---|---|\n"
            body = hdr + "\n".join(rows) + "\n"
            style = next((p for p in (os.path.expanduser(f"~/.{a}/skills/h-md-style/references/style-header.html") for a in ("claude", "codex")) if os.path.exists(p)), None)
            if style:  # render the report in the user's h-md-style when it is installed
                body = open(style, encoding="utf-8").read() + body + "\n</div>\n"
            open(report, "w", encoding="utf-8").write(body)
            print(f"OK  report -> {report}")
        return
    sys.exit(__doc__)


if __name__ == "__main__":
    main()
