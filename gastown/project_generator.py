#!/usr/bin/env python3
"""
Project Structure Generator Agent
Takes a project idea and generates a sensible file/folder structure with stub files.
"""

import os
import sys
import argparse
from pathlib import Path


class ProjectGenerator:
    """Agent that generates project structures based on project ideas."""

    def __init__(self, project_idea, output_dir="."):
        self.project_idea = project_idea.lower()
        self.output_dir = Path(output_dir)
        self.project_type = self._detect_project_type()

    def _detect_project_type(self):
        """Analyze the project idea and determine the type."""
        idea = self.project_idea

        if any(word in idea for word in ["web", "website", "frontend", "react", "vue", "angular"]):
            return "web_frontend"
        elif any(word in idea for word in ["api", "backend", "server", "rest", "graphql"]):
            return "api_backend"
        elif any(word in idea for word in ["cli", "command", "tool", "script"]):
            return "cli_tool"
        elif any(word in idea for word in ["ml", "machine learning", "ai", "model", "neural"]):
            return "ml_project"
        elif any(word in idea for word in ["data", "analytics", "pipeline", "etl"]):
            return "data_project"
        elif any(word in idea for word in ["mobile", "app", "ios", "android"]):
            return "mobile_app"
        else:
            return "general"

    def generate_structure(self):
        """Generate the project structure based on detected type."""
        print(f"\n🎯 Project Idea: {self.project_idea}")
        print(f"📦 Detected Type: {self.project_type}")
        print(f"📁 Output Directory: {self.output_dir.absolute()}\n")

        structure = self._get_structure_template()
        self._create_structure(structure)

        print("\n✅ Project structure generated successfully!")
        print(f"\nCreated files and folders in: {self.output_dir.absolute()}")

    def _get_structure_template(self):
        """Return the appropriate structure template based on project type."""
        templates = {
            "web_frontend": {
                "src/": {
                    "components/": {
                        "App.jsx": self._stub_react_component(),
                        "Header.jsx": self._stub_react_component("Header"),
                    },
                    "styles/": {
                        "main.css": self._stub_css(),
                    },
                    "utils/": {
                        "helpers.js": self._stub_helpers(),
                    },
                    "index.js": self._stub_index_js(),
                },
                "public/": {
                    "index.html": self._stub_html(),
                },
                "tests/": {
                    "App.test.js": self._stub_test(),
                },
                "package.json": self._stub_package_json(),
                "README.md": self._stub_readme(),
                ".gitignore": self._stub_gitignore_node(),
            },
            "api_backend": {
                "src/": {
                    "routes/": {
                        "index.js": self._stub_route(),
                        "users.js": self._stub_route("users"),
                    },
                    "controllers/": {
                        "userController.js": self._stub_controller(),
                    },
                    "models/": {
                        "User.js": self._stub_model(),
                    },
                    "middleware/": {
                        "auth.js": self._stub_middleware(),
                    },
                    "config/": {
                        "database.js": self._stub_db_config(),
                    },
                    "app.js": self._stub_app_js(),
                },
                "tests/": {
                    "api.test.js": self._stub_test(),
                },
                ".env.example": self._stub_env(),
                "package.json": self._stub_package_json(),
                "README.md": self._stub_readme(),
                ".gitignore": self._stub_gitignore_node(),
            },
            "cli_tool": {
                "src/": {
                    "commands/": {
                        "init.py": self._stub_py_command(),
                    },
                    "utils/": {
                        "helpers.py": self._stub_py_helpers(),
                    },
                    "main.py": self._stub_py_main(),
                },
                "tests/": {
                    "test_main.py": self._stub_py_test(),
                },
                "requirements.txt": self._stub_requirements(),
                "README.md": self._stub_readme(),
                "setup.py": self._stub_setup_py(),
                ".gitignore": self._stub_gitignore_python(),
            },
            "ml_project": {
                "data/": {
                    "raw/": {
                        ".gitkeep": "",
                    },
                    "processed/": {
                        ".gitkeep": "",
                    },
                },
                "notebooks/": {
                    "exploration.ipynb": self._stub_notebook(),
                },
                "src/": {
                    "models/": {
                        "model.py": self._stub_ml_model(),
                    },
                    "preprocessing/": {
                        "preprocess.py": self._stub_preprocess(),
                    },
                    "train.py": self._stub_train(),
                },
                "tests/": {
                    "test_model.py": self._stub_py_test(),
                },
                "requirements.txt": self._stub_requirements_ml(),
                "README.md": self._stub_readme(),
                ".gitignore": self._stub_gitignore_python(),
            },
            "data_project": {
                "data/": {
                    "raw/": {".gitkeep": ""},
                    "processed/": {".gitkeep": ""},
                },
                "src/": {
                    "pipeline/": {
                        "extract.py": self._stub_extract(),
                        "transform.py": self._stub_transform(),
                        "load.py": self._stub_load(),
                    },
                    "config/": {
                        "config.yaml": self._stub_yaml_config(),
                    },
                },
                "sql/": {
                    "schema.sql": self._stub_sql_schema(),
                },
                "requirements.txt": self._stub_requirements(),
                "README.md": self._stub_readme(),
                ".gitignore": self._stub_gitignore_python(),
            },
            "mobile_app": {
                "src/": {
                    "screens/": {
                        "HomeScreen.js": self._stub_react_native_screen(),
                    },
                    "components/": {
                        "Button.js": self._stub_react_component("Button"),
                    },
                    "navigation/": {
                        "AppNavigator.js": self._stub_navigation(),
                    },
                    "styles/": {
                        "theme.js": self._stub_theme(),
                    },
                },
                "assets/": {
                    "images/": {".gitkeep": ""},
                },
                "package.json": self._stub_package_json(),
                "README.md": self._stub_readme(),
                ".gitignore": self._stub_gitignore_node(),
            },
            "general": {
                "src/": {
                    "main.py": self._stub_general_main(),
                },
                "tests/": {
                    "test_main.py": self._stub_py_test(),
                },
                "docs/": {
                    "design.md": self._stub_design_doc(),
                },
                "README.md": self._stub_readme(),
                ".gitignore": self._stub_gitignore_general(),
            },
        }

        return templates.get(self.project_type, templates["general"])

    def _create_structure(self, structure, current_path=None):
        """Recursively create the directory structure and files."""
        if current_path is None:
            current_path = self.output_dir

        current_path.mkdir(parents=True, exist_ok=True)

        for name, content in structure.items():
            path = current_path / name

            if isinstance(content, dict):
                # It's a directory
                print(f"📁 Creating directory: {path.relative_to(self.output_dir)}/")
                path.mkdir(parents=True, exist_ok=True)
                self._create_structure(content, path)
            else:
                # It's a file
                print(f"📄 Creating file: {path.relative_to(self.output_dir)}")
                path.write_text(content)

    # Stub file content generators
    def _stub_readme(self):
        return f"""# {self.project_idea.title()}

## Description
TODO: Add project description

## Installation
TODO: Add installation instructions

## Usage
TODO: Add usage examples

## Project Structure
TODO: Describe the project structure

## Contributing
TODO: Add contribution guidelines

## License
TODO: Add license information
"""

    def _stub_react_component(self, name="App"):
        return f"""import React from 'react';

const {name} = () => {{
  return (
    <div className="{name.lower()}">
      <h1>{name} Component</h1>
      {{/* TODO: Add component logic */}}
    </div>
  );
}};

export default {name};
"""

    def _stub_css(self):
        return """/* Main Stylesheet */

:root {
  --primary-color: #007bff;
  --secondary-color: #6c757d;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* TODO: Add more styles */
"""

    def _stub_helpers(self):
        return """// Utility helper functions

/**
 * Format a date into a human-readable string.
 * @param {Date|string|number} date - The date to format
 * @param {Object} [options] - Intl.DateTimeFormat options
 * @returns {string} The formatted date string
 */
export const formatDate = (date, options = { year: 'numeric', month: 'short', day: 'numeric' }) => {
  const d = new Date(date);
  if (isNaN(d.getTime())) {
    return 'Invalid Date';
  }
  return d.toLocaleDateString(undefined, options);
};

/**
 * Create a debounced version of a function that delays invocation
 * until after `wait` milliseconds have elapsed since the last call.
 * @param {Function} func - The function to debounce
 * @param {number} wait - The debounce delay in milliseconds
 * @returns {Function} The debounced function
 */
export const debounce = (func, wait) => {
  let timeout;
  return function (...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
};
"""

    def _stub_index_js(self):
        return """import React from 'react';
import ReactDOM from 'react-dom';
import App from './components/App';
import './styles/main.css';

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);
"""

    def _stub_html(self):
        return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Project</title>
</head>
<body>
  <div id="root"></div>
  <!-- TODO: Add additional HTML elements -->
</body>
</html>
"""

    def _stub_test(self):
        return """// Test suite

describe('Test Suite', () => {
  test('should pass', () => {
    // TODO: Add test implementation
    expect(true).toBe(true);
  });
});
"""

    def _stub_package_json(self):
        return """{
  "name": "project",
  "version": "1.0.0",
  "description": "TODO: Add description",
  "main": "index.js",
  "scripts": {
    "test": "jest",
    "start": "node src/index.js"
  },
  "keywords": [],
  "author": "",
  "license": "MIT",
  "dependencies": {},
  "devDependencies": {}
}
"""

    def _stub_gitignore_node(self):
        return """node_modules/
dist/
build/
.env
.DS_Store
*.log
coverage/
.vscode/
"""

    def _stub_route(self, name="index"):
        return f"""const express = require('express');
const router = express.Router();

// TODO: Define routes for {name}

router.get('/', (req, res) => {{
  res.json({{ message: '{name} route' }});
}});

module.exports = router;
"""

    def _stub_controller(self):
        return """// Controller logic

exports.getAll = async (req, res) => {
  try {
    // TODO: Implement get all logic
    res.json({ data: [] });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

exports.getById = async (req, res) => {
  try {
    // TODO: Implement get by ID logic
    res.json({ data: {} });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
"""

    def _stub_model(self):
        return """// Data model definition

const schema = {
  // TODO: Define schema
};

module.exports = schema;
"""

    def _stub_middleware(self):
        return """// Middleware functions

exports.authenticate = (req, res, next) => {
  // TODO: Implement authentication logic
  next();
};

exports.authorize = (req, res, next) => {
  // TODO: Implement authorization logic
  next();
};
"""

    def _stub_db_config(self):
        return """// Database configuration

module.exports = {
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'mydb',
  // TODO: Add more configuration
};
"""

    def _stub_app_js(self):
        return """const express = require('express');
const app = express();

app.use(express.json());

// TODO: Add routes and middleware

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

module.exports = app;
"""

    def _stub_env(self):
        return """# Environment variables
PORT=3000
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydb
# TODO: Add more environment variables
"""

    def _stub_py_command(self):
        return """\"\"\"Command implementation\"\"\"

def execute(args):
    \"\"\"
    TODO: Implement command logic
    \"\"\"
    print("Command executed")
    pass
"""

    def _stub_py_helpers(self):
        return """\"\"\"Utility helper functions\"\"\"

def format_output(data):
    \"\"\"TODO: Format output data\"\"\"
    return str(data)

def validate_input(data):
    \"\"\"TODO: Validate input data\"\"\"
    return True
"""

    def _stub_py_main(self):
        return """#!/usr/bin/env python3
\"\"\"Main entry point for the application\"\"\"

import argparse

def main():
    \"\"\"Main function\"\"\"
    parser = argparse.ArgumentParser(description='TODO: Add description')
    parser.add_argument('command', help='Command to execute')
    args = parser.parse_args()

    # TODO: Implement main logic
    print(f"Executing: {args.command}")

if __name__ == '__main__':
    main()
"""

    def _stub_py_test(self):
        return """\"\"\"Test suite\"\"\"

import unittest

class TestMain(unittest.TestCase):
    def test_placeholder(self):
        \"\"\"TODO: Add test implementation\"\"\"
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
"""

    def _stub_requirements(self):
        return """# Python dependencies
# TODO: Add project dependencies
"""

    def _stub_setup_py(self):
        return """from setuptools import setup, find_packages

setup(
    name='project',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        # TODO: Add dependencies
    ],
    entry_points={
        'console_scripts': [
            'project=src.main:main',
        ],
    },
)
"""

    def _stub_gitignore_python(self):
        return """__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.env
.venv
*.egg-info/
dist/
build/
.pytest_cache/
.coverage
htmlcov/
.DS_Store
"""

    def _stub_notebook(self):
        return """{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Exploration Notebook\\n",
    "TODO: Add exploration and analysis"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\\n",
    "import numpy as np\\n",
    "\\n",
    "# TODO: Add analysis code"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
"""

    def _stub_ml_model(self):
        return """\"\"\"Machine learning model definition\"\"\"

class Model:
    def __init__(self):
        # TODO: Initialize model
        pass

    def train(self, X, y):
        \"\"\"TODO: Implement training logic\"\"\"
        pass

    def predict(self, X):
        \"\"\"TODO: Implement prediction logic\"\"\"
        return []
"""

    def _stub_preprocess(self):
        return """\"\"\"Data preprocessing functions\"\"\"

def clean_data(data):
    \"\"\"TODO: Implement data cleaning\"\"\"
    return data

def normalize(data):
    \"\"\"TODO: Implement normalization\"\"\"
    return data
"""

    def _stub_train(self):
        return """#!/usr/bin/env python3
\"\"\"Training script\"\"\"

def train_model():
    \"\"\"TODO: Implement model training\"\"\"
    print("Training model...")
    pass

if __name__ == '__main__':
    train_model()
"""

    def _stub_requirements_ml(self):
        return """# Machine Learning dependencies
numpy
pandas
scikit-learn
# TODO: Add more dependencies
"""

    def _stub_extract(self):
        return """\"\"\"Data extraction module\"\"\"

def extract_data(source):
    \"\"\"TODO: Implement data extraction\"\"\"
    return []
"""

    def _stub_transform(self):
        return """\"\"\"Data transformation module\"\"\"

def transform_data(data):
    \"\"\"TODO: Implement data transformation\"\"\"
    return data
"""

    def _stub_load(self):
        return """\"\"\"Data loading module\"\"\"

def load_data(data, destination):
    \"\"\"TODO: Implement data loading\"\"\"
    pass
"""

    def _stub_yaml_config(self):
        return """# Configuration
database:
  host: localhost
  port: 5432
  name: mydb

# TODO: Add more configuration
"""

    def _stub_sql_schema(self):
        return """-- Database schema

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TODO: Add more tables
"""

    def _stub_react_native_screen(self):
        return """import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const HomeScreen = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Home Screen</Text>
      {/* TODO: Add screen content */}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
  },
});

export default HomeScreen;
"""

    def _stub_navigation(self):
        return """import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';

const Stack = createStackNavigator();

const AppNavigator = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        {/* TODO: Add screens */}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigator;
"""

    def _stub_theme(self):
        return """export const theme = {
  colors: {
    primary: '#007AFF',
    secondary: '#5856D6',
    background: '#FFFFFF',
    text: '#000000',
  },
  // TODO: Add more theme properties
};
"""

    def _stub_general_main(self):
        return """#!/usr/bin/env python3
\"\"\"Main application file\"\"\"

def main():
    \"\"\"Main function\"\"\"
    print("Application started")
    # TODO: Implement application logic

if __name__ == '__main__':
    main()
"""

    def _stub_design_doc(self):
        return f"""# Design Document: {self.project_idea.title()}

## Overview
TODO: Describe the project overview

## Architecture
TODO: Describe the architecture

## Components
TODO: List and describe key components

## Data Flow
TODO: Describe data flow

## Implementation Plan
TODO: Add implementation steps
"""

    def _stub_gitignore_general(self):
        return """# General gitignore
*.log
.DS_Store
.env
tmp/
*.tmp
"""


def main():
    parser = argparse.ArgumentParser(
        description='Project Structure Generator - Creates project scaffolding from ideas'
    )
    parser.add_argument(
        'idea',
        nargs='?',
        help='Project idea (e.g., "web app for task management")'
    )
    parser.add_argument(
        '-o', '--output',
        default='./generated_project',
        help='Output directory (default: ./generated_project)'
    )

    args = parser.parse_args()

    # If no idea provided, prompt for it
    if not args.idea:
        print("Project Structure Generator")
        print("=" * 50)
        args.idea = input("Enter your project idea: ").strip()

        if not args.idea:
            print("Error: Project idea is required!")
            sys.exit(1)

    # Generate the project
    generator = ProjectGenerator(args.idea, args.output)
    generator.generate_structure()

    print(f"\n💡 Next steps:")
    print(f"   cd {args.output}")
    print(f"   # Start building your project!")


if __name__ == '__main__':
    main()
