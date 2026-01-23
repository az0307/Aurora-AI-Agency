#!/bin/bash

echo "🏙️  Orchestra Town - Multi-Agent Orchestration System"
echo "======================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Start the server
echo ""
echo "Starting Orchestra Town API Server..."
echo "Dashboard will be available at: http://localhost:5000/dashboard"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Add dashboard route to serve the HTML
cd /root/gastown/orchestra

python3 << 'EOF'
import sys
sys.path.append('/root/gastown/orchestra')

from flask import Flask, send_from_directory
from api.server import app

@app.route('/dashboard')
def dashboard():
    return send_from_directory('/root/gastown/orchestra/dashboard', 'index.html')

if __name__ == '__main__':
    print("🏙️  Orchestra Town is now running!")
    print("=" * 50)
    print("API:       http://localhost:5000/api")
    print("Dashboard: http://localhost:5000/dashboard")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False)
EOF
