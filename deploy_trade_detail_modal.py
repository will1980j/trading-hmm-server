"""
Deploy trade detail modal and diagnostic improvements to dashboard
"""

import re

# Read current dashboard
with open('automated_signals_dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add modal HTML before </body>
modal_html = '''
<!-- Trade Detail Modal -->
<div id="tradeDetailModal" class="modal">
    <div class="modal-content">
        <div class="modal-header">
            <h2>Trade Details</h2>
            <span class="close-modal" onclick="closeTradeDetail()">&times;</span>
        </div>
        <div class="modal-body" id="tradeDetailBody">
            <!-- Populated by JavaScript -->
        </div>
    </div>
</div>

'''

# Add modal styles to existing <style> section
modal_styles = '''
        /* Trade Detail Modal */
        .modal {
            display: none;
            position: fixed;
            z-index: 10000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.8);
        }

        .modal-content {
            background: linear-gradient(135deg, #1a1f3a 0%, #0a0e27 100%);
            margin: 5% auto;
            padding: 0;
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 12px;
            width: 90%;
            max-width: 1200px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 8px 32px rgba(0, 212, 255, 0.3);
        }

        .modal-header {
            padding: 20px 30px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .modal-header h2 {
            color: #00d4ff;
            margin: 0;
        }

        .close-modal {
            color: #aaa;
            font-size: 32px;
            font-weight: bold;
            cursor: pointer;
            transition: color 0.3s;
        }

        .close-modal:hover {
            color: #00d4ff;
        }

        .modal-body {
            padding: 30px;
        }

        .detail-section {
            margin-bottom: 30px;
        }

        .detail-section h3 {
            color: #00d4ff;
            margin-bottom: 15px;
            font-size: 18px;
        }

        .detail-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }

        .detail-item {
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .detail-label {
            color: #94a3b8;
            font-size: 12px;
            margin-bottom: 5px;
        }

        .detail-value {
            color: #e0e6ed;
            font-size: 16px;
            font-weight: 600;
        }

        .event-timeline {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
            padding: 20px;
        }

        .event-item {
            padding: 15px;
            border-left: 3px solid #00d4ff;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 4px;
            margin-bottom: 10px;
        }

        .event-item:last-child {
            margin-bottom: 0;
        }

        .event-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .event-type {
            font-weight: 600;
            color: #00d4ff;
            font-size: 14px;
        }

        .event-time {
            color: #64748b;
            font-size: 12px;
        }

        .event-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            font-size: 12px;
        }

        .event-detail {
            color: #94a3b8;
        }

        .event-detail strong {
            color: #e0e6ed;
        }

        .clickable-row {
            cursor: pointer;
            transition: background 0.2s;
        }

        .clickable-row:hover {
            background: rgba(0, 212, 255, 0.15) !important;
        }
'''

# Add modal JavaScript functions
modal_js = '''
        // Trade Detail Modal Functions
        async function showTradeDetail(tradeId) {
            const modal = document.getElementById('tradeDetailModal');
            const body = document.getElementById('tradeDetailBody');
            
            body.innerHTML = '<div style="text-align: center; padding: 40px; color: #00d4ff;">Loading trade details...</div>';
            modal.style.display = 'block';
            
            try {
                const response = await fetch(`/api/automated-signals/trade-detail/${tradeId}`);
                const data = await response.json();
                
                if (data.success) {
                    renderTradeDetail(data.trade);
                } else {
                    body.innerHTML = `<div style="color: #ef4444; text-align: center; padding: 40px;">Error: ${data.error}</div>`;
                }
            } catch (error) {
                console.error('Error loading trade detail:', error);
                body.innerHTML = `<div style="color: #ef4444; text-align: center; padding: 40px;">Error loading trade details</div>`;
            }
        }

        function renderTradeDetail(trade) {
            const body = document.getElementById('tradeDetailBody');
            
            // Determine current status from latest event
            const latestEvent = trade.events[trade.events.length - 1];
            const isActive = !latestEvent.event_type.startsWith('EXIT_');
            const statusText = isActive ? 'ACTIVE' : 'COMPLETED';
            const statusColor = isActive ? '#4ade80' : '#8b5cf6';
            
            body.innerHTML = `
                <div class="detail-section">
                    <h3>Trade Summary</h3>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <div class="detail-label">Trade ID</div>
                            <div class="detail-value">${trade.trade_id}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Current Status</div>
                            <div class="detail-value" style="color: ${statusColor}">${statusText}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Latest Event</div>
                            <div class="detail-value">${latestEvent.event_type}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Direction</div>
                            <div class="detail-value">${trade.direction}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Session</div>
                            <div class="detail-value">${trade.session || 'N/A'}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Entry Price</div>
                            <div class="detail-value">${trade.entry_price ? trade.entry_price.toFixed(2) : 'N/A'}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Stop Loss</div>
                            <div class="detail-value">${trade.stop_loss ? trade.stop_loss.toFixed(2) : 'N/A'}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Risk Distance</div>
                            <div class="detail-value">${trade.risk_distance ? trade.risk_distance.toFixed(2) : 'N/A'}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">BE=1 MFE</div>
                            <div class="detail-value">${trade.be_mfe ? trade.be_mfe.toFixed(2) + 'R' : 'N/A'}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">No BE MFE</div>
                            <div class="detail-value">${trade.no_be_mfe ? trade.no_be_mfe.toFixed(2) + 'R' : 'N/A'}</div>
                        </div>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h3>Event Timeline (${trade.events.length} events)</h3>
                    <div class="event-timeline">
                        ${trade.events.map(event => `
                            <div class="event-item">
                                <div class="event-header">
                                    <span class="event-type">${event.event_type}</span>
                                    <span class="event-time">${event.signal_time || formatTime(event.timestamp)}</span>
                                </div>
                                <div class="event-details">
                                    ${event.be_mfe !== null && event.be_mfe !== undefined ? `<div class="event-detail">BE MFE: <strong>${event.be_mfe.toFixed(2)}R</strong></div>` : ''}
                                    ${event.no_be_mfe !== null && event.no_be_mfe !== undefined ? `<div class="event-detail">No BE MFE: <strong>${event.no_be_mfe.toFixed(2)}R</strong></div>` : ''}
                                    ${event.entry_price ? `<div class="event-detail">Entry: <strong>${event.entry_price.toFixed(2)}</strong></div>` : ''}
                                    ${event.stop_loss ? `<div class="event-detail">Stop: <strong>${event.stop_loss.toFixed(2)}</strong></div>` : ''}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <div class="detail-section">
                    <h3>Latest Alert Payload</h3>
                    <div style="background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px; font-family: monospace; font-size: 12px; color: #e0e6ed; overflow-x: auto;">
                        <pre>${JSON.stringify(latestEvent, null, 2)}</pre>
                    </div>
                </div>
            `;
        }

        function closeTradeDetail() {
            document.getElementById('tradeDetailModal').style.display = 'none';
        }

        // Close modal when clicking outside
        window.onclick = function(event) {
            const modal = document.getElementById('tradeDetailModal');
            if (event.target == modal) {
                closeTradeDetail();
            }
        }

'''

# Insert modal HTML before </body>
html = html.replace('</body>', modal_html + '</body>')

# Insert modal styles before </style>
html = html.replace('</style>', modal_styles + '    </style>')

# Insert modal JavaScript before the closing </script>
html = html.replace('        // Initialize\n        loadInitialData();', 
                    modal_js + '\n        // Initialize\n        loadInitialData();')

# Make table rows clickable - update the row generation
old_row_start = '                return `\n                    <tr>'
new_row_start = '                return `\n                    <tr class="clickable-row" onclick="showTradeDetail(\'${signal.trade_id}\')">'

html = html.replace(old_row_start, new_row_start)

# Write updated dashboard
with open('automated_signals_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ Trade detail modal added to dashboard")
print("\nNow add this endpoint to web_server.py:")
print("\n" + "="*80)

endpoint_code = '''
@app.route('/api/automated-signals/trade-detail/<trade_id>', methods=['GET'])
def get_trade_detail(trade_id):
    """Get complete event history for a specific trade"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            return jsonify({"success": False, "error": "DATABASE_URL not configured"}), 500
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Get all events for this trade_id
        cursor.execute("""
            SELECT 
                id, trade_id, event_type, direction, entry_price, stop_loss,
                risk_distance, be_mfe, no_be_mfe, session, bias,
                signal_date, signal_time, timestamp
            FROM automated_signals
            WHERE trade_id = %s
            ORDER BY timestamp ASC
        """, (trade_id,))
        
        events = []
        trade_info = None
        
        for row in cursor.fetchall():
            event = {
                "id": row[0],
                "trade_id": row[1],
                "event_type": row[2],
                "direction": row[3],
                "entry_price": float(row[4]) if row[4] else None,
                "stop_loss": float(row[5]) if row[5] else None,
                "risk_distance": float(row[6]) if row[6] else None,
                "be_mfe": float(row[7]) if row[7] is not None else None,
                "no_be_mfe": float(row[8]) if row[8] is not None else None,
                "session": row[9],
                "bias": row[10],
                "signal_date": row[11].isoformat() if row[11] else None,
                "signal_time": row[12].isoformat() if row[12] else None,
                "timestamp": row[13].isoformat() if row[13] else None
            }
            events.append(event)
            
            # Use first event for trade info
            if not trade_info:
                trade_info = event.copy()
        
        cursor.close()
        conn.close()
        
        if not events:
            return jsonify({
                "success": False,
                "error": f"No events found for trade_id: {trade_id}"
            }), 404
        
        # Get latest MFE values from last event
        latest_event = events[-1]
        trade_info['be_mfe'] = latest_event['be_mfe']
        trade_info['no_be_mfe'] = latest_event['no_be_mfe']
        trade_info['events'] = events
        
        return jsonify({
            "success": True,
            "trade": trade_info
        }), 200
        
    except Exception as e:
        logger.error(f"Trade detail error: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
'''

print(endpoint_code)
print("="*80)
print("\n✅ Deployment script complete!")
print("\nFeatures added:")
print("1. Click any trade row to see full event history")
print("2. Modal shows all events with timestamps")
print("3. Shows latest alert payload for debugging")
print("4. Displays current status based on latest event type")
