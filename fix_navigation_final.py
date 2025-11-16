"""
FIX IT PROPERLY THIS TIME
1. Add Home link as FIRST navigation item
2. Remove duplicate navigation comments
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

# CORRECT navigation with Home link FIRST
CORRECT_NAV = '''    <!-- Navigation -->
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
    </nav>
'''

def fix_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"\nFixing: {file_path}")
    
    # Remove ALL navigation sections (including duplicates and comments)
    content = re.sub(r'<!--\s*Navigation\s*-->.*?</nav>', '', content, flags=re.DOTALL)
    content = re.sub(r'<nav[^>]*class="nav-container"[^>]*>.*?</nav>', '', content, flags=re.DOTALL)
    
    # Find where to insert (after header)
    header_end = content.find('</div>\n    </div>')  # End of header
    if header_end > 0:
        # Insert correct navigation after header
        insert_pos = content.find('\n', header_end + 16)
        content = content[:insert_pos] + '\n' + CORRECT_NAV + content[insert_pos:]
        print("✅ Added correct navigation with Home link first")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    for file_path in DASHBOARD_FILES:
        fix_file(file_path)
    
    print("\n✅ DONE - Home link added as first item, duplicates removed")

if __name__ == "__main__":
    main()
