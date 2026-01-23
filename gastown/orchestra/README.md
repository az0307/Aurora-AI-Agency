# 🏙️ Orchestra Town

A simplified multi-agent orchestration system inspired by Gastown, designed for managing AI agents working on complex projects.

## Features

### 🎯 Core Capabilities
- **Mayor Agent**: Main orchestrator that delegates and oversees all work
- **Multi-Agent System**: Workers, Specialists, and Monitors
- **Hierarchical Task Management**: Tasks → Implementation Steps → Subtasks
- **Agent-to-Agent Communication**: Full message bus for inter-agent communication
- **Multiple Thinking Methods**:
  - **Sequential**: Traditional single-agent approach
  - **Swarm**: Multiple agents collaborate on complex tasks
  - **Parallel**: Run multiple solution approaches simultaneously
  - **Twin**: Two agents cross-verify each other's work

### 📊 Dashboard
- Real-time visualization of the entire town
- Live agent status monitoring
- Task creation and tracking
- A2A (Agent-to-Agent) communication viewer
- Auto-refresh capabilities

## Architecture

```
orchestra/
├── core/
│   ├── town_manager.py      # Main orchestration system
│   └── comm_bus.py           # Agent communication bus
├── agents/
│   └── base_agent.py         # Agent types (Mayor, Worker, Specialist, Monitor)
├── tasks/
│   └── task_manager.py       # Hierarchical task management
├── api/
│   └── server.py             # REST API backend
├── dashboard/
│   └── index.html            # Web dashboard UI
└── state/                    # Persistent state storage
```

## Quick Start

### 1. Install Dependencies
```bash
cd ~/gastown/orchestra
pip install -r requirements.txt
```

### 2. Start the Server
```bash
chmod +x run.sh
./run.sh
```

Or manually:
```bash
cd ~/gastown/orchestra
python3 api/server.py
```

### 3. Access Dashboard
Open your browser to: http://localhost:5000/dashboard

### 4. Create Tasks
Use the dashboard UI or the API:

```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Build REST API for user management",
    "description": "Create CRUD endpoints with authentication",
    "priority": "high",
    "thinking_method": "parallel",
    "auto_assign": true
  }'
```

## Thinking Methods

### Sequential
Traditional approach where a single agent handles the entire task.

### Swarm
Multiple specialized agents collaborate:
- Task is broken into subtasks
- Each specialist handles their domain
- Mayor coordinates and synthesizes results

### Parallel
Multiple agents try different approaches simultaneously:
- 2-3 different solution strategies
- Best solution is selected
- Increases chances of optimal solution

### Twin
Two agents work together with cross-verification:
- Agent A implements the solution
- Agent B independently verifies
- Discrepancies are resolved
- Higher reliability

## API Endpoints

### Status & Statistics
- `GET /api/status` - Overall town status
- `GET /api/stats` - Detailed statistics

### Agents
- `GET /api/agents` - List all agents
- `GET /api/agents/<id>` - Get specific agent

### Tasks
- `GET /api/tasks` - List all tasks
- `POST /api/tasks` - Create new task
- `GET /api/tasks/<id>` - Get task details
- `PUT /api/tasks/<id>` - Update task
- `DELETE /api/tasks/<id>` - Delete task
- `POST /api/tasks/<id>/subtasks` - Create subtasks
- `POST /api/tasks/<id>/complete` - Mark task complete
- `POST /api/tasks/<id>/assign` - Assign task

### Messages
- `GET /api/messages` - List messages
- `POST /api/messages` - Send message
- `GET /api/conversation/<agent1>/<agent2>` - Get conversation
- `POST /api/messages/<id>/read` - Mark as read

## Usage Examples

### Creating a Task with Swarm Method
```python
import requests

task = {
    "title": "Build e-commerce platform",
    "description": "Full-stack application with payment integration",
    "priority": "high",
    "thinking_method": "swarm",
    "auto_assign": True
}

response = requests.post("http://localhost:5000/api/tasks", json=task)
print(response.json())
```

### Monitoring Agent Communication
```python
import requests

# Get all messages
messages = requests.get("http://localhost:5000/api/messages").json()

# Get conversation between Mayor and a Worker
conv = requests.get("http://localhost:5000/api/conversation/mayor_id/worker_id").json()
```

### Creating Subtasks
```python
import requests

subtasks = {
    "subtasks": [
        {
            "title": "Setup database schema",
            "description": "Design and implement database",
            "priority": "high",
            "agent_type": "specialist",
            "specialty": "database"
        },
        {
            "title": "Build API endpoints",
            "description": "REST API implementation",
            "priority": "high",
            "agent_type": "specialist",
            "specialty": "backend"
        },
        {
            "title": "Create frontend UI",
            "description": "React dashboard",
            "priority": "medium",
            "agent_type": "specialist",
            "specialty": "frontend"
        }
    ]
}

response = requests.post(
    "http://localhost:5000/api/tasks/task_id/subtasks",
    json=subtasks
)
```

## Agent Roles

### Mayor
- Main orchestrator
- Receives user requests
- Delegates to appropriate agents
- Monitors overall progress
- Synthesizes results

### Workers
- General-purpose execution agents
- Can be specialized (backend, frontend, testing)
- Execute assigned tasks
- Report results to Mayor

### Specialists
- Domain experts
- Deep knowledge in specific areas
- Called for complex specialized work
- Python, JavaScript, DevOps, etc.

### Monitor
- System health checker
- Reports anomalies
- Tracks agent performance
- Ensures system stability

## State Persistence

All state is persisted in `/root/gastown/orchestra/state/`:
- `tasks.json` - Task hierarchy and status
- `messages.json` - Agent communication history
- `town.json` - Agent status and metadata

## Dashboard Features

### Real-time Monitoring
- Live agent status updates
- Task progress tracking
- Message flow visualization
- Statistics dashboard

### Task Creation
- Interactive form
- Choose thinking method
- Set priority levels
- Auto-assignment option

### Auto-refresh
- 5-second refresh cycle
- Can be toggled on/off
- Manual refresh available

## Integration with Claude Code

This system is designed to integrate with Claude Code agents:

1. **Mayor** communicates with user
2. **Mayor** generates optimized prompts for tasks
3. **Agents** would spawn Claude Code instances (in full implementation)
4. **Results** flow back through the communication bus
5. **Dashboard** provides visibility into entire workflow

## Future Enhancements

- [ ] Actual Claude Code agent spawning
- [ ] Git-backed state (like Gastown "hooks")
- [ ] More sophisticated prompt engineering
- [ ] Agent learning and optimization
- [ ] Resource usage tracking
- [ ] Cost monitoring
- [ ] Advanced workflow patterns
- [ ] Plugin system for custom agents

## Comparison to Gastown

| Feature | Orchestra Town | Gastown |
|---------|---------------|---------|
| Multi-agent | ✅ | ✅ |
| Dashboard | ✅ | ❌ |
| Git-backed state | ❌ | ✅ |
| Thinking methods | ✅ (4 types) | ❌ |
| Complexity | Simplified | Full-featured |
| Cost | Lower | $100/hr |
| Learning curve | Gentle | Steep ("Level 6") |

## License

Open source - use freely!

## Credits

Inspired by Steve Yegge's Gastown project.
