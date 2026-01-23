# Project Structure Generator Agent

A simple agent that takes a project idea and generates a sensible file/folder structure with stub files.

## Features

- Detects project type from your description (web, API, CLI, ML, data, mobile, or general)
- Generates appropriate folder structure
- Creates stub files with basic placeholders
- Supports multiple project types

## Usage

### Interactive mode (prompts for input):
```bash
python3 project_generator.py
```

### Command-line mode:
```bash
python3 project_generator.py "web app for task management"
```

### Specify output directory:
```bash
python3 project_generator.py "REST API for user management" -o ~/my-new-project
```

## Supported Project Types

- **Web Frontend**: React/Vue/Angular apps
- **API Backend**: REST/GraphQL servers
- **CLI Tool**: Command-line applications
- **ML Project**: Machine learning projects
- **Data Project**: ETL/analytics pipelines
- **Mobile App**: React Native apps
- **General**: Generic project structure

## Examples

```bash
# Generate a web frontend project
python3 project_generator.py "web app for managing todos"

# Generate an API backend
python3 project_generator.py "REST API for blog management"

# Generate a CLI tool
python3 project_generator.py "command line tool for file conversion"

# Generate an ML project
python3 project_generator.py "machine learning model for sentiment analysis"
```

## Output

The agent will:
1. Analyze your project idea
2. Detect the appropriate project type
3. Create folders and files with sensible defaults
4. Add placeholder code and TODOs

All generated files contain basic boilerplate code and TODO comments to guide development.
