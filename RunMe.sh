#!/bin/bash

echo "Checking if pip is installed..."

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "pip is not installed. Please install Python and ensure pip is installed."
    exit 1
fi

echo "pip is installed!"
echo "Installing packages..."

# Install packages from requirements.txt
pip install -r requirements.txt

# Delete this script
script_path="$0"
batch_path="RunMe.bat"

if [ -f "$script_path" ]; then
    rm -- "$script_path"
fi

if [ -f "$batch_path" ]; then
    rm -- "$batch_path"
fi
