import re
import os

file_path = os.path.join('..', 'tradingview-indicator', 'CascadeProjects', 'windsurf-project', 'macro-new.pine')

try:
    # Read the file
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Define the pattern to match
    pattern = r'array\.push\(macros, MacroData\.new\([^)]+, false, array\.new<float>\(\), array\.new<float>\(\), array\.new<line>\(\), array\.new<line>\(\)\)\)'
    
    # Define the replacement
    replacement = lambda match: match.group(0).replace('array.new<line>())', 'array.new<line>(), false, array.new<float>(), array.new<float>(), array.new<line>(), array.new<line>())')
    
    # Replace all occurrences
    updated_content = re.sub(pattern, replacement, content)
    
    # Write the updated content back to the file
    with open(file_path, 'w') as file:
        file.write(updated_content)
    
    print("File updated successfully!")
    
except FileNotFoundError:
    print(f"Error: File not found at {file_path}")
except IOError as e:
    print(f"Error reading/writing file: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")