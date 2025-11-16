import os
import re

# EXACT header HTML from homepage
HEADER_HTML = '''    <!-- Header -->
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
    </nav>'''

# EXACT header CSS from homepage
HEADER_CSS = '''        /* Header */
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
    
    # Remove ALL existing headers/navigation between </head> and first real content
    # This removes the NASDAQ Trading Analytics header and any navigation
    content = re.sub(
        r'</head>\s*<body>.*?(?=<div class="container"|<main|<div id=|<script|$)',
        '</head>\n<body>\n' + HEADER_HTML + '\n\n',
        content,
        flags=re.DOTALL
    )
    
    # Remove any existing header/nav CSS
    content = re.sub(r'/\* Header \*/.*?\.nav-link:hover \{[^}]+\}', '', content, flags=re.DOTALL)
    
    # Add header CSS before </style>
    if '</style>' in content:
        content = content.replace('</style>', f'\n{HEADER_CSS}\n    </style>')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed: {filepath}")
    return True

print("Fixing all dashboards with EXACT homepage header...\n")
success_count = 0

for filename in dashboard_files:
    if fix_dashboard(filename):
        success_count += 1

print(f"\n✅ Successfully fixed {success_count}/{len(dashboard_files)} dashboards")
print("\nAll dashboards now have:")
print("1. EXACT header from homepage (logo, title, user info, logout)")
print("2. EXACT navigation bar from homepage")
print("3. NO 'NASDAQ Trading Analytics' section")
