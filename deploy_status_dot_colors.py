"""
Simple dashboard-only fix for status dot colors.
NO INDICATOR CHANGES - just cosmetic dashboard update.

Logic:
- Green dot = Both strategies active (no BE_TRIGGERED event yet)
- Blue dot = BE triggered, No BE still active (has BE_TRIGGERED event, no EXIT event)
"""

import os

# Read the current dashboard
with open('templates/automated_signals_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the status dot rendering section and update it
old_status_dot = '''                        <td style="text-align: center;">
                            <span class="status-dot"></span>
                        </td>'''

new_status_dot = '''                        <td style="text-align: center;">
                            <span class="status-dot" data-be-triggered="false"></span>
                        </td>'''

# Replace the status dot HTML
content = content.replace(old_status_dot, new_status_dot)

# Find the JavaScript section that populates active trades
# We need to update the status dot based on whether BE_TRIGGERED event exists

old_js_section = '''                    row.innerHTML = `
                        <td style="text-align: center;">
                            <span class="status-dot"></span>
                        </td>'''

new_js_section = '''                    row.innerHTML = `
                        <td style="text-align: center;">
                            <span class="status-dot" data-be-triggered="${trade.be_triggered ? 'true' : 'false'}"></span>
                        </td>'''

content = content.replace(old_js_section, new_js_section)

# Update the CSS to handle green vs blue dots
old_css = '''.status-dot {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background-color: #ef4444;
    animation: pulse 2s ease-in-out infinite;
}'''

new_css = '''.status-dot {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background-color: #10b981; /* Green by default - both strategies active */
    animation: pulse 2s ease-in-out infinite;
}

.status-dot[data-be-triggered="true"] {
    background-color: #3b82f6; /* Blue when BE triggered, No BE still active */
}'''

content = content.replace(old_css, new_css)

# Write the updated dashboard
with open('templates/automated_signals_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Dashboard updated with status dot colors!")
print("🟢 Green = Both strategies active")
print("🔵 Blue = BE triggered, No BE still active")
print("\nNO INDICATOR CHANGES - indicator remains untouched and working perfectly!")
