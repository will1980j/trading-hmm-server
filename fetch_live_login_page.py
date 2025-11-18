"""
Fetch the live login page to see what's actually rendering
"""
import requests

url = "https://web-production-cd33.up.railway.app/login"

print("=" * 60)
print("FETCHING LIVE LOGIN PAGE")
print("=" * 60)

try:
    response = requests.get(url, timeout=10)
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        html = response.text
        
        # Check for form fields
        has_username = 'name="username"' in html
        has_password = 'name="password"' in html
        has_form = '<form' in html
        
        print(f"\n✅ Form present: {has_form}")
        print(f"✅ Username field: {has_username}")
        print(f"✅ Password field: {has_password}")
        
        if not (has_username and has_password):
            print("\n❌ FORM FIELDS MISSING!")
            print("\nSearching for input fields...")
            if '<input' in html:
                print("Found <input> tags:")
                import re
                inputs = re.findall(r'<input[^>]*>', html)
                for inp in inputs[:5]:
                    print(f"  {inp}")
            else:
                print("No <input> tags found at all!")
                
        # Save to file for inspection
        with open('live_login_page.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("\n📄 Saved to: live_login_page.html")
        
except Exception as e:
    print(f"❌ Error: {e}")
