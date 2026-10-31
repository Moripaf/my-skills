#!/usr/bin/env python3
"""Finish a learning doc: wrap its body in the house style and check its size.

Usage: python -I learn_doc.py <doc.md> --lang fa|en

The explainer writes only the body (Markdown, no CSS). This wraps it with
references/style-header.html (Mikhak font, colours, callouts), RTL for fa and LTR for en,
and is safe to run again. It prints the word count (outside code, diagrams and HTML) and
the Mermaid line count. Exit code 1 when a Mermaid block is not English or Mermaid is
over the line budget; the word count is a guide, not a gate.
"""
import argparse
import re
import sys
from pathlib import Path

HEADER = Path(__file__).resolve().parents[1] / "references" / "style-header.html"
START, END = "<!-- learn-doc:body -->", "<!-- learn-doc:end -->"
MERMAID = re.compile(r"^```mermaid\s*\n(.*?)^```", re.S | re.M)
NON_ENGLISH = re.compile(r"[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]")
WORD_TARGET, MERMAID_MAX = 1000, 70


def body_of(text):
    if START in text:
        return text.split(START, 1)[1].split(END, 1)[0].strip("\n")
    return text.strip("\n")


def count_words(body):
    t = re.sub(r"(?s)```.*?```|<style.*?</style>|<[^>]+>", " ", body)
    return len(re.findall(r"\w+", t))


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Persian text would crash a cp1252 console
    ap = argparse.ArgumentParser()
    ap.add_argument("doc")
    ap.add_argument("--lang", choices=["fa", "en"], required=True)
    args = ap.parse_args()
    doc = Path(args.doc)
    body = body_of(doc.read_text(encoding="utf-8"))
    # the ltr wrapper sits outside the markers, so a rerun reads back only the body
    ltr, end = ('<div class="ltr">\n\n', '\n\n</div>') if args.lang == "en" else ("", "")
    # the header ends with an open <div class="document-body">; blank lines keep the Markdown rendering
    doc.write_text(f"{HEADER.read_text(encoding='utf-8').rstrip()}\n\n{ltr}{START}\n\n{body}\n\n{END}{end}\n\n</div>\n",
                   encoding="utf-8", newline="\n")

    blocks = MERMAID.findall(body)
    mermaid_lines = sum(len(b.strip().splitlines()) for b in blocks)
    bad = [i + 1 for i, b in enumerate(blocks) if NON_ENGLISH.search(b)]
    words = count_words(body)
    print(f"WORDS: {words} (information only, no size target)")
    print(f"MERMAID: {len(blocks)} block(s), {mermaid_lines} line(s) (max {MERMAID_MAX})")
    problems = []
    if bad:
        problems.append(f"Mermaid block(s) {bad} contain non-English text; write diagrams in English")
    if mermaid_lines > MERMAID_MAX:
        problems.append(f"Mermaid has {mermaid_lines} lines; keep it under {MERMAID_MAX}")
    for p in problems:
        print(f"FIX: {p}")
    print("DOC: ok" if not problems else "DOC: fix and run again")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
