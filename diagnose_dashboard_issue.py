"""Diagnose why dashboard isn't loading"""
import requests
import os

BASE_URL = "https://web-production-cd33.up.railway.app"

print("=" * 60)
print("DIAGNOSING AUTOMATED SIGNALS DASHBOARD ISSUE")
print("=" * 60)

# Check 1: Are the HTML files in local templates folder?
print("\n1. Checking local files...")
files_to_check = [
    'templates/automated_signals_dashboard.html',
    'templates/automated_signals_dashboard_option2.html',
    'templates/automated_signals_dashboard_option3.html'
]

for file in files_to_check:
    exists = os.path.exists(file)
    size = os.path.getsize(file) if exists else 0
    print(f"   {'✅' if exists else '❌'} {file} ({size} bytes)")

# Check 2: Test the route with authentication
print("\n2. Testing route (without auth)...")
try:
    r = requests.get(f"{BASE_URL}/automated-signals", allow_redirects=False)
    print(f"   Status: {r.status_code}")
    if r.status_code == 302:
        print(f"   ✅ Route exists (redirects to {r.headers.get('Location')})")
    elif r.status_code == 404:
        print(f"   ❌ Route NOT FOUND - not deployed yet")
    elif r.status_code == 500:
        print(f"   ❌ SERVER ERROR - check Railway logs")
        print(f"   Error: {r.text[:500]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Check 3: Test API endpoint
print("\n3. Testing API endpoint...")
try:
    r = requests.get(f"{BASE_URL}/api/automated-signals/recent")
    print(f"   Status: {r.status_code}")
    if r.status_code == 401:
        print(f"   ✅ API exists (requires auth)")
    elif r.status_code == 404:
        print(f"   ❌ API NOT FOUND")
    elif r.status_code == 200:
        print(f"   ✅ API accessible")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Check 4: Check if files are committed
print("\n4. Checking git status...")
os.system("git status templates/automated_signals_dashboard*.html")

print("\n" + "=" * 60)
print("DIAGNOSIS COMPLETE")
print("=" * 60)
print("\nIf files show as 'Untracked' or 'Modified', you need to:")
print("1. git add templates/automated_signals_dashboard*.html")
print("2. git add web_server.py")
print("3. git commit -m 'Add automated signals dashboards'")
print("4. git push origin main")
print("5. Wait 2-3 minutes for Railway deployment")
