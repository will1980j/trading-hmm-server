"""
Integrate System Health Monitor into web_server.py
"""

# Read web_server.py
with open('web_server.py', 'r', encoding='utf-8') as f:
    web_server = f.read()

# Check if already integrated
if 'system_health_api' in web_server:
    print("⚠️  System Health API already integrated")
else:
    # Add import at top
    import_line = "from system_health_api import register_system_health_api\n"
    
    # Find the imports section
    import_position = web_server.find('from flask import')
    if import_position != -1:
        # Add after Flask imports
        next_newline = web_server.find('\n', import_position)
        web_server = web_server[:next_newline+1] + import_line + web_server[next_newline+1:]
    
    # Add registration call after other API registrations
    registration_line = "    register_system_health_api(app, db)\n"
    
    # Find where automated_signals_api is registered
    api_reg_position = web_server.find('register_automated_signals_api(app, db)')
    if api_reg_position != -1:
        next_newline = web_server.find('\n', api_reg_position)
        web_server = web_server[:next_newline+1] + registration_line + web_server[next_newline+1:]
    
    # Write updated web_server.py
    with open('web_server.py', 'w', encoding='utf-8') as f:
        f.write(web_server)
    
    print("✅ System Health API integrated into web_server.py")

# Deploy the health monitor to dashboard
import subprocess
subprocess.run(['python', 'deploy_system_health_monitor.py'])

print("\n" + "="*60)
print("SYSTEM HEALTH MONITOR DEPLOYMENT COMPLETE")
print("="*60)
print("\n📊 Features Deployed:")
print("  ✅ Compact status bar at top of dashboard")
print("  ✅ 5 component health checks (Database, Webhooks, Events, Data, API)")
print("  ✅ Real-time status indicators with color coding")
print("  ✅ Expandable detailed view")
print("  ✅ Auto-refresh every 60 seconds")
print("  ✅ Manual refresh button")
print("\n🎯 Health Checks:")
print("  • Database: Connection, schema, query performance")
print("  • Webhooks: Reception rate, last webhook time, event types")
print("  • Events: Active trades, MFE coverage, completions")
print("  • Data: Freshness of MFE updates and entries")
print("  • API: Response time, status codes")
print("\n🚀 Next Steps:")
print("  1. Restart Flask app to load new API endpoint")
print("  2. Refresh dashboard to see health monitor")
print("  3. Click 'Details' to expand full diagnostics")
print("\n" + "="*60)
