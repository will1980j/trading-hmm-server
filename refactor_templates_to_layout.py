"""
Refactor HTML templates to use the unified layout system.
This script will convert all dashboard templates to extend layout.html
"""

import re
import os

def extract_content_section(html_content):
    """Extract the main content section from HTML, removing DOCTYPE, head, nav, etc."""
    # Remove everything before the main content starts
    # Look for the container or main content div after navigation
    
    # Find where the actual page content starts (after nav)
    nav_end = html_content.find('</nav>')
    if nav_end == -1:
        # Try finding nav-container end
        nav_end = html_content.find('</div><!-- End nav')
        if nav_end == -1:
            nav_end = 0
    
    # Get content after navigation
    content_start = html_content.find('<div', nav_end)
    if content_start == -1:
        content_start = html_content.find('<main', nav_end)
    
    # Find where body ends
    body_end = html_content.rfind('</body>')
    if body_end == -1:
        body_end = len(html_content)
    
    # Extract the content
    content = html_content[content_start:body_end]
    
    # Clean up - remove closing html tag if present
    content = content.replace('</html>', '').strip()
    
    return content

def extract_scripts(html_content):
    """Extract all <script> tags from the content"""
    script_pattern = r'<script[^>]*>.*?</script>'
    scripts = re.findall(script_pattern, html_content, re.DOTALL)
    
    # Remove inline event handlers and keep only substantial scripts
    substantial_scripts = []
    for script in scripts:
        # Skip very small scripts (likely just inline handlers)
        if len(script) > 100:
            substantial_scripts.append(script)
    
    return '\n'.join(substantial_scripts)

def remove_scripts_from_content(content):
    """Remove script tags from content"""
    script_pattern = r'<script[^>]*>.*?</script>'
    return re.sub(script_pattern, '', content, flags=re.DOTALL)

def extract_external_scripts(html_content):
    """Extract external script references from head"""
    head_match = re.search(r'<head>(.*?)</head>', html_content, re.DOTALL)
    if not head_match:
        return []
    
    head_content = head_match.group(1)
    script_pattern = r'<script[^>]*src=["\']([^"\']+)["\'][^>]*></script>'
    scripts = re.findall(script_pattern, head_content)
    
    return scripts

def refactor_template(input_file, output_file, page_title, extra_head_scripts=None):
    """Refactor a template file to use layout.html"""
    
    print(f"Refactoring {input_file}...")
    
    # Read the original file with error handling for encoding
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
    except UnicodeDecodeError:
        try:
            with open(input_file, 'r', encoding='latin-1') as f:
                original_content = f.read()
        except Exception as e:
            print(f"❌ Error reading {input_file}: {e}")
            return
    
    # Extract external scripts from head
    external_scripts = extract_external_scripts(original_content)
    
    # Extract main content
    content = extract_content_section(original_content)
    
    # Extract and remove scripts from content
    scripts = extract_scripts(content)
    content = remove_scripts_from_content(content)
    
    # Build the new template
    new_template = f"""{{%extends 'layout.html' %}}

{{% block page_title %}}{page_title}{{%endblock %}}
"""
    
    # Add extra_head block if there are external scripts
    if external_scripts or extra_head_scripts:
        new_template += "\n{% block extra_head %}\n"
        for script_src in external_scripts:
            if 'd3.js' in script_src or 'chart.js' in script_src or 'socket.io' in script_src:
                new_template += f'<script src="{script_src}"></script>\n'
        if extra_head_scripts:
            for script in extra_head_scripts:
                new_template += f'{script}\n'
        new_template += "{% endblock %}\n"
    
    # Add content block
    new_template += f"""
{{% block content %}}
{content.strip()}
{{% endblock %}}
"""
    
    # Add scripts block if there are scripts
    if scripts.strip():
        new_template += f"""
{{% block extra_js %}}
{scripts.strip()}
{{% endblock %}}
"""
    
    # Write the new template
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(new_template)
    
    print(f"✅ Created {output_file}")

# Refactor all templates
templates_to_refactor = [
    {
        'input': 'signal_analysis_lab.html',
        'output': 'signal_analysis_lab.html',
        'title': 'Signal Analysis Lab — Second Skies',
        'extra_head': None
    },
    {
        'input': 'automated_signals_dashboard.html',
        'output': 'automated_signals_dashboard.html',
        'title': 'Automated Signals — Second Skies',
        'extra_head': None
    },
    {
        'input': 'ml_feature_dashboard.html',
        'output': 'ml_feature_dashboard.html',
        'title': 'ML Intelligence Hub — Second Skies',
        'extra_head': None
    },
    {
        'input': 'time_analysis.html',
        'output': 'time_analysis.html',
        'title': 'Time Analysis — Second Skies',
        'extra_head': None
    },
    {
        'input': 'strategy_comparison.html',
        'output': 'strategy_comparison.html',
        'title': 'Strategy Comparison — Second Skies',
        'extra_head': None
    },
    {
        'input': 'ai_business_dashboard.html',
        'output': 'ai_business_dashboard.html',
        'title': 'AI Business Advisor — Second Skies',
        'extra_head': None
    },
    {
        'input': 'prop_firms_v2.html',
        'output': 'prop_firms_v2.html',
        'title': 'Prop Portfolio — Second Skies',
        'extra_head': None
    },
    {
        'input': 'trade_manager.html',
        'output': 'trade_manager.html',
        'title': 'Trade Manager — Second Skies',
        'extra_head': None
    },
    {
        'input': 'financial_summary.html',
        'output': 'financial_summary.html',
        'title': 'Financial Summary — Second Skies',
        'extra_head': None
    },
    {
        'input': 'reporting_hub.html',
        'output': 'reporting_hub.html',
        'title': 'Reporting Hub — Second Skies',
        'extra_head': None
    }
]

print("🚀 Starting template refactoring...\n")

for template in templates_to_refactor:
    if os.path.exists(template['input']):
        refactor_template(
            template['input'],
            template['output'],
            template['title'],
            template.get('extra_head')
        )
    else:
        print(f"⚠️  File not found: {template['input']}")

print("\n✅ All templates refactored!")
print("\n📝 Creating missing strategy_optimizer.html...")

# Create the missing strategy_optimizer.html
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
print("\n🎉 Template refactoring complete!")
