#!/usr/bin/env python
"""Fix em dashes and curly quotes in combat message files."""
import os
import glob

path = r'c:\Users\russe\OneDrive\Documents\kowloon\world\combat\messages'

for filepath in glob.glob(os.path.join(path, '*.py')):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace em dashes with regular dashes
    new_content = content.replace('\u2014', '-')  # em dash
    new_content = new_content.replace('\u2013', '-')  # en dash
    # Replace curly quotes with straight quotes
    new_content = new_content.replace('\u2018', "'")  # left single quote
    new_content = new_content.replace('\u2019', "'")  # right single quote
    new_content = new_content.replace('\u201c', '"')  # left double quote
    new_content = new_content.replace('\u201d', '"')  # right double quote
    
    if content != new_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Fixed: {os.path.basename(filepath)}')

print('Done!')
