#!/usr/bin/env python3

def create_debug_v2_dashboard():
    """Create a debug version of the V2 dashboard with better error handling"""
    
    debug_js = """
    // Enhanced error handling and debugging
    async function loadSystemStats() {
        console.log('🔍 Loading V2 stats...');
        try {
            const response = await fetch('/api/v2/stats');
            console.log('📊 V2 Stats response:', response.status, response.statusText);
            
            if (response.ok) {
                const data = await response.json();
                console.log('✅ V2 Stats data:', data);
                
                document.getElementById('totalSignals').textContent = data.total_signals || 0;
                document.getElementById('awaitingConfirmation').textContent = data.pending_trades || 0;
                document.getElementById('activeTrades').textContent = data.active_trades || 0;
                document.getElementById('todaySignals').textContent = data.today_signals || 0;
            } else {
                console.error('❌ V2 Stats failed:', response.status, response.statusText);
                const errorText = await response.text();
                console.error('❌ Error details:', errorText);
                setDefaultStats();
            }
        } catch (error) {
            console.error('❌ V2 Stats error:', error);
            setDefaultStats();
        }
    }

    async function loadCurrentPrice() {
        console.log('🔍 Loading current price...');
        try {
            let response = await fetch('/api/v2/price/current');
            console.log('💰 V2 Price response:', response.status, response.statusText);
            
            if (!response.ok) {
                console.log('⚠️ Primary price endpoint failed, trying fallback...');
                response = await fetch('/api/v2/price/stream?limit=1');
                console.log('💰 V2 Price stream response:', response.status, response.statusText);
            }
            
            if (response.ok) {
                const data = await response.json();
                console.log('✅ Price data:', data);
                
                let priceData = null;
                if (data.current_price) {
                    priceData = data.current_price;
                } else if (data.prices && data.prices.length > 0) {
                    priceData = data.prices[0];
                } else if (data.price) {
                    priceData = data;
                }
                
                if (priceData) {
                    document.getElementById('currentPrice').textContent = parseFloat(priceData.price || priceData.current_price || 0).toFixed(2);
                    document.getElementById('currentSession').textContent = priceData.session || 'Unknown';
                    document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
                    console.log('✅ Price updated successfully');
                } else {
                    console.log('⚠️ No price data in response');
                    showMarketClosedState();
                }
            } else {
                console.error('❌ Both price endpoints failed');
                const errorText = await response.text();
                console.error('❌ Error details:', errorText);
                showMarketClosedState();
            }
        } catch (error) {
            console.error('❌ Price loading error:', error);
            showMarketClosedState();
        }
    }

    async function loadEnhancedSignals() {
        console.log('🔍 Loading V2 signals...');
        try {
            const response = await fetch('/api/v2/active-trades');
            console.log('📋 V2 Active trades response:', response.status, response.statusText);
            
            if (response.ok) {
                const data = await response.json();
                console.log('✅ Active trades data:', data);
                
                const trades = data.trades || [];
                console.log(`📊 Found ${trades.length} trades`);
                
                const container = document.getElementById('signalsContainer');
                
                if (trades.length === 0) {
                    container.innerHTML = `
                        <div class="empty-state">
                            <h3>🎯 V2 System Status</h3>
                            <p>System is ready. Trades will appear here when created.</p>
                            <div class="webhook-info">
                                <strong>V2 Webhook:</strong>
                                <div class="webhook-url">https://web-production-cd33.up.railway.app/api/live-signals-v2</div>
                            </div>
                            <div style="margin-top: 1rem; padding: 1rem; background: rgba(59, 130, 246, 0.1); border-radius: 8px;">
                                <strong>Debug Info:</strong><br>
                                API Response: ${JSON.stringify(data, null, 2)}
                            </div>
                        </div>
                    `;
                } else {
                    // Display trades table
                    let tableHTML = `
                        <table class="signals-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Type</th>
                                    <th>Session</th>
                                    <th>Status</th>
                                    <th>Entry</th>
                                    <th>Stop Loss</th>
                                    <th>MFE</th>
                                </tr>
                            </thead>
                            <tbody>
                    `;
                    
                    trades.forEach(trade => {
                        const typeClass = trade.bias === 'Bullish' ? 'signal-bullish' : 'signal-bearish';
                        tableHTML += `
                            <tr>
                                <td>${trade.id}</td>
                                <td><span class="signal-type ${typeClass}">${trade.bias}</span></td>
                                <td>${trade.session || 'N/A'}</td>
                                <td>${trade.trade_status || 'N/A'}</td>
                                <td>${trade.entry_price || 'Pending'}</td>
                                <td>${trade.stop_loss_price || 'Pending'}</td>
                                <td>${trade.current_mfe || '0.00'}R</td>
                            </tr>
                        `;
                    });
                    
                    tableHTML += '</tbody></table>';
                    container.innerHTML = tableHTML;
                }
            } else {
                console.error('❌ Active trades failed:', response.status, response.statusText);
                const errorText = await response.text();
                console.error('❌ Error details:', errorText);
                
                document.getElementById('signalsContainer').innerHTML = `
                    <div class="empty-state">
                        <h3>❌ API Error</h3>
                        <p>Status: ${response.status} ${response.statusText}</p>
                        <div style="margin-top: 1rem; padding: 1rem; background: rgba(239, 68, 68, 0.1); border-radius: 8px;">
                            <strong>Error Details:</strong><br>
                            ${errorText}
                        </div>
                    </div>
                `;
            }
        } catch (error) {
            console.error('❌ Signals loading error:', error);
            document.getElementById('signalsContainer').innerHTML = `
                <div class="empty-state">
                    <h3>❌ Network Error</h3>
                    <p>Failed to load signals: ${error.message}</p>
                </div>
            `;
        }
    }

    function setDefaultStats() {
        document.getElementById('totalSignals').textContent = '0';
        document.getElementById('awaitingConfirmation').textContent = '0';
        document.getElementById('activeTrades').textContent = '0';
        document.getElementById('todaySignals').textContent = '0';
    }

    function showMarketClosedState() {
        document.getElementById('currentPrice').textContent = '---.--';
        document.getElementById('priceChange').textContent = '--';
        document.getElementById('currentSession').textContent = 'No Data';
        document.getElementById('lastUpdate').textContent = 'No Data';
        document.getElementById('priceUpdates').textContent = '0';
    }

    // Initialize with enhanced logging
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🚀 V2 Dashboard Debug Mode Initialized');
        console.log('🌐 Current URL:', window.location.href);
        console.log('🍪 Cookies:', document.cookie);
        
        loadSystemStats();
        loadCurrentPrice();
        loadEnhancedSignals();
        
        // Auto-refresh every 10 seconds
        setInterval(() => {
            console.log('🔄 Auto-refresh triggered');
            loadSystemStats();
            loadCurrentPrice();
            loadEnhancedSignals();
        }, 10000);
    });
    """
    
    print("📝 Debug JavaScript created!")
    print("\n🔧 To use this debug version:")
    print("1. Copy the debug JavaScript above")
    print("2. Open your V2 dashboard in Chrome")
    print("3. Press F12 → Console tab")
    print("4. Paste the debug code and press Enter")
    print("5. Watch the console for detailed error messages")
    print("\nThis will show exactly what's failing and why!")

if __name__ == '__main__':
    create_debug_v2_dashboard()