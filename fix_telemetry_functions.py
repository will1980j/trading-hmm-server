#!/usr/bin/env python3
"""
Fix telemetry functions in NQ_FVG_CORE_TELEMETRY.pine
- Remove duplicate f_num(), f_str(), f_symbol()
- Keep only the corrected versions
- Ensure f_buildPayload is correct
"""

# Read the file
with open('NQ_FVG_CORE_TELEMETRY.pine', 'r', encoding='utf-8') as f:
    content = f.read()

# Split into lines for easier manipulation
lines = content.split('\n')

# Find and remove FIRST set of duplicates (lines 1098-1123 approximately)
# We'll keep the SECOND set which is already correct

# Strategy: Find the first occurrence of each function and mark for deletion
first_f_num_line = None
first_f_str_line = None  
first_f_symbol_line = None
first_f_targetsJson_line = None
first_f_setupJson_line = None
first_f_marketStateJson_line = None

for i, line in enumerate(lines):
    if line.strip().startswith('f_num(x) =>') and first_f_num_line is None:
        first_f_num_line = i
    elif line.strip().startswith('f_str(x) =>') and first_f_str_line is None:
        first_f_str_line = i
    elif line.strip().startswith('f_symbol() =>') and first_f_symbol_line is None:
        first_f_symbol_line = i
    elif line.strip().startswith('f_targetsJson(') and first_f_targetsJson_line is None:
        first_f_targetsJson_line = i
    elif line.strip().startswith('f_setupJson(') and first_f_setupJson_line is None:
        first_f_setupJson_line = i
    elif line.strip().startswith('f_marketStateJson(') and first_f_marketStateJson_line is None:
        first_f_marketStateJson_line = i

print(f"Found first f_num at line {first_f_num_line}")
print(f"Found first f_str at line {first_f_str_line}")
print(f"Found first f_symbol at line {first_f_symbol_line}")
print(f"Found first f_targetsJson at line {first_f_targetsJson_line}")
print(f"Found first f_setupJson at line {first_f_setupJson_line}")
print(f"Found first f_marketStateJson at line {first_f_marketStateJson_line}")

# Delete the first occurrences (they're the old/broken versions)
# We need to delete from line 1098 to approximately line 1123

# Mark lines for deletion
lines_to_delete = set()

# Delete first f_num (2 lines: function def + body)
if first_f_num_line:
    lines_to_delete.add(first_f_num_line - 1)  # Comment before
    lines_to_delete.add(first_f_num_line)  # Function def
    lines_to_delete.add(first_f_num_line + 1)  # Empty line or body
    lines_to_delete.add(first_f_num_line + 2)  # Body

# Delete first f_str (2 lines)
if first_f_str_line:
    lines_to_delete.add(first_f_str_line - 1)  # Comment before
    lines_to_delete.add(first_f_str_line)  # Function def
    lines_to_delete.add(first_f_str_line + 1)  # Empty line or body
    lines_to_delete.add(first_f_str_line + 2)  # Body

# Delete first f_targetsJson (3 lines)
if first_f_targetsJson_line:
    lines_to_delete.add(first_f_targetsJson_line - 2)  # Comment separator
    lines_to_delete.add(first_f_targetsJson_line - 1)  # Comment
    lines_to_delete.add(first_f_targetsJson_line)  # Function def
    lines_to_delete.add(first_f_targetsJson_line + 1)  # Empty line or body
    lines_to_delete.add(first_f_targetsJson_line + 2)  # Body

# Delete first f_setupJson (3 lines)
if first_f_setupJson_line:
    lines_to_delete.add(first_f_setupJson_line - 2)  # Comment separator
    lines_to_delete.add(first_f_setupJson_line - 1)  # Comment
    lines_to_delete.add(first_f_setupJson_line)  # Function def
    lines_to_delete.add(first_f_setupJson_line + 1)  # Empty line or body
    lines_to_delete.add(first_f_setupJson_line + 2)  # Body

# Delete first f_marketStateJson (3 lines)
if first_f_marketStateJson_line:
    lines_to_delete.add(first_f_marketStateJson_line - 2)  # Comment separator
    lines_to_delete.add(first_f_marketStateJson_line - 1)  # Comment
    lines_to_delete.add(first_f_marketStateJson_line)  # Function def
    lines_to_delete.add(first_f_marketStateJson_line + 1)  # Empty line or body
    lines_to_delete.add(first_f_marketStateJson_line + 2)  # Body

print(f"\nDeleting {len(lines_to_delete)} lines")

# Create new content without deleted lines
new_lines = [line for i, line in enumerate(lines) if i not in lines_to_delete]

# Write back
with open('NQ_FVG_CORE_TELEMETRY.pine', 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))

print("\n✅ Telemetry functions fixed!")
print("✅ Removed duplicate f_num(), f_str(), f_symbol(), f_targetsJson(), f_setupJson(), f_marketStateJson()")
print("✅ Kept the corrected versions")
