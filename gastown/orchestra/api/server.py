"""
REST API Server for Orchestra Dashboard
Provides endpoints for dashboard to interact with the town
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
sys.path.append('/root/gastown/orchestra')

from core.town_manager import TownManager

app = Flask(__name__)
CORS(app)  # Enable CORS for dashboard

# Initialize town manager
town = TownManager()


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get overall town status"""
    return jsonify(town.get_town_status())


@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Get all agents"""
    return jsonify(town.get_all_agents())


@app.route('/api/agents/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    """Get specific agent"""
    agent = town.get_agent(agent_id)
    if agent:
        return jsonify(agent)
    return jsonify({"error": "Agent not found"}), 404


@app.route('/api/tasks', methods=['GET', 'POST'])
def tasks():
    """Get all tasks or create new task"""
    if request.method == 'GET':
        return jsonify(town.get_all_tasks())

    elif request.method == 'POST':
        data = request.json
        task = town.create_task(
            title=data.get('title'),
            description=data.get('description', ''),
            priority=data.get('priority', 'medium'),
            thinking_method=data.get('thinking_method', 'sequential'),
            auto_assign=data.get('auto_assign', True)
        )
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


@app.route('/api/tasks/<task_id>/subtasks', methods=['POST'])
def create_subtasks(task_id):
    """Create subtasks for a task"""
    data = request.json
    subtasks = town.create_subtasks(task_id, data.get('subtasks', []))
    return jsonify(subtasks), 201


@app.route('/api/tasks/<task_id>/complete', methods=['POST'])
def complete_task(task_id):
    """Mark task as completed"""
    data = request.json
    town.complete_task(
        task_id,
        result=data.get('result'),
        agent_id=data.get('agent_id')
    )
    return jsonify({"message": "Task completed"}), 200


@app.route('/api/tasks/<task_id>/assign', methods=['POST'])
def assign_task(task_id):
    """Assign task to agents"""
    assigned = town.assign_task(task_id)
    return jsonify({"assigned_agents": assigned}), 200


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


@app.route('/api/messages/<message_id>/read', methods=['POST'])
def mark_message_read(message_id):
    """Mark message as read"""
    town.comm_bus.mark_read(message_id)
    return jsonify({"message": "Marked as read"}), 200


@app.route('/api/conversation/<agent1>/<agent2>', methods=['GET'])
def get_conversation(agent1, agent2):
    """Get conversation between two agents"""
    messages = town.comm_bus.get_conversation(agent1, agent2)
    return jsonify([msg.to_dict() for msg in messages])


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get detailed statistics"""
    return jsonify({
        "tasks": town.task_manager.get_stats(),
        "communication": town.comm_bus.get_stats(),
        "agents": {
            "total": len(town.agents),
            "by_status": town._get_agent_stats_by_status()
        }
    })


if __name__ == '__main__':
    print("🏙️  Orchestra Town API Server")
    print("=" * 50)
    print("Starting server on http://localhost:5000")
    print("Dashboard will be available at http://localhost:5000/dashboard")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
