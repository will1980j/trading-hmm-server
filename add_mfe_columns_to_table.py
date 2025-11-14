import requests

# Add the missing columns to the automated_signals table
url = "https://web-production-cd33.up.railway.app/api/automated-signals/add-mfe-columns"

print("Adding be_mfe and no_be_mfe columns to automated_signals table...")
response = requests.post(url)

if response.status_code == 200:
    print("✅ Columns added successfully!")
    print(response.json())
else:
    print(f"❌ Failed: {response.status_code}")
    print(response.text)
