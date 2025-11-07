"""
Validate PineScript syntax for common compilation errors
"""

def check_pinescript_file(filename):
    """Check for common PineScript syntax errors"""
    
    with open(filename, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    errors = []
    warnings = []
    
    # Check 1: Variable declaration issues
    for i, line in enumerate(lines, 1):
        # Check for := used without var
        if ':=' in line and 'var ' not in line and '//' not in line[:line.find(':=')]:
            # Check if this is inside an if block (which is allowed)
            indent = len(line) - len(line.lstrip())
            if indent == 0:
                errors.append(f"Line {i}: Using := without 'var' at global scope: {line.strip()}")
    
    # Check 2: Variable scope issues
    var_declarations = {}
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('var '):
            var_name = line.split()[1].split('=')[0].strip()
            var_declarations[var_name] = i
    
    # Check 3: String concatenation
    for i, line in enumerate(lines, 1):
        if '+' in line and '"' in line and '//' not in line[:line.find('+')]:
            # Check if mixing types
            if 'str.tostring' not in line:
                parts = line.split('+')
                has_string = any('"' in part for part in parts)
                has_number = any(part.strip().replace('.', '').replace('-', '').isdigit() for part in parts if '"' not in part)
                if has_string and has_number:
                    warnings.append(f"Line {i}: Possible type mismatch in concatenation: {line.strip()}")
    
    # Check 4: Array/loop bounds
    for i, line in enumerate(lines, 1):
        if 'for ' in line and ' to ' in line:
            # Extract loop bounds
            if 'bar_index' in line:
                warnings.append(f"Line {i}: Loop uses bar_index - verify bounds: {line.strip()}")
    
    # Check 5: Historical reference issues
    for i, line in enumerate(lines, 1):
        if '[' in line and ']' in line and '//' not in line[:line.find('[')]:
            # Check for negative indices without proper bounds checking
            if '[-' in line:
                errors.append(f"Line {i}: Negative array index (not allowed in PineScript): {line.strip()}")
    
    print(f"\n{'='*60}")
    print(f"PineScript Syntax Validation: {filename}")
    print(f"{'='*60}\n")
    
    if errors:
        print(f"❌ ERRORS FOUND ({len(errors)}):")
        for error in errors:
            print(f"  {error}")
    else:
        print("✅ No critical errors found")
    
    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"  {warning}")
    else:
        print("\n✅ No warnings")
    
    print(f"\n{'='*60}\n")
    
    return len(errors) == 0

if __name__ == "__main__":
    result = check_pinescript_file("debug_stop_loss_calc.pine")
    if result:
        print("✅ File should compile successfully")
    else:
        print("❌ File has syntax errors that need fixing")
