"""
Enhance Trading Floor Dashboard with:
1. Calendar Heatmap (hourly 6 AM - 8 PM)
2. Target Progress Indicators (1R, 2R, 3R checkmarks)
"""

import re

# Read current dashboard
with open('automated_signals_dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add calendar heatmap CSS after the completed trades styles
calendar_css = """
        /* Calendar Heatmap */
        .calendar-section {
            margin-bottom: 20px;
        }
        
        .calendar-grid {
            display: grid;
            grid-template-columns: repeat(14, 1fr);
            gap: 8px;
            margin-top: 16px;
        }
        
        .calendar-hour {
            aspect-ratio: 1;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .calendar-hour:hover {
            transform: scale(1.1);
            z-index: 10;
            box-shadow: 0 4px 12px rgba(0, 212, 255, 0.3);
        }
        
        .hour-label {
            color: #64748b;
            font-size: 10px;
            margin-bottom: 4px;
        }
        
        .hour-count {
            font-size: 16px;
            font-weight: 700;
            color: #e1e8ed;
        }
        
        /* Target Progress */
        .target-progress {
            display: flex;
            gap: 8px;
            margin: 12px 0;
            flex-wrap: wrap;
        }
        
        .target-item {
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            background: rgba(255, 255, 255, 0.05);
            color: #64748b;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        
        .target-item.hit {
            background: rgba(16, 185, 129, 0.2);
            color: #10b981;
        }
        
        .target-check {
            font-size: 12px;
        }
"""

# Insert calendar CSS before </style>
html = html.replace('</style>', calendar_css + '\n    </style>')

# Add calendar heatmap HTML after active trades section
calendar_html = """
            <!-- Calendar Heatmap -->
            <div class="calendar-section">
                <div class="section-title">📅 Daily Trading Calendar</div>
                <div class="chart-card">
                    <div class="calendar-grid" id="calendarGrid"></div>
                </div>
            </div>
"""

# Insert calendar after active trades section
html = html.replace('</div>\n\n            <!-- Charts Grid -->', 
                    '</div>\n\n' + calendar_html + '\n            <!-- Charts Grid -->')

# Update active trade card to include target progress
old_trade_card = """                    <div class="trade-details">
                        Entry: ${trade.entry_price || 'N/A'}<br>
                        Stop Loss: ${trade.stop_loss_price || 'N/A'}<br>
                        Session: ${trade.session || 'N/A'}
                    </div>"""

new_trade_card = """                    <div class="target-progress">
                        <div class="target-item ${(trade.current_mfe || 0) >= 1 ? 'hit' : ''}">
                            <span class="target-check">${(trade.current_mfe || 0) >= 1 ? '✓' : '○'}</span> 1R
                        </div>
                        <div class="target-item ${(trade.current_mfe || 0) >= 2 ? 'hit' : ''}">
                            <span class="target-check">${(trade.current_mfe || 0) >= 2 ? '✓' : '○'}</span> 2R
                        </div>
                        <div class="target-item ${(trade.current_mfe || 0) >= 3 ? 'hit' : ''}">
                            <span class="target-check">${(trade.current_mfe || 0) >= 3 ? '✓' : '○'}</span> 3R
                        </div>
                    </div>
                    <div class="trade-details">
                        Entry: ${trade.entry_price || 'N/A'}<br>
                        Stop Loss: ${trade.stop_loss_price || 'N/A'}<br>
                        Session: ${trade.session || 'N/A'}
                    </div>"""

html = html.replace(old_trade_card, new_trade_card)

# Add calendar generation JavaScript
calendar_js = """
        // Generate Calendar Heatmap
        function generateCalendar(hourlyData) {
            const container = document.getElementById('calendarGrid');
            if (!container) return;
            
            const hours = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19];
            const labels = ['6AM', '7AM', '8AM', '9AM', '10AM', '11AM', '12PM', '1PM', '2PM', '3PM', '4PM', '5PM', '6PM', '7PM'];
            
            container.innerHTML = hours.map((hour, index) => {
                const data = hourlyData[hour] || { count: 0, avg_mfe: 0, active: 0, completed: 0 };
                const count = data.count || 0;
                const intensity = Math.min(count / 5, 1); // Max intensity at 5 trades
                const bgColor = `rgba(0, 212, 255, ${0.1 + intensity * 0.7})`;
                
                return `
                    <div class="calendar-hour" style="background: ${bgColor}" 
                         title="${count} trades, Avg MFE: ${(data.avg_mfe || 0).toFixed(2)}R">
                        <div class="hour-label">${labels[index]}</div>
                        <div class="hour-count">${count}</div>
                    </div>
                `;
            }).join('');
        }
"""

# Insert calendar JS before the updateDashboard function
html = html.replace('        function updateDashboard(data) {', 
                    calendar_js + '\n        function updateDashboard(data) {')

# Add calendar update call in updateDashboard
html = html.replace('            // Update session chart\n            updateSessionChart(sessionBreakdown);',
                    '            // Update calendar\n            generateCalendar(data.hourly_distribution || {});\n\n            // Update session chart\n            updateSessionChart(sessionBreakdown);')

# Write enhanced dashboard
with open('automated_signals_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ Enhanced Trading Floor Dashboard with:")
print("   - Calendar Heatmap (hourly 6 AM - 8 PM)")
print("   - Target Progress Indicators (1R, 2R, 3R)")
print("   - Hover tooltips on calendar")
print("   - Color intensity based on trade count")
