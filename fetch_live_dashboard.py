import requests

url = "https://web-production-cd33.up.railway.app/automated-signals"
print(f"Fetching live dashboard from: {url}")

try:
    response = requests.get(url)
    content = response.text
    
    # Save to file
    with open('live_dashboard_snapshot.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ Downloaded {len(content)} characters")
    
    # Check for bulk delete features
    has_checkbox = 'type="checkbox"' in content or 'checkbox' in content.lower()
    has_select_all = 'select all' in content.lower() or 'selectall' in content.lower()
    has_bulk_delete = 'bulk' in content.lower() and 'delete' in content.lower()
    has_delete_selected = 'delete selected' in content.lower() or 'deleteselected' in content.lower()
    
    print(f"\n📋 FEATURE CHECK:")
    print(f"  Checkboxes: {has_checkbox}")
    print(f"  Select All: {has_select_all}")
    print(f"  Bulk Delete: {has_bulk_delete}")
    print(f"  Delete Selected: {has_delete_selected}")
    
    # Search for specific patterns
    if 'checkbox' in content.lower():
        import re
        checkboxes = re.findall(r'<input[^>]*type=["\']checkbox["\'][^>]*>', content, re.IGNORECASE)
        print(f"\n  Found {len(checkboxes)} checkbox inputs")
        if checkboxes:
            print(f"  First checkbox: {checkboxes[0][:100]}")
    
    print(f"\n✅ Saved to: live_dashboard_snapshot.html")
    
except Exception as e:
    print(f"❌ Error: {e}")
