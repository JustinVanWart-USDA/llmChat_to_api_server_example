#!/bin/bash
# Start the GovChat API Server

echo "============================================================"
echo "  GovChat API Server Launcher"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed"
    exit 1
fi

# Install dependencies if needed
echo "[*] Checking dependencies..."
pip3 list | grep -q "fastapi uvicorn requests"
if [ $? -ne 0 ]; then
    echo "[!] Installing dependencies from requirements.txt..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
fi

# Run the server
echo ""
echo "[*] Starting server..."
echo "[*] Server will be available at: http://127.0.0.1:8000"
echo "[*] API docs at: http://127.0.0.1:8000/docs"
echo ""
python3 run.py
