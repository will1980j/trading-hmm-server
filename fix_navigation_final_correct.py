import os
import re

# CORRECT navigation with Home link FIRST and centered
NAVIGATION_HTML = '''    <!-- Navigation -->
    <nav class="nav-container">
        <a href="/homepage" class="nav-link">🏠 Home</a>
        <a href="/ml-dashboard" class="nav-link">🤖 ML</a>
        <a href="/signal-lab-dashboard" class="nav-link">📊 Dashboard</a>
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

# CENTERED navigation CSS
NAVIGATION_CSS = '''        /* Navigation */
        .nav-container {
            background: #141b3d;
            padding: 12px 20px;
            border-bottom: 1px solid #2d3a5f;
            display: flex;
            justify-content: center;
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

all_files = [
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
    'reporting_hub.html'
]

def fix_file(filepath):
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove existing navigation HTML
    content = re.sub(r'<nav class="nav-container">.*?</nav>', NAVIGATION_HTML, content, flags=re.DOTALL)
    
    # Remove existing navigation CSS
    content = re.sub(r'/\* Navigation \*/.*?\.nav-link:hover \{[^}]+\}', '', content, flags=re.DOTALL)
    
    # Add centered navigation CSS before </style>
    if '</style>' in content:
        content = content.replace('</style>', f'\n{NAVIGATION_CSS}\n    </style>')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed: {filepath}")
    return True

print("Fixing navigation: Adding Home link first + centering...\n")
success_count = 0

for filename in all_files:
    if fix_file(filename):
        success_count += 1

print(f"\n✅ Successfully fixed {success_count}/{len(all_files)} files")
print("\nAll pages now have:")
print("1. Home link as FIRST navigation item")
print("2. Centered navigation bar (justify-content: center)")
print("3. Identical navigation across all pages")
