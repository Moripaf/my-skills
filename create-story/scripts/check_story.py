#!/usr/bin/env python3
"""Check a story folder against references/story-contract.md.

Usage: python -I check_story.py <story folder> [--repo <repo root>]
Exit code 1 when there are errors; warnings never fail the check.
"""
import argparse
import re
import sys
from pathlib import Path

PHASE_FILE = re.compile(r"^Phase-(\d\d)-(?!(?:Execution-Report|Build-Notes|Test-Result)\.md$)[A-Za-z0-9-]+\.md$")
FOLDER = re.compile(r"^Story-(\d{3})-[A-Za-z0-9-]+$")
MODELS = {"haiku/low", "haiku/medium", "haiku/high", "sonnet/low", "sonnet/medium", "none"}
HEADER_VALUES = {
    "Mode": {"worker", "interactive"},
    "Attended": {"no", "yes"},
}
SECTIONS = ["Goal", "Implementation", "Tests", "Verification", "Exit criteria", "Phase prompt"]
DIAGRAM_CHARS = re.compile(r"[─│┌┐└┘├┤┬┴┼╭╮╯╰▶►→←↑↓]|--+>|<--+|\|\s*\n\s*v\b|└─")
FENCE = re.compile(r"^```(\w*)\s*\n(.*?)^```", re.S | re.M)
EDGE = re.compile(r"P(\d\d)(?:\[[^\]]*\])?\s*-->\s*(?:\|[^|]*\|\s*)?P(\d\d)")
PATH = re.compile(r"`((?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+\.(?:py|md|toml|cfg|ini|txt|json|ya?ml|cs|csproj|slnx?|[cm]?[jt]sx?|go|java|kt|php|rs|sql|html|css))`")

errors, warnings = [], []


def err(where, msg):
    errors.append(f"ERROR {where}: {msg}")


def warn(where, msg):
    warnings.append(f"WARN  {where}: {msg}")


def read(path):
    return path.read_text(encoding="utf-8")


def check_common(name, text, repo):
    if 'dir="rtl"' in text:
        err(name, 'contains an RTL wrapper; stories are English')
    if "{{" in text:
        err(name, "has unfilled {{placeholders}}")
    for lang, body in FENCE.findall(text):
        if lang != "mermaid" and DIAGRAM_CHARS.search(body):
            err(name, f"a ```{lang or 'plain'} block looks like a diagram; use mermaid")
    if repo:
        for p in sorted(set(PATH.findall(text))):
            if "<" in p or "*" in p or "XX" in p or "NN" in p:
                continue
            if not (repo / p).exists() and not (repo / "docs" / p).exists():
                warn(name, f"path not found in repo: {p}")


def parse_phase(path, story_no):
    name = path.name
    text = read(path)
    no = PHASE_FILE.match(name).group(1)
    lines = text.splitlines()
    h1 = re.compile(rf"^# Story {story_no} / Phase {no} — .+")
    if not lines or not h1.match(lines[0]):
        err(name, f"first line must be '# Story {story_no} / Phase {no} — Title'")
    header = {}
    for line in lines[1:14]:
        m = re.match(r"^(Mode|Depends on|Attended|Worker|Builder|Tester):\s*(.+?)\s*$", line)
        if m:
            header[m.group(1)] = m.group(2)
    for field, allowed in HEADER_VALUES.items():
        if field not in header:
            err(name, f"missing header line '{field}:'")
        elif header[field] not in allowed:
            err(name, f"'{field}: {header[field]}' is not one of {sorted(allowed)}")
    deps = set()
    if "Depends on" not in header:
        err(name, "missing header line 'Depends on:'")
    elif header["Depends on"] != "none":
        for d in header["Depends on"].split(","):
            d = d.strip()
            if not re.fullmatch(r"\d\d", d):
                err(name, f"bad dependency '{d}' (use two digits, comma separated, or 'none')")
            else:
                deps.add(d)
    legacy = "Builder" not in header and "Tester" not in header and "Worker" in header
    if legacy:
        warn(name, "legacy 'Worker:' line; new stories use 'Builder:' and 'Tester:'")
        builder = header["Worker"]
        if builder not in MODELS:
            err(name, f"'Worker: {builder}' is not one of {sorted(MODELS)}")
    elif "Builder" not in header and "Tester" not in header:
        err(name, "missing header lines 'Builder:' and 'Tester:'")
        builder = None
    else:
        for field in ("Builder", "Tester"):
            if field not in header:
                err(name, f"missing header line '{field}:'")
            elif header[field] not in MODELS:
                err(name, f"'{field}: {header[field]}' is not one of {sorted(MODELS)}")
        builder = header.get("Builder")
        if (builder == "none") != (header.get("Tester") == "none"):
            err(name, "'Builder:' and 'Tester:' must both be 'none' or both name a model")
    if builder == "none" and header.get("Mode") == "worker":
        err(name, "a worker phase needs a builder model, not 'none'")
    found = [m.group(1) for m in re.finditer(r"^## (.+?)\s*$", text, re.M)]
    required = [s for s in SECTIONS if s != "Verification" or "Builder" in header and builder != "none"]
    for s in required:
        if s not in found:
            err(name, f"missing section '## {s}'")
    if legacy and builder != "none" and "Verification" not in found:
        warn(name, "no '## Verification' section for the test agent")
    expected = [s for s in SECTIONS if s in found]
    if [s for s in found if s in SECTIONS] != expected:
        err(name, f"sections must appear in order: {', '.join(SECTIONS)}")
    if builder not in (None, "none") and "Verification" in found:
        body = re.search(r"^## Verification\s*$(.*?)(?=^## |\Z)", text, re.M | re.S).group(1)
        if not re.search(r"`(build|test|lint) [^`:]+: [^`]+`", body):
            warn(name, "'## Verification' has no `<build|test|lint> <dir>: <command>` line for verify_phase.py")
    if not re.search(rf"^> Run only Phase {no} of Story {story_no}\b", text, re.M):
        err(name, f"phase prompt must start with '> Run only Phase {no} of Story {story_no}'")
    return no, header, deps, text


def find_cycle(graph):
    state = {}

    def visit(n, stack):
        state[n] = 1
        for d in graph.get(n, ()):
            if state.get(d) == 1:
                return stack + [n, d]
            if d not in state:
                c = visit(d, stack + [n])
                if c:
                    return c
        state[n] = 2
        return None

    for n in graph:
        if n not in state:
            c = visit(n, [])
            if c:
                return c
    return None


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Persian text would crash a cp1252 console
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--repo", help="repo root for path checks (default: detected from the folder)")
    args = ap.parse_args()
    folder = Path(args.folder).resolve()
    if not folder.is_dir():
        print(f"not a folder: {folder}")
        return 2
    repo = Path(args.repo).resolve() if args.repo else next(
        (p for p in folder.parents if (p / ".git").exists()), None)

    m = FOLDER.match(folder.name)
    if not m:
        err(folder.name, "folder must be named Story-NNN-Title-In-Kebab-Case")
        story_no = "???"
    else:
        story_no = m.group(1)

    prompt = folder / "Prompt.md"
    tier = None
    if not prompt.exists():
        err("Prompt.md", "missing")
    else:
        t = read(prompt)
        if not re.match(rf"# Story {story_no} — .+", t):
            err("Prompt.md", f"first line must be '# Story {story_no} — Title'")
        tm = re.search(r"^Tier:\s*(small|large)\s*$", t, re.M)
        if not tm:
            err("Prompt.md", "missing 'Tier: small' or 'Tier: large' line")
        else:
            tier = tm.group(1)
        for s in ("## How to run", "## Fixed rules"):
            if s not in t:
                err("Prompt.md", f"missing section '{s}'")
        if "Execution-Report" not in t:
            err("Prompt.md", "read-first list must include the phase execution reports")
        check_common("Prompt.md", t, repo)

    for required in ["Plan.md", "CheckList.md"] + (["PRD.md"] if tier == "large" else []):
        if not (folder / required).exists():
            err(required, "missing")
    if (folder / "PRD.md").exists():
        check_common("PRD.md", read(folder / "PRD.md"), repo)

    phase_files = sorted(p for p in folder.iterdir() if PHASE_FILE.match(p.name))
    if not phase_files:
        err(folder.name, "no phase guides (Phase-NN-Title.md)")
    phases = {}
    for p in phase_files:
        no, header, deps, text = parse_phase(p, story_no)
        if no in phases:
            err(p.name, f"duplicate phase number {no}")
        phases[no] = (p.name, header, deps)
        check_common(p.name, text, repo)

    graph = {no: deps for no, (_, _, deps) in phases.items()}
    for no, (name, _, deps) in phases.items():
        for d in deps:
            if d not in phases:
                err(name, f"depends on missing phase {d}")
    cycle = find_cycle({k: {d for d in v if d in phases} for k, v in graph.items()})
    if cycle:
        err("phases", "dependency cycle: " + " -> ".join(cycle))

    if tier == "large" and phases:
        first, last = min(phases), max(phases)
        if phases[first][1].get("Mode") != "interactive":
            err(phases[first][0], "a large story starts with an interactive discovery phase")
        lh = phases[last][1]
        if lh.get("Mode") != "interactive" or lh.get("Attended") != "yes":
            err(phases[last][0], "a large story ends with an interactive, attended cutover/docs phase")

    plan_path = folder / "Plan.md"
    if plan_path.exists():
        plan = read(plan_path)
        check_common("Plan.md", plan, repo)
        for no, (name, _, _) in phases.items():
            if f"]({name})" not in plan:
                err("Plan.md", f"phase order has no link to {name}")
        edges = set()
        for lang, body in FENCE.findall(plan):
            if lang == "mermaid":
                edges |= {(a, b) for a, b in EDGE.findall(body)}
        expected = {(d, no) for no, deps in graph.items() for d in deps}
        for a, b in sorted(expected - edges):
            err("Plan.md", f"dependency graph is missing edge P{a} --> P{b}")
        for a, b in sorted(edges - expected):
            err("Plan.md", f"edge P{a} --> P{b} is not in Phase {b}'s 'Depends on'")

        wave_of = {}
        rows = re.findall(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|\s*$", plan, re.M)
        if not rows:
            err("Plan.md", "no waves table (| Wave | Phases | Start when |)")
        for wave, cell, _ in rows:
            for no in re.findall(r"\d\d", cell):
                if no in wave_of:
                    err("Plan.md", f"phase {no} is in waves {wave_of[no]} and {wave}")
                wave_of[no] = int(wave)
            if re.search(r"→|->", cell):
                err("Plan.md", f"wave {wave} chains phases; sequential phases go in separate waves")
        for no in phases:
            if no not in wave_of:
                err("Plan.md", f"phase {no} is in no wave")
        for no in wave_of:
            if no not in phases:
                err("Plan.md", f"waves table names missing phase {no}")
        for no, deps in graph.items():
            for d in deps:
                if no in wave_of and d in wave_of and wave_of[d] >= wave_of[no]:
                    err("Plan.md", f"phase {no} (wave {wave_of[no]}) must come after its dependency {d} (wave {wave_of[d]})")
        if "/Prompt.md` and run Phase" not in plan:
            err("Plan.md", "missing the session start line ('Read `…/Prompt.md` and run Phase NN.')")

    cl = folder / "CheckList.md"
    if cl.exists():
        t = read(cl)
        check_common("CheckList.md", t, repo)
        for no in phases:
            if not re.search(rf"^## Phase {no}\b", t, re.M):
                err("CheckList.md", f"no '## Phase {no}' section")
        if not re.search(r"^## Every phase\s*$", t, re.M):
            err("CheckList.md", "no '## Every phase' section")

    for line in errors + warnings:
        print(line)
    print(f"{len(errors)} error(s), {len(warnings)} warning(s) — {folder.name}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
