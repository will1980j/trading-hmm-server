"""
Fix MFE display issue - dashboard looking for wrong field names.
API returns: be_mfe and no_be_mfe
Dashboard was looking for: final_mfe, current_mfe, mfe
"""

# Read the dashboard
with open('templates/automated_signals_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the MFE extraction logic to use the correct field names
old_mfe_logic = '''                const mfe = signal.final_mfe || signal.current_mfe || signal.mfe;'''

new_mfe_logic = '''                // Use the dual MFE values from API (be_mfe and no_be_mfe)
                const be_mfe = signal.be_mfe || 0;
                const no_be_mfe = signal.no_be_mfe || 0;'''

content = content.replace(old_mfe_logic, new_mfe_logic)

# Update the MFE display to show both values
old_mfe_display = '''                        <td>${mfe ? mfe.toFixed(2) + 'R' : '-'}</td>'''

new_mfe_display = '''                        <td>${be_mfe ? be_mfe.toFixed(2) + 'R' : '-'}</td>
                        <td>${no_be_mfe ? no_be_mfe.toFixed(2) + 'R' : '-'}</td>'''

content = content.replace(old_mfe_display, new_mfe_display)

# Update the table headers to show both MFE columns
old_headers = '''                                <th>Session</th>
                                <th>MFE</th>
                                <th>Status</th>'''

new_headers = '''                                <th>Session</th>
                                <th>MFE (BE=1)</th>
                                <th>MFE (No BE)</th>
                                <th>Status</th>'''

content = content.replace(old_headers, new_headers)

# Update colspan for empty state
content = content.replace('<td colspan="8">', '<td colspan="9">')

# Write the fixed dashboard
with open('templates/automated_signals_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ MFE display issue fixed!")
print("Dashboard now correctly displays:")
print("  - MFE (BE=1) column showing be_mfe values")
print("  - MFE (No BE) column showing no_be_mfe values")
print("\nNo more '-' for active trades with MFE data!")
