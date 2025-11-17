"""
Fix trade numbering in automated signals dashboard
Makes first trade of the day = #1, counting up from there
"""

# Read the file
with open('automated_signals_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the specific section
old_code = '''            tbody.innerHTML = filteredSignals.slice(0, 50).map((signal, index) => {
                const direction = signal.bias || signal.direction;
                const status = (signal.trade_status || signal.status || 'unknown').toUpperCase();
                
                // Determine if trade is active'''

new_code = '''            tbody.innerHTML = filteredSignals.slice(0, 50).map((signal, index) => {
                const direction = signal.bias || signal.direction;
                const status = (signal.trade_status || signal.status || 'unknown').toUpperCase();
                const tradeNumber = filteredSignals.length - index;
                
                // Determine if trade is active'''

# Replace
if old_code in content:
    content = content.replace(old_code, new_code)
    print("✓ Added tradeNumber calculation")
else:
    print("✗ Could not find the code to replace")
    exit(1)

# Now replace the display of the trade number
old_display = '''                        <td onclick="showTradeDetail('${signal.trade_id}')" style="cursor: pointer;"><span class="trade-number">${index + 1}</span></td>'''

new_display = '''                        <td onclick="showTradeDetail('${signal.trade_id}')" style="cursor: pointer;"><span class="trade-number">${tradeNumber}</span></td>'''

if old_display in content:
    content = content.replace(old_display, new_display)
    print("✓ Updated trade number display")
else:
    print("✗ Could not find trade number display to replace")
    exit(1)

# Write back
with open('automated_signals_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✓ Trade numbering fixed successfully!")
print("  - First trade of the day will be #1")
print("  - Numbers count up chronologically")
