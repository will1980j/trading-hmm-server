"""
PROPERLY fix navigation - add complete header + nav structure from homepage
"""

import os
import re

# Complete header + navigation from homepage
COMPLETE_HEADER_NAV = '''    <!-- Header -->
    <div class="header">
        <div class="logo-section">
            <div class="logo">📈</div>
            <div class="platform-info">
                <h1>NASDAQ Trading Analytics</h1>
                <p>Professional Day Trading Platform</p>
            </div>
        </div>
        <div class="user-section">
            <div class="user-info">
                <div class="user-name">Trading Professional</div>
                <div class="user-status">● Online</div>
            </div>
            <a href="/logout" class="logout-btn">Logout</a>
        </div>
    </div>

    <!-- Navigation -->
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
    </nav>
'''

# Complete CSS from homepage
COMPLETE_CSS = '''        /* Header */
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

def fix_file(file_path):
    """Properly fix a file"""
    
    if not os.path.exists(file_path):
        print(f"⚠️  File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Step 1: Remove ALL existing navigation/header code
    patterns_to_remove = [
        (r'<nav[^>]*>.*?</nav>', 'old nav'),
        (r'<div class="header">.*?</div>\s*</div>', 'old header'),
        (r'<!--\s*Header\s*-->.*?<!--\s*Navigation\s*-->', 'header comment block'),
        (r'<!--\s*Navigation\s*-->.*?</nav>', 'nav comment block'),
    ]
    
    for pattern, name in patterns_to_remove:
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, '', content, flags=re.DOTALL)
            print(f"   Removed {name}")
    
    # Step 2: Remove old CSS
    css_patterns_to_remove = [
        r'/\*\s*Header\s*\*/.*?(?=/\*|</style>)',
        r'/\*\s*Navigation\s*\*/.*?(?=/\*|</style>)',
        r'\.header\s*{[^}]+}',
        r'\.nav-container\s*{[^}]+}',
        r'\.nav-link[^{]*{[^}]+}',
    ]
    
    for pattern in css_patterns_to_remove:
        content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # Step 3: Add complete CSS before </style>
    if '</style>' in content:
        content = content.replace('</style>', '\n' + COMPLETE_CSS + '\n    </style>', 1)
        print("   Added complete CSS")
    
    # Step 4: Add complete header + nav after <body>
    body_pattern = r'(<body[^>]*>)'
    if re.search(body_pattern, content):
        content = re.sub(body_pattern, r'\1\n' + COMPLETE_HEADER_NAV + '\n', content, count=1)
        print("   Added complete header + navigation")
    else:
        print("   ❌ Could not find <body> tag")
        return False
    
    # Only write if changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    else:
        print("   No changes needed")
        return False

def main():
    """Fix all files"""
    print("🔧 PROPERLY FIXING NAVIGATION - COMPLETE HEADER + NAV STRUCTURE")
    print("="*80)
    
    fixed_count = 0
    
    for file_path in DASHBOARD_FILES:
        print(f"\n📄 {file_path}")
        print("-" * 80)
        if fix_file(file_path):
            fixed_count += 1
    
    print("\n" + "="*80)
    print(f"✅ Fixed {fixed_count}/{len(DASHBOARD_FILES)} files")
    print("="*80)
    
    if fixed_count > 0:
        print("\n🎯 Next: Run visual_navigation_audit.py to verify")

if __name__ == "__main__":
    main()
