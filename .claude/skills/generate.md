# Generate Skill

Run the AI-powered project generator

## Usage

```
/generate "project description" [options]
```

## What it does

1. Runs the project_generator.py with AI-powered code generation
2. Creates a complete project structure with working code
3. Supports multiple project types (web, cli, api, ml, fullstack)

## Instructions

When the user invokes `/generate`, run:

```bash
cd /home/user/Aurora-AI-Agency && python3 gastown/project_generator.py "${description}" ${options}
```

Common options:
- `-o /path/to/output` - Specify output directory
- `--dry-run` - Preview without creating files (if implemented)
- `--no-ai` - Use templates only (if implemented)

Examples:
- `/generate "REST API for user management"`
- `/generate "React todo app" -o ~/projects/todo-app`
- `/generate "ML pipeline for sentiment analysis"`

After running, show the user:
- Output directory location
- Project structure created
- Next steps to run/test the generated project
