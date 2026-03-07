# Checkpoint Skill

Create a safe checkpoint by running tests and committing working state.

## Usage

```
/checkpoint [message]
```

## What it does

1. Checks for uncommitted changes
2. Runs Python syntax validation
3. Checks imports for main modules
4. Smoke tests the project generator
5. Commits changes with descriptive message
6. Optionally pushes to remote

## Implementation

This skill runs the `/home/user/Aurora-AI-Agency/checkpoint.sh` script.

## Instructions

When the user invokes `/checkpoint`, run the following command:

```bash
cd $CLAUDE_PROJECT_DIR && ./checkpoint.sh "${message:-checkpoint: working state}"
```

If the user provides a message, use it. Otherwise, use the default "checkpoint: working state".

After running, inform the user of the result and whether changes were committed/pushed.
