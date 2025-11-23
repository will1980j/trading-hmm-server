// ============================================================================
// MODULE 22 - REPORTING CENTER (PHASE 2C)
// Wired to Phase 2A Read-Only APIs - Real Data
// ============================================================================

class ReportingCenter {
    constructor() {
        this.isLoading = false;
        this.todayStats = {};
        this.recentSignals = [];
        this.sessionData = {};
        
        this.init();
    }
    
    async init() {
        console.log('🚀 Reporting Center - Phase 2C Initialized (Real Data)');
        
        await this.fetchAllData();
        this.setupCategorySelector();
    }
    
    async fetchAllData() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        try {
            await Promise.all([
                this.fetchTodayStats(),
                this.fetchRecentSignals(),
                this.fetchSessionSummary()
            ]);
            
            this.renderAllReports();
        } catch (error) {
            console.error('❌ Reporting Center - Error fetching data:', error);
            this.renderEmptyReports();
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
    
    async fetchRecentSignals() {
        try {
            const response = await fetch('/api/signals/recent?limit=100');
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
    
    async fetchSessionSummary() {
        try {
            const response = await fetch('/api/session-summary');
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
    
    renderAllReports() {
        this.renderDailyReport();
        this.renderWeeklyReport();
        this.renderMonthlyReport();
    }
    
    renderEmptyReports() {
        this.renderDailyReport({});
        this.renderWeeklyReport([]);
        this.renderMonthlyReport({});
    }
    
    renderDailyReport() {
        const container = document.getElementById('tradingReports');
        if (!container) return;
        
        const signals = this.todayStats.total || 0;
        const avgR = this.todayStats.avg_r ? parseFloat(this.todayStats.avg_r).toFixed(1) : '0.0';
        const winrate = this.todayStats.winrate ? parseFloat(this.todayStats.winrate).toFixed(1) : '0.0';
        const estimatedPnl = parseFloat(avgR) * signals * 100;
        
        const avgRClass = parseFloat(avgR) >= 0 ? 'positive' : 'negative';
        const pnlClass = estimatedPnl >= 0 ? 'positive' : 'negative';
        
        const card = document.createElement('div');
        card.className = 'report-card';
        
        card.innerHTML = `
            <h3 class="report-title">Daily Report</h3>
            <div class="report-metrics">
                <div class="metric-item">
                    <div class="metric-label">Signals</div>
                    <div class="metric-value">${signals}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Est. P&L</div>
                    <div class="metric-value ${pnlClass}">${estimatedPnl >= 0 ? '+' : ''}$${Math.abs(estimatedPnl).toFixed(0)}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Win Rate</div>
                    <div class="metric-value">${winrate}%</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Avg R</div>
                    <div class="metric-value ${avgRClass}">${parseFloat(avgR) >= 0 ? '+' : ''}${avgR}R</div>
                </div>
            </div>
            <div class="chart-placeholder">
                <div class="placeholder-text">Equity curve placeholder</div>
            </div>
        `;
        
        container.innerHTML = '';
        container.appendChild(card);
    }
    
    renderWeeklyReport() {
        const weekSignals = this.recentSignals.slice(0, 50);
        
        if (weekSignals.length === 0) {
            console.log('No signals for weekly report');
            return;
        }
        
        const totalR = weekSignals.reduce((sum, s) => sum + (parseFloat(s.r_multiple) || 0), 0);
        const avgR = totalR / weekSignals.length;
        const wins = weekSignals.filter(s => (parseFloat(s.r_multiple) || 0) > 0).length;
        const winrate = (wins / weekSignals.length) * 100;
        const estimatedPnl = totalR * 100;
        
        console.log('Weekly Report:', {
            signals: weekSignals.length,
            avgR: avgR.toFixed(2),
            winrate: winrate.toFixed(1),
            estimatedPnl: estimatedPnl.toFixed(0)
        });
    }
    
    renderMonthlyReport() {
        const sessions = Object.keys(this.sessionData);
        
        if (sessions.length === 0) {
            console.log('No session data for monthly report');
            return;
        }
        
        const totalTrades = sessions.reduce((sum, s) => sum + (this.sessionData[s].total || 0), 0);
        const avgExpectancy = sessions.reduce((sum, s) => sum + (this.sessionData[s].expectancy || 0), 0) / sessions.length;
        
        console.log('Monthly Report:', {
            sessions: sessions.length,
            totalTrades,
            avgExpectancy: avgExpectancy.toFixed(2)
        });
    }
    
    setupCategorySelector() {
        const categoryCards = document.querySelectorAll('.category-card');
        
        categoryCards.forEach(card => {
            card.addEventListener('click', function() {
                const category = this.getAttribute('data-category');
                
                categoryCards.forEach(c => c.classList.remove('active'));
                this.classList.add('active');
                
                document.querySelectorAll('.report-section').forEach(section => {
                    section.style.display = 'none';
                });
                
                const sectionId = `${category}-section`;
                const section = document.getElementById(sectionId);
                if (section) {
                    section.style.display = 'block';
                }
                
                console.log(`Switched to ${category} category`);
            });
        });
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    window.reportingCenter = new ReportingCenter();
});

console.log('Reporting Center JS loaded successfully (Phase 2C)');
