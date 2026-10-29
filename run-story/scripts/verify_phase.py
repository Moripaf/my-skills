#!/usr/bin/env python3
"""Mechanical checks for one story phase, run by the test agent.

Usage: python3 -I verify_phase.py --base <sha> [--test "dotnet test X"]... [--repo <root>] [--no-build]

Builds the solution, runs each test command, and scans everything changed since <base>
(commits, staged, unstaged and untracked files) for AGENTS.md rule breaks. Prints a short
summary only, never full logs, and ends with `MECHANICAL: PASS` or `MECHANICAL: FAIL`.
Exit code 1 on FAIL.
"""
import argparse
import re
import shlex
import subprocess
import sys
from pathlib import Path

# (label, regex on added lines, applies to path regex)
RULES = [
    ("advisory lock", re.compile(r"pg_advisory", re.I), re.compile(r"\.cs$")),
    ("SELECT … FOR UPDATE", re.compile(r"\bFOR\s+UPDATE\b", re.I), re.compile(r"\.cs$")),
    ("non-default isolation level", re.compile(r"IsolationLevel\.(Serializable|RepeatableRead|Snapshot)"), re.compile(r"\.cs$")),
    ("explicit transaction", re.compile(r"\bBeginTransaction(Async)?\s*\("), re.compile(r"\.cs$")),
    ("static SemaphoreSlim", re.compile(r"static\s+(readonly\s+)?SemaphoreSlim"), re.compile(r"\.cs$")),
    ("skipped test", re.compile(r"\bSkip\s*=\s*\""), re.compile(r"\.cs$")),
    ("suppressed warning", re.compile(r"#pragma\s+warning\s+disable|SuppressMessage\("), re.compile(r"\.cs$")),
    ("module ProjectReference", re.compile(r"<ProjectReference[^>]*Bina\.(?!Common)[A-Za-z]+[\\/]"), re.compile(r"^Bina\.[^/]+/[^/]+\.csproj$")),
]
TEST_FILE = re.compile(r"(^|/)[^/]*Tests?/.*\.cs$|Tests?\.cs$")
RESULT = re.compile(r"(Passed|Failed)!\s+-\s+Failed:\s+(\d+),\s+Passed:\s+(\d+),\s+Skipped:\s+(\d+),\s+Total:\s+(\d+)")
FAILED_TEST = re.compile(r"^\s*Failed\s+([\w.`<>,\[\]() ]+?)\s+\[")
BUILD_ERROR = re.compile(r": error [A-Z]+\d+:")

problems = []


def git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True).stdout


def run(repo, cmd):
    p = subprocess.run(cmd, cwd=repo, shell=True, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def check_build(repo):
    code, out = run(repo, "dotnet build arena-backend.slnx -nologo -v q")
    errors = sorted({re.sub(r"\s*\[[^\]]*\.csproj\]$", "", l.strip()).replace(repo + "/", "")
                     for l in out.splitlines() if BUILD_ERROR.search(l)})
    if code == 0:
        print("BUILD: ok")
        return
    problems.append("build failed")
    print(f"BUILD: FAILED ({len(errors)} distinct errors)")
    for l in errors[:15]:
        print(f"  {l[:300]}")
    if not errors:
        print("  " + "\n  ".join(out.strip().splitlines()[-15:]))


def check_tests(repo, commands):
    for cmd in commands:
        code, out = run(repo, cmd + " --nologo")
        totals = RESULT.findall(out)
        failed = sum(int(f) for _, f, _, _, _ in totals)
        passed = sum(int(p) for _, _, p, _, _ in totals)
        skipped = sum(int(s) for _, _, _, s, _ in totals)
        names = sorted({m.group(1) for l in out.splitlines() if (m := FAILED_TEST.match(l))})
        ok = code == 0 and failed == 0 and totals
        print(f"TEST {'ok' if ok else 'FAILED'}: `{cmd}` passed {passed}, failed {failed}, skipped {skipped}")
        if skipped:
            print("  note: skipped tests present; check they were skipped before this phase")
        if not ok:
            problems.append(f"tests failed: {cmd}")
            for n in names[:20]:
                print(f"  failed: {n}")
            if not totals:
                errs = [l.strip() for l in out.splitlines() if BUILD_ERROR.search(l)]
                print("  " + "\n  ".join((errs or out.strip().splitlines())[-10:]))


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
    if untracked:
        try:
            return (Path(repo) / path).read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            return []
    diff = git(repo, "diff", "-U0", base, "--", path)
    return [l[1:] for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]


def check_rules(repo, base):
    untracked = set(git(repo, "ls-files", "--others", "--exclude-standard").splitlines())
    rows = changed_files(repo, base)
    print(f"CHANGED FILES: {len(rows)}")
    for status, path in rows:
        if status == "A" and re.search(r"(^|/)Migrations/", path):
            problems.append("migration file added")
            print(f"  RULE migration file added: {path}")
        if status == "D" and TEST_FILE.search(path):
            problems.append("test file deleted")
            print(f"  RULE test file deleted: {path}")
        if status == "D":
            continue
        for label, rx, applies in RULES:
            if not applies.search(path):
                continue
            for line in added_lines(repo, base, path, path in untracked):
                if rx.search(line):
                    problems.append(label)
                    print(f"  RULE {label}: {path}: {line.strip()[:160]}")
    trailers = [l for l in git(repo, "log", f"{base}..HEAD", "--format=%B").splitlines()
                if re.match(r"\s*Co-Authored-By:", l, re.I) or "Generated with" in l]
    if trailers:
        problems.append("AI attribution in commits")
        print(f"  RULE AI attribution in commits since base: {trailers[0].strip()}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="commit the phase started from")
    ap.add_argument("--test", action="append", default=[], help="a `dotnet test …` command; repeatable")
    ap.add_argument("--repo", default=".", help="working tree root (default: current directory)")
    ap.add_argument("--no-build", action="store_true", help="skip the solution build")
    args = ap.parse_args()
    repo = str(Path(args.repo).resolve())
    if subprocess.run(["git", "rev-parse", "--verify", "-q", args.base + "^{commit}"],
                      cwd=repo, capture_output=True).returncode:
        print(f"unknown base commit: {args.base}")
        return 2
    for cmd in args.test:
        if not shlex.split(cmd)[:2] == ["dotnet", "test"]:
            print(f"refusing non `dotnet test` command: {cmd}")
            return 2

    check_rules(repo, args.base)
    if not args.no_build:
        check_build(repo)
    if "build failed" not in problems:
        check_tests(repo, args.test)
    elif args.test:
        print("TESTS: not run, build failed")

    print("MECHANICAL: FAIL — " + ", ".join(dict.fromkeys(problems)) if problems else "MECHANICAL: PASS")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
