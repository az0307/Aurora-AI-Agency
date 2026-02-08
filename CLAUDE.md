# CLAUDE.md — Aurora-AI-Agency

## Project Overview

Aurora-AI-Agency is a collection of AI-powered developer tools. The current main component is **gastown**, a project structure generator that scaffolds new projects with sensible defaults based on a natural language description.

## Repository Structure

```
Aurora-AI-Agency/
├── CLAUDE.md                          # This file
├── README.md                          # Repo landing page
└── gastown/                           # Project structure generator
    ├── README.md                      # Usage docs for gastown
    └── project_generator.py           # Main application (843 lines)
```

This is a small, focused repository with a single Python tool. There are no build systems, CI pipelines, or external dependencies yet.

## Tech Stack

- **Language:** Python 3 (standard library only)
- **Dependencies:** None — uses only `os`, `sys`, `argparse`, `pathlib`
- **No package manager config** (no `requirements.txt`, `pyproject.toml`, or `setup.py`)

## Key Entry Points

### gastown/project_generator.py

The entire application lives in a single file. Run it with:

```bash
python3 gastown/project_generator.py "your project idea"
# or interactively:
python3 gastown/project_generator.py
# with custom output directory:
python3 gastown/project_generator.py "idea" -o ./output
```

**Architecture:**
- `main()` — CLI entry point using `argparse`
- `ProjectGenerator` class — core logic
  - `_detect_project_type()` — keyword-based detection (web, api, cli, ml, data, mobile, general)
  - `_get_structure_template()` — returns nested dict representing file/folder tree
  - `_create_structure()` — recursively creates directories and writes files
  - `_stub_*()` methods (30+) — generate boilerplate content for each file type

**Supported project types:** web frontend, API backend, CLI tool, ML project, data/ETL project, mobile app, general/generic.

## Development Conventions

### Code Style
- Single-file architecture for the generator tool
- Class-based design with private methods (underscore prefix)
- No external linter or formatter configured
- Standard Python naming: `snake_case` for functions/variables, `PascalCase` for classes

### Testing
- No test suite exists yet
- Generated project templates include test stubs (Jest for JS, unittest for Python)
- When adding tests, use Python's built-in `unittest` or `pytest`

### Git Workflow
- `main` is the default branch
- Feature branches follow the pattern `claude/<feature-description>-<id>`
- PRs are used for merging features

## Common Tasks

| Task | Command |
|------|---------|
| Run the generator | `python3 gastown/project_generator.py "project idea"` |
| Run with output dir | `python3 gastown/project_generator.py "idea" -o ./out` |
| Check syntax | `python3 -m py_compile gastown/project_generator.py` |

## Things to Know

- The project has **zero external dependencies** — keep it that way unless there's a strong reason to add one.
- There is no `.gitignore` — consider adding one if generated output or Python artifacts accumulate.
- There is no CI/CD — changes should be manually verified by running the generator and inspecting output.
- The keyword detection in `_detect_project_type()` uses simple string matching with implicit priority ordering (checked top to bottom: web → api → cli → ml → data → mobile → general fallback).
