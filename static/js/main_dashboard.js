// ============================================================================
// MODULE 16 - MAIN SYSTEM DASHBOARD (PHASE 2C)
// Wired to Phase 2A Read-Only APIs - Real Data
// ============================================================================

class MainDashboard {
    constructor() {
        this.isLoading = false;
        this.pollingInterval = null;
        this.liveSignals = [];
        this.todayStats = {};
        this.systemStatus = {};
        
        this.init();
    }
    
    async init() {
        console.log('🚀 Main Dashboard - Phase 2C Initialized (Real Data)');
        
        // Initial data fetch
        await this.fetchAllData();
        
        // Start polling every 15 seconds
        this.startPolling();
    }
    
    async fetchAllData() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        try {
            await Promise.all([
                this.fetchLiveSignals(),
                this.fetchTodayStats(),
                this.fetchSystemStatus()
            ]);
            
            this.renderAll();
        } catch (error) {
            console.error('❌ Main Dashboard - Error fetching data:', error);
        } finally {
            this.isLoading = false;
        }
    }
    
    async fetchLiveSignals() {
        try {
            const response = await fetch('/api/signals/live');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            if (data.success && data.signals) {
                this.liveSignals = data.signals;
            }
        } catch (error) {
            console.error('❌ Error fetching live signals:', error);
            this.liveSignals = [];
        }
    }
    
    async fetchTodayStats() {
        try {
            const response = await fetch('/api/signals/stats/today');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            if (data.success && data.stats) {
                this.todayStats = data.stats;
            }
        } catch (error) {
            console.error('❌ Error fetching today stats:', error);
            this.todayStats = {};
        }
    }
    
    async fetchSystemStatus() {
        try {
            const response = await fetch('/api/system-status');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            if (data.success && data.status) {
                this.systemStatus = data.status;
            }
        } catch (error) {
            console.error('❌ Error fetching system status:', error);
            this.systemStatus = {};
        }
    }
    
    renderAll() {
        this.renderTopBar();
        this.renderActiveSignals();
        this.renderAutomationMetrics();
        this.renderPnLToday();
    }
    
    renderTopBar() {
        const webhookHealth = this.systemStatus.webhook_health || 'UNKNOWN';
        const currentSession = this.systemStatus.current_session || 'UNKNOWN';
        const queueDepth = this.systemStatus.queue_depth || 0;
        const latencyMs = this.systemStatus.latency_ms || 0;
        
        const statusClass = webhookHealth === 'HEALTHY' ? 'status-healthy' : 
                           webhookHealth === 'DEGRADED' ? 'status-warning' : 'status-error';
        
        const automationEl = document.getElementById('automation-status');
        if (automationEl) {
            const valueEl = automationEl.querySelector('.pill-value');
            if (valueEl) valueEl.textContent = webhookHealth;
            automationEl.className = `status-pill ${statusClass}`;
        }
        
        const queueEl = document.getElementById('queue-depth');
        if (queueEl) queueEl.textContent = queueDepth;
        
        const webhookEl = document.getElementById('webhook-health');
        if (webhookEl) webhookEl.textContent = webhookHealth;
        
        const sessionEl = document.getElementById('session-label');
        if (sessionEl) sessionEl.textContent = currentSession.replace('_', ' ');
        
        const latencyEl = document.getElementById('latency-ms');
        if (latencyEl) latencyEl.textContent = `${latencyMs}ms`;
    }
    
    renderActiveSignals() {
        const container = document.getElementById('active-signals-list');
        const countBadge = document.getElementById('active-count');
        
        if (!container) return;
        
        if (countBadge) countBadge.textContent = this.liveSignals.length;
        
        if (this.liveSignals.length === 0) {
            container.innerHTML = '<p class="placeholder-text">No active signals</p>';
            return;
        }
        
        const recentSignals = this.liveSignals.slice(0, 5);
        
        container.innerHTML = recentSignals.map(signal => {
            const direction = signal.direction || 'UNKNOWN';
            const entryPrice = signal.entry_price ? parseFloat(signal.entry_price).toFixed(2) : 'N/A';
            const time = signal.signal_time || 'N/A';
            const status = signal.status || 'UNKNOWN';
            
            return `
                <div class="signal-item">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="color: ${direction === 'LONG' ? '#10B981' : '#EF4444'}">
                                ${direction}
                            </strong>
                            <span style="color: #9CA3AF; margin-left: 8px;">NQ</span>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 14px; font-weight: 600;">${entryPrice}</div>
                            <div style="font-size: 11px; color: #9CA3AF;">${time}</div>
                        </div>
                    </div>
                    <div style="margin-top: 8px; font-size: 12px; color: #9CA3AF;">
                        ${status.replace(/_/g, ' ')}
                    </div>
                </div>
            `;
        }).join('');
    }
    
    renderAutomationMetrics() {
        const signalsProcessed = this.todayStats.total || 0;
        const avgR = this.todayStats.avg_r ? parseFloat(this.todayStats.avg_r).toFixed(2) : '0.00';
        const winrate = this.todayStats.winrate ? parseFloat(this.todayStats.winrate).toFixed(1) : '0.0';
        
        const signalsEl = document.getElementById('signals-processed');
        if (signalsEl) signalsEl.textContent = signalsProcessed;
        
        const confirmationsEl = document.getElementById('confirmations-pending');
        if (confirmationsEl) confirmationsEl.textContent = this.liveSignals.length;
        
        const entriesEl = document.getElementById('auto-entries');
        if (entriesEl) entriesEl.textContent = signalsProcessed;
    }
    
    renderPnLToday() {
        const avgR = this.todayStats.avg_r ? parseFloat(this.todayStats.avg_r) : 0;
        const totalSignals = this.todayStats.total || 0;
        const estimatedPnl = avgR * totalSignals * 100;
        
        const pnlEl = document.getElementById('pnl-today');
        if (pnlEl) {
            pnlEl.textContent = (estimatedPnl >= 0 ? '+' : '') + estimatedPnl.toFixed(2);
            pnlEl.style.color = estimatedPnl >= 0 ? '#10B981' : '#EF4444';
        }
        
        const changeEl = document.getElementById('pnl-change');
        if (changeEl) {
            const change = avgR >= 0 ? `+${(avgR * 100).toFixed(1)}%` : `${(avgR * 100).toFixed(1)}%`;
            changeEl.textContent = change;
            changeEl.style.color = avgR >= 0 ? '#10B981' : '#EF4444';
        }
    }
    
    startPolling() {
        this.pollingInterval = setInterval(() => {
            this.fetchAllData();
        }, 15000);
        
        console.log('🔄 Main Dashboard polling started (15s interval)');
    }
    
    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    window.mainDashboard = new MainDashboard();
});

console.log('Main Dashboard JS Module loaded successfully (Phase 2C)');
