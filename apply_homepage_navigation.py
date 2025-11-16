import os
import re

# The exact navigation HTML from homepage
NAVIGATION_HTML = '''    <!-- Navigation -->
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

# The exact navigation CSS from homepage
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

# Dashboard files to update
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

def apply_navigation(filepath):
    """Apply homepage navigation to a dashboard file"""
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove any existing navigation
    content = re.sub(r'<nav[^>]*>.*?</nav>', '', content, flags=re.DOTALL)
    
    # Remove any existing nav-container or nav-link CSS
    content = re.sub(r'/\* Navigation \*/.*?\.nav-link:hover \{[^}]+\}', '', content, flags=re.DOTALL)
    
    # Add navigation CSS before </style>
    if '</style>' in content:
        content = content.replace('</style>', f'{NAVIGATION_CSS}\n    </style>')
    
    # Add navigation HTML after </head> or after opening <body>
    if '</head>' in content:
        # Insert right after </head> and before <body>
        content = content.replace('</head>', f'</head>\n<body>\n{NAVIGATION_HTML}\n')
        # Remove duplicate <body> tags
        content = re.sub(r'<body>\s*<body>', '<body>', content)
    elif '<body>' in content:
        content = content.replace('<body>', f'<body>\n{NAVIGATION_HTML}\n')
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Updated: {filepath}")
    return True

# Apply to all dashboard files
print("Applying homepage navigation to all dashboards...\n")
success_count = 0

for filename in dashboard_files:
    if apply_navigation(filename):
        success_count += 1

print(f"\n✅ Successfully updated {success_count}/{len(dashboard_files)} dashboard files")
print("\nNavigation now matches homepage exactly!")
