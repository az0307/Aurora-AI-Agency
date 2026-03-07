#!/bin/bash
set -euo pipefail

# Only run in Claude Code on the web
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

echo "🏙️  Orchestra Town - Setting up environment..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -q -r "$CLAUDE_PROJECT_DIR/gastown/orchestra/requirements.txt"

# Set up PYTHONPATH for the project
echo "🔧 Configuring PYTHONPATH..."
echo 'export PYTHONPATH="$CLAUDE_PROJECT_DIR:$CLAUDE_PROJECT_DIR/gastown/orchestra:$PYTHONPATH"' >> "$CLAUDE_ENV_FILE"

echo "✅ Orchestra Town environment ready!"
