# Test Skill

Run Orchestra Town test suite

## Usage

```
/test [component]
```

## What it does

1. Runs pytest on the Orchestra Town test suite
2. Shows verbose output for debugging
3. Optionally tests specific components

## Instructions

When the user invokes `/test`, run the following:

```bash
cd /home/user/Aurora-AI-Agency/gastown/orchestra && python3 -m pytest tests/ -v
```

If the user specifies a component (e.g., `/test mayor`), run:

```bash
cd /home/user/Aurora-AI-Agency/gastown/orchestra && python3 -m pytest tests/ -v -k "${component}"
```

After running, summarize the test results:
- Number of tests passed/failed
- Any failures or errors found
- Recommendations for fixing issues
