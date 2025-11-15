#!/usr/bin/env python3
"""Replace the renderPriceChartJourney function with Option 1 visualization"""

# Read the new function
with open('journey_viz_option1.js', 'r', encoding='utf-8') as f:
    new_function = f.read()

# Read the HTML file
with open('automated_signals_dashboard.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Find the start and end of the function
start_marker = "        function renderPriceChartJourney(trade) {"
end_marker = "        .text(isActive ? '● ACTIVE' : '● COMPLETED');\n}"

start_idx = html_content.find(start_marker)
end_idx = html_content.find(end_marker, start_idx)

if start_idx == -1 or end_idx == -1:
    print("ERROR: Could not find function markers")
    print(f"Start found: {start_idx != -1}")
    print(f"End found: {end_idx != -1}")
    exit(1)

# Calculate the end position (include the closing brace)
end_idx = end_idx + len(end_marker)

print(f"Found function from position {start_idx} to {end_idx}")
print(f"Function length: {end_idx - start_idx} characters")

# Replace the function
new_html = html_content[:start_idx] + new_function + html_content[end_idx:]

# Write back
with open('automated_signals_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print("✅ Successfully replaced renderPriceChartJourney function")
print(f"New file size: {len(new_html)} characters")
