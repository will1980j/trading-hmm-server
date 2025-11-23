// ============================================================================
// MODULE 17 - TIME ANALYSIS (PHASE 2C)
// Wired to Phase 2A Read-Only APIs - Real Data
// ============================================================================

class TimeAnalysis {
    constructor() {
        this.isLoading = false;
        this.todaySignals = [];
        this.sessionData = {};
        
        this.init();
    }
    
    async init() {
        console.log('🚀 Time Analysis - Phase 2C Initialized (Real Data)');
        
        await this.fetchAllData();
    }
    
    async fetchAllData() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        try {
            await Promise.all([
                this.fetchTodaySignals(),
                this.fetchSessionSummary()
            ]);
            
            this.renderAll();
        } catch (error) {
            console.error('❌ Time Analysis - Error fetching data:', error);
            this.renderEmpty();
        } finally {
            this.isLoading = false;
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
    
    async fetchSessionSummary() {
        try {
            const endDate = new Date();
            const startDate = new Date();
            startDate.setDate(startDate.getDate() - 30);
            
            const start = startDate.toISOString().split('T')[0];
            const end = endDate.toISOString().split('T')[0];
            
            const response = await fetch(`/api/session-summary?start=${start}&end=${end}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            if (data.success && data.sessions) {
                this.sessionData = data.sessions;
            }
        } catch (error) {
            console.error('❌ Error fetching session summary:', error);
            this.sessionData = {};
        }
    }
    
    renderAll() {
        this.renderMetricSummary();
        this.renderSessionHeatmap();
        this.renderSessionCards();
        this.renderRDistribution();
    }
    
    renderEmpty() {
        this.renderMetricSummary({});
        this.renderSessionHeatmap({});
        this.renderSessionCards({});
        this.renderRDistribution([]);
    }
    
    renderMetricSummary() {
        const overallWinrate = this.calculateOverallWinrate();
        const overallExpectancy = this.calculateOverallExpectancy();
        const overallAvgR = this.calculateOverallAvgR();
        const totalTrades = this.calculateTotalTrades();
        const bestSession = this.findBestSession();
        
        const winrateEl = document.getElementById('winrate-overall');
        if (winrateEl) winrateEl.textContent = overallWinrate.toFixed(1) + '%';
        
        const expectancyEl = document.getElementById('expectancy');
        if (expectancyEl) expectancyEl.textContent = overallExpectancy.toFixed(2) + 'R';
        
        const avgREl = document.getElementById('avg-r');
        if (avgREl) avgREl.textContent = overallAvgR.toFixed(2) + 'R';
        
        const totalEl = document.getElementById('total-trades');
        if (totalEl) totalEl.textContent = totalTrades;
        
        const bestEl = document.getElementById('best-session');
        if (bestEl) bestEl.textContent = bestSession;
    }
    
    renderSessionHeatmap() {
        const container = document.getElementById('session-heatmap');
        if (!container) return;
        
        const sessions = Object.keys(this.sessionData);
        
        if (sessions.length === 0) {
            container.innerHTML = '<div class="no-data">No session data available</div>';
            return;
        }
        
        container.innerHTML = '';
        
        sessions.forEach(session => {
            const data = this.sessionData[session];
            const winrate = data.winrate || 0;
            const intensity = Math.min(winrate / 100, 1);
            const color = intensity > 0.5 ? 
                `rgba(16, 185, 129, ${intensity})` : 
                `rgba(239, 68, 68, ${1 - intensity})`;
            
            const cell = document.createElement('div');
            cell.className = 'session-heatmap-cell';
            cell.style.background = color;
            
            cell.innerHTML = `
                <span class="session-name">${session.replace('_', ' ')}</span>
                <span class="session-value">${winrate.toFixed(1)}%</span>
            `;
            
            container.appendChild(cell);
        });
    }
    
    renderSessionCards() {
        const winrateContainer = document.getElementById('session-winrate-cards');
        const expectancyContainer = document.getElementById('session-expectancy-cards');
        
        if (!winrateContainer || !expectancyContainer) return;
        
        const sessions = Object.keys(this.sessionData);
        
        if (sessions.length === 0) {
            winrateContainer.innerHTML = '<div class="no-data">No data</div>';
            expectancyContainer.innerHTML = '<div class="no-data">No data</div>';
            return;
        }
        
        winrateContainer.innerHTML = '';
        expectancyContainer.innerHTML = '';
        
        sessions.forEach(session => {
            const data = this.sessionData[session];
            
            const winrateCard = document.createElement('div');
            winrateCard.className = 'session-card';
            winrateCard.innerHTML = `
                <div class="session-card-name">${session.replace('_', ' ')}</div>
                <div class="session-card-value">${(data.winrate || 0).toFixed(1)}%</div>
            `;
            winrateContainer.appendChild(winrateCard);
            
            const expectancyCard = document.createElement('div');
            expectancyCard.className = 'session-card';
            expectancyCard.innerHTML = `
                <div class="session-card-name">${session.replace('_', ' ')}</div>
                <div class="session-card-value">${(data.expectancy || 0).toFixed(2)}R</div>
            `;
            expectancyContainer.appendChild(expectancyCard);
        });
    }
    
    renderRDistribution() {
        const container = document.getElementById('session-r-distribution');
        if (!container) return;
        
        if (this.todaySignals.length === 0) {
            const ctx = container.getContext('2d');
            ctx.fillStyle = '#1A1C22';
            ctx.fillRect(0, 0, container.width, container.height);
            ctx.fillStyle = '#9CA3AF';
            ctx.font = '14px Inter, sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText('No signal data available', container.width / 2, container.height / 2);
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
        
        const ctx = container.getContext('2d');
        ctx.fillStyle = '#1A1C22';
        ctx.fillRect(0, 0, container.width, container.height);
        ctx.fillStyle = '#9CA3AF';
        ctx.font = '12px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('R-Distribution Chart (Placeholder)', container.width / 2, container.height / 2);
    }
    
    calculateOverallWinrate() {
        const sessions = Object.values(this.sessionData);
        if (sessions.length === 0) return 0;
        
        const totalWins = sessions.reduce((sum, s) => sum + (s.wins || 0), 0);
        const totalTrades = sessions.reduce((sum, s) => sum + (s.total || 0), 0);
        
        return totalTrades > 0 ? (totalWins / totalTrades) * 100 : 0;
    }
    
    calculateOverallExpectancy() {
        const sessions = Object.values(this.sessionData);
        if (sessions.length === 0) return 0;
        
        const totalExpectancy = sessions.reduce((sum, s) => sum + (s.expectancy || 0), 0);
        return totalExpectancy / sessions.length;
    }
    
    calculateOverallAvgR() {
        const sessions = Object.values(this.sessionData);
        if (sessions.length === 0) return 0;
        
        const totalAvgR = sessions.reduce((sum, s) => sum + (s.avg_r || 0), 0);
        return totalAvgR / sessions.length;
    }
    
    calculateTotalTrades() {
        const sessions = Object.values(this.sessionData);
        return sessions.reduce((sum, s) => sum + (s.total || 0), 0);
    }
    
    findBestSession() {
        const sessions = Object.entries(this.sessionData);
        if (sessions.length === 0) return 'N/A';
        
        let best = sessions[0];
        sessions.forEach(([name, data]) => {
            if ((data.expectancy || 0) > (best[1].expectancy || 0)) {
                best = [name, data];
            }
        });
        
        return best[0].replace('_', ' ');
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    window.timeAnalysis = new TimeAnalysis();
});

console.log('Time Analysis JS Module loaded successfully (Phase 2C)');
