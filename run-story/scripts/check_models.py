"""Check that every agent of one run-story session ran on the model and effort it was meant to.

Reads the session transcript and its subagent transcripts under ~/.claude/projects/. An agent started
with subagent_type "story-worker-<model>-<effort>" must show claude-<model>-5-5 and that effort.
Any other agent type is listed so a fallback to session defaults is visible.

Usage: check_models.py --session <session id> [--repo <working tree>] [--orchestrator claude-opus-5-5/medium]
Exit code 1 when anything does not match.
"""
import argparse
import json
import re
import sys
from pathlib import Path


def project_dir(repo):
    return Path.home() / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(Path(repo).resolve()))


def read(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def seen(path):
    """(models, efforts, first user prompt) of one transcript."""
    models, efforts, prompt = set(), set(), None
    for d in read(path):
        if d.get("effort"):
            efforts.add(d["effort"])
        m = d.get("message")
        if not isinstance(m, dict):
            continue
        if d.get("type") == "assistant" and m.get("model"):
            models.add(m["model"])
        if prompt is None and d.get("type") == "user":
            c = m.get("content")
            prompt = c if isinstance(c, str) else "".join(x.get("text", "") for x in c if isinstance(x, dict))
    return models, efforts, prompt or ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", required=True)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--orchestrator", default="claude-opus-5-5/medium", help="expected model/effort of the session")
    a = ap.parse_args()

    base = project_dir(a.repo)
    main_file = base / f"{a.session}.jsonl"
    if not main_file.exists():
        print(f"MODELS: SKIP no transcript at {main_file}")
        return 0

    bad = []
    want_m, want_e = a.orchestrator.split("/")
    models, efforts, _ = seen(main_file)
    line = f"orchestrator: {','.join(sorted(models)) or '?'} / {','.join(sorted(efforts)) or '?'}"
    if models != {want_m} or efforts != {want_e}:
        bad.append(line + f"  (want {a.orchestrator})")
    print(line)

    calls = []  # (subagent_type, prompt)
    for d in read(main_file):
        m = d.get("message")
        if d.get("type") == "assistant" and isinstance(m, dict) and isinstance(m.get("content"), list):
            for c in m["content"]:
                if c.get("type") == "tool_use" and c.get("name") in ("Agent", "Task"):
                    i = c.get("input", {})
                    calls.append((i.get("subagent_type") or "general-purpose", (i.get("prompt") or "")[:200]))

    for f in sorted((base / a.session / "subagents").glob("*.jsonl")):
        models, efforts, prompt = seen(f)
        kind = next((t for t, p in calls if p and prompt.startswith(p[:120])), "?")
        got = f"{','.join(sorted(models)) or '?'} / {','.join(sorted(efforts)) or '-'}"
        hit = re.fullmatch(r"story-worker-(haiku|sonnet)-(low|medium|high)", kind)
        if hit:
            ok = models == {f"claude-{hit[1]}-5-5"} and efforts == {hit[2]}
        else:
            ok = kind == "Explore"  # read-only fact-finders may stay on their own defaults
        print(f"{'ok  ' if ok else 'BAD '} {kind}: {got}")
        if not ok:
            bad.append(f"{kind}: {got}")

    print("MODELS: PASS" if not bad else f"MODELS: WARN {len(bad)} mismatch(es)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
