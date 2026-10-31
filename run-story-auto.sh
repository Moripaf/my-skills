#!/usr/bin/env bash
# Unattended run-story: one fresh `claude -p` per wave. No /clear needed, every wave starts with an empty context.
# Usage (from the project root, in Git Bash):  bash run-story-auto.sh 001 [max_waves]
# State lives in git and in docs/stories/Story-NNN-*/ (Build-Notes, Test-Result, CheckList), so a new call resumes where the last one stopped.
# Needs the story-worker-* agents in ~/.claude/agents/ (copied from this repo's agents/ folder).
set -u
STORY="${1:?story number, e.g. 001}"
MAX="${2:-10}"
ORCH_MODEL="claude-opus-5-5"
ORCH_EFFORT="medium"
SKILLS="$HOME/.claude/skills"
LOG="docs/stories/run-$STORY.log"

for i in $(seq 1 "$MAX"); do
  PROMPT="Read $SKILLS/run-story/SKILL.md and follow it with the arguments: $STORY --auto"

  # --strict-mcp-config with no --mcp-config: no MCP servers, so every agent starts without their tool schemas.
  "${CLAUDE_BIN:-claude}" -p "$PROMPT" \
    --model "$ORCH_MODEL" --effort "$ORCH_EFFORT" --strict-mcp-config \
    --permission-mode acceptEdits \
    --allowedTools "Bash Edit Write Read Glob Grep Agent" \
    --output-format json --max-turns 400 < /dev/null > ".wave.json" 2> ".wave.err"

  SESSION=$(python - <<'PY'
import json
d = json.load(open(".wave.json", encoding="utf-8"))
with open("docs/stories/run.tmp", "w", encoding="utf-8") as f:
    f.write(f"turns={d.get('num_turns')} cost=${d.get('total_cost_usd') or 0:.2f} error={d.get('is_error')}\n")
    f.write(str(d.get("result"))[-600:] + "\n")
print(d.get("session_id", ""))
PY
)
  { cat docs/stories/run.tmp; python -I "$SKILLS/run-story/scripts/check_models.py" --session "$SESSION" \
      --orchestrator "$ORCH_MODEL/$ORCH_EFFORT"; } >> "$LOG"
  rm -f docs/stories/run.tmp
  tail -n 8 "$LOG"

  if grep -q "ALL WAVES DONE" .wave.json; then echo "finished"; break; fi
  if grep -q "NEEDS USER" .wave.json || grep -q '"is_error": *true' .wave.json; then echo "stopped: read $LOG and NEEDS-USER.md"; break; fi
done
rm -f .wave.json .wave.err
