import requests

r = requests.get('https://web-production-f8c3.up.railway.app/reporting-hub')

print("REPORTING HUB DIAGNOSIS")
print("=" * 80)
print(f"1. Route works: {r.status_code == 200}")
print(f"2. Has category cards: {'category-card' in r.text}")
print(f"3. Has development card: {'data-category=\"development\"' in r.text}")
print(f"4. Has development section: {'development-section' in r.text}")
print(f"5. Has upload button: {'weeklyReportUpload' in r.text}")
print(f"6. Loads reporting.js: {'reporting.js' in r.text}")
print(f"7. Has handleReportUpload: {'handleReportUpload' in r.text}")

# Check for JavaScript errors
print("\n" + "=" * 80)
print("JavaScript includes:")
if 'reporting.js' in r.text:
    print("  ✅ reporting.js included")
else:
    print("  ❌ reporting.js NOT included")

# Check console errors
print("\n" + "=" * 80)
print("Checking for error-causing code:")
print(f"  Has fetchAllData: {'fetchAllData' in r.text}")
print(f"  Has API calls: {'/api/signals/stats/today' in r.text}")

# Show first 500 chars of body
print("\n" + "=" * 80)
print("Page content preview:")
print(r.text[:1000])
