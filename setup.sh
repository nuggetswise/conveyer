#!/bin/bash

echo "🔐 Setting up Security Intake Assistant"
echo "======================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed. Please install pip first."
    exit 1
fi

echo "✅ Python and pip found"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp env_template.txt .env
    echo "✅ .env file created. Please edit it to add your Google API key if needed."
fi

# Create sample PDF if it doesn't exist
if [ ! -f "sample_security_policy.pdf" ]; then
    echo "📄 Creating sample PDF..."
    python create_sample_pdf.py
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To run the application:"
echo "1. Activate virtual environment: source .venv/bin/activate"
echo "2. Run the app: streamlit run app.py"
echo "3. Open browser to: http://localhost:8502"
echo ""
echo "Optional: Add your Google Gemini API key to .env for enhanced features" 