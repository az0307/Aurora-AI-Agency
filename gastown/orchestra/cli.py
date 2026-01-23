#!/usr/bin/env python3
"""
Orchestra Town CLI
Interactive command-line interface for the orchestration system
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.append('/root/gastown/orchestra')

from core.town_manager import TownManager
from tasks.task_manager import TaskPriority


class OrchestraCLI:
    """Command-line interface for Orchestra Town"""

    def __init__(self):
        self.town = TownManager()

    def status(self):
        """Show town status"""
        status = self.town.get_town_status()

        print("\n🏙️  ORCHESTRA TOWN STATUS")
        print("=" * 60)

        # Agents
        print(f"\n🤖 AGENTS ({status['agents']['total']} total)")
        print("-" * 60)
        for agent in status['agents']['list']:
            status_emoji = {
                'idle': '✅',
                'working': '⚙️',
                'waiting': '⏳',
                'completed': '✔️',
                'error': '❌'
            }.get(agent['status'], '❓')

            role_emoji = {
                'mayor': '👑',
                'worker': '👷',
                'specialist': '🎯',
                'monitor': '👁️'
            }.get(agent['role'], '🤖')

            print(f"{role_emoji} {agent['name']:<20} {status_emoji} {agent['status']:<12} "
                  f"Tasks: {agent['tasks_completed']}/{agent['tasks_failed']}")

        # Tasks
        tasks = status['tasks']
        print(f"\n📋 TASKS ({tasks['total']} total)")
        print("-" * 60)
        for status_name, count in tasks['by_status'].items():
            print(f"  {status_name.upper():<15} {count:>3}")

        # Communication
        comm = status['communication']
        print(f"\n💬 COMMUNICATION ({comm['total_messages']} messages)")
        print("-" * 60)
        print(f"  Unread: {comm['unread_messages']}")

        print("\n" + "=" * 60 + "\n")

    def create_task(self, title, description="", priority="medium", thinking_method="sequential"):
        """Create a new task"""
        task = self.town.create_task(
            title=title,
            description=description,
            priority=priority,
            thinking_method=thinking_method,
            auto_assign=True
        )

        print(f"\n✅ Task created: {task['id']}")
        print(f"   Title: {task['title']}")
        print(f"   Priority: {task['priority']}")
        print(f"   Thinking Method: {task['thinking_method']}")
        print(f"   Status: {task['status']}")
        if task.get('assigned_to'):
            print(f"   Assigned to: {task['assigned_to']}")
        print()

        return task

    def list_tasks(self, status_filter=None):
        """List all tasks"""
        tasks = self.town.get_all_tasks()

        if status_filter:
            tasks = [t for t in tasks if t['status'] == status_filter]

        if not tasks:
            print("\nNo tasks found.\n")
            return

        print(f"\n📋 TASKS ({len(tasks)} found)")
        print("=" * 80)

        for task in tasks:
            status_emoji = {
                'pending': '⏸️',
                'in_progress': '▶️',
                'completed': '✅',
                'failed': '❌',
                'blocked': '🚫'
            }.get(task['status'], '❓')

            print(f"\n{status_emoji} [{task['id']}] {task['title']}")
            print(f"   Status: {task['status']} | Priority: {task['priority']}")
            if task.get('description'):
                print(f"   Description: {task['description']}")
            if task.get('thinking_method'):
                print(f"   Thinking Method: {task['thinking_method']}")
            if task.get('assigned_to'):
                print(f"   Assigned to: {task['assigned_to']}")
            if task.get('children'):
                print(f"   Subtasks: {len(task['children'])}")

        print()

    def list_messages(self, agent_id=None, limit=10):
        """List messages"""
        messages = self.town.get_messages(agent_id=agent_id)[:limit]

        if not messages:
            print("\nNo messages found.\n")
            return

        print(f"\n💬 MESSAGES ({len(messages)} shown)")
        print("=" * 80)

        for msg in messages:
            type_emoji = {
                'info': 'ℹ️',
                'task_assignment': '📋',
                'result': '✅',
                'error': '❌',
                'request': '❓'
            }.get(msg['message_type'], '💬')

            print(f"\n{type_emoji} {msg['from_agent']} → {msg['to_agent']}")
            print(f"   {msg['content']}")
            print(f"   {msg['timestamp']}")

        print()

    def task_info(self, task_id):
        """Show detailed task information"""
        task = self.town.get_task_with_hierarchy(task_id)

        if not task:
            print(f"\n❌ Task not found: {task_id}\n")
            return

        print(f"\n📋 TASK DETAILS: {task['id']}")
        print("=" * 80)
        print(f"Title: {task['title']}")
        print(f"Status: {task['status']}")
        print(f"Priority: {task['priority']}")
        print(f"Type: {task['task_type']}")
        if task.get('description'):
            print(f"Description: {task['description']}")
        if task.get('thinking_method'):
            print(f"Thinking Method: {task['thinking_method']}")
        if task.get('assigned_to'):
            print(f"Assigned to: {task['assigned_to']}")
        if task.get('created_at'):
            print(f"Created: {task['created_at']}")
        if task.get('completed_at'):
            print(f"Completed: {task['completed_at']}")

        if task.get('prompt'):
            print("\n--- Generated Prompt ---")
            print(task['prompt'])

        if task.get('result'):
            print("\n--- Result ---")
            print(task['result'])

        if task.get('children'):
            print(f"\n--- Subtasks ({len(task['children'])}) ---")
            for child in task['children']:
                print(f"  • [{child['id']}] {child['title']} ({child['status']})")

        print()

    def interactive(self):
        """Interactive mode"""
        print("\n🏙️  Orchestra Town - Interactive Mode")
        print("=" * 60)
        print("Commands:")
        print("  status          - Show town status")
        print("  task <title>    - Create a new task")
        print("  tasks           - List all tasks")
        print("  messages        - List recent messages")
        print("  info <task_id>  - Show task details")
        print("  quit            - Exit")
        print("=" * 60)

        while True:
            try:
                command = input("\n🏙️  > ").strip()

                if not command:
                    continue

                if command == "quit" or command == "exit":
                    print("\nGoodbye! 👋\n")
                    break

                elif command == "status":
                    self.status()

                elif command.startswith("task "):
                    title = command[5:].strip()
                    if title:
                        self.create_task(title)
                    else:
                        print("Usage: task <title>")

                elif command == "tasks":
                    self.list_tasks()

                elif command == "messages":
                    self.list_messages()

                elif command.startswith("info "):
                    task_id = command[5:].strip()
                    if task_id:
                        self.task_info(task_id)
                    else:
                        print("Usage: info <task_id>")

                elif command == "help":
                    print("\nAvailable commands:")
                    print("  status, task <title>, tasks, messages, info <task_id>, quit")

                else:
                    print(f"Unknown command: {command}")
                    print("Type 'help' for available commands")

            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋\n")
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(description='Orchestra Town CLI')
    parser.add_argument('command', nargs='?', help='Command to execute')
    parser.add_argument('args', nargs='*', help='Command arguments')
    parser.add_argument('-d', '--description', help='Task description')
    parser.add_argument('-p', '--priority', default='medium', help='Task priority')
    parser.add_argument('-m', '--method', default='sequential', help='Thinking method')

    args = parser.parse_args()
    cli = OrchestraCLI()

    if not args.command:
        cli.interactive()
        return

    if args.command == 'status':
        cli.status()

    elif args.command == 'create':
        if not args.args:
            print("Error: Task title required")
            sys.exit(1)
        title = ' '.join(args.args)
        cli.create_task(
            title=title,
            description=args.description or "",
            priority=args.priority,
            thinking_method=args.method
        )

    elif args.command == 'tasks':
        status_filter = args.args[0] if args.args else None
        cli.list_tasks(status_filter)

    elif args.command == 'messages':
        agent_id = args.args[0] if args.args else None
        cli.list_messages(agent_id)

    elif args.command == 'info':
        if not args.args:
            print("Error: Task ID required")
            sys.exit(1)
        cli.task_info(args.args[0])

    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
