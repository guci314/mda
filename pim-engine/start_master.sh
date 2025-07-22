#!/bin/bash

# Start PIM Engine Master Controller

echo "Starting PIM Engine Master Controller..."

# Create necessary directories
mkdir -p instances logs

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start the master controller
cd src && python main.py