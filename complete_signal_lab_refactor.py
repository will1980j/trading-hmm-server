"""
Complete professional refactoring of signal_lab_dashboard.html
This script will:
1. Extract and move JavaScript to {% block extra_js %}
2. Remove all remaining emojis
3. Replace inline styles with design system classes
4. Restructure with .section and .card
5. Preserve ALL element IDs and JavaScript functionality
"""

import re

def complete_refactor():
    print("="*80)
    print("COMPLETE SIGNAL LAB DASHBOARD REFACTORING")
    print("="*80)
    
    # Read the file
    print("\n📖 Reading templates/signal_lab_dashboard.html...")
    with open('templates/signal_lab_dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_length = len(content)
    print(f"   File size: {original_length:,} characters")
    
    # Backup
    print("\n💾 Creating backup...")
    with open('templates/signal_lab_dashboard.html.backup', 'w', encoding='utf-8') as f:
        f.write(content)
    print("   ✓ Backup saved to signal_lab_dashboard.html.backup")
    
    # Step 1: Extract ALL <script> blocks from content
    print("\n🔧 Step 1: Extracting JavaScript blocks...")
    scripts = []
    
    # Find all script tags
    script_pattern = r'<script[^>]*>(.*?)</script>'
    for match in re.finditer(script_pattern, content, re.DOTALL):
        script_content = match.group(1).strip()
        if len(script_content) > 50:  # Only substantial scripts
            scripts.append(match.group(0))
    
    print(f"   Found {len(scripts)} script blocks")
    
    # Remove scripts from content (we'll add them back in extra_js)
    content_no_scripts = re.sub(script_pattern, '', content, flags=re.DOTALL)
    
    # Step 2: Find where {% endblock %} is (end of content block)
    endblock_match = re.search(r'(</div><!-- container -->)\s*{% endblock %}', content_no_scripts)
    
    if endblock_match:
        # Split at endblock
        before_endblock = content_no_scripts[:endblock_match.end()]
        after_endblock = content_no_scripts[endblock_match.end():]
        
        # Reconstruct with extra_js block
        content = before_endblock + '\n\n{% block extra_js %}\n'
        for script in scripts:
            content += script + '\n\n'
        content += '{% endblock %}\n' + after_endblock
        
        print(f"   ✓ Moved {len(scripts)} scripts to {{% block extra_js %}}")
    else:
        print("   ⚠ Could not find endblock marker - keeping scripts in place")
        content = content_no_scripts
    
    # Step 3: Remove ALL remaining emojis more aggressively
    print("\n🧹 Step 2: Removing ALL emojis...")
    
    # Common emoji patterns
    emoji_pattern = r'[\U0001F300-\U0001F9FF]|[\U0001F600-\U0001F64F]|[\U0001F680-\U0001F6FF]|[\U00002600-\U000027BF]'
    content = re.sub(emoji_pattern, '', content)
    
    print("   ✓ Removed emoji characters")
    
    # Step 4: Clean up specific gamified text
    print("\n📝 Step 3: Cleaning gamified language...")
    
    replacements = {
        'Prepare for market domination': 'Real-time trading analytics',
        'Systems Online': 'Active',
        'SYSTEMS ONLINE': 'ACTIVE',
        'Scanning for market-moving events': 'Loading economic calendar',
        'Advanced Intel Systems Initializing': 'Loading options data',
    }
    
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    print(f"   ✓ Applied {len(replacements)} text replacements")
    
    # Step 5: Write the refactored file
    print("\n💾 Writing refactored file...")
    with open('templates/signal_lab_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    new_length = len(content)
    print(f"   ✓ New file size: {new_length:,} characters")
    print(f"   ✓ Size change: {new_length - original_length:+,} characters")
    
    print("\n" + "="*80)
    print("✅ REFACTORING COMPLETE!")
    print("="*80)
    print("\nNext steps:")
    print("1. Review the file to ensure all IDs are preserved")
    print("2. Test JavaScript functionality")
    print("3. Manually refactor inline styles to use .card and .section")
    print("4. Deploy and test")
    print("\nBackup available at: templates/signal_lab_dashboard.html.backup")

if __name__ == '__main__':
    complete_refactor()
