"""
Manual template refactoring - Following strict GPT5.1 instructions
Refactor each HTML template to use layout.html following the exact pattern from signal_lab_dashboard.html
"""

import os
import re

# First, let's create the missing strategy_optimizer.html
print("Creating strategy_optimizer.html...")

strategy_optimizer_content = """{% extends 'layout.html' %}

{% block page_title %}Strategy Optimizer — Second Skies{% endblock %}

{% block content %}
<section class="section">
    <h1 class="section-title">Strategy Optimizer</h1>
    <p class="section-subtitle">
        This page will host the exact-methodology backtesting and optimization engine for your NASDAQ scalping strategies.
        It is currently in scaffold mode and will be wired to real data and logic as development continues.
    </p>
</section>
{% endblock %}

{% block extra_js %}
{# No page-specific JS yet. This will be added when Strategy Optimizer logic is implemented. #}
{% endblock %}
"""

with open('strategy_optimizer.html', 'w', encoding='utf-8') as f:
    f.write(strategy_optimizer_content)

print("✅ Created strategy_optimizer.html")

print("\n" + "="*80)
print("MANUAL REFACTORING INSTRUCTIONS")
print("="*80)
print("""
For each of the following files, you need to manually refactor them:

FILES TO REFACTOR:
1. signal_analysis_lab.html
2. automated_signals_dashboard.html  
3. ml_feature_dashboard.html
4. time_analysis.html
5. strategy_comparison.html
6. ai_business_dashboard.html
7. prop_firms_v2.html
8. trade_manager.html
9. financial_summary.html
10. reporting_hub.html

REFACTORING PATTERN (from signal_lab_dashboard.html):

{% extends 'layout.html' %}

{% block page_title %}[PAGE TITLE] — Second Skies{% endblock %}

{% block extra_head %}
[External scripts like D3.js, Chart.js, Socket.IO if needed]
{% endblock %}

{% block content %}
[ALL PAGE CONTENT - everything between navigation end and </body>]
{% endblock %}

{% block extra_js %}
[ALL <script> tags from the page]
{% endblock %}

WHAT TO REMOVE:
- <!DOCTYPE html>
- <html>, </html>
- <head>, </head> (but extract external scripts to extra_head block)
- <body>, </body>
- All navigation markup
- All header markup

WHAT TO KEEP:
- All page-specific content (divs, sections, cards, tables, charts)
- All IDs and classes (unchanged)
- All inline styles
- All data attributes

The script has created strategy_optimizer.html.
Now you need to manually refactor the other 10 files.
""")

print("\n✅ strategy_optimizer.html created successfully!")
print("⚠️  Manual refactoring required for the remaining 10 files")
