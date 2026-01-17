"""
Test script to verify escape sequence processing in room descriptions.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from world.utils import process_escape_sequences


def test_escape_sequences():
    """Test that escape sequences are properly processed."""
    
    # Test 1: Single newline
    input_text = "Line 1\\nLine 2"
    result = process_escape_sequences(input_text)
    expected = "Line 1\nLine 2"
    assert result == expected, f"Expected {repr(expected)}, got {repr(result)}"
    print(f"✓ Test 1 passed: Single newline")
    
    # Test 2: Multiple newlines
    input_text = "Line 1\\nLine 2\\nLine 3"
    result = process_escape_sequences(input_text)
    expected = "Line 1\nLine 2\nLine 3"
    assert result == expected, f"Expected {repr(expected)}, got {repr(result)}"
    print(f"✓ Test 2 passed: Multiple newlines")
    
    # Test 3: Tab character
    input_text = "Text\\twith\\ttabs"
    result = process_escape_sequences(input_text)
    expected = "Text\twith\ttabs"
    assert result == expected, f"Expected {repr(expected)}, got {repr(result)}"
    print(f"✓ Test 3 passed: Tab characters")
    
    # Test 4: Empty string
    input_text = ""
    result = process_escape_sequences(input_text)
    expected = ""
    assert result == expected, f"Expected {repr(expected)}, got {repr(result)}"
    print(f"✓ Test 4 passed: Empty string")
    
    # Test 5: None input
    input_text = None
    result = process_escape_sequences(input_text)
    expected = None
    assert result == expected, f"Expected {repr(expected)}, got {repr(result)}"
    print(f"✓ Test 5 passed: None input")
    
    # Test 6: Mixed content with newlines
    input_text = "A door stands before you.\\nIt is heavily reinforced with iron bands."
    result = process_escape_sequences(input_text)
    expected = "A door stands before you.\nIt is heavily reinforced with iron bands."
    assert result == expected, f"Expected {repr(expected)}, got {repr(result)}"
    print(f"✓ Test 6 passed: Mixed content with newlines")
    
    print("\nAll tests passed!")


if __name__ == "__main__":
    test_escape_sequences()
