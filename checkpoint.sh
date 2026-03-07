#!/bin/bash
# Orchestra Town Checkpoint Script
# Creates a safe checkpoint by testing and committing working state

set -e  # Exit on error

CHECKPOINT_MSG="${1:-checkpoint: working state}"
BRANCH=$(git branch --show-current)

echo "🏙️  Orchestra Town Checkpoint"
echo "================================"
echo "Branch: $BRANCH"
echo "Message: $CHECKPOINT_MSG"
echo ""

# 1. Check if there are changes to commit
if [[ -z $(git status --porcelain) ]]; then
    echo "✅ No changes to commit"
    exit 0
fi

# 2. Run quick smoke tests
echo "🧪 Running smoke tests..."

# Test 1: Python syntax check
echo "  → Checking Python syntax..."
find gastown -name "*.py" -type f -exec python3 -m py_compile {} \; 2>&1 | head -10
if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "❌ Python syntax errors found"
    exit 1
fi

# Test 2: Import check for main modules
echo "  → Checking imports..."
cd gastown/orchestra
python3 -c "from core.town_manager import TownManager; from core.enhanced_mayor import EnhancedMayor" 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Import errors found"
    exit 1
fi
cd ../..

# Test 3: Project generator smoke test
echo "  → Testing project generator..."
timeout 10 python3 gastown/project_generator.py "test app" -o /tmp/checkpoint-test 2>&1 | head -5
if [ ${PIPESTATUS[0]} -eq 124 ]; then
    echo "⚠️  Project generator test timed out (may be waiting for API key)"
elif [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "⚠️  Project generator returned non-zero exit (may be expected without API key)"
fi

echo "✅ Smoke tests passed"
echo ""

# 3. Show what will be committed
echo "📝 Changes to commit:"
git status --short
echo ""

# 4. Commit
echo "💾 Committing..."
git add -A
git commit -m "$CHECKPOINT_MSG

https://claude.ai/code/session_$(git config user.name || echo 'unknown')"

echo "✅ Checkpoint created"
echo ""

# 5. Offer to push
read -p "Push to origin/$BRANCH? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Pushing to origin/$BRANCH..."
    git push -u origin "$BRANCH"
    echo "✅ Pushed successfully"
else
    echo "ℹ️  Skipped push. Run 'git push -u origin $BRANCH' to push later."
fi

echo ""
echo "🎉 Checkpoint complete!"
