import re

# Read the file
with open('c:\\Users\\Will\\CascadeProjects\\tradingview-indicator\\CascadeProjects\\windsurf-project\\macro-new.pine', 'r') as file:
    content = file.read()

# Define the pattern to match
pattern = r'array\.push\(macros, MacroData\.new\([^)]+, false, array\.new<float>\(\), array\.new<float>\(\), array\.new<line>\(\), array\.new<line>\(\)\)\)'

# Define the replacement
replacement = lambda match: match.group(0).replace('array.new<line>())', 'array.new<line>(), false, array.new<float>(), array.new<float>(), array.new<line>(), array.new<line>())')

# Replace all occurrences
updated_content = re.sub(pattern, replacement, content)

# Write the updated content back to the file
with open('c:\\Users\\Will\\CascadeProjects\\tradingview-indicator\\CascadeProjects\\windsurf-project\\macro-new.pine', 'w') as file:
    file.write(updated_content)

print("File updated successfully!")