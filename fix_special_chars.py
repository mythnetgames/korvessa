"""
Script to replace em dashes and curly quotes in combat message files.
"""
import os
import sys

combat_dir = r"c:\Users\russe\OneDrive\Documents\kowloon\world\combat"

replacements = {
    '—': ' - ',  # em dash to space-dash-space
    ''': "'",   # curly single quote (left)
    ''': "'",   # curly single quote (right)
    '"': '"',   # curly double quote (left)
    '"': '"',   # curly double quote (right)
}

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

if __name__ == "__main__":
    print(f"Starting scan of: {combat_dir}", flush=True)
    print(f"Directory exists: {os.path.exists(combat_dir)}", flush=True)
    
    count = 0
    files_scanned = 0
    for root, dirs, files in os.walk(combat_dir):
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                files_scanned += 1
                try:
                    if fix_file(filepath):
                        print(f"Fixed: {filepath}", flush=True)
                        count += 1
                except Exception as e:
                    print(f"Error with {filepath}: {e}", flush=True)

    print(f"\nScanned {files_scanned} files", flush=True)
    print(f"Total files updated: {count}", flush=True)
