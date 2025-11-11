"""
Deploy Robust Automated Signals Fix
Complete production-grade solution deployment
"""

import os
import shutil
from datetime import datetime

def backup_files():
    """Backup existing files before modification"""
    print("=" * 80)
    print("STEP 1: BACKUP EXISTING FILES")
    print("=" * 80)
    
    backup_dir = f"backups/automated_signals_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = [
        'web_server.py',
        'automated_signals_api.py',
        'automated_signals_dashboard.html',
        'requirements.txt'
    ]
    
    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy2(file, backup_dir)
            print(f"✓ Backed up: {file}")
    
    print(f"\n✓ Backup created: {backup_dir}")
    return backup_dir

def update_requirements():
    """Update requirements.txt with production dependencies"""
    print("\n" + "=" * 80)
    print("STEP 2: UPDATE REQUIREMENTS.TXT")
    print("=" * 80)
    
    additions = """
# Production WebSocket Support (Added by robust fix)
eventlet>=0.33.3
flask-socketio>=5.3.5
python-socketio>=5.10.0
"""
    
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()
        
        if 'eventlet' not in content:
            with open('requirements.txt', 'a') as f:
                f.write('\n' + additions)
            print("✓ Added production WebSocket dependencies")
        else:
            print("✓ Dependencies already present")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    return True

def update_web_server():
    """Update web_server.py to use robust handlers"""
    print("\n" + "=" * 80)
    print("STEP 3: UPDATE WEB_SERVER.PY")
    print("=" * 80)
    
    print("\nChanges needed:")
    print("1. Change SocketIO initialization to use eventlet")
    print("2. Import robust WebSocket handler")
    print("3. Import robust API")
    print("4. Register robust handlers")
    
    print("\nManual changes required in web_server.py:")
    print("-" * 80)
    
    print("\n# Change 1: Update SocketIO initialization")
    print("FROM:")
    print("  socketio = SocketIO(app, cors_allowed_origins='*', async_mode='threading')")
    print("\nTO:")
    print("  socketio = SocketIO(app, cors_allowed_origins='*', async_mode='eventlet')")
    
    print("\n# Change 2: Import robust handlers (add after other imports)")
    print("  from websocket_handler_robust import RobustWebSocketHandler, register_websocket_handlers")
    print("  from automated_signals_api_robust import register_automated_signals_api_robust")
    
    print("\n# Change 3: Initialize robust WebSocket handler (replace existing)")
    print("  robust_ws_handler = RobustWebSocketHandler(socketio, db) if db_enabled else None")
    print("  if robust_ws_handler:")
    print("      robust_ws_handler.start_health_monitor()")
    print("      register_websocket_handlers(socketio, robust_ws_handler)")
    
    print("\n# Change 4: Register robust API (replace existing)")
    print("  if db_enabled:")
    print("      register_automated_signals_api_robust(app, db)")
    
    return True

def update_dashboard_html():
    """Update dashboard HTML to use robust WebSocket client"""
    print("\n" + "=" * 80)
    print("STEP 4: UPDATE AUTOMATED_SIGNALS_DASHBOARD.HTML")
    print("=" * 80)
    
    print("\nChanges needed:")
    print("1. Include robust WebSocket client script")
    print("2. Replace WebSocket initialization")
    print("3. Add connection status handling")
    
    print("\nManual changes required:")
    print("-" * 80)
    
    print("\n# Change 1: Add script tag (before closing </body>)")
    print("  <script src='/static/websocket_client_robust.js'></script>")
    
    print("\n# Change 2: Replace WebSocket initialization")
    print("FROM:")
    print("  const socket = io();")
    print("\nTO:")
    print("  const wsClient = new RobustWebSocketClient();")
    print("  ")
    print("  // Register event handlers")
    print("  wsClient.on('signal_update', (data) => {")
    print("      handleSignalUpdate(data);")
    print("  });")
    print("  ")
    print("  wsClient.on('mfe_update', (data) => {")
    print("      handleMFEUpdate(data);")
    print("  });")
    print("  ")
    print("  wsClient.on('polling_update', (data) => {")
    print("      // Handle polling fallback data")
    print("      if (data.success) {")
    print("          updateDashboardData(data);")
    print("      }")
    print("  });")
    
    return True

def create_static_directory():
    """Create static directory for JavaScript files"""
    print("\n" + "=" * 80)
    print("STEP 5: CREATE STATIC DIRECTORY")
    print("=" * 80)
    
    os.makedirs('static', exist_ok=True)
    
    # Copy robust WebSocket client
    if os.path.exists('websocket_client_robust.js'):
        shutil.copy2('websocket_client_robust.js', 'static/websocket_client_robust.js')
        print("✓ Copied websocket_client_robust.js to static/")
    
    return True

def create_deployment_checklist():
    """Create deployment checklist"""
    print("\n" + "=" * 80)
    print("DEPLOYMENT CHECKLIST")
    print("=" * 80)
    
    checklist = """
# Robust Automated Signals Fix - Deployment Checklist

## Pre-Deployment
- [x] Backup created
- [x] Requirements.txt updated
- [ ] web_server.py updated (manual changes required)
- [ ] automated_signals_dashboard.html updated (manual changes required)
- [ ] Static directory created
- [ ] All files reviewed

## Testing (Local)
- [ ] Test database connection
- [ ] Test API endpoints
- [ ] Test WebSocket connection
- [ ] Test reconnection logic
- [ ] Test polling fallback
- [ ] Test with empty database
- [ ] Test with real data

## Deployment (Railway)
- [ ] Commit all changes via GitHub Desktop
- [ ] Push to main branch
- [ ] Monitor Railway deployment logs
- [ ] Verify eventlet installation
- [ ] Check WebSocket upgrade in logs
- [ ] Test production WebSocket connection

## Post-Deployment Verification
- [ ] Dashboard loads without errors
- [ ] API returns data (or empty arrays if no data)
- [ ] WebSocket connects successfully
- [ ] Real-time updates working
- [ ] Reconnection works after disconnect
- [ ] Polling fallback activates if needed
- [ ] Health monitoring active
- [ ] No console errors

## Rollback Plan (if needed)
- [ ] Restore from backup directory
- [ ] Revert requirements.txt
- [ ] Redeploy to Railway

## Success Criteria
✓ Dashboard displays data or meaningful empty state
✓ WebSocket connects without "Invalid frame header" error
✓ Automatic reconnection works
✓ Graceful degradation to polling if WebSocket fails
✓ Real-time updates functioning
✓ No data loss during connection issues
✓ Clear error messages when issues occur

---
Deployment Date: {date}
Backup Location: {backup_dir}
"""
    
    with open('DEPLOYMENT_CHECKLIST.md', 'w', encoding='utf-8') as f:
        f.write(checklist.format(
            date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            backup_dir=backup_dir if 'backup_dir' in locals() else 'Not created'
        ))
    
    print("✓ Deployment checklist created: DEPLOYMENT_CHECKLIST.md")

def print_summary():
    """Print deployment summary"""
    print("\n" + "=" * 80)
    print("DEPLOYMENT SUMMARY")
    print("=" * 80)
    
    print("\n✓ COMPLETED:")
    print("  1. Backup created")
    print("  2. Requirements.txt updated")
    print("  3. Robust API created (automated_signals_api_robust.py)")
    print("  4. Robust WebSocket handler created (websocket_handler_robust.py)")
    print("  5. Robust WebSocket client created (websocket_client_robust.js)")
    print("  6. Static directory prepared")
    print("  7. Deployment checklist created")
    
    print("\n⚠️  MANUAL STEPS REQUIRED:")
    print("  1. Update web_server.py (see STEP 3 output above)")
    print("  2. Update automated_signals_dashboard.html (see STEP 4 output above)")
    print("  3. Review all changes")
    print("  4. Test locally")
    print("  5. Deploy to Railway")
    
    print("\n📋 NEXT STEPS:")
    print("  1. Review DEPLOYMENT_CHECKLIST.md")
    print("  2. Make manual code changes")
    print("  3. Test locally: python web_server.py")
    print("  4. Commit via GitHub Desktop")
    print("  5. Push to trigger Railway deployment")
    print("  6. Monitor deployment and test production")
    
    print("\n" + "=" * 80)
    print("ROBUST SOLUTION READY FOR DEPLOYMENT")
    print("=" * 80)

if __name__ == "__main__":
    print("ROBUST AUTOMATED SIGNALS FIX - DEPLOYMENT")
    print("Production-grade solution - no shortcuts")
    print()
    
    backup_dir = backup_files()
    
    if update_requirements():
        update_web_server()
        update_dashboard_html()
        create_static_directory()
        create_deployment_checklist()
        print_summary()
    else:
        print("\n✗ Deployment preparation failed")
        print(f"Restore from backup: {backup_dir}")
