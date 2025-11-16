"""
Standardize navigation bar across all dashboard pages
Extracts navigation from homepage and applies it to all pages
"""

import os
import re

# Standard navigation HTML from homepage
STANDARD_NAV = '''    <!-- Navigation -->
    <nav class="nav-container">
        <a href="/ml-dashboard" class="nav-link">🤖 ML</a>
        <a href="/signal-lab-dashboard" class="nav-link">🏠 Dashboard</a>
        <a href="/signal-analysis-lab" class="nav-link">🧪 Signal Lab</a>
        <a href="/automated-signals" class="nav-link">📡 Automated Signals</a>
        <a href="/time-analysis" class="nav-link">⏰ Time</a>
        <a href="/strategy-optimizer" class="nav-link">🎯 Optimizer</a>
        <a href="/strategy-comparison" class="nav-link">🏆 Compare</a>
        <a href="/ai-business-advisor" class="nav-link">🧠 AI Advisor</a>
        <a href="/prop-portfolio" class="nav-link">💼 Prop</a>
        <a href="/trade-manager" class="nav-link">📋 Trades</a>
        <a href="/financial-summary" class="nav-link">💰 Finance</a>
        <a href="/reporting-hub" class="nav-link">📊 Reports</a>
    </nav>'''

# Standard navigation CSS from homepage
STANDARD_NAV_CSS = '''        /* Navigation */
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
        }'''

# List of all dashboard HTML files to update
DASHBOARD_FILES = [
    'ml_feature_dashboard.html',
    'signal_lab_dashboard.html',
    'signal_analysis_lab.html',
    'automated_signals_dashboard.html',  # Already done manually
    'time_analysis.html',
    'strategy_optimizer.html',
    'strategy_comparison.html',
    'ai_business_dashboard.html',  # Correct filename
    'prop_firm_management.html',  # Correct filename
    'trade_manager.html',
    'financial_summary.html',
    'reporting_hub.html',
]

def update_navigation(file_path):
    """Update navigation in a single file"""
    
    if not os.path.exists(file_path):
        print(f"⚠️  File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern 1: Replace existing <nav> section
    nav_pattern = r'<nav[^>]*>.*?</nav>'
    if re.search(nav_pattern, content, re.DOTALL):
        content = re.sub(nav_pattern, STANDARD_NAV.strip(), content, flags=re.DOTALL)
        print(f"✅ Replaced <nav> section in {file_path}")
    else:
        # Pattern 2: Insert after header/before main content
        # Look for common insertion points
        insertion_patterns = [
            (r'(</header>)', r'\1\n\n' + STANDARD_NAV),
            (r'(</div>\s*<!--\s*Header\s*-->)', r'\1\n\n' + STANDARD_NAV),
            (r'(<div class="container">)', STANDARD_NAV + r'\n\n    \1'),
            (r'(<main[^>]*>)', STANDARD_NAV + r'\n\n    \1'),
        ]
        
        inserted = False
        for pattern, replacement in insertion_patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content, count=1)
                print(f"✅ Inserted <nav> section in {file_path}")
                inserted = True
                break
        
        if not inserted:
            print(f"⚠️  Could not find insertion point in {file_path}")
            return False
    
    # Update CSS if needed
    if '.nav-container' not in content:
        # Find </style> tag and insert before it
        style_pattern = r'(</style>)'
        if re.search(style_pattern, content):
            content = re.sub(style_pattern, '\n' + STANDARD_NAV_CSS + r'\n    \1', content, count=1)
            print(f"✅ Added navigation CSS to {file_path}")
    else:
        # Replace existing nav CSS
        nav_css_pattern = r'/\*\s*Navigation\s*\*/.*?(?=\n\s*/\*|\n\s*</style>)'
        if re.search(nav_css_pattern, content, re.DOTALL):
            content = re.sub(nav_css_pattern, STANDARD_NAV_CSS.strip(), content, flags=re.DOTALL)
            print(f"✅ Updated navigation CSS in {file_path}")
    
    # Only write if content changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    else:
        print(f"ℹ️  No changes needed for {file_path}")
        return False

def main():
    """Update all dashboard files"""
    print("🚀 Standardizing navigation across all dashboards...\n")
    
    updated_count = 0
    failed_count = 0
    
    for file_path in DASHBOARD_FILES:
        try:
            if update_navigation(file_path):
                updated_count += 1
            print()
        except Exception as e:
            print(f"❌ Error updating {file_path}: {e}\n")
            failed_count += 1
    
    print("=" * 60)
    print(f"✅ Updated: {updated_count} files")
    print(f"❌ Failed: {failed_count} files")
    print(f"📋 Total: {len(DASHBOARD_FILES)} files")
    print("=" * 60)
    
    if updated_count > 0:
        print("\n🎯 Next steps:")
        print("1. Review changes in updated files")
        print("2. Test navigation on each dashboard")
        print("3. Commit and push to Railway for deployment")

if __name__ == "__main__":
    main()
