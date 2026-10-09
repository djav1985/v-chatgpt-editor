#!/bin/bash
set -e

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Function to list and choose a file from the ./input directory
choose_file() {
    echo "Available files in ./input directory:"
    local files=(./input/*.docx)
    if [ ! -e "${files[0]}" ]; then
        echo "No .docx files found in ./input."
        exit 1
    fi
    local i=1
    for f in "${files[@]}"; do
        echo "$i: $(basename "$f")"
        i=$((i + 1))
    done
    echo "Enter the number of the file to process:"
    read -r file_choice
    if ! [[ "$file_choice" =~ ^[0-9]+$ ]] || [ "$file_choice" -lt 1 ] || [ "$file_choice" -gt "${#files[@]}" ]; then
        echo "Invalid selection."
        exit 1
    fi
    selected_file="${files[$((file_choice - 1))]}"
}

choose_token_budget() {
    echo "Choose the maximum token budget per section (serialized manuscript text)."
    echo "A paragraph longer than the budget will stay intact and may exceed it."
    echo "1: 256"
    echo "2: 512"
    echo "3: 1024"
    echo "4: 2048"  # New option for 2048 sections
    read -r budget_choice

    case $budget_choice in
        1) max_tokens="256" ;;
        2) max_tokens="512" ;;
        3) max_tokens="1024" ;;
        4) max_tokens="2048" ;;
        *) echo "Invalid selection. Defaulting to 256."
           max_tokens="256" ;;
    esac
    echo "Maximum token budget set to: $max_tokens"
}

# Function to execute Python script with provided arguments
run_python_script() {
    local filename="$1"
    local max_tokens="$2"
    local language="$3"
    local action="$4"

    case $action in
        1) # Edit
            "$VENV_DIR/bin/python" main.py edit "$filename" "$max_tokens"
        ;;
        2) # Translate
            "$VENV_DIR/bin/python" main.py translate "$filename" "$language" "$max_tokens"
        ;;
        *)
            echo "Invalid action selected."
        ;;
    esac
}

# Directory for the virtual environment
VENV_DIR="$SCRIPT_DIR/venv"

# Create the environment if it is missing or incomplete.
if [ ! -x "$VENV_DIR/bin/python" ]; then
    echo "Creating the Python virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

echo "Installing Python dependencies..."
"$VENV_DIR/bin/python" -m pip install -r "$SCRIPT_DIR/requirements.txt"
source "$VENV_DIR/bin/activate"

# Main menu for actions
echo "Choose an action:"
echo "1: Edit"
echo "2: Translate"
read -r action

# Process based on selected action
case $action in
    1|2)
        choose_file
        filename=$(basename "$selected_file")
        # For edit and translate, choose sections
        if [[ $action == 1 || $action == 2 ]]; then
            choose_token_budget
        fi
        # For translate, also choose language
        if [[ $action == 2 ]]; then
            echo "Enter the language for translation:"
            read -r language
        fi
        # Execute the Python script with the selected options
        run_python_script "./input/$filename" "$max_tokens" "$language" "$action"
    ;;
    *)
        echo "Invalid action selected."
    ;;
esac

# Deactivate virtual environment
deactivate
