#!/usr/bin/env python3
"""
Project Structure Generator Agent
Takes a project idea and generates a sensible file/folder structure with AI-powered working code.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class ProjectGenerator:
    """Agent that generates project structures based on project ideas with AI-powered code generation."""

    def __init__(self, project_idea, output_dir=".", use_ai=True):
        self.project_idea = project_idea.lower()
        self.project_idea_original = project_idea
        self.output_dir = Path(output_dir)
        self.project_type = self._detect_project_type()
        self.use_ai = use_ai and ANTHROPIC_AVAILABLE

        # Initialize Claude API if available
        self.client = None
        if self.use_ai:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.client = Anthropic(api_key=api_key)
                print("🤖 AI-powered code generation enabled")
            else:
                print("⚠️  ANTHROPIC_API_KEY not found, using template-based generation")
                self.use_ai = False

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

    def _generate_with_ai(self, file_type: str, file_purpose: str, context: str = "") -> Optional[str]:
        """
        Generate code content using Claude API.

        Args:
            file_type: Type of file (e.g., "python", "javascript", "react_component")
            file_purpose: What this file is supposed to do
            context: Additional context about the project

        Returns:
            Generated code or None if AI is not available
        """
        if not self.client:
            return None

        prompt = f"""Generate complete, working code for a {file_type} file.

Project Context: {self.project_idea_original}
Project Type: {self.project_type}
File Purpose: {file_purpose}
{f"Additional Context: {context}" if context else ""}

Requirements:
1. Generate COMPLETE, FUNCTIONAL code - NO TODOs or placeholders
2. Include proper error handling and validation
3. Follow best practices and modern standards
4. Add helpful comments only where logic is complex
5. Make it production-ready and immediately runnable
6. Include all necessary imports
7. Use realistic implementations, not stubs

Return ONLY the code, no explanations or markdown formatting."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract the generated code
            code = response.content[0].text.strip()

            # Remove markdown code blocks if present
            if code.startswith("```"):
                lines = code.split("\n")
                code = "\n".join(lines[1:-1]) if len(lines) > 2 else code

            return code

        except Exception as e:
            print(f"⚠️  AI generation failed for {file_purpose}: {str(e)}")
            return None

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

    # Helper methods
    def _get_test_command(self):
        """Get the appropriate test command based on project type."""
        if self.project_type in ["web_frontend", "api_backend"]:
            return "```bash\nnpm test\n```"
        else:
            return "```bash\npython -m pytest tests/\n```"

    # File content generators
    def _stub_readme(self):
        if self.use_ai:
            code = self._generate_with_ai(
                "markdown",
                "README.md file",
                f"Project: {self.project_idea_original}, Type: {self.project_type}. Include description, installation, usage, and examples."
            )
            if code:
                return code

        # Generate context-aware README based on project type
        project_name = self.project_idea_original.title()

        installation_steps = ""
        usage_examples = ""

        if self.project_type == "web_frontend":
            installation_steps = """```bash
npm install
npm start
```

The application will open at `http://localhost:3000`"""
            usage_examples = """```javascript
// Main component is in src/components/App.jsx
import App from './components/App';
```"""

        elif self.project_type == "api_backend":
            installation_steps = """```bash
npm install

# Create .env file
cp .env.example .env

# Start the server
npm start
```

The API will be available at `http://localhost:3000`"""
            usage_examples = """```bash
# Health check
curl http://localhost:3000/health

# API endpoints
curl http://localhost:3000/api
```"""

        elif self.project_type == "cli_tool":
            installation_steps = """```bash
pip install -r requirements.txt

# Install as package (optional)
pip install -e .
```"""
            usage_examples = """```bash
# Run the CLI
python src/main.py help
python src/main.py init
python src/main.py run --verbose
```"""

        else:
            installation_steps = "```bash\npip install -r requirements.txt\n```"
            usage_examples = "See source code for usage examples"

        return f"""# {project_name}

## Description

{self.project_idea_original}

This project was generated with AI-powered scaffolding to provide a complete, working starting point.

## Installation

{installation_steps}

## Usage

{usage_examples}

## Project Structure

- `src/` - Main source code
- `tests/` - Test files
- `README.md` - This file

## Development

### Running Tests

{self._get_test_command()}

### Adding Features

1. Create new files in appropriate directories
2. Import and use in your main application
3. Add tests for new functionality

## License

MIT License - feel free to use this project as you wish!
"""

    def _stub_react_component(self, name="App"):
        if self.use_ai and name == "App":
            code = self._generate_with_ai(
                "react_component",
                f"Main React component for {name}",
                f"Web application for: {self.project_idea_original}. Include state management and example functionality."
            )
            if code:
                return code

        if name == "App":
            return f"""import React, {{ useState, useEffect }} from 'react';

const {name} = () => {{
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {{
    // Example: Fetch data on component mount
    const fetchData = async () => {{
      setLoading(true);
      try {{
        // Replace with your actual API endpoint
        const response = await fetch('/api/data');
        if (!response.ok) throw new Error('Failed to fetch');
        const result = await response.json();
        setData(result.data || []);
      }} catch (err) {{
        setError(err.message);
      }} finally {{
        setLoading(false);
      }}
    }};

    // Uncomment to enable data fetching
    // fetchData();
  }}, []);

  const handleAction = (item) => {{
    console.log('Action triggered for:', item);
    // Add your action logic here
  }};

  return (
    <div className="{name.lower()}-container">
      <header className="{name.lower()}-header">
        <h1>Welcome to {name}</h1>
        <p>Your application is ready to build!</p>
      </header>

      <main className="{name.lower()}-main">
        {{loading && <div className="loading">Loading...</div>}}
        {{error && <div className="error">Error: {{error}}</div>}}

        {{!loading && !error && (
          <div className="content">
            {{data.length > 0 ? (
              <ul className="data-list">
                {{data.map((item, index) => (
                  <li key={{index}} onClick={{() => handleAction(item)}}>
                    {{item.name || item.title || JSON.stringify(item)}}
                  </li>
                ))}}
              </ul>
            ) : (
              <p>No data available</p>
            )}}
          </div>
        )}}
      </main>

      <footer className="{name.lower()}-footer">
        <p>Built with React</p>
      </footer>
    </div>
  );
}};

export default {name};
"""
        else:
            return f"""import React from 'react';

const {name} = ({{ children, ...props }}) => {{
  return (
    <div className="{name.lower()}" {{...props}}>
      <h2>{name}</h2>
      {{children}}
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
        if self.use_ai:
            code = self._generate_with_ai(
                "javascript",
                "Utility helper functions for a web application",
                "Include common utilities like date formatting, debouncing, validation, etc."
            )
            if code:
                return code

        return """// Utility helper functions

/**
 * Format a date object into a readable string
 */
export const formatDate = (date) => {
  if (!(date instanceof Date)) {
    date = new Date(date);
  }

  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return date.toLocaleDateString('en-US', options);
};

/**
 * Debounce function to limit how often a function is called
 */
export const debounce = (func, wait = 300) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

/**
 * Validate email address format
 */
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Generate a unique ID
 */
export const generateId = () => {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
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
        if self.use_ai:
            code = self._generate_with_ai(
                "json",
                "package.json with appropriate dependencies",
                f"Project type: {self.project_type}, Project: {self.project_idea_original}"
            )
            if code:
                return code

        # Context-aware dependencies based on project type
        if self.project_type == "api_backend":
            return """{
  "name": "api-project",
  "version": "1.0.0",
  "description": "RESTful API server",
  "main": "src/app.js",
  "scripts": {
    "start": "node src/app.js",
    "dev": "nodemon src/app.js",
    "test": "jest --coverage"
  },
  "keywords": ["api", "rest", "server"],
  "author": "",
  "license": "MIT",
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "dotenv": "^16.0.3"
  },
  "devDependencies": {
    "nodemon": "^2.0.22",
    "jest": "^29.5.0",
    "supertest": "^6.3.3"
  }
}
"""
        elif self.project_type == "web_frontend":
            return """{
  "name": "web-app",
  "version": "1.0.0",
  "description": "React web application",
  "main": "src/index.js",
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "keywords": ["react", "web", "app"],
  "author": "",
  "license": "MIT",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "devDependencies": {
    "@testing-library/react": "^13.4.0",
    "@testing-library/jest-dom": "^5.16.5",
    "@testing-library/user-event": "^14.4.3"
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  }
}
"""
        else:
            return """{
  "name": "project",
  "version": "1.0.0",
  "description": "Node.js project",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "test": "jest"
  },
  "keywords": [],
  "author": "",
  "license": "MIT",
  "dependencies": {
    "dotenv": "^16.0.3"
  },
  "devDependencies": {
    "jest": "^29.5.0"
  }
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
        if self.use_ai and name != "index":
            code = self._generate_with_ai(
                "javascript",
                f"Express router for {name} with RESTful routes",
                "Include GET, POST, PUT, DELETE routes with proper controller integration"
            )
            if code:
                return code

        if name == "users":
            return f"""const express = require('express');
const router = express.Router();

// Import controller if available
let controller;
try {{
  controller = require('../controllers/userController');
}} catch (err) {{
  console.log('Controller not loaded yet');
}}

// GET all users
router.get('/', controller?.getAll || ((req, res) => {{
  res.json({{ data: [] }});
}}));

// GET user by ID
router.get('/:id', controller?.getById || ((req, res) => {{
  res.json({{ data: {{ id: req.params.id }} }});
}}));

// CREATE new user
router.post('/', controller?.create || ((req, res) => {{
  res.status(201).json({{ data: req.body }});
}}));

// UPDATE user
router.put('/:id', controller?.update || ((req, res) => {{
  res.json({{ data: {{ id: req.params.id, ...req.body }} }});
}}));

// DELETE user
router.delete('/:id', controller?.delete || ((req, res) => {{
  res.json({{ data: {{ id: req.params.id, deleted: true }} }});
}}));

module.exports = router;
"""
        else:
            return f"""const express = require('express');
const router = express.Router();

// Index route
router.get('/', (req, res) => {{
  res.json({{
    message: 'API Index',
    version: '1.0.0',
    endpoints: {{
      users: '/api/users'
    }}
  }});
}});

module.exports = router;
"""

    def _stub_controller(self):
        if self.use_ai:
            code = self._generate_with_ai(
                "javascript",
                "RESTful API controller with CRUD operations",
                "Include getAll, getById, create, update, delete methods with proper error handling"
            )
            if code:
                return code

        return """// Controller logic

// In-memory storage (replace with database in production)
let dataStore = [];
let nextId = 1;

exports.getAll = async (req, res) => {
  try {
    const { limit = 100, offset = 0 } = req.query;
    const results = dataStore.slice(offset, offset + parseInt(limit));

    res.json({
      data: results,
      total: dataStore.length,
      limit: parseInt(limit),
      offset: parseInt(offset)
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

exports.getById = async (req, res) => {
  try {
    const { id } = req.params;
    const item = dataStore.find(item => item.id === parseInt(id));

    if (!item) {
      return res.status(404).json({ error: 'Item not found' });
    }

    res.json({ data: item });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

exports.create = async (req, res) => {
  try {
    const newItem = {
      id: nextId++,
      ...req.body,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    dataStore.push(newItem);
    res.status(201).json({ data: newItem });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

exports.update = async (req, res) => {
  try {
    const { id } = req.params;
    const index = dataStore.findIndex(item => item.id === parseInt(id));

    if (index === -1) {
      return res.status(404).json({ error: 'Item not found' });
    }

    dataStore[index] = {
      ...dataStore[index],
      ...req.body,
      id: parseInt(id),
      updatedAt: new Date().toISOString()
    };

    res.json({ data: dataStore[index] });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

exports.delete = async (req, res) => {
  try {
    const { id } = req.params;
    const index = dataStore.findIndex(item => item.id === parseInt(id));

    if (index === -1) {
      return res.status(404).json({ error: 'Item not found' });
    }

    const deleted = dataStore.splice(index, 1)[0];
    res.json({ data: deleted });
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
        if self.use_ai:
            code = self._generate_with_ai(
                "javascript",
                "Express.js API server with routes, middleware, and error handling",
                f"API for: {self.project_idea_original}"
            )
            if code:
                return code

        return """const express = require('express');
const app = express();

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// CORS middleware
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  if (req.method === 'OPTIONS') {
    return res.sendStatus(200);
  }
  next();
});

// Request logging middleware
app.use((req, res, next) => {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] ${req.method} ${req.path}`);
  next();
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// API routes
try {
  const indexRouter = require('./routes/index');
  const usersRouter = require('./routes/users');

  app.use('/api', indexRouter);
  app.use('/api/users', usersRouter);
} catch (err) {
  console.log('Routes not yet loaded:', err.message);
}

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'API Server',
    version: '1.0.0',
    endpoints: {
      health: '/health',
      api: '/api'
    }
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Endpoint not found' });
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(err.status || 500).json({
    error: err.message || 'Internal server error'
  });
});

// Start server
const PORT = process.env.PORT || 3000;
const server = app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
  console.log(`📡 Health check: http://localhost:${PORT}/health`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully...');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
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
        if self.use_ai:
            code = self._generate_with_ai(
                "python",
                "Utility helper functions for a CLI application",
                "Include functions for formatting output, validating input, file operations, etc."
            )
            if code:
                return code

        return """\"\"\"Utility helper functions\"\"\"

import os
import json
from typing import Any, Dict, List


def format_output(data: Any, format_type: str = 'pretty') -> str:
    \"\"\"Format output data for display\"\"\"
    if format_type == 'json':
        return json.dumps(data, indent=2)
    elif format_type == 'pretty':
        if isinstance(data, (dict, list)):
            return json.dumps(data, indent=2)
        return str(data)
    return str(data)


def validate_input(data: str, input_type: str = 'text') -> bool:
    \"\"\"Validate input data based on type\"\"\"
    if not data or not isinstance(data, str):
        return False

    if input_type == 'email':
        return '@' in data and '.' in data.split('@')[-1]
    elif input_type == 'number':
        try:
            float(data)
            return True
        except ValueError:
            return False
    elif input_type == 'path':
        return os.path.isabs(data) or os.path.exists(data)

    return len(data.strip()) > 0


def read_config(config_path: str) -> Dict:
    \"\"\"Read configuration from JSON file\"\"\"
    if not os.path.exists(config_path):
        return {}

    with open(config_path, 'r') as f:
        return json.load(f)


def write_config(config_path: str, config: Dict) -> None:
    \"\"\"Write configuration to JSON file\"\"\"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
"""

    def _stub_py_main(self):
        if self.use_ai:
            code = self._generate_with_ai(
                "python",
                "Main entry point for a CLI application with argument parsing and command execution",
                f"CLI tool for: {self.project_idea_original}"
            )
            if code:
                return code

        return """#!/usr/bin/env python3
\"\"\"Main entry point for the application\"\"\"

import argparse
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from utils.helpers import format_output, validate_input
except ImportError:
    # Fallback if helpers aren't available yet
    def format_output(data, format_type='pretty'):
        return str(data)
    def validate_input(data, input_type='text'):
        return bool(data)


def main():
    \"\"\"Main function\"\"\"
    parser = argparse.ArgumentParser(
        description=f'CLI tool for {Path.cwd().name}',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'command',
        nargs='?',
        default='help',
        help='Command to execute (help, init, run, status)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '-f', '--format',
        choices=['pretty', 'json'],
        default='pretty',
        help='Output format'
    )

    args = parser.parse_args()

    # Command dispatcher
    commands = {
        'help': cmd_help,
        'init': cmd_init,
        'run': cmd_run,
        'status': cmd_status
    }

    if args.command not in commands:
        print(f"Error: Unknown command '{args.command}'")
        print(f"Available commands: {', '.join(commands.keys())}")
        sys.exit(1)

    try:
        result = commands[args.command](args)
        if result:
            print(format_output(result, args.format))
    except KeyboardInterrupt:
        print("\\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            raise
        sys.exit(1)


def cmd_help(args):
    \"\"\"Display help information\"\"\"
    return {
        'available_commands': {
            'help': 'Show this help message',
            'init': 'Initialize the application',
            'run': 'Run the application',
            'status': 'Show current status'
        }
    }


def cmd_init(args):
    \"\"\"Initialize the application\"\"\"
    if args.verbose:
        print("Initializing application...")

    # Perform initialization steps
    return {'status': 'initialized', 'message': 'Application initialized successfully'}


def cmd_run(args):
    \"\"\"Run the application\"\"\"
    if args.verbose:
        print("Running application...")

    # Execute main application logic
    return {'status': 'running', 'message': 'Application is running'}


def cmd_status(args):
    \"\"\"Show current status\"\"\"
    return {
        'status': 'ready',
        'version': '1.0.0',
        'config': 'default'
    }


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
        if self.use_ai:
            code = self._generate_with_ai(
                "text",
                "requirements.txt with appropriate Python dependencies",
                f"Project type: {self.project_type}, Project: {self.project_idea_original}"
            )
            if code:
                return code

        # Context-aware dependencies based on project type
        if self.project_type == "cli_tool":
            return """# Python CLI tool dependencies
click>=8.1.0
colorama>=0.4.6
requests>=2.31.0
pyyaml>=6.0
"""
        elif self.project_type == "data_project":
            return """# Data project dependencies
pandas>=2.0.0
numpy>=1.24.0
sqlalchemy>=2.0.0
python-dotenv>=1.0.0
"""
        else:
            return """# Python dependencies
requests>=2.31.0
python-dotenv>=1.0.0
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
