import requests

# Test the delete endpoint
base_url = "https://web-production-cd33.up.railway.app"

print("Testing DELETE endpoint...")
print("=" * 80)

# Try DELETE request
try:
    response = requests.delete(f"{base_url}/api/automated-signals/delete/TEST_123")
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Response: {response.text[:500]}")
    
    if response.status_code == 405:
        print("\n❌ 405 Method Not Allowed - DELETE method not registered")
        print("This means the endpoint exists but DELETE isn't allowed")
        
    elif response.status_code == 404:
        print("\n❌ 404 Not Found - Endpoint doesn't exist")
        
    elif response.status_code == 200:
        print("\n✅ Success! Endpoint is working")
        
except Exception as e:
    print(f"❌ Error: {e}")

# Also try OPTIONS to see what methods are allowed
print("\n" + "=" * 80)
print("Checking allowed methods with OPTIONS...")
try:
    response = requests.options(f"{base_url}/api/automated-signals/delete/TEST_123")
    print(f"Status Code: {response.status_code}")
    print(f"Allow Header: {response.headers.get('Allow', 'Not specified')}")
except Exception as e:
    print(f"❌ Error: {e}")
