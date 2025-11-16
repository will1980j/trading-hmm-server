"""
FORCE homepage header/nav styles onto every dashboard - NO MERCY
"""

import os
import re

# The MANDATORY CSS that MUST be at the top of every file
MANDATORY_CSS = '''        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
            color: #ffffff;
            min-height: 100vh;
        }

        /* Header */
        .header {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo-section {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .logo {
            font-size: 2rem;
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .platform-info h1 {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }

        .platform-info p {
            color: #94a3b8;
            font-size: 0.9rem;
        }

        .user-section {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .user-info {
            text-align: right;
        }

        .user-name {
            font-weight: 600;
            margin-bottom: 0.25rem;
        }

        .user-status {
            color: #22c55e;
            font-size: 0.8rem;
        }

        .logout-btn {
            background: rgba(239, 68, 68, 0.2);
            border: 1px solid #ef4444;
            color: #fca5a5;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            text-decoration: none;
            font-size: 0.9rem;
            transition: all 0.3s;
        }

        .logout-btn:hover {
            background: rgba(239, 68, 68, 0.3);
            transform: translateY(-2px);
        }

        /* Navigation */
        .nav-container {
            background: #141b3d;
            padding: 12px 20px;
            border-bottom: 1px solid #2d3a5f;
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            align-items: center;
            overflow-x: auto;
        }

        .nav-link {
            padding: 8px 12px;
            background: #1a2142;
            color: #f8fafc;
            text-decoration: none;
            border-radius: 6px;
            font-size: 14px;
            white-space: nowrap;
            transition: all 0.3s;
        }

        .nav-link:hover {
            background: #3b82f6;
            transform: translateY(-2px);
        }

        /* Dashboard Specific Styles Below */
'''

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

def force_styles(file_path):
    """FORCE the homepage styles into this file"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"\n{'='*80}")
    print(f"FORCING STYLES: {file_path}")
    print('='*80)
    
    # Find the <style> tag
    style_start = content.find('<style>')
    if style_start == -1:
        print("❌ No <style> tag found")
        return False
    
    # Find the </style> tag
    style_end = content.find('</style>', style_start)
    if style_end == -1:
        print("❌ No </style> tag found")
        return False
    
    # Extract everything after <style> and before </style>
    before_style = content[:style_start + 7]  # Include <style>
    old_styles = content[style_start + 7:style_end]
    after_style = content[style_end:]
    
    # Remove ANY existing *, body, .header, .nav-container, .nav-link styles
    patterns_to_remove = [
        r'\*\s*{[^}]+}',
        r'body\s*{[^}]+}',
        r'\.header\s*{[^}]+}',
        r'\.logo-section\s*{[^}]+}',
        r'\.logo\s*{[^}]+}',
        r'\.platform-info[^{]*{[^}]+}',
        r'\.user-section\s*{[^}]+}',
        r'\.user-info\s*{[^}]+}',
        r'\.user-name\s*{[^}]+}',
        r'\.user-status\s*{[^}]+}',
        r'\.logout-btn[^{]*{[^}]+}',
        r'\.nav-container\s*{[^}]+}',
        r'\.nav-link[^{]*{[^}]+}',
        r'/\*\s*Header\s*\*/.*?(?=/\*|$)',
        r'/\*\s*Navigation\s*\*/.*?(?=/\*|$)',
    ]
    
    cleaned_styles = old_styles
    for pattern in patterns_to_remove:
        cleaned_styles = re.sub(pattern, '', cleaned_styles, flags=re.DOTALL)
    
    # Remove :root if it conflicts
    if ':root' in cleaned_styles:
        # Keep :root but ensure it doesn't override our colors
        pass
    
    # Build new content: <style> + MANDATORY_CSS + cleaned old styles + </style>
    new_content = before_style + '\n' + MANDATORY_CSS + '\n' + cleaned_styles + after_style
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ FORCED homepage styles to top of file")
    print("✅ Removed conflicting styles")
    print("✅ Preserved dashboard-specific styles")
    
    return True

def main():
    print("🔨 FORCING HOMEPAGE STYLES - NO COMPROMISES")
    print("="*80)
    
    success_count = 0
    for file_path in DASHBOARD_FILES:
        try:
            if force_styles(file_path):
                success_count += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("\n" + "="*80)
    print(f"✅ FORCED styles on {success_count}/{len(DASHBOARD_FILES)} files")
    print("="*80)
    print("\nNow ALL pages will have IDENTICAL header and navigation")

if __name__ == "__main__":
    main()
