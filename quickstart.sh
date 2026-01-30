#!/bin/bash
# Quick start script for Academic Radar

set -e

echo "🎯 Academic Radar - Quick Start"
echo "================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys!"
    echo "   Required: OPENAI_API_KEY (or ANTHROPIC_API_KEY)"
    echo "   Required: OPENALEX_EMAIL"
    echo "   Required: SMTP_USER, SMTP_PASS, RECIPIENT_EMAIL"
    echo ""
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
echo "📁 Setting up directories..."
mkdir -p data/user_papers
mkdir -p cache
mkdir -p data/papers

# Run setup check
echo ""
echo "🔍 Running configuration check..."
python setup.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Add your research papers to data/user_papers/"
echo "  2. Run: python main.py --mode profile"
echo "  3. Run: python main.py --mode search"
echo ""
