#!/bin/bash
# Copyright (c) 2026 Nillard Ltd (company no. 16312961). Nillard Ltd Skills License 1.0, see LICENSE. Not for resale or redistribution.
# Install the borumi-video-editor skill into ~/.claude/skills/.
# Usage: bash install.sh
# Asks before overwriting an existing copy (the old folder is moved to ~/.claude/skills-backup/).
# Set CLAUDE_SKILLS_DIR to install elsewhere. Checks for ffmpeg and Python packages and prints hints;
# it does NOT install any dependency itself.
set -euo pipefail

KIT="$(cd "$(dirname "$0")" && pwd)"
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
s=borumi-video-editor
src="$KIT/skills/$s"

echo "Installing $s into $DEST"
mkdir -p "$DEST"
if [ -e "$DEST/$s" ]; then
  printf "  %s already exists in %s. Overwrite? [y/N] " "$s" "$DEST"
  { read -r answer </dev/tty; } 2>/dev/null || read -r answer || answer=""
  case "$answer" in
    y|Y|yes|YES)
      # back up OUTSIDE the skills folder, so Claude Code doesn't load the old copy as a duplicate skill
      backup_root="$(dirname "$DEST")/skills-backup"
      mkdir -p "$backup_root"
      backup="$backup_root/$s-$(date +%Y%m%d-%H%M%S)"
      mv "$DEST/$s" "$backup"
      echo "    old folder moved to $backup"
      ;;
    *)
      echo "    kept the existing $s; nothing installed"
      exit 0
      ;;
  esac
fi
mkdir -p "$DEST/$s"
(cd "$src" && tar --exclude '._*' --exclude '.DS_Store' --exclude '__pycache__' -cf - .) | (cd "$DEST/$s" && tar -xf -)
echo "  + installed $s"

echo
echo "Checking tools (nothing is installed automatically):"
missing=0
check() {
  local cmd="$1" hint="$2"
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "  ok      $cmd"
  else
    echo "  MISSING $cmd  -> $hint"
    missing=1
  fi
}
check ffmpeg  "brew install ffmpeg"
check ffprobe "comes with ffmpeg: brew install ffmpeg"
check python3 "brew install python"
if command -v python3 >/dev/null 2>&1; then
  if python3 -c "import numpy, PIL" >/dev/null 2>&1; then
    echo "  ok      python packages numpy + Pillow"
  else
    echo "  MISSING python packages -> python3 -m pip install numpy pillow"
    missing=1
  fi
  if python3 -c "import scipy" >/dev/null 2>&1; then
    echo "  ok      python package scipy"
  else
    echo "  optional scipy -> python3 -m pip install scipy   (filler pass)"
  fi
fi

echo
echo "Next steps:"
echo "  1. Borumi: open Settings -> AI -> Enable MCP, so Claude Code sees the mcp__borumi__* tools."
echo "  2. Tell Claude your folders the first time (or write them to $DEST/$s/config.md):"
echo "       <WORKSPACE>, <SFX_LIBRARY>, <MUSIC_LIBRARY>, <EXPORT_DIR>   (sounds and music are yours to source)"
echo "  3. Make the taste profile yours: $DEST/$s/references/taste-rules.md"
echo "  4. Start a new Claude Code session and say: \"Edit this video in Borumi. Start with a section map.\""
if [ "$missing" -ne 0 ]; then
  echo
  echo "Some required tools are missing; install them with the hints above."
fi
