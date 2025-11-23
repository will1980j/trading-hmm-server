// ============================================================================
// MODULE 21 - FINANCIAL SUMMARY (PHASE 2C)
// Wired to Phase 2A Read-Only APIs - Real Data
// ============================================================================

class FinancialSummary {
    constructor() {
        this.isLoading = false;
        this.todayStats = {};
        this.todaySignals = [];
        this.recentSignals = [];
        
        this.init();
    }
    
    async init() {
        console.log('🚀 Financial Summary - Phase 2C Initialized (Real Data)');
        
        await this.fetchAllData();
    }
    
    async fetchAllData() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        try {
            await Promise.all([
                this.fetchTodayStats(),
                this.fetchTodaySignals(),
                this.fetchRecentSignals()
            ]);
            
            this.renderAll();
        } catch (error) {
            console.error('❌ Financial Summary - Error fetching data:', error);
            this.renderEmpty();
        } finally {
            this.isLoading = false;
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
    
    async fetchTodaySignals() {
        try {
            const response = await fetch('/api/signals/today');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            if (data.success && data.signals) {
                this.todaySignals = data.signals;
            }
        } catch (error) {
            console.error('❌ Error fetching today signals:', error);
            this.todaySignals = [];
        }
    }
    
    async fetchRecentSignals() {
        try {
            const response = await fetch('/api/signals/recent?limit=50');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            if (data.success && data.signals) {
                this.recentSignals = data.signals;
            }
        } catch (error) {
            console.error('❌ Error fetching recent signals:', error);
            this.recentSignals = [];
        }
    }
    
    renderAll() {
        this.renderGlobalMetrics();
        this.renderPersonalPerformance();
        this.renderRDistribution();
        this.renderSessionProfitability();
    }
    
    renderEmpty() {
        this.renderGlobalMetrics({});
        this.renderPersonalPerformance({});
        this.renderRDistribution([]);
        this.renderSessionProfitability([]);
    }
    
    renderGlobalMetrics() {
        const avgR = this.todayStats.avg_r ? parseFloat(this.todayStats.avg_r) : 0;
        const totalSignals = this.todayStats.total || 0;
        const estimatedPnl = avgR * totalSignals * 100;
        const winrate = this.todayStats.winrate ? parseFloat(this.todayStats.winrate).toFixed(1) : '0.0';
        
        const totalPnLEl = document.getElementById('totalPnL');
        if (totalPnLEl) {
            totalPnLEl.textContent = estimatedPnl.toFixed(2);
            totalPnLEl.style.color = estimatedPnl >= 0 ? '#10B981' : '#EF4444';
        }
        
        const combinedREl = document.getElementById('combinedR');
        if (combinedREl) {
            combinedREl.textContent = avgR.toFixed(2) + 'R';
            combinedREl.style.color = avgR >= 0 ? '#10B981' : '#EF4444';
        }
        
        const activeAccountsEl = document.getElementById('activeAccounts');
        if (activeAccountsEl) activeAccountsEl.textContent = totalSignals;
        
        const scalingIndexEl = document.getElementById('scalingIndex');
        if (scalingIndexEl) scalingIndexEl.textContent = (winrate / 100).toFixed(2);
    }
    
    renderPersonalPerformance() {
        const avgR = this.todayStats.avg_r ? parseFloat(this.todayStats.avg_r) : 0;
        const totalSignals = this.todayStats.total || 0;
        const estimatedPnl = avgR * totalSignals * 100;
        
        const rTodayEl = document.getElementById('personalRToday');
        if (rTodayEl) {
            rTodayEl.textContent = (avgR >= 0 ? '+' : '') + avgR.toFixed(2) + 'R';
            rTodayEl.className = `pnl-r ${avgR >= 0 ? 'positive' : 'negative'}`;
        }
        
        const dollarTodayEl = document.getElementById('personalDollarToday');
        if (dollarTodayEl) {
            dollarTodayEl.textContent = estimatedPnl.toFixed(2);
            dollarTodayEl.style.color = estimatedPnl >= 0 ? '#10B981' : '#EF4444';
        }
    }
    
    renderRDistribution() {
        if (this.todaySignals.length === 0) {
            console.log('No signals for R-distribution');
            return;
        }
        
        const rBuckets = {
            '-2 to -1': 0,
            '-1 to 0': 0,
            '0 to 1': 0,
            '1 to 2': 0,
            '2 to 3': 0,
            '3+': 0
        };
        
        this.todaySignals.forEach(signal => {
            const r = signal.r_multiple ? parseFloat(signal.r_multiple) : 0;
            
            if (r >= -2 && r < -1) rBuckets['-2 to -1']++;
            else if (r >= -1 && r < 0) rBuckets['-1 to 0']++;
            else if (r >= 0 && r < 1) rBuckets['0 to 1']++;
            else if (r >= 1 && r < 2) rBuckets['1 to 2']++;
            else if (r >= 2 && r < 3) rBuckets['2 to 3']++;
            else if (r >= 3) rBuckets['3+']++;
        });
        
        console.log('R-Distribution calculated:', rBuckets);
    }
    
    renderSessionProfitability() {
        const sessionMap = {};
        
        this.todaySignals.forEach(signal => {
            const session = signal.session || 'UNKNOWN';
            const r = signal.r_multiple ? parseFloat(signal.r_multiple) : 0;
            
            if (!sessionMap[session]) {
                sessionMap[session] = { total: 0, count: 0 };
            }
            
            sessionMap[session].total += r;
            sessionMap[session].count += 1;
        });
        
        Object.keys(sessionMap).forEach(session => {
            const data = sessionMap[session];
            const avgR = data.count > 0 ? data.total / data.count : 0;
            const estimatedPnl = avgR * data.count * 100;
            
            const sessionEl = document.getElementById(`session-${session.toLowerCase().replace(' ', '-')}`);
            if (sessionEl) {
                sessionEl.textContent = (estimatedPnl >= 0 ? '+' : '') + '$' + estimatedPnl.toFixed(0);
                sessionEl.style.color = estimatedPnl >= 0 ? '#10B981' : '#EF4444';
            }
        });
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    window.financialSummary = new FinancialSummary();
});

console.log('Financial Summary JS loaded successfully (Phase 2C)');
