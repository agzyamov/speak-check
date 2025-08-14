#!/bin/bash
set -e

echo "🐳 Building Docker image for CEFR Speaking Exam Simulator..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed or not in PATH"
    echo "Please install Docker CLI and ensure Colima is running"
    exit 1
fi

# Check if Colima is running
if ! docker info &> /dev/null; then
    echo "❌ Error: Docker daemon is not running"
    echo "Please start Colima: colima start"
    exit 1
fi

# Build the image
echo "📦 Building image..."
docker build -t speak-check:latest .

echo "✅ Build complete!"
echo ""
echo "🚀 To run the app:"
echo "   ./scripts/run-docker.sh"
echo ""
echo "🔧 Or manually:"
echo "   docker run -p 8501:8501 --env-file .env.docker speak-check:latest"
echo ""
echo "📊 To view image details:"
echo "   docker images speak-check"
