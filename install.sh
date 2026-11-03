#!/usr/bin/env bash
# Link every skill (dir with SKILL.md) and agent (agents/*.md) from this repo
# into ~/.claude. Idempotent: re-run after adding a skill. Edits to existing
# skills need no re-run, since the links point at the repo.
# Never overwrites real files/dirs; prunes dead links that point into this repo.
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
claude="${CLAUDE_HOME:-$HOME/.claude}"
mkdir -p "$claude/skills" "$claude/agents"

link() { # src dest
  local src=$1 dest=$2
  if [ -L "$dest" ]; then
    [ "$(readlink "$dest")" = "$src" ] && return
    ln -sfn "$src" "$dest"; echo "relinked $dest"
  elif [ -e "$dest" ]; then
    echo "SKIP (real file exists, not touching): $dest" >&2
  else
    ln -s "$src" "$dest"; echo "linked   $dest"
  fi
}

for d in "$repo"/*/; do
  d=${d%/}
  [ -f "$d/SKILL.md" ] && link "$d" "$claude/skills/$(basename "$d")"
done
for f in "$repo"/agents/*.md; do
  [ -f "$f" ] && link "$f" "$claude/agents/$(basename "$f")"
done

# prune links into this repo whose target is gone (removed/renamed skills)
for l in "$claude"/skills/* "$claude"/agents/*; do
  [ -L "$l" ] && [ ! -e "$l" ] && case "$(readlink "$l")" in "$repo"/*) rm "$l"; echo "pruned   $l";; esac
done
exit 0
