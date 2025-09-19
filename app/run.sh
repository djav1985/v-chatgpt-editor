#!/bin/bash

# Determine the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INPUT_DIR="$SCRIPT_DIR/input"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"
MAIN_SCRIPT="$SCRIPT_DIR/main.py"

# Function to list and choose a file from the input directory
choose_file() {
    echo "Available files in $INPUT_DIR directory:"
    if [ ! -d "$INPUT_DIR" ]; then
        echo "Input directory not found: $INPUT_DIR"
        exit 1
    fi

    shopt -s nullglob
    local files=("$INPUT_DIR"/*)
    shopt -u nullglob

    if [ ${#files[@]} -eq 0 ]; then
        echo "No files found in $INPUT_DIR"
        exit 1
    fi

    for i in "${!files[@]}"; do
        echo "$((i+1)): ${files[i]##*/}"
    done

    echo "Select a file by number:"
    read -r file_number
    selected_file="${files[$((file_number-1))]}"
    echo "You selected: $selected_file"
}

# Function to choose the number of sections
choose_sections() {
    echo "Choose the number of sections:"
    echo "1: 256"
    echo "2: 512"
    echo "3: 1024"
    echo "4: 2048"  # New option for 2048 sections
    read -r sections_choice

    case $sections_choice in
        1) sections="256" ;;
        2) sections="512" ;;
        3) sections="1024" ;;
        4) sections="2048" ;;  # Handling the new option
        *) echo "Invalid selection. Defaulting to 256."
           sections="256" ;;
    esac
    echo "Sections set to: $sections"
}

# Function to execute Python script with provided arguments
run_python_script() {
    local filename="$1"
    local sections="$2"
    local language="$3"
    local action="$4"

    case $action in
        1) # Edit
            python3 "$MAIN_SCRIPT" edit "$filename" "$sections"
        ;;
        2) # Translate
            python3 "$MAIN_SCRIPT" translate "$filename" "$language" "$sections"
        ;;
        *)
            echo "Invalid action selected."
        ;;
    esac
}

# Main menu for actions
echo "Choose an action:"
echo "1: Edit"
echo "2: Translate"
read -r action

# Directory for the virtual environment
VENV_DIR="$SCRIPT_DIR/venv"

# Check and activate virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Setting up the Python virtual environment..."
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    pip3 install -r "$REQUIREMENTS_FILE"
else
    echo "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
fi

# Process based on selected action
case $action in
    1|2)
        choose_file
        filename=$(basename "$selected_file")
        # For edit and translate, choose sections
        if [[ $action == 1 || $action == 2 ]]; then
            choose_sections
        fi
        # For translate, also choose language
        if [[ $action == 2 ]]; then
            echo "Enter the language for translation:"
            read -r language
        fi
        # Execute the Python script with the selected options
        run_python_script "$INPUT_DIR/$filename" "$sections" "$language" "$action"
    ;;
    *)
        echo "Invalid action selected."
    ;;
esac

# Deactivate virtual environment
deactivate
