#!/bin/bash

# Directory for the virtual environment
VENV_DIR="venv"

# Check and activate virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Setting up the Python virtual environment..."
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    pip3 install -r requirements.txt

    # Create necessary directories
    mkdir -p output input tmp
else
    echo "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
fi

# Main menu for actions
echo "Choose an action:"
echo "1: Edit"
echo "2: Translate"
echo "3: Build"
read -r action

# Function to list and choose a file from the ./input directory
choose_file() {
    echo "Available files in ./input directory:"
    local files=(./input/*)
    for i in "${!files[@]}"; do
        echo "$((i + 1)): ${files[i]##*/}"
    done

    echo "Select a file by number:"
    read -r file_number
    selected_file="${files[$((file_number - 1))]}"
    echo "You selected: $selected_file"
}

# Function to choose the number of sections
choose_sections() {
    echo "Choose the number of sections:"
    echo "1: 256"
    echo "2: 512"
    echo "3: 1024"
    read -r sections_choice

    case $sections_choice in
    1) sections="256" ;;
    2) sections="512" ;;
    3) sections="1024" ;;
    *)
        echo "Invalid selection. Defaulting to 256."
        sections="256"
        ;;
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
        python3 main.py edit "$filename" "$sections"
        ;;
    2) # Translate
        python3 main.py translate "$filename" "$language" "$sections"
        ;;
    3) # Build
        python3 main.py build "$filename"
        ;;
    *)
        echo "Invalid action selected."
        ;;
    esac
}

# Process based on selected action
case $action in
1 | 2)
    choose_file
    filename=$(basename "$selected_file")
    choose_sections
    if [[ $action == 2 ]]; then
        echo "Enter the language for translation:"
        read -r language
    fi
    run_python_script "./input/$filename" "$sections" "$language" "$action"
    ;;
3)
    choose_file
    filename=$(basename "$selected_file")
    run_python_script "./input/$filename" "" "" "$action"
    ;;
*)
    echo "Invalid action selected."
    ;;
esac

# Deactivate virtual environment
deactivate
