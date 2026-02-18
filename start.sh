#!/bin/bash
# Quick start script for WorkBot Agent

echo "🤖 WorkBot Agent - Quick Start"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if claude-internal is installed
if ! command -v claude-internal &> /dev/null; then
    echo "⚠️  Warning: claude-internal command not found in PATH"
    echo "   Make sure claude-internal is installed and accessible"
    echo ""
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt --quiet

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed"
else
    echo "⚠️  Warning: Some dependencies may not have installed correctly"
fi

# Run the agent
echo ""
echo "🚀 Starting WorkBot Agent..."
echo ""
python3 source/main.py
