"""
Fix the refactored templates - remove duplicates and ensure proper structure
"""

import re
import os

def fix_template(filename):
    """Fix duplicate extends blocks and clean up template"""
    print(f"Fixing {filename}...")
    
    if not os.path.exists(filename):
        print(f"  ❌ File not found")
        return False
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove duplicate extends blocks
        # Keep only the first occurrence
        extends_pattern = r"{%\s*extends\s+'layout\.html'\s*%}"
        extends_matches = list(re.finditer(extends_pattern, content))
        
        if len(extends_matches) > 1:
            # Remove all but the first
            for match in reversed(extends_matches[1:]):
                content = content[:match.start()] + content[match.end():]
            print(f"  ✓ Removed {len(extends_matches) - 1} duplicate extends blocks")
        
        # Remove duplicate page_title blocks
        title_pattern = r"{%\s*block\s+page_title\s*%}.*?{%\s*endblock\s*%}"
        title_matches = list(re.finditer(title_pattern, content, re.DOTALL))
        
        if len(title_matches) > 1:
            # Keep only the first
            for match in reversed(title_matches[1:]):
                content = content[:match.start()] + content[match.end():]
            print(f"  ✓ Removed {len(title_matches) - 1} duplicate page_title blocks")
        
        # Remove duplicate content blocks (keep first opening, last closing)
        content_start_pattern = r"{%\s*block\s+content\s*%}"
        content_end_pattern = r"{%\s*endblock\s*%}"
        
        content_starts = list(re.finditer(content_start_pattern, content))
        
        if len(content_starts) > 1:
            # Remove duplicate opening tags (keep first)
            for match in reversed(content_starts[1:]):
                content = content[:match.start()] + content[match.end():]
            print(f"  ✓ Removed {len(content_starts) - 1} duplicate content block starts")
        
        # Clean up excessive whitespace
        content = re.sub(r'\n{4,}', '\n\n\n', content)
        
        # Write fixed content
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✅ Fixed {filename}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

# Fix all refactored files
files = [
    'signal_analysis_lab.html',
    'automated_signals_dashboard.html',
    'ml_feature_dashboard.html',
    'time_analysis.html',
    'strategy_comparison.html',
    'ai_business_dashboard.html',
    'prop_firms_v2.html',
    'trade_manager.html',
    'financial_summary.html',
    'reporting_hub.html',
]

print("🔧 Fixing refactored templates...\n")

for filename in files:
    fix_template(filename)

print("\n✅ All templates fixed!")
