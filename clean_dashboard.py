#!/usr/bin/env python3

# Replace the dashboard function in hmm_server.py with this clean version

@app.route('/', methods=['GET'])
def dashboard():
    """Clean trading dashboard with performance analytics"""
    # Calculate performance metrics
    total_trades = performance_stats['total_trades']
    win_rate = (performance_stats['winning_trades'] / total_trades * 100) if total_trades > 0 else 0
    avg_rr = sum([t.get('actual_rr', 0) for t in trade_log]) / len(trade_log) if trade_log else 0
    avg_mae = sum([t.get('mae_percentage', 0) for t in trade_log]) / len(trade_log) if trade_log else 0
    avg_mfe = sum([t.get('mfe_percentage', 0) for t in trade_log]) / len(trade_log) if trade_log else 0
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Trading System Dashboard</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
            * {{ box-sizing: border-box; }}
            body {{ 
                font-family: 'Inter', sans-serif; 
                margin: 0; 
                background: #0f172a; 
                color: #cbd5e1; 
                min-height: 100vh;
            }}
            .container {{ max-width: 1400px; margin: 0 auto; padding: 24px; }}
            .header {{ text-align: center; margin-bottom: 32px; border-bottom: 1px solid #334155; padding-bottom: 24px; }}
            .header h1 {{ font-size: 2em; font-weight: 300; color: #f8fafc; margin: 0; }}
            .section {{ background: #1e293b; padding: 24px; margin: 20px 0; border-radius: 8px; border: 1px solid #334155; }}
            .section h2 {{ color: #f1f5f9; margin: 0 0 20px 0; font-size: 1.1em; font-weight: 500; text-transform: uppercase; }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }}
            .stat-box {{ background: #0f172a; padding: 20px; border-radius: 6px; text-align: center; border: 1px solid #334155; }}
            .stat-box h3 {{ color: #94a3b8; margin: 0 0 10px 0; font-size: 0.8em; text-transform: uppercase; }}
            .stat-box p {{ font-size: 1.8em; font-weight: 600; margin: 0; color: #f8fafc; }}
            .success {{ color: #10b981; }}
            .warning {{ color: #f59e0b; }}
            .error {{ color: #ef4444; }}
            button {{ background: #334155; color: #f1f5f9; padding: 12px 20px; border: 1px solid #475569; border-radius: 6px; cursor: pointer; font-weight: 500; font-family: inherit; transition: all 0.2s ease; }}
            button:hover {{ background: #475569; }}
            .performance-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }}
            .metric-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #334155; }}
            .metric-label {{ color: #94a3b8; }}
            .metric-value {{ color: #f8fafc; font-weight: 500; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>TRADING SYSTEM DASHBOARD</h1>
                <p style="color: #64748b; margin: 5px 0;">Performance Analytics & Signal Management</p>
            </div>
            
            <div class="section">
                <h2>System Status</h2>
                <div class="stats">
                    <div class="stat-box">
                        <h3>Model Status</h3>
                        <p class="success">{'TRAINED' if hmm_engine.is_trained else 'LEARNING'}</p>
                    </div>
                    <div class="stat-box">
                        <h3>Total Trades</h3>
                        <p>{total_trades}</p>
                    </div>
                    <div class="stat-box">
                        <h3>Win Rate</h3>
                        <p class="{'success' if win_rate > 60 else 'warning' if win_rate > 40 else 'error'}">{win_rate:.1f}%</p>
                    </div>
                    <div class="stat-box">
                        <h3>Avg R:R</h3>
                        <p class="{'success' if avg_rr > 2 else 'warning' if avg_rr > 1 else 'error'}">{avg_rr:.2f}</p>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>Performance Analytics</h2>
                <div class="performance-grid">
                    <div>
                        <h3 style="color: #f1f5f9; margin-bottom: 15px;">Trade Metrics</h3>
                        <div class="metric-row">
                            <span class="metric-label">Total P&L:</span>
                            <span class="metric-value {'success' if performance_stats['total_pnl'] > 0 else 'error'}">{performance_stats['total_pnl']:.2f}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Winning Trades:</span>
                            <span class="metric-value">{performance_stats['winning_trades']}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Losing Trades:</span>
                            <span class="metric-value">{performance_stats['losing_trades']}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Avg Per Trade:</span>
                            <span class="metric-value">{(performance_stats['total_pnl'] / total_trades):.2f if total_trades > 0 else 0}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Avg MAE:</span>
                            <span class="metric-value error">{avg_mae:.2f}%</span>
                        </div>
                    </div>
                    <div>
                        <h3 style="color: #f1f5f9; margin-bottom: 15px;">Risk Analysis</h3>
                        <div class="metric-row">
                            <span class="metric-label">Best Trade:</span>
                            <span class="metric-value success">{max([t.get('pnl', 0) for t in trade_log]) if trade_log else 0:.2f}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Worst Trade:</span>
                            <span class="metric-value error">{min([t.get('pnl', 0) for t in trade_log]) if trade_log else 0:.2f}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Avg MFE:</span>
                            <span class="metric-value success">{avg_mfe:.2f}%</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Exit Efficiency:</span>
                            <span class="metric-value">{(sum([t.get('exit_efficiency', 0) for t in trade_log]) / len(trade_log)):.2f if trade_log else 0}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">R:R Efficiency:</span>
                            <span class="metric-value">{(sum([t.get('rr_efficiency', 0) for t in trade_log]) / len(trade_log)):.2f if trade_log else 0}</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>Signal Management</h2>
                <div id="signalList">No pending signals</div>
                <button onclick="refreshSignals()">REFRESH SIGNALS</button>
            </div>
            
            <div class="section">
                <h2>Quick Actions</h2>
                <div style="display: flex; gap: 16px; flex-wrap: wrap;">
                    <button onclick="window.open('/performance', '_blank')">DETAILED METRICS</button>
                    <button onclick="window.open('/model_insights', '_blank')">MODEL INSIGHTS</button>
                    <button onclick="refreshSignals()">REFRESH DATA</button>
                </div>
            </div>
        </div>
        
        <script>
            function refreshSignals() {{
                document.getElementById('signalList').innerHTML = 'No pending signals - System monitoring';
            }}
            
            // Auto-refresh every 30 seconds
            setInterval(() => {{
                refreshSignals();
            }}, 30000);
        </script>
    </body>
    </html>
    '''
    return html