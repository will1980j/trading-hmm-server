"""
Check what files Railway actually has
"""
import requests

BASE_URL = "https://web-production-cd33.up.railway.app"

print("Checking Railway deployment...")
print("="*60)

# Test each dashboard file
files_to_test = [
    ('automated_signals_dashboard.html', '/automated-signals'),
    ('automated_signals_dashboard_option2.html', '/automated-signals-analytics'),
    ('automated_signals_dashboard_option3.html', '/automated-signals-command'),
]

for filename, route in files_to_test:
    try:
        r = requests.get(f"{BASE_URL}{route}", allow_redirects=False, timeout=5)
        
        if r.status_code == 302:
            print(f"✅ {filename}: Route exists (redirects to login)")
        elif r.status_code == 404:
            print(f"❌ {filename}: Route NOT FOUND")
        elif r.status_code == 200:
            if "File not found" in r.text:
                print(f"❌ {filename}: File missing on Railway")
            elif len(r.text) < 1000:
                print(f"⚠️  {filename}: File too small ({len(r.text)} bytes)")
            else:
                print(f"✅ {filename}: Working ({len(r.text)} bytes)")
    except Exception as e:
        print(f"❌ {filename}: Error - {e}")

print("\n" + "="*60)
print("DIAGNOSIS:")
print("="*60)
print("\nIf files show 'File missing on Railway', the deployment failed.")
print("Railway might not have picked up the files from your push.")
print("\nCheck Railway dashboard for deployment logs.")
