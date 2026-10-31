#!/usr/bin/env python3
"""Detect the projects in a repo and suggest their build, test and lint commands.

Usage: python -I detect_project.py [--repo <root>]

Looks for marker files (pyproject.toml, package.json, *.sln, go.mod, pom.xml, ...) at the
repo root and up to two folders down, and prints the Markdown table that goes into
docs/stories/settings.md. Reads only small manifest files; no network, no installs.
Prints "none detected" when it finds nothing it knows; then ask the user.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

SKIP = {".git", "node_modules", ".venv", "venv", "vendor", "bin", "obj", "dist", "build", "target",
        "__pycache__", ".claude", ".idea", ".vscode", "site-packages", ".tox", ".next", "out"}


def text(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def python(d):
    if not any((d / f).exists() for f in ("pyproject.toml", "setup.py", "requirements.txt")):
        return None
    py = text(d / "pyproject.toml")
    if (d / "uv.lock").exists():
        run = "uv run "
    elif (d / "poetry.lock").exists():
        run = "poetry run "
    elif (d / ".venv").exists():
        run = "python -m "  # verify_phase.py runs it with the .venv interpreter
    else:
        run = "python -m "
    test = f"{run}pytest -q" if "pytest" in py or (d / "tests").is_dir() or (d / "conftest.py").exists() else ""
    lint = []
    if "[tool.ruff" in py or (d / "ruff.toml").exists():
        lint.append(f"{run}ruff check .")
    if "[tool.mypy" in py or (d / "mypy.ini").exists():
        lint.append(f"{run}mypy .")
    return "python", "", test, " ; ".join(lint)


def node(d):
    if not (d / "package.json").exists():
        return None
    try:
        scripts = json.loads(text(d / "package.json")).get("scripts", {})
    except ValueError:
        scripts = {}
    pm = next((m for f, m in (("pnpm-lock.yaml", "pnpm"), ("yarn.lock", "yarn"), ("bun.lockb", "bun"),
                              ("bun.lock", "bun")) if (d / f).exists()), "npm")
    r = f"{pm} run "
    build = r + "build" if "build" in scripts else ""
    if "typecheck" in scripts:
        build = (build + " ; " if build else "") + r + "typecheck"
    test = f"{'bun run' if pm == 'bun' else pm} test" if "test" in scripts and "no test specified" not in scripts["test"] else ""
    lint = r + "lint" if "lint" in scripts else ""
    stack = "typescript" if (d / "tsconfig.json").exists() else "javascript"
    return stack, build, test, lint


def dotnet(d):
    sln = sorted(list(d.glob("*.slnx")) + list(d.glob("*.sln")))
    if not sln and not list(d.glob("*.csproj")):
        return None
    target = f" {sln[0].name}" if sln else ""
    return "dotnet", f"dotnet build{target} -nologo -v q", f"dotnet test{target} --nologo", ""


def go(d):
    return ("go", "go build ./...", "go test ./...", "go vet ./...") if (d / "go.mod").exists() else None


WRAP = "" if os.name == "nt" else "./"  # cmd.exe finds gradlew.bat / mvnw.cmd without ./


def java(d):
    if (d / "pom.xml").exists():
        mvn = WRAP + "mvnw" if (d / "mvnw").exists() else "mvn"
        return "java", f"{mvn} -q compile", f"{mvn} -q test", ""
    if (d / "build.gradle").exists() or (d / "build.gradle.kts").exists():
        g = WRAP + "gradlew" if (d / "gradlew").exists() else "gradle"
        return "java", f"{g} build -x test", f"{g} test", ""
    return None


def php(d):
    if not (d / "composer.json").exists():
        return None
    c = text(d / "composer.json")
    test = "vendor/bin/phpunit" if "phpunit" in c else ("php artisan test" if (d / "artisan").exists() else "")
    lint = "vendor/bin/phpstan analyse --error-format=raw" if "phpstan" in c else ""
    return "php", "", test, lint


def rust(d):
    return ("rust", "cargo build", "cargo test", "cargo clippy") if (d / "Cargo.toml").exists() else None


DETECTORS = [python, node, dotnet, go, java, php, rust]


def candidates(root, depth=2):
    yield root
    if depth:
        for d in sorted(p for p in root.iterdir() if p.is_dir() and p.name not in SKIP and not p.name.startswith(".")):
            yield from candidates(d, depth - 1)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Persian text would crash a cp1252 console
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    root = Path(ap.parse_args().repo).resolve()
    rows, seen = [], {}
    for d in candidates(root):
        for detect in DETECTORS:
            found = detect(d)
            if not found:
                continue
            stack = found[0]
            # a member of a workspace already found above (uv / npm workspaces) needs no row of its own
            parent = next((p for p in seen.get(stack, []) if p in d.parents), None)
            if parent and re.search(r"workspace", text(parent / "pyproject.toml") + text(parent / "package.json"), re.I):
                continue
            seen.setdefault(stack, []).append(d)
            rows.append((d.relative_to(root).as_posix() or ".", *found))
    if not rows:
        print("none detected")
        return 0
    print("| Dir | Stack | Build | Test | Lint |")
    print("|---|---|---|---|---|")
    for r in rows:
        print("| " + " | ".join(f"`{c}`" if c and i != 1 else (c or "-") for i, c in enumerate(r)) + " |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
