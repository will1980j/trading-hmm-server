"""
Build the complete Trading Floor Command Center dashboard
This script generates the full HTML file with all features
"""

dashboard_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trading Floor Command Center | Automated Signals</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #0a0e27;
            color: #e1e8ed;
            min-height: 100vh;
        }
        
        .dashboard-wrapper {
            display: grid;
            grid-template-columns: 280px 1fr;
            min-height: 100vh;
        }
        
        /* Sidebar */
        .sidebar {
            background: linear-gradient(180deg, #1a1f2e 0%, #0a0e27 100%);
            border-right: 1px solid rgba(0, 212, 255, 0.1);
            padding: 30px 20px;
            position: fixed;
            height: 100vh;
            width: 280px;
            overflow-y: auto;
        }
        
        .sidebar-header {
            margin-bottom: 40px;
        }
        
        .sidebar-title {
            font-size: 20px;
            font-weight: 700;
            color: #00d4ff;
            margin-bottom: 5px;
        }
        
        .sidebar-subtitle {
            font-size: 13px;
            color: #64748b;
        }
        
        .sidebar-section {
            margin-bottom: 30px;
        }
        
        .section-label {
            font-size: 11px;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
        }
        
        .metric-item {
            padding: 12px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
            margin-bottom: 8px;
            border-left: 3px solid transparent;
            transition: all 0.2s;
        }
        
        .metric-item:hover {
            background: rgba(0, 212, 255, 0.05);
            border-left-color: #00d4ff;
        }
        
        .metric-label {
            font-size: 12px;
            color: #94a3b8;
            margin-bottom: 4px;
        }
        
        .metric-value {
            font-size: 20px;
            font-weight: 700;
            color: #e1e8ed;
        }
        
        .metric-value.positive { color: #10b981; }
        .metric-value.negative { color: #ef4444; }
        
        /* Main Content */
        .main-content {
            margin-left: 280px;
            padding: 30px;
            overflow-y: auto;
            max-height: 100vh;
        }
        
        .content-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }
        
        .page-title {
            font-size: 32px;
            font-weight: 700;
            color: #e1e8ed;
        }
        
        /* Connection Indicator */
        .connection-indicator {
            position: fixed;
            top: 20px;
            right: 20px;
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 16px;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            z-index: 1000;
        }
        
        .conn-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #10b981;
            animation: pulse 2s infinite;
        }
        
        .conn-dot.disconnected {
            background: #ef4444;
            animation: none;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }
        
        /* Performance Grid */
        .performance-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 20px;
        }
        
        .perf-card {
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 212, 255, 0.02) 100%);
            border: 1px solid rgba(0, 212, 255, 0.2);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }
        
        .perf-icon {
            font-size: 32px;
            margin-bottom: 12px;
        }
        
        .perf-value {
            font-size: 28px;
            font-weight: 700;
            color: #00d4ff;
            margin-bottom: 4px;
        }
        
        .perf-label {
            font-size: 13px;
            color: #94a3b8;
        }
        
        /* Active Trades */
        .active-trades-section {
            margin-bottom: 20px;
        }
        
        .section-title {
            font-size: 18px;
            font-weight: 600;
            color: #e1e8ed;
            margin-bottom: 16px;
        }
        
        .active-trades-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 16px;
            margin-bottom: 20px;
        }
        
        .trade-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(0, 212, 255, 0.2);
            border-radius: 12px;
            padding: 20px;
            animation: pulse-border 2s infinite;
        }
        
        @keyframes pulse-border {
            0%, 100% { border-color: rgba(0, 212, 255, 0.2); }
            50% { border-color: rgba(0, 212, 255, 0.5); }
        }
        
        .trade-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        
        .trade-id {
            font-size: 14px;
            font-weight: 700;
            color: #64748b;
        }
        
        .trade-direction {
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 700;
        }
        
        .direction-long {
            background: rgba(16, 185, 129, 0.2);
            color: #10b981;
        }
        
        .direction-short {
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
        }
        
        .trade-mfe {
            font-size: 32px;
            font-weight: 700;
            color: #10b981;
            margin: 12px 0;
        }
        
        .trade-details {
            font-size: 13px;
            color: #94a3b8;
            line-height: 1.8;
        }
        
        .trade-duration {
            font-size: 12px;
            color: #64748b;
            margin-top: 12px;
            text-align: right;
        }
        
        /* Empty State */
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #64748b;
        }
        
        .empty-state-icon {
            font-size: 48px;
            margin-bottom: 16px;
            opacity: 0.5;
        }
        
        /* Charts */
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .chart-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 24px;
        }
        
        .chart-card.full-width {
            grid-column: 1 / -1;
        }
        
        .chart-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .chart-title {
            font-size: 16px;
            font-weight: 600;
            color: #e1e8ed;
        }
        
        .chart-badge {
            padding: 4px 12px;
            background: rgba(0, 212, 255, 0.1);
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 6px;
            font-size: 12px;
            color: #00d4ff;
            font-weight: 600;
        }
        
        .chart-container {
            position: relative;
            height: 280px;
        }
        
        /* Completed Trades */
        .completed-trades-list {
            display: grid;
            gap: 12px;
        }
        
        .completed-trade-item {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 16px;
            display: grid;
            grid-template-columns: 100px 1fr 120px 120px 80px;
            gap: 16px;
            align-items: center;
        }
        
        .completed-trade-item:hover {
            background: rgba(0, 212, 255, 0.05);
        }
        
        .trade-time {
            font-size: 13px;
            color: #64748b;
        }
        
        .trade-info {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .trade-bias-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }
        
        .bias-bullish { background: #10b981; }
        .bias-bearish { background: #ef4444; }
        
        .trade-mfe-value {
            font-size: 18px;
            font-weight: 700;
            color: #10b981;
        }
        
        .trade-session {
            font-size: 12px;
            color: #94a3b8;
        }
        
        .db-badge {
            padding: 4px 8px;
            background: rgba(16, 185, 129, 0.1);
            border-radius: 4px;
            font-size: 11px;
            color: #10b981;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <!-- Connection Indicator -->
    <div class="connection-indicator">
        <div class="conn-dot" id="connDot"></div>
        <span id="connText">Live</span>
    </div>

    <div class="dashboard-wrapper">
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="sidebar-header">
                <div class="sidebar-title">📊 Trading Floor</div>
                <div class="sidebar-subtitle">Command Center</div>
            </div>

            <div class="sidebar-section">
                <div class="section-label">Today's Performance</div>
                <div class="metric-item">
                    <div class="metric-label">Total Signals</div>
                    <div class="metric-value" id="sidebarTotal">0</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Win Rate</div>
                    <div class="metric-value positive" id="sidebarWinRate">0%</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Avg MFE</div>
                    <div class="metric-value" id="sidebarAvgMFE">0.00R</div>
                </div>
            </div>

            <div class="sidebar-section">
                <div class="section-label">Session Breakdown</div>
                <div class="metric-item">
                    <div class="metric-label">Asia</div>
                    <div class="metric-value" id="sessionAsia">0</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">London</div>
                    <div class="metric-value" id="sessionLondon">0</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">NY Pre</div>
                    <div class="metric-value" id="sessionNYPre">0</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">NY AM</div>
                    <div class="metric-value" id="sessionNYAM">0</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">NY Lunch</div>
                    <div class="metric-value" id="sessionNYLunch">0</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">NY PM</div>
                    <div class="metric-value" id="sessionNYPM">0</div>
                </div>
            </div>
        </div>

        <!-- Main Content -->
        <div class="main-content">
            <div class="content-header">
                <h1 class="page-title">Trading Floor Command Center</h1>
            </div>

            <!-- Performance Grid -->
            <div class="performance-grid">
                <div class="perf-card">
                    <div class="perf-icon">🎯</div>
                    <div class="perf-value" id="perfTotal">0</div>
                    <div class="perf-label">Total Signals</div>
                </div>
                <div class="perf-card">
                    <div class="perf-icon">🔴</div>
                    <div class="perf-value" id="perfActive">0</div>
                    <div class="perf-label">Active Trades</div>
                </div>
                <div class="perf-card">
                    <div class="perf-icon">✅</div>
                    <div class="perf-value" id="perfCompleted">0</div>
                    <div class="perf-label">Completed Today</div>
                </div>
                <div class="perf-card">
                    <div class="perf-icon">📈</div>
                    <div class="perf-value" id="perfAvgMFE">0.00R</div>
                    <div class="perf-label">Avg MFE</div>
                </div>
            </div>

            <!-- Active Trades -->
            <div class="active-trades-section">
                <div class="section-title">🔴 Active Trades</div>
                <div class="active-trades-grid" id="activeTradesContainer">
                    <div class="empty-state">
                        <div class="empty-state-icon">📊</div>
                        <div>No active trades</div>
                    </div>
                </div>
            </div>

            <!-- Charts Grid -->
            <div class="charts-grid">
                <div class="chart-card">
                    <div class="chart-header">
                        <div class="chart-title">Session Performance</div>
                        <div class="chart-badge">Real-time</div>
                    </div>
                    <div class="chart-container">
                        <canvas id="sessionChart"></canvas>
                    </div>
                </div>

                <div class="chart-card">
                    <div class="chart-header">
                        <div class="chart-title">MFE Distribution</div>
                        <div class="chart-badge">Last 7 Days</div>
                    </div>
                    <div class="chart-container">
                        <canvas id="mfeChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Completed Trades -->
            <div class="chart-card full-width">
                <div class="chart-header">
                    <div class="chart-title">✅ Completed Trades (Database Verified)</div>
                    <div class="chart-badge" id="completedCount">0 trades</div>
                </div>
                <div class="completed-trades-list" id="completedTradesContainer">
                    <div class="empty-state">
                        <div class="empty-state-icon">📋</div>
                        <div>No completed trades today</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // WebSocket connection
        const socket = io();
        let charts = {};

        // Connection Status
        socket.on('connect', () => {
            document.getElementById('connDot').classList.remove('disconnected');
            document.getElementById('connText').textContent = 'Live';
            loadData();
        });

        socket.on('disconnect', () => {
            document.getElementById('connDot').classList.add('disconnected');
            document.getElementById('connText').textContent = 'Offline';
        });

        // Load Dashboard Data
        async function loadData() {
            try {
                const [dashboardData, mfeData] = await Promise.all([
                    fetch('/api/automated-signals/dashboard-data').then(r => r.json()),
                    fetch('/api/automated-signals/mfe-distribution').then(r => r.json())
                ]);

                if (dashboardData.success) {
                    updateDashboard(dashboardData);
                }
                
                if (mfeData.success) {
                    updateMFEChart(mfeData.distribution);
                }
            } catch (error) {
                console.error('Error loading data:', error);
            }
        }

        function updateDashboard(data) {
            const stats = data.stats || {};
            const activeTrades = data.active_trades || [];
            const completedTrades = data.completed_trades || [];
            const sessionBreakdown = data.session_breakdown || {};

            // Update sidebar
            document.getElementById('sidebarTotal').textContent = stats.total_signals || 0;
            document.getElementById('sidebarWinRate').textContent = (stats.win_rate || 0).toFixed(1) + '%';
            document.getElementById('sidebarAvgMFE').textContent = (stats.avg_mfe || 0).toFixed(2) + 'R';

            // Update performance cards
            document.getElementById('perfTotal').textContent = stats.total_signals || 0;
            document.getElementById('perfActive').textContent = stats.active_count || 0;
            document.getElementById('perfCompleted').textContent = stats.completed_count || 0;
            document.getElementById('perfAvgMFE').textContent = (stats.avg_mfe || 0).toFixed(2) + 'R';

            // Update session breakdown
            const sessions = ['Asia', 'London', 'NY Pre', 'NY AM', 'NY Lunch', 'NY PM'];
            sessions.forEach(session => {
                const id = 'session' + session.replace(/ /g, '');
                const count = sessionBreakdown[session]?.count || 0;
                const el = document.getElementById(id);
                if (el) el.textContent = count;
            });

            // Update active trades
            updateActiveTrades(activeTrades);

            // Update completed trades
            updateCompletedTrades(completedTrades);

            // Update session chart
            updateSessionChart(sessionBreakdown);
        }

        function updateActiveTrades(trades) {
            const container = document.getElementById('activeTradesContainer');
            
            if (trades.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">📊</div>
                        <div>No active trades</div>
                    </div>
                `;
                return;
            }

            container.innerHTML = trades.map(trade => `
                <div class="trade-card">
                    <div class="trade-header">
                        <div class="trade-id">TRADE #${trade.id}</div>
                        <div class="trade-direction ${trade.bias === 'bullish' ? 'direction-long' : 'direction-short'}">
                            ${trade.bias === 'bullish' ? 'LONG' : 'SHORT'}
                        </div>
                    </div>
                    <div class="trade-mfe">+${(trade.current_mfe || 0).toFixed(2)}R</div>
                    <div class="trade-details">
                        Entry: ${trade.entry_price || 'N/A'}<br>
                        Stop Loss: ${trade.stop_loss_price || 'N/A'}<br>
                        Session: ${trade.session || 'N/A'}
                    </div>
                    <div class="trade-duration">${trade.duration_display || '0s'}</div>
                </div>
            `).join('');
        }

        function updateCompletedTrades(trades) {
            const container = document.getElementById('completedTradesContainer');
            document.getElementById('completedCount').textContent = trades.length + ' trades';
            
            if (trades.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">📋</div>
                        <div>No completed trades today</div>
                    </div>
                `;
                return;
            }

            container.innerHTML = trades.map(trade => `
                <div class="completed-trade-item">
                    <div class="trade-time">${trade.time || 'N/A'}</div>
                    <div class="trade-info">
                        <div class="trade-bias-dot ${trade.bias === 'bullish' ? 'bias-bullish' : 'bias-bearish'}"></div>
                        <span>${trade.bias === 'bullish' ? 'LONG' : 'SHORT'}</span>
                    </div>
                    <div class="trade-mfe-value">${(trade.final_mfe || 0).toFixed(2)}R</div>
                    <div class="trade-session">${trade.session || 'N/A'}</div>
                    <div class="db-badge">✓ DB</div>
                </div>
            `).join('');
        }

        function updateSessionChart(sessionBreakdown) {
            const ctx = document.getElementById('sessionChart');
            if (charts.session) charts.session.destroy();

            const sessions = ['Asia', 'London', 'NY Pre', 'NY AM', 'NY Lunch', 'NY PM'];
            const counts = sessions.map(s => sessionBreakdown[s]?.count || 0);

            charts.session = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: sessions,
                    datasets: [{
                        label: 'Trades',
                        data: counts,
                        backgroundColor: '#00d4ff',
                        borderRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { color: '#94a3b8' },
                            grid: { color: 'rgba(255,255,255,0.05)' }
                        },
                        x: {
                            ticks: { color: '#94a3b8' },
                            grid: { display: false }
                        }
                    }
                }
            });
        }

        function updateMFEChart(distribution) {
            const ctx = document.getElementById('mfeChart');
            if (charts.mfe) charts.mfe.destroy();

            const labels = Object.keys(distribution);
            const values = Object.values(distribution);

            charts.mfe = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Trade Count',
                        data: values,
                        backgroundColor: '#10b981',
                        borderRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { color: '#94a3b8' },
                            grid: { color: 'rgba(255,255,255,0.05)' }
                        },
                        x: {
                            ticks: { color: '#94a3b8' },
                            grid: { display: false }
                        }
                    }
                }
            });
        }

        // Initialize
        loadData();
        setInterval(loadData, 5000); // Refresh every 5 seconds

        // WebSocket listeners for real-time updates
        socket.on('mfe_update', (data) => {
            console.log('MFE Update:', data);
            loadData();
        });

        socket.on('trade_completed', (data) => {
            console.log('Trade Completed:', data);
            loadData();
        });
    </script>
</body>
</html>
"""

# Write the file
with open('automated_signals_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(dashboard_html)

print("✅ Trading Floor Command Center dashboard created!")
print("File: automated_signals_dashboard.html")
print("Size:", len(dashboard_html), "characters")
