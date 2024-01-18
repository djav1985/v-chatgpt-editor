#!/bin/bash

# Function to execute Python script with provided arguments
run_python_script() {
    local filename="$1"
    local action="$2"
    local language="$3"

    case $action in
        1) # Edit
            python3 main.py --filename "$filename" --edit
        ;;
        2) # Translate
            python3 main.py --filename "$filename" --translate "$language"
        ;;
        3) # Build
            python3 main.py --filename "$filename" --build
        ;;
        4) # Split for Edit
            python3 main.py --split edit
        ;;
        5) # Split for Translate
            python3 main.py --split translate
        ;;
        *)
            echo "Invalid action selected."
        ;;
    esac
}

# Directory for the virtual environment
VENV_DIR="venv"

# Check if the virtual environment directory exists.
if [ ! -d "$VENV_DIR" ]; then
    # If it doesn't exist, set one up and install dependencies.
    echo "Setting up the Python virtual environment..."
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    pip3 install -r requirements.txt
else
    # If it exists, activate the existing virtual environment.
    echo "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
fi

# Prompt user for action
echo "Choose an action:"
echo "1: Edit single file"
echo "2: Translate single file"
echo "3: Build single file"
echo "4: Split files in input directory for Edit"
echo "5: Split files in input directory for Translate"
read action

# Handle actions for single file operations
if [ "$action" == "1" ] || [ "$action" == "2" ] || [ "$action" == "3" ]; then
    echo "Enter the path to your DOCX file:"
    read docx_file

    # Check if file exists
    if [ ! -f "$docx_file" ]; then
        echo "Error: The file $docx_file does not exist."
        exit 1
    fi

    # Handle translation
    if [ "$action" == "2" ]; then
        echo "Enter the language for translation:"
        read language
    fi

    # Run Python script for single file operation
    run_python_script "$docx_file" "$action" "$language"
else
    # Run Python script for splitting files in the input directory
    run_python_script "" "$action" ""
fi

# Deactivate virtual environment
deactivate
