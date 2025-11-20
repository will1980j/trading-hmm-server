"""
PHASE 7: DASHBOARD TELEMETRY UPGRADE
Upgrades automated_signals_dashboard.html to display telemetry-enhanced data
"""

import os
from datetime import datetime

def upgrade_dashboard_html():
    """Upgrade the dashboard to display telemetry data"""
    print("🎨 Upgrading Automated Signals Dashboard with Telemetry Display")
    print("=" * 70)
    
    dashboard_path = "templates/automated_signals_dashboard.html"
    
    # Read current dashboard
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the trade card rendering section
    # We'll add telemetry display after the existing fields
    
    # Add telemetry display CSS
    telemetry_css = """
    /* Telemetry-Enhanced Display Styles */
    .telemetry-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 8px;
    }
    
    .telemetry-badge.schema-v1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .telemetry-section {
        margin-top: 12px;
        padding: 12px;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 8px;
        border-left: 3px solid #667eea;
    }
    
    .telemetry-section h6 {
        font-size: 0.85rem;
        font-weight: 600;
        color: #a0aec0;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .telemetry-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 8px;
        margin-top: 8px;
    }
    
    .telemetry-item {
        display: flex;
        flex-direction: column;
    }
    
    .telemetry-label {
        font-size: 0.7rem;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    
    .telemetry-value {
        font-size: 0.9rem;
        color: #e2e8f0;
        font-weight: 500;
        margin-top: 2px;
    }
    
    .setup-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        background: rgba(102, 126, 234, 0.2);
        color: #a5b4fc;
        border: 1px solid rgba(102, 126, 234, 0.3);
    }
    
    .confidence-bar {
        width: 100%;
        height: 6px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 3px;
        overflow: hidden;
        margin-top: 4px;
    }
    
    .confidence-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        transition: width 0.3s ease;
    }
    
    .market-state-indicator {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .market-state-indicator.bullish {
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .market-state-indicator.bearish {
        background: rgba(239, 68, 68, 0.2);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    .target-list {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-top: 6px;
    }
    
    .target-chip {
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 600;
        background: rgba(59, 130, 246, 0.2);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
    """
    
    # Find the </style> tag and insert before it
    style_end = content.find('</style>')
    if style_end != -1:
        content = content[:style_end] + telemetry_css + "\n    " + content[style_end:]
        print("✅ Added telemetry CSS styles")
    
    # Add JavaScript function to render telemetry data
    telemetry_js = """
    
    // Render telemetry-enhanced trade card
    function renderTelemetryTrade(trade) {
        const hasTelemetry = trade.targets || trade.setup || trade.market_state;
        
        let html = `
            <div class="signal-card ${trade.direction?.toLowerCase() || 'unknown'}">
                <div class="signal-header">
                    <div class="signal-id">
                        ${trade.trade_id}
                        ${hasTelemetry ? '<span class="telemetry-badge schema-v1">TELEMETRY</span>' : ''}
                    </div>
                    <div class="signal-status status-${trade.status?.toLowerCase() || 'unknown'}">
                        ${trade.status || 'UNKNOWN'}
                    </div>
                </div>
                
                <div class="signal-body">
                    <div class="signal-row">
                        <span class="signal-label">Direction:</span>
                        <span class="signal-value">${trade.direction || 'N/A'}</span>
                    </div>
                    <div class="signal-row">
                        <span class="signal-label">Session:</span>
                        <span class="signal-value">${trade.session || 'N/A'}</span>
                    </div>
                    <div class="signal-row">
                        <span class="signal-label">Entry:</span>
                        <span class="signal-value">${trade.entry_price || 'N/A'}</span>
                    </div>
                    <div class="signal-row">
                        <span class="signal-label">Stop Loss:</span>
                        <span class="signal-value">${trade.stop_loss || 'N/A'}</span>
                    </div>
                    <div class="signal-row">
                        <span class="signal-label">Current MFE:</span>
                        <span class="signal-value">${trade.current_mfe ? trade.current_mfe.toFixed(2) + 'R' : 'N/A'}</span>
                    </div>
                    ${trade.final_mfe !== null && trade.final_mfe !== undefined ? `
                    <div class="signal-row">
                        <span class="signal-label">Final MFE:</span>
                        <span class="signal-value">${trade.final_mfe.toFixed(2)}R</span>
                    </div>
                    ` : ''}
                    ${trade.exit_price ? `
                    <div class="signal-row">
                        <span class="signal-label">Exit Price:</span>
                        <span class="signal-value">${trade.exit_price}</span>
                    </div>
                    ` : ''}
                    ${trade.exit_reason ? `
                    <div class="signal-row">
                        <span class="signal-label">Exit Reason:</span>
                        <span class="signal-value">${trade.exit_reason}</span>
                    </div>
                    ` : ''}
        `;
        
        // Add telemetry sections if available
        if (hasTelemetry) {
            html += '<div class="telemetry-section">';
            
            // Targets
            if (trade.targets) {
                html += `
                    <h6>🎯 Targets</h6>
                    <div class="target-list">
                        ${trade.targets.tp1_price ? `<div class="target-chip">TP1: ${trade.targets.tp1_price}</div>` : ''}
                        ${trade.targets.tp2_price ? `<div class="target-chip">TP2: ${trade.targets.tp2_price}</div>` : ''}
                        ${trade.targets.tp3_price ? `<div class="target-chip">TP3: ${trade.targets.tp3_price}</div>` : ''}
                    </div>
                `;
            }
            
            // Setup
            if (trade.setup) {
                const signalStrength = trade.setup.signal_strength || 0;
                html += `
                    <h6 style="margin-top: 12px;">⚙️ Setup</h6>
                    <div class="setup-badge">
                        ${trade.setup.setup_family || 'UNKNOWN'} - ${trade.setup.setup_variant || 'UNKNOWN'}
                    </div>
                    <div class="telemetry-item" style="margin-top: 8px;">
                        <span class="telemetry-label">Signal Strength</span>
                        <span class="telemetry-value">${signalStrength.toFixed(0)}%</span>
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: ${signalStrength}%"></div>
                        </div>
                    </div>
                `;
                
                // Confidence components
                if (trade.setup.confidence_components) {
                    html += '<div class="telemetry-grid" style="margin-top: 8px;">';
                    const components = trade.setup.confidence_components;
                    if (components.trend_alignment !== undefined) {
                        html += `
                            <div class="telemetry-item">
                                <span class="telemetry-label">Trend Align</span>
                                <span class="telemetry-value">${(components.trend_alignment * 100).toFixed(0)}%</span>
                            </div>
                        `;
                    }
                    if (components.structure_quality !== undefined) {
                        html += `
                            <div class="telemetry-item">
                                <span class="telemetry-label">Structure</span>
                                <span class="telemetry-value">${(components.structure_quality * 100).toFixed(0)}%</span>
                            </div>
                        `;
                    }
                    if (components.volatility_fit !== undefined) {
                        html += `
                            <div class="telemetry-item">
                                <span class="telemetry-label">Volatility</span>
                                <span class="telemetry-value">${(components.volatility_fit * 100).toFixed(0)}%</span>
                            </div>
                        `;
                    }
                    html += '</div>';
                }
            }
            
            // Market State
            if (trade.market_state) {
                const trendRegime = trade.market_state.trend_regime || 'UNKNOWN';
                const trendScore = trade.market_state.trend_score || 0;
                html += `
                    <h6 style="margin-top: 12px;">📊 Market State</h6>
                    <div class="market-state-indicator ${trendRegime.toLowerCase()}">
                        ${trendRegime} Trend (${(trendScore * 100).toFixed(0)}%)
                    </div>
                    <div class="telemetry-grid" style="margin-top: 8px;">
                        <div class="telemetry-item">
                            <span class="telemetry-label">Volatility</span>
                            <span class="telemetry-value">${trade.market_state.volatility_regime || 'N/A'}</span>
                        </div>
                        ${trade.market_state.structure ? `
                        <div class="telemetry-item">
                            <span class="telemetry-label">Swing State</span>
                            <span class="telemetry-value">${trade.market_state.structure.swing_state || 'N/A'}</span>
                        </div>
                        ` : ''}
                    </div>
                `;
            }
            
            html += '</div>'; // Close telemetry-section
        }
        
        html += `
                </div>
                <div class="signal-footer">
                    <button class="btn-delete" onclick="deleteTrade('${trade.trade_id}')">
                        Delete
                    </button>
                </div>
            </div>
        `;
        
        return html;
    }
    
    // Update the renderTrades function to use telemetry renderer
    function renderTrades(trades, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        if (!trades || trades.length === 0) {
            container.innerHTML = '<p style="color: #718096; text-align: center; padding: 20px;">No trades found</p>';
            return;
        }
        
        container.innerHTML = trades.map(trade => renderTelemetryTrade(trade)).join('');
    }
    """
    
    # Find the existing renderTrades function and replace it
    render_start = content.find('function renderTrades(')
    if render_start != -1:
        # Find the end of the function (next function or script end)
        render_end = content.find('function ', render_start + 1)
        if render_end == -1:
            render_end = content.find('</script>', render_start)
        
        # Replace the old function with new telemetry-aware version
        content = content[:render_start] + telemetry_js.strip() + "\n\n    " + content[render_end:]
        print("✅ Updated JavaScript to render telemetry data")
    else:
        # If function not found, add before </script>
        script_end = content.rfind('</script>')
        if script_end != -1:
            content = content[:script_end] + telemetry_js + "\n    " + content[script_end:]
            print("✅ Added telemetry rendering JavaScript")
    
    # Write updated dashboard
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Dashboard upgraded: {dashboard_path}")
    return True

def create_backup():
    """Create backup of current dashboard"""
    dashboard_path = "templates/automated_signals_dashboard.html"
    backup_path = f"templates/automated_signals_dashboard_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    
    try:
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Backup created: {backup_path}")
        return True
    except Exception as e:
        print(f"⚠️  Backup failed: {e}")
        return False

def main():
    print("\n" + "=" * 70)
    print("PHASE 7: DASHBOARD TELEMETRY UPGRADE")
    print("=" * 70 + "\n")
    
    # Create backup
    create_backup()
    
    # Upgrade dashboard
    if upgrade_dashboard_html():
        print("\n" + "=" * 70)
        print("✅ PHASE 7 COMPLETE")
        print("=" * 70)
        print("\n🎯 DASHBOARD UPGRADED WITH:")
        print("   ✅ Telemetry badge indicators")
        print("   ✅ Nested targets display")
        print("   ✅ Setup family/variant badges")
        print("   ✅ Signal strength visualization")
        print("   ✅ Confidence components breakdown")
        print("   ✅ Market state indicators")
        print("   ✅ Enhanced visual styling")
        print("\n📋 NEXT STEPS:")
        print("   1. Test dashboard locally")
        print("   2. Deploy to Railway")
        print("   3. Update TradingView indicator")
    else:
        print("\n❌ PHASE 7 FAILED")
        print("   Review errors above and retry")

if __name__ == "__main__":
    main()
