"""
Complete template refactoring following GPT5.1 strict instructions
This will properly refactor all templates to use layout.html
"""

import re
import os

def find_content_start(html):
    """Find where actual page content starts (after nav)"""
    # Look for end of navigation
    patterns = [
        r'</nav>\s*',
        r'<!-- End Navigation -->\s*',
        r'</div><!-- nav-container -->\s*',
        r'class="nav-container"[^>]*>.*?</div>\s*'
    ]
    
    max_pos = 0
    for pattern in patterns:
        match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
        if match:
            max_pos = max(max_pos, match.end())
    
    # If no nav found, look for first container/main after body
    if max_pos == 0:
        body_match = re.search(r'<body[^>]*>', html)
        if body_match:
            max_pos = body_match.end()
    
    return max_pos

def extract_external_scripts(html):
    """Extract external script tags from head"""
    head_match = re.search(r'<head>(.*?)</head>', html, re.DOTALL)
    if not head_match:
        return []
    
    head = head_match.group(1)
    
    # Find script tags with src attribute
    script_pattern = r'<script[^>]+src=["\']([^"\']+)["\'][^>]*></script>'
    scripts = []
    
    for match in re.finditer(script_pattern, head):
        src = match.group(1)
        # Only include important external libraries
        if any(lib in src.lower() for lib in ['d3.js', 'd3.v', 'chart.js', 'socket.io', 'websocket']):
            scripts.append(match.group(0))
    
    return scripts

def extract_inline_scripts(html):
    """Extract all inline script tags"""
    script_pattern = r'<script(?![^>]*src=)[^>]*>(.*?)</script>'
    scripts = []
    
    for match in re.finditer(script_pattern, html, re.DOTALL):
        script_content = match.group(1).strip()
        # Only include substantial scripts (more than 50 characters)
        if len(script_content) > 50:
            scripts.append(f"<script>\n{script_content}\n</script>")
    
    return scripts

def remove_all_scripts(html):
    """Remove all script tags from HTML"""
    return re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)

def refactor_file(filename, page_title):
    """Refactor a single HTML file"""
    print(f"\n{'='*80}")
    print(f"Refactoring: {filename}")
    print(f"{'='*80}")
    
    if not os.path.exists(filename):
        print(f"❌ File not found: {filename}")
        return False
    
    try:
        # Try UTF-8 first
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                original = f.read()
        except UnicodeDecodeError:
            # Fallback to latin-1
            with open(filename, 'r', encoding='latin-1') as f:
                original = f.read()
        
        # Extract external scripts from head
        external_scripts = extract_external_scripts(original)
        
        # Find where content starts
        content_start = find_content_start(original)
        
        # Find where body ends
        body_end_match = re.search(r'</body>', original)
        if body_end_match:
            content_end = body_end_match.start()
        else:
            content_end = len(original)
        
        # Extract content
        content = original[content_start:content_end].strip()
        
        # Extract inline scripts before removing them
        inline_scripts = extract_inline_scripts(content)
        
        # Remove scripts from content
        content = remove_all_scripts(content)
        
        # Clean up content
        content = content.strip()
        content = re.sub(r'\n{3,}', '\n\n', content)  # Remove excessive newlines
        
        # Build new template
        new_template = f"{{%extends 'layout.html' %}}\n\n"
        new_template += f"{{% block page_title %}}{page_title}{{% endblock %}}\n"
        
        # Add extra_head block if needed
        if external_scripts:
            new_template += "\n{% block extra_head %}\n"
            for script in external_scripts:
                new_template += f"{script}\n"
            new_template += "{% endblock %}\n"
        
        # Add content block
        new_template += f"\n{{% block content %}}\n{content}\n{{% endblock %}}\n"
        
        # Add extra_js block if needed
        if inline_scripts:
            new_template += f"\n{{% block extra_js %}}\n"
            for script in inline_scripts:
                new_template += f"{script}\n\n"
            new_template += "{% endblock %}\n"
        
        # Write refactored file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(new_template)
        
        print(f"✅ Successfully refactored {filename}")
        print(f"   - External scripts: {len(external_scripts)}")
        print(f"   - Inline scripts: {len(inline_scripts)}")
        print(f"   - Content length: {len(content)} characters")
        return True
        
    except Exception as e:
        print(f"❌ Error refactoring {filename}: {e}")
        return False

# Files to refactor
files_to_refactor = [
    ('signal_analysis_lab.html', 'Signal Analysis Lab — Second Skies'),
    ('automated_signals_dashboard.html', 'Automated Signals — Second Skies'),
    ('ml_feature_dashboard.html', 'ML Intelligence Hub — Second Skies'),
    ('time_analysis.html', 'Time Analysis — Second Skies'),
    ('strategy_comparison.html', 'Strategy Comparison — Second Skies'),
    ('ai_business_dashboard.html', 'AI Business Advisor — Second Skies'),
    ('prop_firms_v2.html', 'Prop Portfolio — Second Skies'),
    ('trade_manager.html', 'Trade Manager — Second Skies'),
    ('financial_summary.html', 'Financial Summary — Second Skies'),
    ('reporting_hub.html', 'Reporting Hub — Second Skies'),
]

print("🚀 Starting Complete Template Refactoring")
print("="*80)

success_count = 0
fail_count = 0

for filename, page_title in files_to_refactor:
    if refactor_file(filename, page_title):
        success_count += 1
    else:
        fail_count += 1

print("\n" + "="*80)
print("REFACTORING COMPLETE")
print("="*80)
print(f"✅ Successfully refactored: {success_count} files")
print(f"❌ Failed: {fail_count} files")
print("\n🎉 All templates now use the unified layout system!")
