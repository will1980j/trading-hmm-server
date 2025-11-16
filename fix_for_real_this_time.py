"""
ACTUALLY fix the navigation - remove body padding and ensure proper structure
"""

import os
import re

DASHBOARD_FILES = [
    'ml_feature_dashboard.html',
    'signal_lab_dashboard.html',
    'signal_analysis_lab.html',
    'automated_signals_dashboard.html',
    'time_analysis.html',
    'strategy_optimizer.html',
    'strategy_comparison.html',
    'ai_business_dashboard.html',
    'prop_firm_management.html',
    'trade_manager.html',
    'financial_summary.html',
    'reporting_hub.html',
]

def fix_file(file_path):
    """Actually fix the file properly"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"\n{'='*80}")
    print(f"Fixing: {file_path}")
    print('='*80)
    
    # 1. Remove body padding
    content = re.sub(
        r'body\s*{([^}]*?)padding:\s*20px;([^}]*?)}',
        r'body {\1\2}',
        content,
        flags=re.DOTALL
    )
    print("✓ Removed body padding")
    
    # 2. Ensure body has no padding at all
    content = re.sub(
        r'(body\s*{[^}]*?)}',
        lambda m: m.group(0) if 'padding' not in m.group(0) else m.group(0).replace('padding: 20px;', '').replace('padding:20px;', ''),
        content
    )
    
    # 3. Add container wrapper CSS if not exists
    if '.container {' not in content and '.dashboard-container {' not in content:
        container_css = '''
        .container {
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
'''
        content = content.replace('</style>', container_css + '    </style>', 1)
        print("✓ Added container CSS")
    
    # 4. Wrap main content in container div (after nav)
    # Find the main content start (after </nav>)
    nav_end = content.find('</nav>')
    if nav_end > 0:
        # Find next significant element after nav
        after_nav = content[nav_end + 6:]  # After </nav>
        
        # Look for common content starts
        content_starts = [
            (r'(<div class="header">)', r'<div class="container">\n    \1'),
            (r'(<div class="stats-grid">)', r'<div class="container">\n    \1'),
            (r'(<div class="dashboard-container">)', r'\1'),  # Already has container
            (r'(<h1)', r'<div class="container">\n    \1'),
            (r'(<!--[^>]*-->[\s\n]*<div)', r'<div class="container">\n    \1'),
        ]
        
        wrapped = False
        for pattern, replacement in content_starts:
            if re.search(pattern, after_nav[:500]):
                before_nav = content[:nav_end + 6]
                content = before_nav + re.sub(pattern, replacement, after_nav, count=1)
                wrapped = True
                print(f"✓ Wrapped content in container")
                break
        
        if not wrapped:
            print("⚠ Could not find content to wrap")
    
    # 5. Close container before </body>
    if '<div class="container">' in content and not content.count('<div class="container">') == content.count('</div><!-- container -->'):
        content = content.replace('</body>', '</div><!-- container -->\n</body>', 1)
        print("✓ Closed container div")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    print("🔧 ACTUALLY FIXING NAVIGATION - REMOVING BODY PADDING")
    print("="*80)
    
    for file_path in DASHBOARD_FILES:
        try:
            fix_file(file_path)
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "="*80)
    print("✅ DONE - Now pages should match homepage appearance")
    print("="*80)

if __name__ == "__main__":
    main()
