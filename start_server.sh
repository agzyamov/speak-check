#!/bin/bash
# Quick start script for CEFR Speaking Exam Simulator
# This is the "Tremlett command" for starting the server

echo "🎤 Starting CEFR Speaking Exam Simulator..."
echo "📍 Working directory: $(pwd)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python -m venv venv"
    echo "Then: pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment and start server
echo "🔧 Activating virtual environment and starting server..."
./venv/bin/Activate.ps1 && python -m streamlit run app.py --server.port 8501 --server.headless true

echo ""
echo "🎉 Server started successfully!"
echo "🌐 Open your browser and navigate to: http://localhost:8501"
echo ""
echo "✨ Features available:"
echo "   • Premium Edge TTS (8 high-quality voices)"
echo "   • Voice recording (up to 2 minutes)"
echo "   • CEFR levels A2-C1"
echo "   • Real-time audio controls"
echo ""
echo "⏹️  Press Ctrl+C to stop the server"