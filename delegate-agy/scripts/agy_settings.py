#!/usr/bin/env python3
"""Build the per-run `agy --settings` JSON from a project permissions file.

The file lives in the project at .delegate-agy/permissions.json:
  {"base": ["command(git status)", ...], "profiles": {"build": [...], "test": [...]}}

Usage:
  agy_settings.py init [--force]                 write a read-only base + detected stack profiles
  agy_settings.py emit [--profile P]... [--extra RULE]...   print the --settings JSON
  agy_settings.py add RULE [--profile P]         save a rule into base (or a profile)
  agy_settings.py show                           print the file

Every rule is checked: command(...) prefix rules only, no regex:, no shell syntax,
and no shell/interpreter/destructive/network command as the first word.
"""
import argparse, json, os, subprocess, sys

FILE = os.path.join(".delegate-agy", "permissions.json")
BANNED = {"sh", "bash", "zsh", "fish", "dash", "env", "sudo", "su", "doas", "xargs", "eval", "exec", "nohup",
          "python", "python3", "node", "deno", "bun", "perl", "ruby", "php", "lua", "pwsh", "powershell",
          "rm", "rmdir", "mv", "cp", "touch", "chmod", "chown", "ln", "dd", "tee", "install", "mkdir",
          "curl", "wget", "ssh", "scp", "rsync", "nc", "ncat", "docker", "podman", "kubectl", "find",
          "sed", "awk", "cat", "head", "tail", "rg", "grep", "less", "more", "make", "npx", "pip", "pip3", "npm", "pnpm", "yarn"}
BANNED_SUB = {"git": {"push", "checkout", "reset", "clean", "rebase", "commit", "switch", "restore", "stash",
                      "merge", "pull", "fetch", "remote", "config", "rm", "mv", "branch", "tag", "apply", "am"}}
BAD_CHARS = [";", "&&", "||", "|", ">", "<", "$(", "`", "\n", "#"]
BASE = ["command(git status)", "command(git diff)", "command(git log)", "command(git show)",
        "command(ls)"]
STACKS = [  # marker file/glob suffix -> profiles
    ((".slnx", ".sln", ".csproj"), {"build": ["command(dotnet build)"], "test": ["command(dotnet test)"]}),
    (("package.json",), {"build": ["command(npm run build)"], "test": ["command(npm test)", "command(npm run test)"],
                         "lint": ["command(npm run lint)"]}),
    (("Cargo.toml",), {"build": ["command(cargo build)"], "test": ["command(cargo test)"], "lint": ["command(cargo clippy)"]}),
    (("go.mod",), {"build": ["command(go build)"], "test": ["command(go test)"], "lint": ["command(go vet)"]}),
    (("pyproject.toml", "requirements.txt"), {"test": ["command(pytest)"], "lint": ["command(ruff check)"]}),
]

def root():
    try:
        return subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True,
                                       stderr=subprocess.DEVNULL).strip()
    except Exception:
        return os.getcwd()

def path(): return os.path.join(root(), FILE)

def load():
    p = path()
    if not os.path.exists(p):
        sys.exit(f"no {FILE} in {root()}; run: agy_settings.py init")
    with open(p) as f:
        return json.load(f)

def check(rule):
    if not (rule.startswith("command(") and rule.endswith(")")):
        sys.exit(f"rejected {rule!r}: only command(<words>) prefix rules are allowed")
    body = rule[len("command("):-1].strip()
    if body.startswith("regex:") or body in ("", "*"):
        sys.exit(f"rejected {rule!r}: regex and wildcard rules let chained commands through")
    for c in BAD_CHARS:
        if c in body:
            sys.exit(f"rejected {rule!r}: shell syntax {c!r} in a rule")
    words = body.split()
    if words[0] in BANNED:
        sys.exit(f"rejected {rule!r}: {words[0]} is not safe to allow on arbitrary paths/input")
    if len(words) < 2 and words[0] in BANNED_SUB:
        sys.exit(f"rejected {rule!r}: name the git subcommand")
    if words[0] in BANNED_SUB and len(words) > 1 and words[1] in BANNED_SUB[words[0]]:
        sys.exit(f"rejected {rule!r}: {words[0]} {words[1]} changes state")
    return rule

def detect():
    r = root(); names = set()
    for _, _, fs in os.walk(r):
        names.update(fs)
        break
    for sub in ("src", "tests"):
        d = os.path.join(r, sub)
        if os.path.isdir(d):
            for _, _, fs in os.walk(d): names.update(fs)
    prof = {}
    for markers, profiles in STACKS:
        if any(n.endswith(m) or n == m for n in names for m in markers):
            for k, v in profiles.items(): prof.setdefault(k, []).extend(v)
    return prof

def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("init"); i.add_argument("--force", action="store_true")
    e = sub.add_parser("emit"); e.add_argument("--profile", action="append", default=[]); e.add_argument("--extra", action="append", default=[])
    a = sub.add_parser("add"); a.add_argument("rule"); a.add_argument("--profile")
    sub.add_parser("show")
    ns = ap.parse_args()
    if ns.cmd == "init":
        p = path()
        if os.path.exists(p) and not ns.force:
            sys.exit(f"{p} exists; use --force to overwrite")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        data = {"base": BASE, "profiles": detect()}
        for r in data["base"] + [x for v in data["profiles"].values() for x in v]: check(r)
        json.dump(data, open(p, "w"), indent=2); open(p, "a").write("\n")
        print(f"wrote {p}\n{json.dumps(data, indent=2)}", file=sys.stderr)
    elif ns.cmd == "show":
        print(json.dumps(load(), indent=2))
    elif ns.cmd == "add":
        d = load(); check(ns.rule)
        tgt = d["base"] if not ns.profile else d["profiles"].setdefault(ns.profile, [])
        if ns.rule not in tgt: tgt.append(ns.rule)
        json.dump(d, open(path(), "w"), indent=2); open(path(), "a").write("\n")
    else:
        d = load(); rules = list(d.get("base", []))
        for p in ns.profile:
            if p not in d.get("profiles", {}): sys.exit(f"unknown profile {p!r}; have {sorted(d.get('profiles', {}))}")
            rules += d["profiles"][p]
        rules += ns.extra
        seen = []
        for r in rules:
            if check(r) not in seen: seen.append(r)
        print(json.dumps({"permissions": {"allow": seen}}, separators=(",", ":")))

main()
