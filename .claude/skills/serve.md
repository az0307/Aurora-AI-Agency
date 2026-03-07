# Serve Skill

Start Orchestra Town dashboard server

## Usage

```
/serve
```

## What it does

1. Starts the Flask server with all subsystems
2. Opens the dashboard at http://localhost:5000/dashboard/kanban
3. Initializes all managers (TownManager, LiveMCPManager, etc.)

## Instructions

When the user invokes `/serve`, run the following in the background:

```bash
cd /home/user/Aurora-AI-Agency/gastown/orchestra && ./run.sh
```

After starting, inform the user:
- Server is running at http://localhost:5000
- Dashboard available at http://localhost:5000/dashboard/kanban
- API docs at http://localhost:5000/api/status
- How to stop the server (Ctrl+C or find and kill the process)

Note: This runs in the foreground, so the user will need to stop it manually or run in background with `run_in_background: true`.
