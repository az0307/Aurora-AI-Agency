# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Orchestra Town is a multi-agent AI orchestration system built in Python/Flask. A central **Mayor** agent delegates tasks to **Worker**, **Specialist**, and **Monitor** agents using configurable thinking methods (sequential, swarm, parallel, twin). The Mayor has three advisory teams (Advisor, Utility, Prompting) that inform delegation decisions.

A separate **Project Generator** (`gastown/project_generator.py`) scaffolds new project structures from natural language descriptions.

## Running the System

```bash
# Start the web server + dashboard (uses venv, installs deps)
cd gastown/orchestra && ./run.sh

# Or run directly
pip install -r gastown/orchestra/requirements.txt
python3 gastown/orchestra/api/enhanced_server.py
# → http://localhost:5000/dashboard/kanban

# CLI interface
python3 gastown/orchestra/cli.py              # interactive REPL
python3 gastown/orchestra/cli.py status       # show town status
python3 gastown/orchestra/cli.py create "Build REST API" -p high -m swarm

# Project generator
python3 gastown/project_generator.py "web app for task management"
python3 gastown/project_generator.py "REST API" -o ~/my-project
```

## Environment Variables

- `ANTHROPIC_API_KEY` — Enables real Claude API execution (without it, executor uses local fallback)
- `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET` — Enables real Google OAuth (without them, auth runs in demo mode)
- `FLASK_SECRET_KEY` — Session encryption key (auto-generated if not set)

## Architecture

The system has a layered architecture where the **API server** (`api/enhanced_server.py`) is the main entry point, initializing all subsystems:

```
API Server (enhanced_server.py)
  └── TownManager (core/town_manager.py)          ← central coordinator
        ├── EnhancedMayor (core/enhanced_mayor.py) ← orchestrator with 3 teams
        │     ├── AdvisorAgents (agents/teams.py)  ← planning/arch/optim/risk
        │     ├── UtilityAgents (agents/teams.py)  ← web_search/deep_think/browser/computer_use
        │     └── PromptingAgents (agents/teams.py)← CoT/few-shot/ToT/zero-shot
        ├── TaskManager (tasks/task_manager.py)    ← hierarchical task tree
        ├── CommunicationBus (core/comm_bus.py)    ← agent-to-agent messaging
        ├── TaskExecutor (core/executor.py)        ← AI execution (Anthropic API / subprocess / local)
        └── GitStateManager (core/git_state.py)    ← persistent state with snapshots

Standalone systems initialized at server level:
  ├── LiveMCPManager (integrations/live_mcp.py)    ← filesystem/git/web tool servers
  ├── GoogleAuthManager (auth/google_auth.py)      ← OAuth with demo fallback
  ├── TokenManager (core/token_manager.py)         ← token counting, bias detection, quality metrics
  └── Observer (monitoring/observer.py)            ← event tracking, performance, anomaly detection
```

### Key Data Flow

1. User creates task via API or chat → Mayor `think()` runs 6-step analysis (consult advisors, determine utilities, generate prompt, plan delegation)
2. Mayor delegates to agents based on thinking method → agents assigned via `TownManager.assign_task()`
3. If `auto_execute=True`, `TaskExecutor` runs the prompt through Anthropic API (or falls back to local generation)
4. Execution callback updates task status and agent state automatically
5. All events flow through `Observer` for monitoring; all messages through `CommunicationBus`

### Agent Hierarchy

Base classes in `agents/base_agent.py`: `BaseAgent` → `MayorAgent`, `WorkerAgent`, `SpecialistAgent`, `MonitorAgent`. Team agents in `agents/teams.py` (`AdvisorAgent`, `UtilityAgent`, `PromptingAgent`) are separate classes, not subclasses of BaseAgent. The `EnhancedMayor` extends `MayorAgent` with team management.

### State Persistence

All state saves to `gastown/orchestra/state/` as JSON files (tasks.json, messages.json, town.json, auth.json). The `.gitignore` in that directory excludes all JSON files from git. `GitStateManager` supports snapshots and git-tracked history.

### Path Resolution

All modules use `Path(__file__).parent.parent` for relative path resolution — no hardcoded absolute paths. The `sys.path.append()` in several files points to the orchestra directory to enable cross-module imports.

## Key API Endpoints

- `POST /api/tasks` — Create task (supports `auto_execute`, `thinking_method`, `priority`)
- `POST /api/tasks/<id>/execute` — Execute assigned task via AI
- `POST /api/mayor/chat` — Natural language chat with Mayor
- `POST /api/mcp/execute` — Run live MCP tools (`{server, tool, params}`)
- `POST /api/tokens/evaluate` — Analyze text for bias and quality
- `GET /api/observer/dashboard` — Real-time system monitoring
- `GET /api/status` — Full system status including all subsystems

## Dependencies

Python 3.x with: `flask`, `flask-cors`, `tiktoken`, `anthropic` (optional for API execution).

## Session Management & Best Practices

### Working with Claude Code

**Checkpoint Pattern**: Save progress frequently to avoid losing work to rate limits or session interruptions.

```bash
# Create checkpoints at milestones
git add -A && git commit -m "checkpoint: <feature> working" && git push -u origin <branch>

# Use the /checkpoint skill (if available) to auto-test and commit
/checkpoint "feature description"
```

**Testing Before Committing**: Always validate changes before committing:

```bash
# Run Orchestra Town tests
cd gastown/orchestra
python3 -m pytest tests/ -v                    # unit tests
python3 api/enhanced_server.py &               # integration test
sleep 3 && curl http://localhost:5000/health
kill %1

# Project generator smoke test
python3 gastown/project_generator.py "test app" -o /tmp/test-output
```

**Session Recovery**: If a session is interrupted:

1. Check branch status: `git status` and `git log -3`
2. Review uncommitted changes: `git diff`
3. Check running processes: `ps aux | grep python`
4. Verify state files: `ls -lh gastown/orchestra/state/`

### Development Workflow

**Incremental Development**: Break large features into small, testable chunks:

1. Plan feature in small steps (use TodoWrite)
2. Implement one step at a time
3. Test each step individually
4. Commit working state before moving to next step
5. Push to remote branch regularly

**Testing Strategy**:

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Start server, test API endpoints
- **Smoke tests**: Run CLI commands, verify basic functionality
- **State validation**: Check JSON files in `state/` directory

**Common Pitfalls**:

- Don't commit broken code (always test first)
- Don't skip testing "small changes" (they often break things)
- Don't batch too many changes in one commit
- Don't forget to push to remote (work can be lost otherwise)

### Sub-Agent Usage

When tasks require extensive exploration or multiple parallel queries, use sub-agents:

```python
# Instead of manually searching through many files:
# Use Agent tool with subagent_type="Explore" for broad codebase searches

# Instead of running multiple independent tests:
# Use Agent tool to parallelize test execution
```

**When to use sub-agents**:
- Exploring unfamiliar codebases (> 3 search queries needed)
- Running multiple independent test suites
- Researching external documentation or APIs
- Parallelizing independent work items
