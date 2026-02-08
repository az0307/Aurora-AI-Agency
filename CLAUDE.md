# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Aurora-AI-Agency contains **gastown**, a zero-dependency Python 3 CLI tool that generates project scaffolding from natural language descriptions. It detects project type (web frontend, API backend, CLI tool, ML project, data project, mobile app, or general) via keyword matching and creates appropriate directory structures with boilerplate files.

## Commands

```bash
# Run interactively (prompts for input)
python3 gastown/project_generator.py

# Run with a project description
python3 gastown/project_generator.py "web app for task management"

# Specify output directory
python3 gastown/project_generator.py "REST API for users" -o ~/output-dir

# Validate Python syntax
python3 -m py_compile gastown/project_generator.py
```

There is no test suite, linter, build system, or CI/CD pipeline configured.

## Architecture

The entire application is a single file: `gastown/project_generator.py` (~843 lines).

- **`ProjectGenerator` class** — Core logic. Takes a project idea string and output directory. Key flow:
  1. `_detect_project_type()` — Keyword-based classification into one of 7 project types
  2. `_get_structure_template()` — Returns a nested dict defining the directory/file tree for that type
  3. `_create_structure()` — Recursively walks the template dict to create directories and files
  4. 50+ `_stub_*()` methods — Each returns boilerplate content for a specific file type (e.g., `_stub_react_component()`, `_stub_py_main()`, `_stub_ml_model()`)

- **`main()` function** — CLI entry point using argparse. Supports both interactive and command-line modes.

No external dependencies are used — only Python standard library (`os`, `sys`, `argparse`, `pathlib`).
