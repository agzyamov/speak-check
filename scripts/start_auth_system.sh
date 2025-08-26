#!/bin/bash
# Startup script for CEFR Speaking Exam Simulator with Authentication

echo "🚀 Starting CEFR Speaking Exam Simulator with Authentication..."
echo "📍 Working directory: $(pwd)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python -m venv venv"
    echo "Then: source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing/updating dependencies..."
pip install -r requirements.txt

# Check if MongoDB is running
echo "🔍 Checking MongoDB connection..."
python -c "
import sys
try:
    from db_mongo.client import db
    db.admin.command('ping')
    print('✅ MongoDB connection successful')
except Exception as e:
    print(f'❌ MongoDB connection failed: {e}')
    print('Please ensure MongoDB is running on the configured URI')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    exit 1
fi

# Create database indexes
echo "🏗️ Creating database indexes..."
python -c "
from db_mongo.crud import create_database_indexes
try:
    create_database_indexes()
    print('✅ Database indexes created successfully')
except Exception as e:
    print(f'⚠️ Warning: Could not create indexes: {e}')
"

# Set environment variables
export JWT_SECRET=${JWT_SECRET:-$(python -c "import secrets; print(secrets.token_urlsafe(32))")}
export API_HOST=${API_HOST:-127.0.0.1}
export API_PORT=${API_PORT:-8000}
export STREAMLIT_PORT=${STREAMLIT_PORT:-8501}

echo ""
echo "🔐 JWT Secret: ${JWT_SECRET:0:10}... (truncated)"
echo "🌐 API will start on: http://${API_HOST}:${API_PORT}"
echo "🌐 Streamlit will start on: http://localhost:${STREAMLIT_PORT}"
echo ""

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null
        echo "🔌 API server stopped"
    fi
    if [ ! -z "$STREAMLIT_PID" ]; then
        kill $STREAMLIT_PID 2>/dev/null
        echo "🔌 Streamlit server stopped"
    fi
    echo "👋 Goodbye!"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start API server in background
echo "🚀 Starting authentication API server..."
python -m uvicorn api.main:app --host $API_HOST --port $API_PORT --reload &
API_PID=$!

# Wait a moment for API to start
sleep 3

# Check if API is running
if ! curl -s http://${API_HOST}:${API_PORT}/health > /dev/null; then
    echo "❌ Failed to start API server"
    cleanup
fi

echo "✅ Authentication API server started (PID: $API_PID)"
echo "📚 API documentation available at: http://${API_HOST}:${API_PORT}/docs"

# Start Streamlit app in background
echo "🚀 Starting Streamlit application..."
python -m streamlit run app.py --server.port $STREAMLIT_PORT --server.headless false &
STREAMLIT_PID=$!

# Wait a moment for Streamlit to start
sleep 3

echo "✅ Streamlit application started (PID: $STREAMLIT_PID)"
echo ""
echo "🎉 System started successfully!"
echo ""
echo "📊 Services Status:"
echo "   🔗 Authentication API: http://${API_HOST}:${API_PORT}"
echo "   🔗 API Documentation: http://${API_HOST}:${API_PORT}/docs"
echo "   🔗 Streamlit App: http://localhost:${STREAMLIT_PORT}"
echo ""
echo "✨ Features available:"
echo "   • User registration and authentication"
echo "   • JWT token-based security"
echo "   • Rate limiting and input validation"
echo "   • Premium Edge TTS (8 high-quality voices)"
echo "   • Voice recording (up to 2 minutes)"
echo "   • CEFR levels A2-C1"
echo "   • Real-time audio controls"
echo "   • User session management"
echo ""
echo "⏹️  Press Ctrl+C to stop all services"
echo ""

# Wait for both processes
wait