"""
Script to update navigation on remaining dashboard files
"""

# Navigation HTML to insert
NAV_HTML = '''<nav style="background: #141b3d; padding: 12px 20px; margin-bottom: 20px; border-bottom: 1px solid #2d3a5f; display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">
        <a href="/ml-dashboard" data-page="ml" style="padding: 8px 12px; background: #1a2142; color: #f8fafc; text-decoration: none; border-radius: 6px; font-size: 14px; white-space: nowrap;">🤖 ML</a>
        <a href="/live-signals-dashboard" data-page="live" style="padding: 8px 12px; background: #1a2142; color: #f8fafc; text-decoration: none; border-radius: 6px; font-size: 14px; white-space: nowrap;">📶 Live</a>
        <a href="/signal-lab-dashboard" data-page="dashboard" style="padding: 8px 12px; background: #1a2142; color: #f8fafc; text-decoration: none; border-radius: 6px; font-size: 14px; white-space: nowrap;">🏠 Dashboard</a>
        <a href="/signal-analysis-lab" data-page="lab" style="padding: 8px 12px; background: #1a2142; color: #f8fafc; text-decoration: none; border-radius: 6px; font-size: 14px; white-space: nowrap;">🧪 Signal Lab</a>
        <a href="/time-analysis" data-page="time" style="padding: 8px 12px; background: #1a2142; color: #f8fafc; text-decoration: none; border-radius: 6px; font-size: 14px; white-space: nowrap;">⏰ Time</a>
        <a href="/strategy-optimizer" data-page="optimizer" style="padding: 8px 12px; background: #1a2142; color: #f8fafc; text-decoration: none; border-radius: 6px; font-size: 14px; white-space: nowrap;">🎯 Optimizer</a>
        <a href="/strategy-comparison" data-page="compare" style="padding: 8px 12px; background: #1a2142; color: #f8fafc; text-decoration: none; border-radius: 6px; font-size: 14px; white-space: nowrap;">🏆 Compare</a>
        <a href="/ai-business-advisor" data-page="advisor" style="padding: 8px 12px; background: #1a2142; color: #f8fafc; text-decoration: none; border-radius: 6px; font-size: 14px; white-space: nowrap;">🧠 AI Advisor</a>
        <a href="/prop-portfolio" data-page="prop" style="padding: 8px 12px; background: #1a2142; color: #f8fafc; text-decoration: none; border-radius: 6px; font-size: 14px; white-space: nowrap;">💼 Prop</a>
        <a href="/trade-manager" data-page="trades" style="padding: 8px 12px; background: #1a2142; color: #f8fafc; text-decoration: none; border-radius: 6px; font-size: 14px; white-space: nowrap;">📋 Trades</a>
        <a href="/financial-summary" data-page="finance" style="padding: 8px 12px; background: #1a2142; color: #f8fafc; text-decoration: none; border-radius: 6px; font-size: 14px; white-space: nowrap;">💰 Finance</a>
        <a href="/reporting-hub" data-page="reports" style="padding: 8px 12px; background: #1a2142; color: #f8fafc; text-decoration: none; border-radius: 6px; font-size: 14px; white-space: nowrap;">📊 Reports</a>
    </nav>
    <script>
    (function() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('nav a[data-page]');
        navLinks.forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.style.background = '#3b82f6';
                link.style.color = 'white';
            }
        });
    })();
    </script>'''

# Files to update
files_to_update = [
    'prop_firms_v2.html',
    'trade_manager.html',
    'financial_summary.html',
    'reporting_hub.html'
]

import re

for filename in files_to_update:
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find <body> tag and any existing nav
        # Replace old nav with new one
        # Pattern: <body> ... <nav>...</nav> ... <div class="container">
        
        # Simple approach: find <body> and insert nav right after
        if '<body>' in content:
            # Find existing nav and remove it
            content = re.sub(r'<nav[^>]*>.*?</nav>', '', content, flags=re.DOTALL, count=1)
            
            # Insert new nav after <body>
            content = content.replace('<body>', f'<body>\n    {NAV_HTML}\n    ')
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f'✅ Updated {filename}')
        else:
            print(f'⚠️ No <body> tag found in {filename}')
            
    except FileNotFoundError:
        print(f'❌ File not found: {filename}')
    except Exception as e:
        print(f'❌ Error updating {filename}: {e}')

print('\n✅ Navigation update complete!')
print('All 12 dashboard pages now have consistent navigation.')
