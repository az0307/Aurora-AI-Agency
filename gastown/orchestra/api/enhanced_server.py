"""
Enhanced REST API Server with Teams and Mayor Thinking
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sys
sys.path.append('/root/gastown/orchestra')

from core.town_manager import TownManager
from core.enhanced_mayor import EnhancedMayor
from agents.teams import AdvisorAgent, UtilityAgent, PromptingAgent

app = Flask(__name__)
CORS(app)

# Initialize town manager
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


# ===== Standard Endpoints =====

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get overall town status"""
    status = town.get_town_status()
    status['mayor'] = enhanced_mayor.to_dict()
    return jsonify(status)


@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Get all agents including team members"""
    all_agents = []

    for agent in town.agents.values():
        agent_dict = agent.to_dict() if hasattr(agent, 'to_dict') else {
            'id': agent.id,
            'name': agent.name,
            'role': agent.role,
            'status': agent.status
        }
        all_agents.append(agent_dict)

    return jsonify(all_agents)


@app.route('/api/tasks', methods=['GET', 'POST'])
def tasks():
    """Get all tasks or create new task with enhanced Mayor thinking"""
    if request.method == 'GET':
        return jsonify(town.get_all_tasks())

    elif request.method == 'POST':
        data = request.json

        # Mayor thinks about the task first
        task_preview = {
            'title': data.get('title'),
            'description': data.get('description', ''),
            'priority': data.get('priority', 'medium'),
            'thinking_method': data.get('thinking_method', 'sequential')
        }

        thinking_process = enhanced_mayor.think(task_preview)

        # Create the actual task
        task = town.create_task(
            title=data.get('title'),
            description=data.get('description', ''),
            priority=data.get('priority', 'medium'),
            thinking_method=data.get('thinking_method', 'sequential'),
            auto_assign=data.get('auto_assign', True)
        )

        # Attach Mayor's thinking to the task
        task['mayor_thinking'] = thinking_process

        return jsonify(task), 201


@app.route('/api/tasks/<task_id>', methods=['GET', 'PUT', 'DELETE'])
def task_detail(task_id):
    """Get, update, or delete specific task"""
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


@app.route('/api/messages', methods=['GET', 'POST'])
def messages():
    """Get messages or send new message"""
    if request.method == 'GET':
        agent_id = request.args.get('agent_id')
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        msgs = town.get_messages(agent_id, unread_only)
        return jsonify(msgs)

    elif request.method == 'POST':
        data = request.json
        msg = town.send_message(
            from_agent=data.get('from_agent'),
            to_agent=data.get('to_agent'),
            content=data.get('content'),
            message_type=data.get('message_type', 'info')
        )
        return jsonify(msg), 201


# ===== Enhanced Endpoints =====

@app.route('/api/mayor', methods=['GET'])
def get_mayor():
    """Get enhanced Mayor details"""
    return jsonify(enhanced_mayor.to_dict())


@app.route('/api/mayor/thinking', methods=['GET'])
def get_mayor_thinking():
    """Get Mayor's current thinking process"""
    return jsonify({
        'current_thinking': enhanced_mayor.get_current_thinking(),
        'recent_decisions': enhanced_mayor.get_recent_decisions(10)
    })


@app.route('/api/mayor/chat', methods=['POST'])
def chat_with_mayor():
    """Chat with the Mayor in natural language"""
    data = request.json
    user_message = data.get('message', '')

    # Generate Mayor's response
    response = generate_mayor_response(user_message)

    # Log the conversation
    town.comm_bus.send_message(
        from_agent="user",
        to_agent=enhanced_mayor.id,
        content=user_message,
        message_type="chat"
    )

    town.comm_bus.send_message(
        from_agent=enhanced_mayor.id,
        to_agent="user",
        content=response,
        message_type="chat"
    )

    return jsonify({
        'user_message': user_message,
        'mayor_response': response,
        'timestamp': town.comm_bus.messages[list(town.comm_bus.messages.keys())[-1]].timestamp
    })


def generate_mayor_response(message: str) -> str:
    """Generate natural language response from Mayor"""
    msg_lower = message.lower()

    if any(word in msg_lower for word in ['create', 'build', 'make', 'develop']):
        return ("I'll orchestrate this task for you. Let me consult with my advisor team "
                "to plan the approach, then assign the right specialists. I'll also check "
                "if we need any utility tools like web search or browser automation.")

    elif 'status' in msg_lower or 'how' in msg_lower:
        active_tasks = len([t for t in town.get_all_tasks() if t['status'] == 'in_progress'])
        return (f"Currently managing {len(town.agents)} agents with {active_tasks} active tasks. "
                f"My teams are: 4 advisors for strategic planning, 4 utilities for special capabilities, "
                f"and 4 prompting specialists for optimized execution.")

    elif 'team' in msg_lower:
        return ("I have three specialized teams: Advisor Team (planning, architecture, optimization, risk), "
                "Utility Team (web search, deep thinking, browser automation, computer use), "
                "and Prompting Team (various prompting strategies for optimal task execution).")

    elif 'help' in msg_lower or 'what can' in msg_lower:
        return ("I can help you: 1) Create and orchestrate complex tasks, 2) Delegate work to specialized "
                "agents using different thinking methods (swarm, parallel, twin), 3) Consult my advisor "
                "team for strategic guidance, 4) Use utility tools for web search, deep thinking, and more.")

    elif 'thinking' in msg_lower or 'method' in msg_lower:
        return ("I support four thinking methods: Sequential (single agent), Swarm (multiple specialists "
                "collaborating), Parallel (multiple approaches simultaneously), and Twin (cross-verification). "
                "For each task, I consult my advisors and prompting team to determine the best approach.")

    else:
        return ("I understand. I'll coordinate with my teams to handle this efficiently. "
                "Feel free to ask me about status, teams, or create new tasks.")


@app.route('/api/teams', methods=['GET'])
def get_teams():
    """Get all teams"""
    teams = [team.to_dict() for team in enhanced_mayor.teams.values()]
    return jsonify(teams)


@app.route('/api/teams/<team_id>', methods=['GET'])
def get_team(team_id):
    """Get specific team details"""
    team = enhanced_mayor.teams.get(team_id)
    if team:
        team_dict = team.to_dict()

        # Add member details
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

    return jsonify({"error": "Team not found"}), 404


@app.route('/api/advisors', methods=['GET'])
def get_advisors():
    """Get all advisor agents"""
    return jsonify([adv.to_dict() for adv in enhanced_mayor.advisors.values()])


@app.route('/api/utilities', methods=['GET'])
def get_utilities():
    """Get all utility agents"""
    return jsonify([util.to_dict() for util in enhanced_mayor.utilities.values()])


@app.route('/api/utilities/<utility_id>/execute', methods=['POST'])
def execute_utility(utility_id):
    """Execute a utility function"""
    utility = enhanced_mayor.utilities.get(utility_id)
    if not utility:
        return jsonify({"error": "Utility not found"}), 404

    data = request.json
    task = data.get('task', {})
    params = data.get('params', {})

    result = utility.execute(task, params)
    return jsonify(result)


@app.route('/api/prompters', methods=['GET'])
def get_prompters():
    """Get all prompting agents"""
    return jsonify([prom.to_dict() for prom in enhanced_mayor.prompters.values()])


@app.route('/api/integrations', methods=['GET'])
def get_integrations():
    """Get integration point configurations"""
    return jsonify(enhanced_mayor.integration_points)


@app.route('/api/stats/enhanced', methods=['GET'])
def get_enhanced_stats():
    """Get enhanced statistics including teams"""
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
        "communication": town.comm_bus.get_stats()
    })


# ===== Dashboard Routes =====

@app.route('/dashboard')
def dashboard_classic():
    """Serve classic dashboard"""
    return send_from_directory('/home/user/Aurora-AI-Agency/gastown/orchestra/dashboard', 'index.html')


@app.route('/dashboard/kanban')
def dashboard_kanban():
    """Serve Kanban dashboard"""
    return send_from_directory('/home/user/Aurora-AI-Agency/gastown/orchestra/dashboard', 'kanban.html')


@app.route('/')
def root():
    """Redirect to Kanban dashboard"""
    return send_from_directory('/home/user/Aurora-AI-Agency/gastown/orchestra/dashboard', 'kanban.html')


if __name__ == '__main__':
    print("🏙️  Orchestra Town Enhanced API Server")
    print("=" * 60)
    print("Starting server on http://localhost:5000")
    print("")
    print("Dashboards:")
    print("  Kanban:  http://localhost:5000/dashboard/kanban")
    print("  Classic: http://localhost:5000/dashboard")
    print("")
    print("Features:")
    print("  ✅ Enhanced Mayor with Teams")
    print("  ✅ Advisor Team (4 specialists)")
    print("  ✅ Utility Team (4 tools)")
    print("  ✅ Prompting Team (4 strategies)")
    print("  ✅ Mayor Thinking Visibility")
    print("  ✅ Natural Language Chat")
    print("  ✅ Claude Code Integration")
    print("  ✅ OpenCode Ready")
    print("  ✅ Antigravity Conceptual")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
