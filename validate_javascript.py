"""
Validate JavaScript syntax in automated_signals_dashboard.html
Find unclosed functions or misplaced return statements
"""

with open('automated_signals_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_script = False
function_stack = []
brace_count = 0
errors = []

for i, line in enumerate(lines, 1):
    stripped = line.strip()
    
    # Track script tags
    if '<script' in line and not stripped.startswith('//'):
        in_script = True
        continue
    elif '</script>' in line:
        if brace_count != 0:
            errors.append(f"Line {i}: Unmatched braces at end of script block (count: {brace_count})")
        in_script = False
        function_stack = []
        brace_count = 0
        continue
    
    if not in_script:
        continue
    
    # Skip comments
    if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
        continue
    
    # Track function declarations
    if 'function ' in line or '=>' in line:
        if 'function ' in line:
            func_name = line.split('function ')[1].split('(')[0].strip() if 'function ' in line else 'anonymous'
            function_stack.append((func_name, i))
    
    # Count braces
    open_braces = line.count('{')
    close_braces = line.count('}')
    brace_count += open_braces - close_braces
    
    # Pop function stack when closing
    if close_braces > 0 and function_stack:
        for _ in range(close_braces):
            if function_stack and brace_count >= 0:
                function_stack.pop()
    
    # Check for return outside function
    if 'return' in stripped and not stripped.startswith('//'):
        if brace_count <= 0 and not function_stack:
            errors.append(f"Line {i}: Illegal return statement outside function: {stripped[:50]}")

print("JavaScript Validation Results:")
print("=" * 80)

if errors:
    print(f"\n❌ Found {len(errors)} error(s):\n")
    for error in errors:
        print(f"  {error}")
else:
    print("\n✅ No syntax errors found!")

print(f"\nFinal brace count: {brace_count}")
if function_stack:
    print(f"Unclosed functions: {[f[0] for f in function_stack]}")
