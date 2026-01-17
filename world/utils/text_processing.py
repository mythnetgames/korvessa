"""
Text processing utilities for room and description display.
"""

import codecs


def process_escape_sequences(text):
    """
    Process common escape sequences in admin-set descriptions.
    
    This is intended for admin-only room and door descriptions to allow
    multi-line descriptions using \\n escape sequences.
    
    Args:
        text (str): The text to process
        
    Returns:
        str: The text with escape sequences converted to actual characters
    """
    if not text:
        return text
    
    try:
        # Use codecs.decode to handle unicode_escape
        # This will convert \\n to actual newlines, \\t to tabs, etc.
        return codecs.decode(text, 'unicode_escape')
    except Exception:
        # If decode fails for any reason, return the original text
        return text
