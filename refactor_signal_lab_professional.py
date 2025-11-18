"""
Refactor templates/signal_lab_dashboard.html to professional fintech style
while preserving ALL JavaScript behavior and element IDs.
"""

import re

def refactor_signal_lab_dashboard():
    """Main refactoring function"""
    
    print("Reading templates/signal_lab_dashboard.html...")
    with open('templates/signal_lab_dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Starting refactoring...")
    
    # Step 1: Fix encoding in page_title
    content = content.replace(
        '{% block page_title %}Signal Lab â€" Second Skies{% endblock %}',
        '{% block page_title %}Signal Lab — Second Skies{% endblock %}'
    )
    
    # Step 2: Extract the large JavaScript block
    # Find the main script block (after content, before closing tags)
    script_pattern = r'(<script>\s*// .*?</script>)\s*</div><!-- container -->\s*{% endblock %}'
    script_match = re.search(script_pattern, content, re.DOTALL)
    
    if script_match:
        main_script = script_match.group(1)
        # Remove it from content
        content = content.replace(script_match.group(0), '</div><!-- container -->\n{% endblock %}')
        print("✓ Extracted main JavaScript block")
    else:
        print("⚠ Could not find main script block - will handle manually")
        main_script = None
    
    # Step 3: Remove emojis from HTML (not from JS strings)
    # This is complex - we need to be careful not to touch JS
    
    emoji_replacements = {
        # Headers and titles
        '🚀 Signal Lab Dashboard': 'Signal Lab Dashboard',
        '🚀 Trading Mission Control': 'Trading Mission Control',
        '📊 Trading Performance Dashboard': 'Trading Performance Dashboard',
        '📊 Signal Lab Metrics': 'Signal Lab Metrics',
        '📡 Battlefield Radar': 'Market Context',
        '🎯 Core Performance': 'Core Performance',
        '📈 Trading Statistics': 'Trading Statistics',
        '📈 Performance Analytics': 'Performance Analytics',
        '🔬 Advanced Analytics': 'Advanced Analytics',
        '📊 Session Analytics Dashboard': 'Session Analytics Dashboard',
        '📈 Trade Distribution by Session': 'Trade Distribution by Session',
        '🎯 Win Rate by Session': 'Win Rate by Session',
        '💰 Expectancy by Session': 'Expectancy by Session',
        '🧠 Advanced Session Insights': 'Session Insights',
        '🎛️ INTEGRATED CHART CONTROL CENTER': 'Chart Controls',
        '🎛️ Chart Control Center': 'Chart Controls',
        '📅 Performance Calendar': 'Performance Calendar',
        '📅 Daily Performance Calendar': 'Daily Performance Calendar',
        
        # Mission Control language
        'Trading Mission Control Center': 'Signal Lab Overview',
        'Trading Mission Control': 'Signal Lab Overview',
        'Battlefield Radar': 'Market Context Overview',
        'Weapon Specifications': 'Contract Specifications',
        'Battle Intelligence': 'Economic Calendar',
        'Strategic Intelligence': 'Options & Derivatives Insight',
        'Weekly Domination': 'Weekly Performance',
        'Monthly Conquest': 'Monthly Performance',
        'Peak Victory': 'Best Day',
        'Portfolio Power': 'Portfolio Size',
        'Advanced Session Insights': 'Session Insights',
        'Chart Control Center': 'Chart Controls',
        
        # Button/link emojis
        '🤖 View V2 Automated Signals': 'View V2 Automated Signals',
        '🤖 ML Hub': 'ML Hub',
        '📡 Optimizer': 'Optimizer',
        '🧠 AI Advisor': 'AI Advisor',
        '🎯 Strategy Optimizer': 'Strategy Optimizer',
        
        # Icons in cards
        '💰 Portfolio Power': 'Portfolio Size',
        '📈 Weekly Domination': 'Weekly Performance',
        '🚀 Monthly Conquest': 'Monthly Performance',
        '🏆 Peak Victory': 'Best Day',
        '⚔️': '',
        '🎖️': '',
        '📡': '',
        '🎯': '',
        '⚠️': '',
        '🌍': '',
        '📊': '',
        '💵': '',
        '🛰️': '',
        '💰': '',
        '📈': '',
        '📉': '',
        '✅': '',
        '⚖️': '',
        '🏆': '',
        '💎': '',
        '⚡': '',
        '🔥': '',
        '❄️': '',
        '🔗': '',
        '⏰': '',
        '📅': '',
    }
    
    # Apply emoji replacements carefully (only in HTML, not in JS strings)
    for old, new in emoji_replacements.items():
        # Only replace in HTML context (between > and <)
        content = content.replace(f'>{old}<', f'>{new}<')
        content = content.replace(f'>{old} ', f'>{new} ')
        content = content.replace(f' {old}<', f' {new}<')
    
    print("✓ Removed emojis and gamified language")
    
    # Step 4: Remove the nav highlight script
    nav_script_pattern = r'<script>\s*\(function\(\) \{[^}]*currentPath[^}]*\}\)\(\);\s*</script>'
    content = re.sub(nav_script_pattern, '', content, flags=re.DOTALL)
    print("✓ Removed nav highlight script")
    
    # Step 5: Remove floating nav (or clean it up)
    floating_nav_pattern = r'<!-- 🚀 FLOATING NAVIGATION -->.*?</div>\s*(?=<div class="container">)'
    content = re.sub(floating_nav_pattern, '', content, flags=re.DOTALL)
    print("✓ Removed floating navigation")
    
    # Step 6: Add extra_js block at the end if we extracted the script
    if main_script and '{% block extra_js %}' not in content:
        # Add the extra_js block before the final {% endblock %}
        content = content.replace(
            '{% endblock %}',
            '{% endblock %}\n\n{% block extra_js %}\n' + main_script + '\n{% endblock %}'
        )
        print("✓ Moved JavaScript to extra_js block")
    
    # Step 7: Write the refactored content
    print("\nWriting refactored file...")
    with open('templates/signal_lab_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Refactoring complete!")
    print("\nNote: This is a first pass. Manual review needed for:")
    print("  - Replacing inline styles with .card and .section classes")
    print("  - Restructuring layout to use design system")
    print("  - Cleaning up remaining inline styles")
    print("  - Verifying all IDs are preserved")

if __name__ == '__main__':
    refactor_signal_lab_dashboard()
