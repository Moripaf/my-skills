#!/usr/bin/env python3
"""Mechanical checks for one story phase, run by the test agent. Works for any stack.

Usage: python -I verify_phase.py --base <sha> [--run build|test|lint <dir> "<cmd>"]... [--repo <root>] [--timeout 900]

--run kinds, each run from <dir> (relative to the repo root, "." for the root):
  build  must exit 0; every error counts (a change can break code it doesn't touch)
  test   must exit 0; prints the runner's summary and failed test names
  lint   only issues on lines this phase added count; older issues are the repo's debt
Python tools (pytest, ruff, mypy, pyright) run in the project's environment (uv, poetry or .venv)
even when the command says plain `python -m` or `pytest`.

Also scans everything changed since <base> (commits, staged, unstaged and untracked files) for rule
breaks: skipped or disabled tests, lint/type suppressions, migrations, deleted tests, secrets, .env
files, model weights and large files. Prints a short summary, never full logs, and ends with
`MECHANICAL: PASS` or `MECHANICAL: FAIL`. Exit code 1 on FAIL, 2 on bad arguments.
"""
import argparse
import ast
import re
import shlex
import subprocess
import sys
from pathlib import Path

ANY = re.compile(r"")
# (label, regex on added lines, applies to path regex)
RULES = [
    ("skipped test", re.compile(r"pytest\.mark\.skip\b|pytest\.skip\(|unittest\.skip|\.mark\.xfail\b|pytest\.xfail\("), re.compile(r"\.py$")),
    ("suppressed lint", re.compile(r"#\s*noqa\b", re.I), re.compile(r"\.py$")),
    ("suppressed type check", re.compile(r"#\s*type:\s*ignore", re.I), re.compile(r"\.py$")),
    ("excluded from coverage", re.compile(r"#\s*pragma:\s*no\s*cover", re.I), re.compile(r"\.py$")),
    ("skipped test", re.compile(r"\b(it|test|describe)\.(skip|only)\(|\bx(it|describe|test)\("), re.compile(r"\.[cm]?[jt]sx?$")),
    ("suppressed lint", re.compile(r"eslint-disable|@ts-(ignore|nocheck|expect-error)|biome-ignore"), re.compile(r"\.[cm]?[jt]sx?$")),
    ("skipped test", re.compile(r"\bSkip\s*=\s*\""), re.compile(r"\.cs$")),
    ("suppressed warning", re.compile(r"#pragma\s+warning\s+disable|SuppressMessage\("), re.compile(r"\.cs$")),
    ("skipped test", re.compile(r"\bt\.Skip(Now|f)?\("), re.compile(r"\.go$")),
    ("suppressed lint", re.compile(r"//\s*nolint"), re.compile(r"\.go$")),
    ("skipped test", re.compile(r"@(Disabled|Ignore)\b"), re.compile(r"\.(java|kt)$")),
    ("suppressed warning", re.compile(r"@SuppressWarnings\b"), re.compile(r"\.(java|kt)$")),
    ("skipped test", re.compile(r"markTestSkipped|markTestIncomplete|@group\s+skip"), re.compile(r"\.php$")),
    ("suppressed lint", re.compile(r"@phpstan-ignore|@psalm-suppress|phpcs:ignore"), re.compile(r"\.php$")),
    ("skipped test", re.compile(r"#\[ignore\]"), re.compile(r"\.rs$")),
    ("suppressed lint", re.compile(r"#!?\[allow\("), re.compile(r"\.rs$")),
    ("secret in code", re.compile(
        r"\bsk-(ant-)?[A-Za-z0-9_-]{20,}|\bAKIA[0-9A-Z]{16}\b|\bgh[pousr]_[A-Za-z0-9]{36}\b|\bglpat-[A-Za-z0-9_-]{20}\b"
        r"|\bhf_[A-Za-z0-9]{30,}\b|\bxox[abprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----"), ANY),
]
# a literal assigned to a key-like name, outside test files (they hold fake keys); URLs are not secrets
SECRET_ASSIGN = re.compile(r"(api[_-]?key|secret|token|password)\w*\s*[:=]\s*[\"'](?!https?://)[^\"'\s]{16,}[\"']", re.I)
MIGRATION = re.compile(r"(^|/)(migrations?|Migrations|alembic/versions|db/migrate|db/migration)/")
TEST_FILE = re.compile(r"(^|/)(tests?|Tests?|__tests__|spec)/|(^|/)test_[^/]*\.py$|_test\.(py|go)$"
                       r"|\.(test|spec)\.[cm]?[jt]sx?$|Tests?\.(cs|java|kt|php)$|(^|/)conftest\.py$|\.Tests?/")
DEPS_FILE = re.compile(r"(^|/)(pyproject\.toml|requirements[^/]*\.(txt|in)|setup\.(py|cfg)|uv\.lock|poetry\.lock"
                       r"|Pipfile(\.lock)?|package\.json|package-lock\.json|pnpm-lock\.yaml|yarn\.lock|bun\.lockb?"
                       r"|[^/]+\.csproj|Directory\.Packages\.props|packages\.lock\.json|go\.(mod|sum)|pom\.xml"
                       r"|build\.gradle(\.kts)?|composer\.(json|lock)|Cargo\.(toml|lock)|Gemfile(\.lock)?)$")
ENV_FILE = re.compile(r"(^|/)\.env(\.(?!example$|sample$|template$|dist$)[^/]+)?$")
WEIGHTS = re.compile(r"\.(pt|pth|ckpt|safetensors|onnx|gguf|h5|keras|tflite|mlmodel)$", re.I)
MAX_BYTES = 5 * 1024 * 1024
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")
# file:line[:col]: … (ruff, mypy, eslint unix, go, tsc --pretty false is file(line,col))
# eslint / stylelint "stylish": a line with the file, then "  line:col  error|warning  …"
STYLISH_LINE = re.compile(r"^\s+(\d+):\d+\s+(error|warning)\b")
LINT_LINE = re.compile(r"^\s*(?:-->\s*)?(?P<f>[^\s:()][^:()]*?\.\w+)(?::(?P<l1>\d+)(?::\d+)?:|\((?P<l2>\d+),\d+\))")
SUMMARY = re.compile(r"\d+ (passed|failed)|Passed!|Failed!|^Tests?:|Tests run:|test result:|^(ok|FAIL)\s|^\s*\d+ (passing|failing)")
FAILED = re.compile(r"^(FAILED|ERROR) \S+|^--- FAIL: \S+|^\s*Failed \S+|^\s*✕ |^\s*\d+\) |^FAIL\s+\S+")
ERROR_LINE = re.compile(r"\berror\b|\bERROR\b|: E\d|\bFailed\b", re.I)
SHELL_META = re.compile(r"[;&|<>`$]|\$\(")
PY_TOOLS = {"pytest", "ruff", "mypy", "pyright"}

problems = []
timeout = 900


def git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout


def run(cwd, cmd):
    try:
        p = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        # shortcut: on Windows a child of the shell can outlive the timeout, kill it by hand if it hangs
        return 124, f"timed out after {timeout}s (a test may be waiting on the network or a real model API)"
    return p.returncode, p.stdout + p.stderr


def py_runner(d):
    """Prefix that runs a Python tool inside the environment of project dir d (or a parent)."""
    for p in (d, *d.parents):
        if (p / "uv.lock").exists():
            return "uv run "
        if (p / "poetry.lock").exists():
            return "poetry run "
        for exe in (".venv/Scripts/python.exe", ".venv/bin/python", "venv/Scripts/python.exe", "venv/bin/python"):
            if (p / exe).exists():
                return f'"{p / exe}" -m '
        if (p / ".git").exists():
            break
    return f'"{sys.executable}" -m '


def quote(arg):
    return arg if re.fullmatch(r"[\w./:=,@+%-]+", arg) else '"' + arg.replace('"', '\\"') + '"'


def in_env(d, cmd):
    """A Python tool command rerun through the project's environment; any other command unchanged."""
    words = shlex.split(cmd)
    if words[:2] in (["uv", "run"], ["poetry", "run"]):
        return cmd
    if len(words) > 2 and re.fullmatch(r"python[\d.]*(\.exe)?|py", Path(words[0]).name) and words[1] == "-m":
        words = words[2:]
    if words and words[0] in PY_TOOLS:
        return py_runner(d) + " ".join(quote(w) for w in words)
    return cmd


def rel_path(repo, d, p):
    p = Path(p.strip())
    full = p if p.is_absolute() else (d / p)
    try:
        return full.resolve().relative_to(repo).as_posix()
    except ValueError:
        return p.as_posix()


def show(label, ok, lines, tail):
    print(f"{label}: {'ok' if ok else 'FAILED'}")
    if not ok:
        problems.append(f"{label.split(' `')[0].lower()} failed")
        for l in (lines or tail)[:15]:
            print(f"  {l.strip()[:300]}")


def do_build(repo, d, cmd, out, code):
    errors = [l for l in out.splitlines() if ERROR_LINE.search(l)]
    show(f"BUILD `{cmd}`", code == 0, sorted(set(errors)), out.strip().splitlines()[-15:])


def do_test(repo, d, cmd, out, code):
    summary = [l.strip() for l in out.splitlines() if SUMMARY.search(l)][-3:]
    failed = sorted({l.strip() for l in out.splitlines() if FAILED.search(l)})
    print(f"TEST {'ok' if code == 0 else 'FAILED'}: `{cmd}`" + (f" — {' | '.join(summary)}" if summary else ""))
    if re.search(r"\d+ skipped|Skipped:\s*[1-9]|\bSKIP\b", out):
        print("  note: skipped tests present; check they were skipped before this phase")
    if code != 0:
        problems.append(f"tests failed: {cmd}")
        for n in failed[:20]:
            print(f"  failed: {n[:200]}")
        if code == 5 and "pytest" in cmd:
            print("  no tests were collected")
        elif not failed:
            print("  " + "\n  ".join(out.strip().splitlines()[-10:]))


def do_lint(repo, d, cmd, out, code, changed):
    lines = out.splitlines()
    issues, current = [], None  # (file, line, text)
    for i, l in enumerate(lines):
        if m := LINT_LINE.match(l):
            # ruff's default format puts the message on the line before " --> file:line:col"
            issues.append((m.group("f"), int(m.group("l1") or m.group("l2")),
                           f"{lines[i - 1].strip()} {l.strip()}" if "-->" in l and i else l))
        elif (m := STYLISH_LINE.match(l)) and current:
            issues.append((current, int(m.group(1)), f"{current}: {l.strip()}"))
        elif l.strip() and not l[0].isspace():
            current = l.strip()
    if code and not issues:  # the tool itself failed (not installed, bad config)
        show(f"LINT `{cmd}`", False, [], out.strip().splitlines()[-15:])
        return
    new = [t for f, n, t in issues if n in changed.get(rel_path(repo, d, f), ())]
    show(f"LINT `{cmd}`", not new, new, [])
    if len(issues) > len(new):
        print(f"  note: {len(issues) - len(new)} older issue(s) on unchanged lines ignored")


def changed_files(repo, base):
    """name-status of everything since base, untracked files included as added."""
    rows = []
    for line in git(repo, "diff", "--name-status", "-M", base).splitlines():
        parts = line.split("\t")
        rows.append((parts[0][0], parts[-1]))
    for path in git(repo, "ls-files", "--others", "--exclude-standard").splitlines():
        rows.append(("A", path))
    return rows


def added_lines(repo, base, path, untracked):
    """(line number, text) of every line this phase added; [] for binary or huge files."""
    file = Path(repo) / path
    if untracked:
        try:
            if file.stat().st_size > MAX_BYTES or b"\0" in file.read_bytes()[:8192]:
                return []
            return list(enumerate(file.read_text(encoding="utf-8", errors="replace").splitlines(), 1))
        except OSError:
            return []
    rows, no = [], 0
    for l in git(repo, "diff", "-U0", base, "--", path).splitlines():
        if m := HUNK.match(l):
            no = int(m.group(1))
        elif l.startswith("+") and not l.startswith("+++"):
            rows.append((no, l[1:]))
            no += 1
    return rows


def check_rules(repo, base):
    """Scan the phase's changes; return {changed file: added line numbers} for the linters."""
    untracked = set(git(repo, "ls-files", "--others", "--exclude-standard").splitlines())
    rows = changed_files(repo, base)
    print(f"CHANGED FILES: {len(rows)}")

    def rule(label, detail):
        problems.append(label)
        print(f"  RULE {label}: {detail}")

    changed, syntax = {}, []
    for status, path in rows:
        if status == "A" and MIGRATION.search(path):
            rule("migration file added", path)
        if status == "D" and TEST_FILE.search(path):
            rule("test file deleted", path)
        if DEPS_FILE.search(path):
            print(f"  NOTE dependency files changed: {path} (check the guide allows it)")
        if status == "D":
            continue
        if ENV_FILE.search(path):
            rule(".env file added", path)
        file = Path(repo) / path
        size = file.stat().st_size if file.is_file() else 0
        if WEIGHTS.search(path) or size > MAX_BYTES and not DEPS_FILE.search(path):  # lock files can be big
            rule("model weights or large file", f"{path} ({size // 1024} KB)")
        lines = added_lines(repo, base, path, path in untracked)
        changed[path] = {n for n, _ in lines}
        if path.endswith(".py") and file.is_file():
            try:  # parse in-process: compileall would leave __pycache__ files in the tree
                ast.parse(file.read_text(encoding="utf-8"), path)
            except (SyntaxError, UnicodeDecodeError) as e:
                syntax.append(f"{path}: {e}")
        if path.endswith(".ipynb") and any('"output_type"' in t for _, t in lines):
            print(f"  NOTE notebook saved with outputs: {path} (clear them unless the guide wants them)")
        for label, rx, applies in RULES:
            if applies.search(path):
                for n, text in lines:
                    if rx.search(text):
                        rule(label, f"{path}:{n}: {text.strip()[:160]}")
        if not TEST_FILE.search(path):
            for n, text in lines:
                if SECRET_ASSIGN.search(text):
                    rule("secret in code", f"{path}:{n}: {text.strip()[:160]}")
    if syntax:
        show("PYTHON SYNTAX", False, syntax, [])
    trailers = [l for l in git(repo, "log", f"{base}..HEAD", "--format=%B").splitlines()
                if re.match(r"\s*Co-Authored-By:", l, re.I) or "Generated with" in l]
    if trailers:
        rule("AI attribution in commits", f"since base: {trailers[0].strip()}")
    return changed


def main():
    global timeout
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Persian text would crash a cp1252 console
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="commit the phase started from")
    ap.add_argument("--run", nargs=3, action="append", default=[], metavar=("KIND", "DIR", "CMD"),
                    help="build|test|lint, the folder to run in, the command; repeatable")
    ap.add_argument("--repo", default=".", help="working tree root (default: current directory)")
    ap.add_argument("--timeout", type=int, default=timeout, help="seconds per command (default 900)")
    args = ap.parse_args()
    timeout = args.timeout
    repo = Path(args.repo).resolve()
    if subprocess.run(["git", "rev-parse", "--verify", "-q", args.base + "^{commit}"],
                      cwd=repo, capture_output=True).returncode:
        print(f"unknown base commit: {args.base}")
        return 2
    for kind, d, cmd in args.run:
        if kind not in ("build", "test", "lint") or SHELL_META.search(cmd) or not (repo / d).is_dir() \
                or Path(d).is_absolute() or ".." in Path(d).parts:
            print(f"refusing --run {kind} {d} {cmd!r}: kind must be build/test/lint, the folder must be inside"
                  " the repo, and the command one plain command (no ; & | < > ` $)")
            return 2

    changed = check_rules(repo, args.base)
    for kind in ("build", "lint", "test"):
        for k, d, given in args.run:
            if k != kind:
                continue
            cwd = (repo / d).resolve()
            code, out = run(cwd, in_env(cwd, given))
            label = given if d == "." else f"{d}: {given}"
            if kind == "build":
                do_build(repo, cwd, label, out, code)
            elif kind == "lint":
                do_lint(repo, cwd, label, out, code, changed)
            else:
                do_test(repo, cwd, label, out, code)

    print("MECHANICAL: FAIL — " + ", ".join(dict.fromkeys(problems)) if problems else "MECHANICAL: PASS")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
