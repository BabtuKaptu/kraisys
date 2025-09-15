#!/bin/bash
# Installation script for KRAI Desktop

echo "Installing KRAI Desktop dependencies..."

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python packages..."
pip install --upgrade pip
pip install PyQt6 sqlmodel psycopg2-binary python-dotenv pandas openpyxl

echo "Installation complete!"
echo ""
echo "To run the application:"
echo "  source venv/bin/activate"
echo "  python main.py"