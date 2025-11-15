"""
Fix the syntax error in automated_signals_dashboard.html
- Function name mismatch: renderPriceChartJourney vs renderTradeJourney
- Check for any stray return statements
"""

with open('automated_signals_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Rename function call to match function definition
content = content.replace(
    'setTimeout(() => renderTradeJourney(trade), 100);',
    'setTimeout(() => renderPriceChartJourney(trade), 100);'
)

# Fix 2: Check if there are any return statements outside functions
# This shouldn't happen, but let's be safe
lines = content.split('\n')
fixed_lines = []
in_script = False
in_function = 0

for i, line in enumerate(lines, 1):
    # Track if we're in a script tag
    if '<script' in line:
        in_script = True
    elif '</script>' in line:
        in_script = False
        in_function = 0
    
    # Track function depth
    if in_script:
        if 'function ' in line or '=>' in line:
            in_function += line.count('{')
        in_function += line.count('{') - line.count('}')
    
    # Check for illegal return
    if in_script and 'return' in line and in_function <= 0:
        # This is a return outside a function - comment it out
        print(f"⚠️  Found potential illegal return at line {i}: {line.strip()}")
        if not line.strip().startswith('//'):
            line = '// ' + line  # Comment it out
    
    fixed_lines.append(line)

content = '\n'.join(fixed_lines)

with open('automated_signals_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed syntax errors in automated_signals_dashboard.html")
print("\nChanges made:")
print("1. Fixed function name mismatch: renderTradeJourney → renderPriceChartJourney")
print("2. Checked for illegal return statements")
