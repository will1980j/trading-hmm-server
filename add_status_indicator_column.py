"""
Add a visual status indicator column to the Automated Signals Dashboard.
Shows green/blue pulsating dot based on BE status.
"""

import re

# Read the dashboard
with open('templates/automated_signals_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add CSS for the status indicator dots
css_addition = """
        /* Trade Status Indicators */
        .trade-status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            animation: pulse 2s ease-in-out infinite;
        }
        
        .trade-status-indicator.both-active {
            background-color: #10b981; /* Green - both strategies active */
        }
        
        .trade-status-indicator.be-triggered {
            background-color: #3b82f6; /* Blue - BE triggered, No BE still active */
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
"""

# Find the closing </style> tag and insert before it
content = content.replace('</style>', css_addition + '    </style>')

# 2. Add a new column header for the status indicator
old_header = '''                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>Direction</th>
                                <th>Entry</th>
                                <th>Stop Loss</th>
                                <th>Session</th>
                                <th>MFE</th>
                                <th>Status</th>
                            </tr>
                        </thead>'''

new_header = '''                        <thead>
                            <tr>
                                <th>●</th>
                                <th>Time</th>
                                <th>Direction</th>
                                <th>Entry</th>
                                <th>Stop Loss</th>
                                <th>Session</th>
                                <th>MFE</th>
                                <th>Status</th>
                            </tr>
                        </thead>'''

content = content.replace(old_header, new_header)

# 3. Update the empty state colspan
content = content.replace('<td colspan="7">', '<td colspan="8">')

# 4. Update the row rendering to include status indicator
old_row_start = '''                return `
                    <tr>
                        <td>${signal.time || (timestamp ? formatTime(timestamp) : '-')}</td>'''

new_row_start = '''                // Determine status indicator color
                const beTriggered = signal.be_triggered || false;
                const isActive = status === 'CONFIRMED' || status === 'ACTIVE';
                const indicatorClass = isActive ? (beTriggered ? 'be-triggered' : 'both-active') : '';
                const indicatorHtml = isActive ? `<span class="trade-status-indicator ${indicatorClass}"></span>` : '';
                
                return `
                    <tr>
                        <td style="text-align: center;">${indicatorHtml}</td>
                        <td>${signal.time || (timestamp ? formatTime(timestamp) : '-')}</td>'''

content = content.replace(old_row_start, new_row_start)

# Write the updated dashboard
with open('templates/automated_signals_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Status indicator column added to dashboard!")
print("🟢 Green dot = Both BE=1 and No BE strategies active")
print("🔵 Blue dot = BE triggered, No BE still active")
print("   (No dot shown for resolved trades)")
print("\nNO INDICATOR CHANGES - indicator remains untouched!")
