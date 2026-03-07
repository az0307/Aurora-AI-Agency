# Orchestra Town Skills Reference

Quick reference for all available Claude Code skills in this project.

## 📋 Available Skills

### Development Workflow

**`/checkpoint [message]`** - Safe Progress Checkpointing
- Validates syntax, checks imports, runs smoke tests
- Commits changes with descriptive message
- Optionally pushes to remote
- **Use when**: You want to save progress safely

**`/test [component]`** - Run Test Suite
- Runs pytest with verbose output
- Optional component filtering (e.g., `/test mayor`)
- Shows pass/fail summary
- **Use when**: Testing changes or debugging

**`/smoke-test`** - Quick Health Check
- Validates Python syntax in core modules
- Tests imports and basic functionality
- Verifies server can start
- **Use when**: Quick validation before committing

### Server & Generation

**`/serve`** - Start Dashboard Server
- Launches Flask server at http://localhost:5000
- Opens dashboard at /dashboard/kanban
- Initializes all subsystems
- **Use when**: Running the Orchestra Town web interface

**`/generate "description" [options]`** - AI Project Generator
- Creates complete project with AI-generated code
- Supports web, cli, api, ml, fullstack types
- Options: `-o /path/to/output`
- **Use when**: Scaffolding new projects

**`/status [subsystem]`** - System Status Check
- Shows git status, running processes, state files
- Queries API endpoints if server is running
- Optional subsystem focus
- **Use when**: Checking system health

**`/cleanup [--hard]`** - Clean Temporary Files
- Stops running processes
- Removes Python cache and temp files
- `--hard`: Also removes state files (⚠️ destructive)
- **Use when**: Resetting environment

### Code Quality

**`/simplify`** - Code Quality Review
- Reviews changed code for reuse and efficiency
- Suggests improvements
- **Use when**: After making changes

**`/claude-api`** - Claude API Development
- Help with Anthropic SDK usage
- Auto-triggers when working with `anthropic` imports
- **Use when**: Working with AI API integrations

## 🔄 Common Workflows

### Feature Development
```
1. Make changes to code
2. /test                    # Verify tests pass
3. /simplify                # Review code quality
4. /checkpoint "feature: X" # Save progress
```

### Testing Changes
```
1. /smoke-test             # Quick validation
2. /test                   # Full test suite
3. /status                 # Check system state
```

### Starting Fresh Session
```
1. /status                 # Check current state
2. /cleanup                # Clean temp files
3. /serve                  # Start server
```

### Project Generation
```
1. /generate "REST API for users" -o ~/my-api
2. cd ~/my-api
3. /test                   # Verify generated code works
```

## 🎯 Skill Development Tips

- Skills live in `.claude/skills/`
- Each skill is a markdown file with instructions
- Skills appear automatically in Claude Code
- Test skills before committing

## 📖 More Information

See `/help` for general Claude Code commands and `CLAUDE.md` for project-specific guidance.
