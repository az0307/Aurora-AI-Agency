"""
Enhanced REST API Server for Orchestra Town
Integrates: AI Execution, Live MCP, OAuth, Token Management, Observer
"""

from flask import Flask, jsonify, request, send_from_directory, redirect, session
from flask_cors import CORS
import sys
import os

# Ensure imports work from any directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.town_manager import TownManager
from core.enhanced_mayor import EnhancedMayor
from core.token_manager import TokenManager
from core.git_state import GitStateManager
from agents.teams import AdvisorAgent, UtilityAgent, PromptingAgent
from integrations.live_mcp import LiveMCPManager
from monitoring.observer import Observer, EventType, global_observer
from auth.google_auth import GoogleAuthManager

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(32).hex())
CORS(app)

# Dashboard directory
DASHBOARD_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "dashboard"
)

# ===== Initialize Systems =====
town = TownManager()

# Replace standard mayor with enhanced mayor
enhanced_mayor = EnhancedMayor()
town.mayor = enhanced_mayor
town.agents[enhanced_mayor.id] = enhanced_mayor

# Add team members to agents dict for visibility
for advisor in enhanced_mayor.advisors.values():
    town.agents[advisor.id] = advisor
for utility in enhanced_mayor.utilities.values():
    town.agents[utility.id] = utility
for prompter in enhanced_mayor.prompters.values():
    town.agents[prompter.id] = prompter

# Enterprise systems
token_manager = TokenManager()
live_mcp = LiveMCPManager()
auth_manager = GoogleAuthManager()
observer = global_observer


# ===== Authentication Middleware =====

def get_current_user():
    """Get current user from session (returns None if not authenticated)"""
    token = session.get("token")
    if token:
        return auth_manager.verify_session(token)
    return None


# ===== Standard Endpoints =====

@app.route('/api/status', methods=['GET'])
def get_status():
    status = town.get_town_status()
    status['mayor'] = enhanced_mayor.to_dict()
    status['systems'] = {
        'executor': town.executor.get_stats(),
        'mcp': live_mcp.get_stats(),
        'auth': auth_manager.get_stats(),
        'tokens': token_manager.get_comprehensive_stats(),
        'observer': observer.get_realtime_dashboard(),
    }
    return jsonify(status)


@app.route('/api/agents', methods=['GET'])
def get_agents():
    all_agents = []
    for agent in town.agents.values():
        agent_dict = agent.to_dict() if hasattr(agent, 'to_dict') else {
            'id': agent.id, 'name': agent.name,
            'role': agent.role, 'status': agent.status
        }
        all_agents.append(agent_dict)
    return jsonify(all_agents)


@app.route('/api/tasks', methods=['GET', 'POST'])
def tasks():
    if request.method == 'GET':
        return jsonify(town.get_all_tasks())

    data = request.json

    # Mayor thinks about the task first
    task_preview = {
        'title': data.get('title'),
        'description': data.get('description', ''),
        'priority': data.get('priority', 'medium'),
        'thinking_method': data.get('thinking_method', 'sequential')
    }

    thinking_process = enhanced_mayor.think(task_preview)

    # Emit observer event
    observer.emit(EventType.MAYOR_THINKING, {
        "task": task_preview['title'],
        "thinking": thinking_process
    }, source=enhanced_mayor.id)

    # Create the actual task
    auto_execute = data.get('auto_execute', False)
    task = town.create_task(
        title=data.get('title'),
        description=data.get('description', ''),
        priority=data.get('priority', 'medium'),
        thinking_method=data.get('thinking_method', 'sequential'),
        auto_assign=data.get('auto_assign', True),
        auto_execute=auto_execute
    )

    task['mayor_thinking'] = thinking_process

    # Evaluate with token manager
    if task.get('prompt'):
        eval_result = token_manager.evaluate_output(task['prompt'])
        task['prompt_analysis'] = eval_result

    observer.emit(EventType.TASK_CREATED, {
        "task_id": task['id'],
        "title": task['title']
    }, source="api")

    return jsonify(task), 201


@app.route('/api/tasks/<task_id>', methods=['GET', 'PUT', 'DELETE'])
def task_detail(task_id):
    if request.method == 'GET':
        task = town.get_task_with_hierarchy(task_id)
        if task:
            return jsonify(task)
        return jsonify({"error": "Task not found"}), 404

    elif request.method == 'PUT':
        data = request.json
        task = town.task_manager.update_task(task_id, **data)
        if task:
            return jsonify(task.to_dict())
        return jsonify({"error": "Task not found"}), 404

    elif request.method == 'DELETE':
        if town.task_manager.delete_task(task_id):
            return jsonify({"message": "Task deleted"}), 200
        return jsonify({"error": "Task not found"}), 404


@app.route('/api/tasks/<task_id>/execute', methods=['POST'])
def execute_task(task_id):
    """Execute a task using the AI executor"""
    data = request.json or {}
    method = data.get('method', 'api')

    task = town.task_manager.get_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    agent_id = task.assigned_to
    if not agent_id:
        return jsonify({"error": "Task not assigned to any agent"}), 400

    # Execute synchronously or async
    if data.get('async', False):
        town.execute_task_async(task_id, agent_id, method)
        return jsonify({"status": "executing", "task_id": task_id})
    else:
        result = town.execute_task(task_id, agent_id, method)
        observer.emit(EventType.TASK_COMPLETED, {
            "task_id": task_id,
            "result_status": result.get("status")
        }, source=agent_id)
        return jsonify(result)


@app.route('/api/tasks/<task_id>/status', methods=['GET'])
def task_execution_status(task_id):
    """Get execution status for a task"""
    status = town.executor.get_execution_status(task_id)
    if status:
        return jsonify(status)
    return jsonify({"error": "No execution found for task"}), 404


@app.route('/api/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        agent_id = request.args.get('agent_id')
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        msgs = town.get_messages(agent_id, unread_only)
        return jsonify(msgs)

    data = request.json
    msg = town.send_message(
        from_agent=data.get('from_agent'),
        to_agent=data.get('to_agent'),
        content=data.get('content'),
        message_type=data.get('message_type', 'info')
    )
    return jsonify(msg), 201


# ===== Mayor Endpoints =====

@app.route('/api/mayor', methods=['GET'])
def get_mayor():
    return jsonify(enhanced_mayor.to_dict())


@app.route('/api/mayor/thinking', methods=['GET'])
def get_mayor_thinking():
    return jsonify({
        'current_thinking': enhanced_mayor.get_current_thinking(),
        'recent_decisions': enhanced_mayor.get_recent_decisions(10)
    })


@app.route('/api/mayor/chat', methods=['POST'])
def chat_with_mayor():
    data = request.json
    user_message = data.get('message', '')

    response = generate_mayor_response(user_message)

    town.comm_bus.send_message(
        from_agent="user", to_agent=enhanced_mayor.id,
        content=user_message, message_type="chat"
    )
    town.comm_bus.send_message(
        from_agent=enhanced_mayor.id, to_agent="user",
        content=response, message_type="chat"
    )

    # Evaluate response quality
    quality = token_manager.evaluate_output(response)

    return jsonify({
        'user_message': user_message,
        'mayor_response': response,
        'quality': quality,
        'timestamp': town.comm_bus.messages[
            list(town.comm_bus.messages.keys())[-1]
        ].timestamp
    })


def generate_mayor_response(message: str) -> str:
    msg_lower = message.lower()

    if any(word in msg_lower for word in ['create', 'build', 'make', 'develop']):
        return ("I'll orchestrate this task for you. Let me consult with my advisor team "
                "to plan the approach, then assign the right specialists. I'll also check "
                "if we need any utility tools like web search or browser automation.")

    elif 'status' in msg_lower or 'how' in msg_lower:
        active_tasks = len([
            t for t in town.get_all_tasks() if t['status'] == 'in_progress'
        ])
        exec_stats = town.executor.get_stats()
        return (f"Currently managing {len(town.agents)} agents with {active_tasks} active tasks. "
                f"Executor: {exec_stats['total_executions']} total executions, "
                f"API {'available' if exec_stats['api_available'] else 'not configured'}. "
                f"My teams: 4 advisors, 4 utilities, 4 prompting specialists.")

    elif 'team' in msg_lower:
        return ("I have three specialized teams: Advisor Team (planning, architecture, "
                "optimization, risk), Utility Team (web search, deep thinking, browser "
                "automation, computer use), and Prompting Team (chain-of-thought, few-shot, "
                "tree-of-thought, zero-shot).")

    elif any(word in msg_lower for word in ['execute', 'run', 'do']):
        return ("To execute a task, create it first and I'll assign it to the best agent. "
                "Then use the execute endpoint or set auto_execute=true when creating. "
                "I support API-based execution (Claude), subprocess, and local fallback.")

    elif 'mcp' in msg_lower or 'tool' in msg_lower:
        tools = live_mcp.get_all_tools()
        return (f"I have {len(tools)} live MCP tools available: "
                f"filesystem (read, write, search, list), "
                f"git (status, diff, log, branch), "
                f"and web (fetch). All are operational and ready.")

    elif 'help' in msg_lower or 'what can' in msg_lower:
        return ("I can: 1) Create and orchestrate complex tasks, 2) Execute them via "
                "Claude API or locally, 3) Use live MCP tools for file/git/web ops, "
                "4) Monitor execution with bias detection and quality metrics, "
                "5) Delegate with swarm/parallel/twin thinking methods.")

    elif 'thinking' in msg_lower or 'method' in msg_lower:
        return ("I support four thinking methods: Sequential (single agent), "
                "Swarm (specialists collaborating), Parallel (multiple approaches), "
                "and Twin (cross-verification). For each task, I consult my advisors "
                "and prompting team to determine the best approach.")

    else:
        return ("I understand. I'll coordinate with my teams to handle this. "
                "Try: 'create a REST API', 'status', 'teams', 'execute', or 'help'.")


# ===== Team Endpoints =====

@app.route('/api/teams', methods=['GET'])
def get_teams():
    return jsonify([team.to_dict() for team in enhanced_mayor.teams.values()])


@app.route('/api/teams/<team_id>', methods=['GET'])
def get_team(team_id):
    team = enhanced_mayor.teams.get(team_id)
    if not team:
        return jsonify({"error": "Team not found"}), 404

    team_dict = team.to_dict()
    members = []
    for member_id in team.members:
        if member_id in enhanced_mayor.advisors:
            members.append(enhanced_mayor.advisors[member_id].to_dict())
        elif member_id in enhanced_mayor.utilities:
            members.append(enhanced_mayor.utilities[member_id].to_dict())
        elif member_id in enhanced_mayor.prompters:
            members.append(enhanced_mayor.prompters[member_id].to_dict())
    team_dict['member_details'] = members
    return jsonify(team_dict)


@app.route('/api/advisors', methods=['GET'])
def get_advisors():
    return jsonify([adv.to_dict() for adv in enhanced_mayor.advisors.values()])


@app.route('/api/utilities', methods=['GET'])
def get_utilities():
    return jsonify([
        util.to_dict() for util in enhanced_mayor.utilities.values()
    ])


@app.route('/api/utilities/<utility_id>/execute', methods=['POST'])
def execute_utility(utility_id):
    utility = enhanced_mayor.utilities.get(utility_id)
    if not utility:
        return jsonify({"error": "Utility not found"}), 404

    data = request.json
    result = utility.execute(data.get('task', {}), data.get('params', {}))

    observer.emit(EventType.UTILITY_CALLED, {
        "utility": utility_id,
        "capability": utility.capability
    }, source=utility_id)

    return jsonify(result)


@app.route('/api/prompters', methods=['GET'])
def get_prompters():
    return jsonify([
        prom.to_dict() for prom in enhanced_mayor.prompters.values()
    ])


@app.route('/api/integrations', methods=['GET'])
def get_integrations():
    return jsonify(enhanced_mayor.integration_points)


# ===== Execution Endpoints =====

@app.route('/api/executor/stats', methods=['GET'])
def executor_stats():
    return jsonify(town.executor.get_stats())


@app.route('/api/executor/history', methods=['GET'])
def executor_history():
    limit = int(request.args.get('limit', 20))
    history = [
        e.to_dict() for e in town.executor.executions[-limit:]
    ]
    return jsonify(history)


# ===== Live MCP Endpoints =====

@app.route('/api/mcp/servers', methods=['GET'])
def mcp_servers():
    return jsonify(live_mcp.to_dict())


@app.route('/api/mcp/tools', methods=['GET'])
def mcp_tools():
    return jsonify(live_mcp.get_all_tools())


@app.route('/api/mcp/execute', methods=['POST'])
def mcp_execute():
    """Execute an MCP tool"""
    data = request.json
    server = data.get('server')
    tool = data.get('tool')
    params = data.get('params', {})

    if not server or not tool:
        return jsonify({"error": "server and tool are required"}), 400

    result = live_mcp.execute_tool(server, tool, params)

    observer.emit(EventType.UTILITY_CALLED, {
        "server": server, "tool": tool, "success": "error" not in result
    }, source="mcp")

    return jsonify(result)


@app.route('/api/mcp/stats', methods=['GET'])
def mcp_stats():
    return jsonify(live_mcp.get_stats())


# ===== Auth Endpoints =====

@app.route('/auth/login', methods=['GET'])
def auth_login():
    """Start OAuth flow or demo login"""
    if auth_manager.is_configured:
        auth_url = auth_manager.get_auth_url()
        return redirect(auth_url)
    else:
        # Demo mode - auto login
        sess = auth_manager.login_demo()
        session['token'] = sess.token
        return redirect('/dashboard/kanban')


@app.route('/auth/callback', methods=['GET'])
def auth_callback():
    """Handle OAuth callback"""
    code = request.args.get('code')
    state = request.args.get('state')

    if not code:
        return jsonify({"error": "No authorization code"}), 400

    # Exchange code for tokens
    tokens = auth_manager.exchange_code(code)
    if not tokens or "error" in tokens:
        return jsonify({"error": tokens.get("error", "Token exchange failed")}), 400

    # Get user info
    user_info = auth_manager.get_user_info(tokens.get('access_token', ''))
    if not user_info or "error" in user_info:
        return jsonify({"error": "Failed to get user info"}), 400

    # Create session
    sess = auth_manager.create_session(
        user_info['id'], user_info['email'],
        user_info['name'], user_info.get('picture')
    )
    session['token'] = sess.token
    return redirect('/dashboard/kanban')


@app.route('/auth/logout', methods=['GET', 'POST'])
def auth_logout():
    token = session.get('token')
    if token:
        auth_manager.logout(token)
    session.clear()
    return redirect('/')


@app.route('/auth/me', methods=['GET'])
def auth_me():
    user = get_current_user()
    if user:
        return jsonify(user.to_dict())
    return jsonify({"authenticated": False, "mode": auth_manager.mode})


@app.route('/auth/stats', methods=['GET'])
def auth_stats():
    return jsonify(auth_manager.get_stats())


# ===== Token Manager Endpoints =====

@app.route('/api/tokens/stats', methods=['GET'])
def token_stats():
    return jsonify(token_manager.get_comprehensive_stats())


@app.route('/api/tokens/evaluate', methods=['POST'])
def token_evaluate():
    """Evaluate text for bias and quality"""
    data = request.json
    text = data.get('text', '')
    result = token_manager.evaluate_output(
        text,
        check_bias=data.get('check_bias', True),
        check_quality=data.get('check_quality', True)
    )
    return jsonify(result)


# ===== Observer Endpoints =====

@app.route('/api/observer/dashboard', methods=['GET'])
def observer_dashboard():
    return jsonify(observer.get_realtime_dashboard())


@app.route('/api/observer/events', methods=['GET'])
def observer_events():
    event_type = request.args.get('type')
    limit = int(request.args.get('limit', 50))

    if event_type:
        try:
            et = EventType(event_type)
            return jsonify(observer.get_event_stream(et, limit))
        except ValueError:
            return jsonify({"error": f"Unknown event type: {event_type}"}), 400

    return jsonify(observer.get_event_stream(limit=limit))


@app.route('/api/observer/report', methods=['GET'])
def observer_report():
    hours = int(request.args.get('hours', 24))
    return jsonify(observer.generate_report(hours))


@app.route('/api/observer/agent/<agent_id>', methods=['GET'])
def observer_agent(agent_id):
    return jsonify(observer.get_agent_insights(agent_id))


# ===== Git State Endpoints =====

@app.route('/api/state/snapshot', methods=['POST'])
def create_snapshot():
    data = request.json or {}
    label = data.get('label')
    path = town.git_state.save_snapshot(label)
    return jsonify({"status": "saved", "path": path})


@app.route('/api/state/snapshots', methods=['GET'])
def list_snapshots():
    return jsonify(town.git_state.list_snapshots())


@app.route('/api/state/history', methods=['GET'])
def state_history():
    key = request.args.get('key')
    limit = int(request.args.get('limit', 10))
    return jsonify(town.git_state.get_history(key, limit))


@app.route('/api/state/stats', methods=['GET'])
def state_stats():
    return jsonify(town.git_state.get_stats())


# ===== Stats =====

@app.route('/api/stats/enhanced', methods=['GET'])
def get_enhanced_stats():
    return jsonify({
        "town": town.get_town_status(),
        "mayor": {
            "thinking_entries": len(enhanced_mayor.current_thinking),
            "decisions_made": len(enhanced_mayor.decisions),
            "teams_managed": len(enhanced_mayor.teams)
        },
        "teams": {
            "advisors": len(enhanced_mayor.advisors),
            "utilities": len(enhanced_mayor.utilities),
            "prompters": len(enhanced_mayor.prompters)
        },
        "tasks": town.task_manager.get_stats(),
        "communication": town.comm_bus.get_stats(),
        "execution": town.executor.get_stats(),
        "mcp": live_mcp.get_stats(),
        "auth": auth_manager.get_stats(),
        "tokens": token_manager.get_comprehensive_stats()
    })


# ===== Dashboard Routes =====

@app.route('/dashboard')
def dashboard_classic():
    return send_from_directory(DASHBOARD_DIR, 'index.html')


@app.route('/dashboard/kanban')
def dashboard_kanban():
    return send_from_directory(DASHBOARD_DIR, 'kanban.html')


@app.route('/')
def root():
    return send_from_directory(DASHBOARD_DIR, 'kanban.html')


# ===== Startup =====

if __name__ == '__main__':
    print("=" * 60)
    print("  Orchestra Town Enhanced API Server")
    print("=" * 60)
    print()
    print("Dashboards:")
    print("  Kanban:  http://localhost:5000/dashboard/kanban")
    print("  Classic: http://localhost:5000/dashboard")
    print()
    print("Core Systems:")
    print(f"  Enhanced Mayor with {len(enhanced_mayor.teams)} teams")
    exec_stats = town.executor.get_stats()
    print(f"  AI Executor: API {'available' if exec_stats['api_available'] else 'not configured (set ANTHROPIC_API_KEY)'}")
    print(f"  Live MCP: {live_mcp.get_stats()['tools_available']} tools across {len(live_mcp.servers)} servers")
    print(f"  Auth: {auth_manager.mode} mode")
    print(f"  Token Manager: {token_manager.budget.total_budget:,} token budget")
    print(f"  Observer: Active")
    print(f"  Git State: {town.git_state.state_dir}")
    print()
    print("API Endpoints:")
    print("  /api/status          - Full system status")
    print("  /api/tasks           - Task CRUD + execution")
    print("  /api/mayor/chat      - Chat with Mayor")
    print("  /api/mcp/execute     - Live MCP tools")
    print("  /api/executor/stats  - Execution statistics")
    print("  /api/tokens/evaluate - Bias & quality analysis")
    print("  /api/observer/dashboard - Real-time monitoring")
    print("  /auth/login          - Authentication")
    print("=" * 60)

    app.run(host='0.0.0.0', port=5000, debug=True)
