import requests

base_url = "https://web-production-cd33.up.railway.app"

urls = [
    f"{base_url}/automated-signals-option1",
    f"{base_url}/automated-signals-option2",
    f"{base_url}/automated-signals-option3"
]

for url in urls:
    try:
        response = requests.get(url, allow_redirects=False)
        print(f"\n{url}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text[:500]
            # Check for distinctive markers
            if "Minimalist Trader's Cockpit" in content:
                print("✅ LIGHT THEME - Option 2")
            elif "Trading Floor Command Center" in content or "#0f1419" in content:
                print("❌ DARK THEME - Option 1 (duplicate)")
            elif "Mission Control" in content:
                print("✅ MISSION CONTROL - Option 3")
            
            # Check background color
            if "background: #f8f9fa" in response.text:
                print("Background: LIGHT (#f8f9fa)")
            elif "background: #0f1419" in response.text:
                print("Background: DARK (#0f1419)")
            elif "background: #1a1a2e" in response.text:
                print("Background: PURPLE (#1a1a2e)")
                
    except Exception as e:
        print(f"Error: {e}")
