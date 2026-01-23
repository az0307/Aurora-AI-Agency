#!/bin/bash

echo "🏙️  Orchestra Town - Enhanced Multi-Agent Orchestration"
echo "=========================================================="
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

# Start the enhanced server
echo ""
echo "Starting Orchestra Town Enhanced Server..."
echo ""
echo "🎯 Features Enabled:"
echo "  ✅ Enhanced Mayor with Teams"
echo "  ✅ Advisor Team (4 specialists)"
echo "  ✅ Utility Team (4 tools)"
echo "  ✅ Prompting Team (4 strategies)"
echo "  ✅ Kanban Dashboard"
echo "  ✅ Natural Language Chat"
echo "  ✅ Mayor Thinking Visibility"
echo "  ✅ Claude Code Integration"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run the enhanced server
cd /home/user/Aurora-AI-Agency/gastown/orchestra
python3 api/enhanced_server.py
