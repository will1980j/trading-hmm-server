import requests

r = requests.get('https://web-production-f8c3.up.railway.app/reporting-hub')

print(f"Status: {r.status_code}")
print(f"Has 'Development Reports': {'Development Reports' in r.text}")
print(f"Has development category: {'data-category=\"development\"' in r.text}")
print(f"Has development-section: {'development-section' in r.text}")

# Check if it's the old or new version
if 'Weekly Development Reports' in r.text:
    print("✅ NEW VERSION deployed")
else:
    print("❌ OLD VERSION still showing")
