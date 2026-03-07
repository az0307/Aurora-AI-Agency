# Status Skill

Check Orchestra Town system status

## Usage

```
/status [subsystem]
```

## What it does

1. Shows current git branch and uncommitted changes
2. Displays running processes (if server is active)
3. Shows state file information
4. Optionally checks specific subsystem status via API

## Instructions

When the user invokes `/status`, run:

```bash
cd /home/user/Aurora-AI-Agency

echo "📊 Orchestra Town Status"
echo ""

# Git status
echo "🔧 Git Status:"
git status -s
echo "Branch: $(git branch --show-current)"
echo ""

# Running processes
echo "🏃 Running Processes:"
ps aux | grep -E 'enhanced_server|project_generator' | grep -v grep || echo "  No Orchestra Town processes running"
echo ""

# State files
echo "💾 State Files:"
ls -lh gastown/orchestra/state/*.json 2>/dev/null || echo "  No state files found"
echo ""

# If server is running, check API status
echo "🌐 Server Status:"
curl -s http://localhost:5000/api/status 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "  Server not running (start with /serve)"
```

If the user specifies a subsystem (e.g., `/status tasks`), query that specific endpoint:

```bash
curl -s http://localhost:5000/api/${subsystem} | python3 -m json.tool
```

After running, summarize the system health and any issues found.
