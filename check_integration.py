"""Quick check if hyperparameter integration is ready"""
import os
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("🔍 Checking Hyperparameter Optimization Integration...\n")

files_to_check = [
    'hyperparameter_status.py',
    'init_hyperparameter_table.py',
    'ml_auto_optimizer.py',
    'web_server.py'
]

all_good = True

for file in files_to_check:
    if os.path.exists(file):
        print(f"✅ {file}")
    else:
        print(f"❌ {file} - MISSING")
        all_good = False

print("\n📝 Checking web_server.py for endpoint...")
with open('web_server.py', 'r', encoding='utf-8') as f:
    content = f.read()
    if '/api/hyperparameter-status' in content:
        print("✅ API endpoint added to web_server.py")
    else:
        print("❌ API endpoint NOT found in web_server.py")
        all_good = False

print("\n📝 Checking ml_auto_optimizer.py for database storage...")
with open('ml_auto_optimizer.py', 'r', encoding='utf-8') as f:
    content = f.read()
    if 'hyperparameter_optimization_results' in content:
        print("✅ Database storage added to ml_auto_optimizer.py")
    else:
        print("❌ Database storage NOT found in ml_auto_optimizer.py")
        all_good = False

if all_good:
    print("\n🎉 Integration is complete!")
    print("\n⚠️  NEXT STEP: Restart your Flask server")
    print("   - Railway: Will auto-restart on deployment")
    print("   - Local: Stop and restart web_server.py")
else:
    print("\n❌ Integration incomplete - check missing files")
