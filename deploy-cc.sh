#!/usr/bin/env bash
# Deploy job-hunter into Claude Code (user scope): skill + /job-* slash commands.
# Run this after editing anything under job-hunting/ or claude-code/commands/.
set -e
cd "$(dirname "$0")"
DEST_SKILL="$HOME/.claude/skills/job-hunting"
DEST_CMD="$HOME/.claude/commands"
mkdir -p "$DEST_CMD"
rm -rf "$DEST_SKILL" && mkdir -p "$DEST_SKILL"
cp -r job-hunting/. "$DEST_SKILL"/
rm -f "$DEST_CMD"/job-*.md
cp claude-code/commands/job-*.md "$DEST_CMD"/
echo "Deployed skill    -> $DEST_SKILL"
echo "Deployed commands -> $DEST_CMD"
echo "Restart Claude Code to pick up new commands/skill."
