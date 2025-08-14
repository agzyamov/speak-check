#!/bin/bash
set -e

echo "🚀 Starting CEFR Speaking Exam Simulator with Docker Compose..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed or not in PATH"
    echo "Please install Docker CLI and ensure Colima is running"
    exit 1
fi

# Check if Docker Compose is available
if ! /opt/homebrew/bin/docker compose version &> /dev/null; then
    echo "❌ Error: Docker Compose is not available"
    echo "Please install Docker Compose: brew install docker-compose"
    exit 1
fi

# Set Docker host for Colima
export DOCKER_HOST=unix:///Users/rustemagziamov/.colima/default/docker.sock

# Check if Colima is running
if ! /opt/homebrew/bin/docker info &> /dev/null; then
    echo "❌ Error: Docker daemon is not running"
    echo "Please start Colima: colima start"
    exit 1
fi

# Check if .env.docker exists
if [ ! -f ".env.docker" ]; then
    echo "⚠️  Warning: .env.docker file not found!"
    echo "Creating .env.docker template..."
    cat > .env.docker << EOF
# Docker Environment Configuration
# Fill in your actual values

# OpenAI API Key (required for STT and AI assessment)
OPENAI_API_KEY=your_openai_api_key_here

# MongoDB Configuration
MONGODB_URI=mongodb://mongo:27017
MONGODB_DB=speak_check

# GitHub Personal Access Token (for MCP features)
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_pat_here
EOF
    echo "📝 Created .env.docker template. Please edit it with your actual API keys."
    echo "Then run this script again."
    exit 1
fi

# Check if required environment variables are set
if grep -q "your_openai_api_key_here" .env.docker; then
    echo "❌ Error: Please update .env.docker with your actual API keys"
    echo "Edit .env.docker and replace placeholder values with your real keys"
    exit 1
fi

# Create necessary directories
mkdir -p data logs

echo "📦 Building and starting services..."
/opt/homebrew/bin/docker compose up --build -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are healthy
echo "🔍 Checking service health..."
if /opt/homebrew/bin/docker compose ps | grep -q "healthy"; then
    echo "✅ Services are healthy!"
else
    echo "⚠️  Some services may still be starting up..."
fi

echo ""
echo "🎉 CEFR Speaking Exam Simulator is running!"
echo ""
echo "📱 App URL: http://localhost:8501"
echo "🗄️  MongoDB: localhost:27017"
echo ""
echo "📋 Useful commands:"
echo "   View logs:     /opt/homebrew/bin/docker compose logs -f"
echo "   Stop services: /opt/homebrew/bin/docker compose down"
echo "   Restart:       /opt/homebrew/bin/docker compose restart"
echo "   Status:        /opt/homebrew/bin/docker compose ps"
echo ""
echo "🔧 To access MongoDB shell:"
echo "   /opt/homebrew/bin/docker compose exec mongo mongosh speak_check"
