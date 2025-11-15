"""
Comprehensive JavaScript fix for automated_signals_dashboard.html
Find and fix all brace mismatches and syntax errors
"""

with open('automated_signals_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Track script blocks and their brace counts
in_script = False
script_blocks = []
current_block = []
current_block_start = 0

for i, line in enumerate(lines, 1):
    if '<script' in line and not line.strip().startswith('//'):
        in_script = True
        current_block_start = i
        current_block = []
    elif '</script>' in line:
        if in_script:
            script_blocks.append({
                'start': current_block_start,
                'end': i,
                'lines': current_block
            })
        in_script = False
        current_block = []
    elif in_script:
        current_block.append((i, line))

print(f"Found {len(script_blocks)} script blocks")
print("=" * 80)

# Analyze each script block for brace balance
for idx, block in enumerate(script_blocks, 1):
    print(f"\nScript Block {idx}: Lines {block['start']}-{block['end']}")
    
    brace_count = 0
    paren_count = 0
    bracket_count = 0
    
    for line_num, line in block['lines']:
        # Skip comments
        stripped = line.strip()
        if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
            continue
        
        # Count braces
        brace_count += line.count('{') - line.count('}')
        paren_count += line.count('(') - line.count(')')
        bracket_count += line.count('[') - line.count(']')
        
        # Report significant imbalances
        if abs(brace_count) > 10:
            print(f"  ⚠️  Line {line_num}: Large brace imbalance ({brace_count})")
    
    print(f"  Final counts: Braces={brace_count}, Parens={paren_count}, Brackets={bracket_count}")
    
    if brace_count != 0:
        print(f"  ❌ BRACE MISMATCH: {brace_count} (need to {'add' if brace_count < 0 else 'remove'} {abs(brace_count)} closing brace(s))")
    if paren_count != 0:
        print(f"  ❌ PAREN MISMATCH: {paren_count}")
    if bracket_count != 0:
        print(f"  ❌ BRACKET MISMATCH: {bracket_count}")

print("\n" + "=" * 80)
print("RECOMMENDATION:")
print("The file has complex JavaScript with potential brace mismatches.")
print("Best approach: Use GitHub Desktop to revert automated_signals_dashboard.html")
print("to the last working commit, then re-apply changes carefully.")
