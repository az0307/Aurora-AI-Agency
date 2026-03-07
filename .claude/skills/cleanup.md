# Cleanup Skill

Clean up temporary files and reset state

## Usage

```
/cleanup [--hard]
```

## What it does

1. Removes temporary test files
2. Cleans up Python cache files (__pycache__, *.pyc)
3. Optionally removes state files (with --hard flag)
4. Stops any running Orchestra Town processes

## Instructions

When the user invokes `/cleanup`, run:

```bash
cd /home/user/Aurora-AI-Agency

echo "🧹 Cleaning up..."

# Stop running processes
echo "Stopping processes..."
pkill -f enhanced_server || echo "  No server process found"
pkill -f project_generator || echo "  No generator process found"

# Remove Python cache
echo "Removing Python cache..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# Remove temporary files
echo "Removing temporary files..."
rm -rf /tmp/smoke-test-* 2>/dev/null
rm -rf /tmp/orchestra-test-* 2>/dev/null

echo "✅ Cleanup complete!"
```

If the user invokes `/cleanup --hard`, also remove state files:

```bash
echo "⚠️  Hard cleanup - removing state files..."
rm -f gastown/orchestra/state/*.json 2>/dev/null
echo "State files removed. Server will start fresh on next run."
```

**Warning**: Always confirm with the user before running `--hard` cleanup as it removes all task and message history.
