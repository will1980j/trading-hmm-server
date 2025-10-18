"""
Script to fix the truncated ML insights endpoint in web_server.py
"""

# Read the file
with open('web_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find where to add the import
import_line = "from unified_ml_intelligence import get_unified_ml"
if import_line not in content:
    # Add import after other imports
    insert_pos = content.find("# Auto-train ML on startup")
    if insert_pos > 0:
        content = content[:insert_pos] + f"# Import ML insights helper\nfrom ml_insights_endpoint import get_ml_insights_response\n\n" + content[insert_pos:]

# Find and replace the truncated endpoint
old_endpoint_start = "@app.route('/api/ml-insights', methods=['GET'])\n@login_required\ndef get_ml_insights():\n    \"\"\"Get unified ML insights from all trading data\"\"\"\n    try:\n        if not ml_available:\n            return jsonify({\n                'performance': {\n                    'is_trained': False,\n                    'best_model': 'Dependencies Missing',"

new_endpoint = """@app.route('/api/ml-insights', methods=['GET'])
@login_required
def get_ml_insights():
    \"\"\"Get unified ML insights from all trading data\"\"\"
    return get_ml_insights_response(ml_available, db_enabled, db)"""

# Find the start of the truncated endpoint
start_pos = content.find("@app.route('/api/ml-insights'")
if start_pos > 0:
    # Find the next @app.route after this one
    next_route_pos = content.find("@app.route", start_pos + 50)
    if next_route_pos > 0:
        # Replace everything between
        content = content[:start_pos] + new_endpoint + "\n\n" + content[next_route_pos:]
        print("Fixed ML insights endpoint")
    else:
        print("Could not find next route")
else:
    print("Could not find ML insights endpoint")

# Write back
with open('web_server.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("web_server.py updated successfully")
