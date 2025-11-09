"""
Deploy the dashboard HTML directly via Railway API endpoint
"""
import requests
import os

# Read the working HTML file
with open('templates/automated_signals_dashboard_option2.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

print(f"Read HTML file: {len(html_content)} bytes")

# Create a deployment endpoint that writes the file
deploy_code = f'''
@app.route('/api/deploy-dashboard-fix', methods=['POST'])
def deploy_dashboard_fix():
    """Emergency dashboard deployment"""
    try:
        html_content = request.json.get('html_content')
        
        # Write to templates folder
        with open('templates/automated_signals_dashboard.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return jsonify({{"success": True, "message": "Dashboard deployed", "size": len(html_content)}})
    except Exception as e:
        return jsonify({{"success": False, "error": str(e)}}), 500
'''

print("\n" + "="*60)
print("DIRECT FIX")
print("="*60)
print("\nThe HTML file is 0 bytes on Railway because it wasn't pushed.")
print("\nHere's what to do RIGHT NOW:")
print("\n1. Open GitHub Desktop")
print("2. Look for 'templates/automated_signals_dashboard.html'")
print("3. If you see it, CHECK THE BOX")
print("4. Commit: 'Fix automated signals dashboard'")
print("5. Push to main")
print("6. Wait 2 minutes")
print("\nOR just use one of the working dashboards:")
print("   https://web-production-cd33.up.railway.app/automated-signals-analytics")
print("   https://web-production-cd33.up.railway.app/automated-signals-command")
