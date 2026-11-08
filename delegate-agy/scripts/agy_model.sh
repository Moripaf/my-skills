#!/usr/bin/env bash
# Print the newest agy model slug for a tier.
# Usage: agy_model.sh flash [low|medium|high]   (default medium; effort is part of the flash slug)
#        agy_model.sh sonnet | opus
set -euo pipefail
tier=${1:?usage: agy_model.sh flash [effort] | sonnet | opus}
effort=${2:-medium}
slugs=$(agy models 2>/dev/null | awk -F'\t' 'NF>=2{print $1}')
case $tier in
  flash)  re="^gemini-[0-9.]+-flash-${effort}$"; ver='s/^gemini-([0-9.]+)-.*/\1/' ;;
  sonnet) re='^claude-sonnet-[0-9.-]+$';          ver='s/^claude-sonnet-(.*)/\1/' ;;
  opus)   re='^claude-opus-[0-9.-]+-thinking$';   ver='s/^claude-opus-([0-9.-]+)-thinking/\1/' ;;
  *) echo "unknown tier $tier" >&2; exit 2 ;;
esac
best=$(echo "$slugs" | grep -E "$re" | while read -r s; do
  echo "$(echo "$s" | sed -E "$ver" | tr '-' '.') $s"
done | sort -V | tail -1 | cut -d' ' -f2 || true)
[ -n "$best" ] || { echo "no $tier model found" >&2; exit 1; }
echo "$best"
