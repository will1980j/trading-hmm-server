"""
Add trade detail modal to dashboard to see full event history for each trade
"""

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

<style>
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
}

.clickable-row:hover {
    background: rgba(0, 212, 255, 0.1) !important;
}
</style>
'''

javascript = '''
// Trade Detail Modal Functions
async function showTradeDetail(tradeId) {
    const modal = document.getElementById('tradeDetailModal');
    const body = document.getElementById('tradeDetailBody');
    
    body.innerHTML = '<div style="text-align: center; padding: 40px;">Loading...</div>';
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
    
    // Determine current status
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
                    <div class="detail-label">Status</div>
                    <div class="detail-value" style="color: ${statusColor}">${statusText}</div>
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
                            <span class="event-time">${formatTime(event.timestamp)}</span>
                        </div>
                        <div class="event-details">
                            ${event.be_mfe ? `<div class="event-detail">BE MFE: <strong>${event.be_mfe.toFixed(2)}R</strong></div>` : ''}
                            ${event.no_be_mfe ? `<div class="event-detail">No BE MFE: <strong>${event.no_be_mfe.toFixed(2)}R</strong></div>` : ''}
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

print("Modal HTML to add before </body>:")
print(modal_html)
print("\nJavaScript to add to <script> section:")
print(javascript)
print("\nUpdate table row generation to add onclick:")
print('row.onclick = () => showTradeDetail(signal.trade_id);')
print('row.className = "clickable-row";')
