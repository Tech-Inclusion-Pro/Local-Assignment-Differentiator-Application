#!/bin/bash
# UDL Differentiation Wizard - Run Script

# Change to script directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv

    echo "Installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo ""
    echo "⚠️  Warning: Ollama doesn't appear to be running."
    echo "   Start it with: ollama serve"
    echo "   And make sure you have a model: ollama pull llama3.2"
    echo ""
fi

# Run the application
python main.py
