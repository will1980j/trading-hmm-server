import requests

# Check if the new route comment is in the logs
r = requests.get('https://web-production-f8c3.up.railway.app/reporting-hub')

print("Checking deployed version...")
print("=" * 80)

# The page shows login, which means either:
# 1. Not logged in (but you said you are)
# 2. Route is broken
# 3. Railway didn't deploy

# Let's check a working route to verify you're logged in
r2 = requests.get('https://web-production-f8c3.up.railway.app/homepage')
print(f"Homepage status: {r2.status_code}")
print(f"Homepage shows login: {'Login' in r2.text[:500]}")

# Check if reporting-hub route exists
r3 = requests.get('https://web-production-f8c3.up.railway.app/api/health')
print(f"\nHealth check: {r3.status_code if r3.status_code else 'Failed'}")

# Try to access without auth
print("\n" + "=" * 80)
print("The issue: reporting-hub requires login but you're logged in")
print("This suggests Railway hasn't deployed the new code yet")
print("\nCheck Railway dashboard:")
print("1. Go to Railway dashboard")
print("2. Check latest deployment time")
print("3. Check if build succeeded")
print("4. Check deployment logs for errors")
