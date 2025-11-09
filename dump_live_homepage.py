"""
Dump the actual live homepage content to see what's there
"""
import requests

BASE_URL = "https://web-production-cd33.up.railway.app"

try:
    response = requests.get(f'{BASE_URL}/homepage', timeout=10)
    
    if response.status_code == 200:
        content = response.text
        
        # Find the featured section
        if '<div class="featured-section">' in content:
            start = content.find('<div class="featured-section">')
            end = content.find('</div>', start + 500)
            featured = content[start:end+6]
            print("\n📌 FEATURED SECTION:")
            print("=" * 70)
            print(featured[:500])
            print("=" * 70)
        
        # Find navigation
        if '<nav class="nav-container">' in content:
            start = content.find('<nav class="nav-container">')
            end = content.find('</nav>', start)
            nav = content[start:end+6]
            print("\n🧭 NAVIGATION:")
            print("=" * 70)
            print(nav[:500])
            print("=" * 70)
        
        # Search for any V2 references
        print("\n🔍 SEARCHING FOR 'V2' REFERENCES:")
        print("=" * 70)
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'v2' in line.lower() or 'V2' in line:
                print(f"Line {i}: {line.strip()[:100]}")
        
        # Search for automated-signals references
        print("\n🔍 SEARCHING FOR 'automated-signals' REFERENCES:")
        print("=" * 70)
        for i, line in enumerate(lines):
            if 'automated-signals' in line.lower():
                print(f"Line {i}: {line.strip()[:100]}")
                
    else:
        print(f"Error: Status code {response.status_code}")
        
except Exception as e:
    print(f"Error: {e}")
