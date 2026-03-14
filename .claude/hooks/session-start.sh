#!/bin/bash
set -euo pipefail

# Only run in remote (Claude Code on the web) environments
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Ensure Python 3 is available
python3 --version >/dev/null 2>&1 || { echo "Python 3 is required but not found"; exit 1; }

# Validate project syntax
python3 -m py_compile "$CLAUDE_PROJECT_DIR/gastown/project_generator.py"
