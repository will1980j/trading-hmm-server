import requests

# Login first
session = requests.Session()
login_data = {
    'username': 'admin',  # Update if different
    'password': 'your_password'  # Update with actual password
}

# Try to get the page
r = session.get('https://web-production-f8c3.up.railway.app/reporting-hub')

print(f"Status: {r.status_code}")
print(f"Content length: {len(r.text)}")
print("\nFirst 2000 characters:")
print(r.text[:2000])

# Check for key elements
print("\n" + "=" * 80)
print("CHECKING FOR KEY ELEMENTS:")
print(f"Has 'Reporting Center': {'Reporting Center' in r.text}")
print(f"Has 'category-card': {'category-card' in r.text}")
print(f"Has 'Development Reports': {'Development Reports' in r.text}")
print(f"Has 'development-section': {'development-section' in r.text}")

# Save full HTML for inspection
with open('live_reporting_hub.html', 'w', encoding='utf-8') as f:
    f.write(r.text)
print("\n✅ Full HTML saved to live_reporting_hub.html")
