#!/usr/bin/env bash
# Print the newest Codex model slug for a tier (luna|terra|sol) from the local cache.
# Usage: latest_model.sh <luna|terra|sol>
set -euo pipefail
tier=${1:?usage: latest_model.sh luna|terra|sol}
cache="${CODEX_HOME:-$HOME/.codex}/models_cache.json"
[ -f "$cache" ] || { echo "no $cache; run 'codex' once to populate it" >&2; exit 1; }
jq -r '.models[].slug' "$cache" | grep -E "^gpt-[0-9.]+-${tier}$" \
  | sed -E "s/^gpt-([0-9.]+)-${tier}$/\1 &/" | sort -V | tail -1 | cut -d' ' -f2 \
  | grep . || { echo "no $tier model in $cache" >&2; exit 1; }
