#!/bin/bash

# Streamoid Backend Startup Script

echo "🚀 Starting Streamoid Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp env.example .env
    echo "📝 Please edit .env file with your configuration"
fi

# Create database if it doesn't exist
if [ ! -f "products.db" ]; then
    echo "🗄️  Database will be created on first run"
fi

# Start the application
echo "🌟 Starting FastAPI application..."
echo "📖 API Documentation available at: http://localhost:8000/docs"
echo "🔍 Alternative docs at: http://localhost:8000/redoc"
echo "❤️  Health check at: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

