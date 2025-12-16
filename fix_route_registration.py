#!/usr/bin/env python3
"""
Fix route registration by moving indicator export routes inside register function.
"""

def fix_routes():
    with open('automated_signals_api_robust.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find where register function ends (first module-level def after it)
    register_start = None
    register_end = None
    
    for i, line in enumerate(lines):
        if 'def register_automated_signals_api_robust(app, db):' in line:
            register_start = i
        elif register_start and line.startswith('def _'):
            register_end = i
            break
    
    print(f"Register function: lines {register_start} to {register_end}")
    
    # Find all indicator export routes (they start with "    @app.route('/api/indicator-export" or "/api/all-signals" or "/api/data-quality")
    indicator_routes_start = None
    indicator_routes_end = None
    
    for i in range(register_end, len(lines)):
        line = lines[i]
        if indicator_routes_start is None:
            if "    @app.route('/api/indicator-export" in line or \
               "    @app.route('/api/all-signals" in line or \
               "    @app.route('/api/data-quality/reconcile" in line:
                indicator_routes_start = i
        elif indicator_routes_start and i > indicator_routes_start:
            # Check if we've reached the end (no more routes or end of file)
            if line.startswith('def ') or i == len(lines) - 1:
                indicator_routes_end = i if i < len(lines) - 1 else i + 1
                break
    
    if not indicator_routes_start:
        print("No indicator routes found outside register function")
        return
    
    print(f"Indicator routes: lines {indicator_routes_start} to {indicator_routes_end}")
    
    # Extract the indicator routes
    indicator_routes = lines[indicator_routes_start:indicator_routes_end]
    
    # Remove them from their current location
    new_lines = lines[:indicator_routes_start] + lines[indicator_routes_end:]
    
    # Insert them before register_end (inside the register function)
    # Add a comment and call to helper
    insert_point = register_end
    
    helper_call = [
        '\n',
        '    # Register indicator export routes\n',
        '    register_indicator_export_routes(app)\n',
        '    logger.warning("[ROBUST_API_REGISTRATION] ✅ Indicator export routes registered")\n',
        '\n'
    ]
    
    new_lines = new_lines[:insert_point] + helper_call + new_lines[insert_point:]
    
    # Add the helper function at the end with the routes
    helper_header = [
        '\n',
        'def register_indicator_export_routes(app):\n',
        '    """\n',
        '    Register indicator-export ingestion/import/ledger/reconciliation routes.\n',
        '    Called from register_automated_signals_api_robust().\n',
        '    """\n',
    ]
    
    new_lines = new_lines + helper_header + indicator_routes
    
    # Write back
    with open('automated_signals_api_robust.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"✅ Fixed! Moved {len(indicator_routes)} lines of indicator routes into helper function")
    print(f"   Helper function added at end of file")
    print(f"   Helper called from line {insert_point}")

if __name__ == '__main__':
    fix_routes()
