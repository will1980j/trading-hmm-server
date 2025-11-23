// ============================================================================
// MODULE 20 - ML INTELLIGENCE HUB (PHASE 2C)
// Overview tiles wired to Phase 2A APIs - Model/AI panels remain mock
// ============================================================================

class MLHub {
    constructor() {
        this.isLoading = false;
        this.pollingInterval = null;
        this.systemStatus = {};
        this.todayStats = {};
        
        this.init();
    }
    
    async init() {
        console.log('🚀 ML Hub - Phase 2C Initialized (Real Overview Data)');
        
        // Fetch real data for overview tiles
        await this.fetchOverviewData();
        
        // Render mock panels (MODEL-, FORECAST-, AI- remain as placeholders)
        this.renderModelPanels();
        this.renderForecastPanels();
        this.renderAIPanels();
        
        // Start polling for overview data only
        this.startPolling();
    }
    
    async fetchOverviewData() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        try {
            await Promise.all([
                this.fetchSystemStatus(),
                this.fetchTodayStats()
            ]);
            
            this.renderOverviewTiles();
        } catch (error) {
            console.error('❌ ML Hub - Error fetching overview data:', error);
        } finally {
            this.isLoading = false;
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
    
    renderOverviewTiles() {
        const currentSession = this.systemStatus.current_session || 'UNKNOWN';
        const todaySignals = this.todayStats.total || 0;
        const avgR = this.todayStats.avg_r ? parseFloat(this.todayStats.avg_r).toFixed(1) : '0.0';
        const lastSignalTime = this.systemStatus.last_signal_timestamp ? 
            new Date(this.systemStatus.last_signal_timestamp).toLocaleTimeString() : 'N/A';
        
        const avgRClass = parseFloat(avgR) >= 0 ? 'positive' : 'negative';
        
        const marketRegimeEl = document.getElementById('marketRegime');
        if (marketRegimeEl) marketRegimeEl.textContent = currentSession.replace('_', ' ');
        
        const signalQualityEl = document.getElementById('signalQuality');
        if (signalQualityEl) signalQualityEl.textContent = todaySignals;
        
        const volatilityEl = document.getElementById('volatilityOutlook');
        if (volatilityEl) volatilityEl.textContent = avgR + 'R';
        
        const modelConfidenceEl = document.getElementById('modelConfidence');
        if (modelConfidenceEl) modelConfidenceEl.textContent = lastSignalTime;
        
        const strategyEl = document.getElementById('strategyRecommendation');
        if (strategyEl) {
            strategyEl.textContent = avgR + 'R Avg';
            strategyEl.className = avgRClass;
        }
    }
    
    renderModelPanels() {
        console.log('MODEL panels remain as Phase 1 placeholders');
    }
    
    renderForecastPanels() {
        console.log('FORECAST panels remain as Phase 1 placeholders');
    }
    
    renderAIPanels() {
        console.log('AI panels remain as Phase 1 placeholders');
    }
    
    startPolling() {
        this.pollingInterval = setInterval(() => {
            this.fetchOverviewData();
        }, 20000);
        
        console.log('🔄 ML Hub polling started (20s interval)');
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
    window.mlHub = new MLHub();
});

console.log('ML Intelligence Hub JS loaded successfully (Phase 2C)');
