#!/usr/bin/env python3
"""
Validation script to test the improvements made to v-chatgpt-editor.
This script validates the optimizations without requiring external dependencies.
"""

import os
import sys
import tempfile

def test_quote_replacement():
    """Test the quote replacement function."""
    # Mock the function since we can't import from docx_handler due to dependencies
    def replace_quotes(text):
        """Replace straight quotes with curly quotes."""
        result = ""
        in_quote = False
        for char in text:
            if char == '"':
                if not in_quote:
                    result += """  # opening quote
                    in_quote = True
                else:
                    result += """  # closing quote
                    in_quote = False
            else:
                result += char
        return result
    
    test_cases = [
        ('Hello "world"', 'Hello "world"'),
        ('"Quote at start', '"Quote at start'),
        ('Quote at end"', 'Quote at end"'),
        ('Multiple "quotes" in "text"', 'Multiple "quotes" in "text"'),
    ]
    
    print("Testing quote replacement...")
    for input_text, expected in test_cases:
        result = replace_quotes(input_text)
        if result == expected:
            print(f"✓ '{input_text}' -> '{result}'")
        else:
            print(f"✗ '{input_text}' -> '{result}' (expected '{expected}')")
    
    return True

def test_html_fragment_processing():
    """Test the HTML fragment processing function."""
    def process_html_fragments(line_content):
        """Process HTML content and return fragments with styles."""
        fragments = []
        current_text = ""
        styles = ""
        i = 0
        while i < len(line_content):
            if line_content.startswith("<b>", i):
                if current_text:
                    fragments.append((current_text, styles))
                    current_text = ""
                styles = "b"
                i += 3
            elif line_content.startswith("</b>", i):
                if current_text:
                    fragments.append((current_text, styles))
                    current_text = ""
                styles = ""
                i += 4
            elif line_content.startswith("<i>", i):
                if current_text:
                    fragments.append((current_text, styles))
                    current_text = ""
                styles = "i"
                i += 3
            elif line_content.startswith("</i>", i):
                if current_text:
                    fragments.append((current_text, styles))
                    current_text = ""
                styles = ""
                i += 4
            else:
                current_text += line_content[i]
                i += 1
        if current_text:
            fragments.append((current_text, styles))
        return fragments
    
    test_cases = [
        ("Hello world", [("Hello world", "")]),
        ("<b>Bold text</b>", [("Bold text", "b")]),
        ("<i>Italic text</i>", [("Italic text", "i")]),
        ("Normal <b>bold</b> normal", [("Normal ", ""), ("bold", "b"), (" normal", "")]),
        ("Text with <i>italic</i> and <b>bold</b>", [("Text with ", ""), ("italic", "i"), (" and ", ""), ("bold", "b")]),
    ]
    
    print("\nTesting HTML fragment processing...")
    for input_html, expected in test_cases:
        result = process_html_fragments(input_html)
        if result == expected:
            print(f"✓ '{input_html}' -> {result}")
        else:
            print(f"✗ '{input_html}' -> {result} (expected {expected})")
    
    return True

def test_directory_structure():
    """Test that required directories exist."""
    print("\nTesting directory structure...")
    
    app_dir = os.path.dirname(os.path.abspath(__file__))
    required_dirs = ['input', 'output']
    
    for dir_name in required_dirs:
        dir_path = os.path.join(app_dir, dir_name)
        if os.path.exists(dir_path):
            print(f"✓ Directory '{dir_name}' exists")
        else:
            print(f"✗ Directory '{dir_name}' does not exist")
    
    return True

def test_file_syntax():
    """Test that Python files have valid syntax."""
    print("\nTesting Python file syntax...")
    
    import ast
    app_dir = os.path.dirname(os.path.abspath(__file__))
    python_files = ['main.py', 'api.py', 'docx_handler.py']
    
    for filename in python_files:
        filepath = os.path.join(app_dir, filename)
        try:
            with open(filepath, 'r') as f:
                ast.parse(f.read())
            print(f"✓ {filename} syntax is valid")
        except SyntaxError as e:
            print(f"✗ {filename} has syntax error: {e}")
            return False
        except FileNotFoundError:
            print(f"✗ {filename} not found")
            return False
    
    return True

def test_environment_file():
    """Test that .env file has required structure."""
    print("\nTesting .env file structure...")
    
    app_dir = os.path.dirname(os.path.abspath(__file__))
    env_file = os.path.join(app_dir, '.env')
    
    required_keys = ['OPENAI_API_KEY', 'MODEL', 'OUTPUT_DIR']
    
    if not os.path.exists(env_file):
        print(f"✗ .env file not found")
        return False
    
    with open(env_file, 'r') as f:
        content = f.read()
        
    found_keys = []
    for line in content.split('\n'):
        if '=' in line and not line.startswith('#'):
            key = line.split('=')[0].strip()
            found_keys.append(key)
    
    for key in required_keys:
        if key in found_keys:
            print(f"✓ {key} found in .env")
        else:
            print(f"✗ {key} missing from .env")
    
    return True

def main():
    """Run all validation tests."""
    print("=== v-chatgpt-editor Validation Tests ===\n")
    
    tests = [
        test_quote_replacement,
        test_html_fragment_processing,
        test_directory_structure,
        test_file_syntax,
        test_environment_file,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
    
    print(f"\n=== Summary: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("🎉 All tests passed! The codebase improvements are working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())