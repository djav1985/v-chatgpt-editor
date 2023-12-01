#!/bin/bash

# Check if the virtual environment directory exists.
if [ ! -d "venv" ]; then
    # If it doesn't exist, set one up.
    echo "Setting up the Python virtual environment..."

    # Create the Python virtual environment.
    python3 -m venv venv

    # Activate the newly created virtual environment.
    source venv/bin/activate

    # Install the project's Python dependencies from the requirements file.
    echo "Installing dependencies from requirements.txt..."
    pip3 install -r requirements.txt
else
    # If it exists, just activate the existing virtual environment.
    echo "Everything is setup! Run source venv/bin/activate then python3 main.py --filename ./file.docx then to build python3 main.py --filename ./file.docx --build"
fi