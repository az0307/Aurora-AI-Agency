# Smoke Test Skill

Run quick smoke tests to verify system health

## Usage

```
/smoke-test
```

## What it does

1. Validates Python syntax in core modules
2. Tests project generator with simple example
3. Verifies imports work correctly
4. Checks server can start (doesn't keep it running)
5. Reports any issues found

## Instructions

When the user invokes `/smoke-test`, run the following commands:

```bash
cd /home/user/Aurora-AI-Agency

echo "🧪 Running smoke tests..."

# 1. Python syntax validation
echo "📝 Checking Python syntax..."
python3 -m py_compile gastown/project_generator.py
python3 -m py_compile gastown/orchestra/api/enhanced_server.py
python3 -m py_compile gastown/orchestra/core/town_manager.py

# 2. Import validation
echo "📦 Checking imports..."
python3 -c "import sys; sys.path.append('gastown/orchestra'); from core.town_manager import TownManager"
python3 -c "from gastown.project_generator import ProjectGenerator"

# 3. Project generator smoke test
echo "🏗️  Testing project generator..."
python3 gastown/project_generator.py "test cli app" -o /tmp/smoke-test-$$
rm -rf /tmp/smoke-test-$$

# 4. Server startup test
echo "🌐 Testing server startup..."
cd gastown/orchestra && timeout 5 python3 api/enhanced_server.py > /dev/null 2>&1 &
SERVER_PID=$!
sleep 2
curl -f http://localhost:5000/health > /dev/null 2>&1 && echo "✅ Server health check passed" || echo "⚠️  Server health check failed"
kill $SERVER_PID 2>/dev/null

echo "✅ Smoke tests complete!"
```

After running, summarize results and report any failures.
