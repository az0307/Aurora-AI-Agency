# 🏙️ Orchestra Town - Quick Start Guide

## What You Got

A complete multi-agent orchestration system with:
- **Mayor Agent** - Your main orchestrator (you talk to the Mayor)
- **Worker & Specialist Agents** - Execute tasks
- **Monitor Agent** - Watches system health
- **Full Dashboard** - Real-time visualization
- **A2A Communication** - All agent messages visible
- **4 Thinking Methods** - Sequential, Swarm, Parallel, Twin

## File Structure

```
gastown/
├── first-loop/              # Your original project generator
│   └── project_generator.py
└── orchestra/               # NEW: Orchestration system
    ├── core/
    │   ├── town_manager.py      # Main orchestrator
    │   └── comm_bus.py           # Agent messaging
    ├── agents/
    │   └── base_agent.py         # Agent types
    ├── tasks/
    │   └── task_manager.py       # Task hierarchy
    ├── api/
    │   └── server.py             # REST API
    ├── dashboard/
    │   └── index.html            # Web UI
    ├── cli.py                    # Command-line tool
    ├── run.sh                    # Launcher
    └── README.md                 # Full documentation
```

## Start in 3 Steps

### 1. Install
```bash
cd gastown/orchestra
pip install -r requirements.txt
```

### 2. Launch Dashboard
```bash
./run.sh
```

Opens at: **http://localhost:5000/dashboard**

### 3. Create Tasks

**Via Dashboard:**
- Open http://localhost:5000/dashboard
- Fill in the "Create New Task" form
- Choose thinking method
- Submit!

**Via CLI:**
```bash
# Interactive mode
python3 cli.py

# Direct command
python3 cli.py create "Build REST API" -p high -m swarm
```

## Thinking Methods Explained

### Sequential (Default)
Single agent handles everything.
```bash
python3 cli.py create "Fix bug in auth" -m sequential
```

### Swarm
Multiple specialists collaborate.
```bash
python3 cli.py create "Build full-stack app" -m swarm
```
Mayor breaks it down → assigns to specialists → synthesizes results

### Parallel
Multiple agents try different approaches simultaneously.
```bash
python3 cli.py create "Optimize performance" -m parallel
```
Best solution wins!

### Twin
Two agents cross-verify each other.
```bash
python3 cli.py create "Security audit" -m twin
```
Agent A implements → Agent B verifies → discrepancies resolved

## CLI Commands

```bash
# Interactive mode
python3 cli.py

# Show status
python3 cli.py status

# Create task
python3 cli.py create "Task title" -d "Description" -p high -m swarm

# List tasks
python3 cli.py tasks

# View messages
python3 cli.py messages

# Task details
python3 cli.py info <task_id>
```

## Dashboard Features

### Stats Panel
- Total agents
- Active tasks
- Messages sent
- Completed tasks

### Agents Panel
- Live status (idle/working/waiting)
- Role badges (Mayor/Worker/Specialist/Monitor)
- Task completion counts
- Current assignments

### Tasks Panel
- All tasks with status
- Priority levels
- Thinking methods
- Agent assignments
- Subtask counts

### Communications Panel
- All A2A messages
- Message types (info/task_assignment/result/error)
- Timestamps
- Unread indicators

### Auto-Refresh
Toggle on/off - refreshes every 5 seconds

## Example Usage

### Create a Complex Task
```bash
python3 cli.py create \
  "Build e-commerce platform" \
  -d "Full-stack with payment integration" \
  -p critical \
  -m swarm
```

**What happens:**
1. Mayor receives task
2. Generates optimized prompts
3. Breaks into subtasks
4. Assigns to specialists (backend, frontend, DevOps)
5. Specialists execute in parallel
6. Results flow back through communication bus
7. Mayor synthesizes final result

### Monitor in Real-Time

**Terminal 1:**
```bash
./run.sh  # Start server
```

**Terminal 2:**
```bash
python3 cli.py  # Interactive CLI
> status
> tasks
> messages
```

**Browser:**
```
http://localhost:5000/dashboard
```

Watch agents work in real-time!

## API Endpoints

```bash
# Status
curl http://localhost:5000/api/status

# Create task
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Build REST API",
    "description": "CRUD with auth",
    "priority": "high",
    "thinking_method": "swarm",
    "auto_assign": true
  }'

# List tasks
curl http://localhost:5000/api/tasks

# Messages
curl http://localhost:5000/api/messages
```

## Current Agents

Your town starts with:

1. **👑 Mayor** - Orchestrator
2. **👷 Worker-Alpha** - Backend specialist
3. **👷 Worker-Beta** - Frontend specialist
4. **👷 Worker-Gamma** - Testing specialist
5. **🎯 Specialist-Python** - Python expert
6. **🎯 Specialist-JS** - JavaScript/React expert
7. **🎯 Specialist-DevOps** - Infrastructure expert
8. **👁️ Monitor** - System health watcher

## State Persistence

All state saved in `gastown/orchestra/state/`:
- `tasks.json` - Task hierarchy
- `messages.json` - Communication history
- `town.json` - Agent metadata

## Compared to Real Gastown

| Feature | Orchestra | Gastown |
|---------|-----------|---------|
| Dashboard | ✅ Yes | ❌ No |
| Multi-agent | ✅ Yes | ✅ Yes |
| Thinking methods | ✅ 4 types | ❌ 1 type |
| Git hooks | ❌ No | ✅ Yes |
| Cost | 💰 Low | 💰💰💰 $100/hr |
| Complexity | 🎯 Simple | 🔥 "Level 6" |

## Next Steps

1. **Test it out** - Create tasks, watch agents work
2. **Explore the dashboard** - See real-time updates
3. **Try different thinking methods** - Compare results
4. **Check the code** - It's all readable Python
5. **Extend it** - Add custom agents, new thinking methods

## Need Help?

Check the full docs:
```bash
cat gastown/orchestra/README.md
```

Or just start using it - it's designed to be intuitive!

## Integration Potential

This system is ready to integrate with:
- Claude Code (for actual agent execution)
- Git workflows (version control)
- CI/CD pipelines
- Monitoring systems
- Custom tools and APIs

Right now it's a **framework** - you can plug in actual execution engines.

---

**Built and tested** ✅
**Committed and pushed** ✅
**Ready to use** ✅

Enjoy your orchestration system! 🏙️
