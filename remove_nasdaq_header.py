import os
import re

# ONLY navigation - NO header section
NAVIGATION_ONLY = '''    <!-- Navigation -->
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

# ONLY navigation CSS - NO header CSS
NAVIGATION_CSS = '''        /* Navigation */
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

dashboard_files = [
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

def fix_dashboard(filepath):
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove EVERYTHING between </head> and first real content
    content = re.sub(
        r'</head>\s*<body>.*?(?=<div class="container"|<main|<div id=|<script|$)',
        '</head>\n<body>\n' + NAVIGATION_ONLY + '\n\n',
        content,
        flags=re.DOTALL
    )
    
    # Remove ALL header CSS (logo, platform-info, user-section, etc.)
    content = re.sub(r'/\* Header \*/.*?(?=/\* Navigation \*/|</style>)', '', content, flags=re.DOTALL)
    
    # Remove any existing nav CSS
    content = re.sub(r'/\* Navigation \*/.*?\.nav-link:hover \{[^}]+\}', '', content, flags=re.DOTALL)
    
    # Add ONLY navigation CSS before </style>
    if '</style>' in content:
        content = content.replace('</style>', f'\n{NAVIGATION_CSS}\n    </style>')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed: {filepath}")
    return True

print("Removing NASDAQ header, keeping ONLY navigation bar...\n")
success_count = 0

for filename in dashboard_files:
    if fix_dashboard(filename):
        success_count += 1

print(f"\n✅ Successfully fixed {success_count}/{len(dashboard_files)} dashboards")
print("\nAll dashboards now have:")
print("1. ONLY navigation bar (NO NASDAQ header)")
print("2. Navigation links matching homepage")
print("3. NO logo, NO title, NO user info section")
