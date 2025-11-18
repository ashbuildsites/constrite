#!/bin/bash

echo ""
echo "========================================"
echo " ConStrite - Construction Safety Monitor"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
if ! pip show streamlit > /dev/null 2>&1; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "WARNING: .env file not found!"
    echo "Please copy .env.example to .env and add your Gemini API key."
    echo ""
    exit 1
fi

# Start Streamlit
echo ""
echo "Starting ConStrite..."
echo "Access the application at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
streamlit run app.py
