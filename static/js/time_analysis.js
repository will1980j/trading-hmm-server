// ============================================================================
// MODULE 17 - TIME ANALYSIS (H1.3 - Canonical API)
// Uses /api/time-analysis as single source of truth
// ============================================================================

class TimeAnalysis {
    constructor() {
        this.isLoading = false;
        this.data = null;
        
        this.init();
    }
    
    async init() {
        console.log('🚀 Time Analysis - H1.3 Initialized (Canonical API)');
        
        await this.fetchAllData();
    }
    
    async fetchAllData() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        try {
            const res = await fetch('/api/time-analysis');
            if (!res.ok) {
                console.error('❌ Time Analysis API returned:', res.status);
                this.renderEmpty();
                return;
            }
            
            const data = await res.json();
            this.data = data;
            console.log('✅ Time Analysis data loaded:', data);
            this.renderAll();
        } catch (e) {
            console.error('❌ Time Analysis fetch error:', e);
            this.renderEmpty();
        } finally {
            this.isLoading = false;
        }
    }
    
    renderAll() {
        if (!this.data) {
            this.renderEmpty();
            return;
        }
        
        this.renderMetricSummary();
        this.renderSessionAnalysis();
        this.renderHourlyAnalysis();
        this.renderDayAnalysis();
        this.renderSessionHotspots();
        this.renderHotColdHours();
    }
    
    renderEmpty() {
        const elements = [
            'winrate-overall', 'expectancy', 'avg-r', 'total-trades', 'best-session'
        ];
        elements.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.textContent = '--';
        });
        
        console.log('📊 Time Analysis - No data available');
    }
    
    renderMetricSummary() {
        if (!this.data) return;
        
        // Calculate overall win rate from session data
        let totalWins = 0;
        let totalTrades = this.data.total_trades || 0;
        
        if (this.data.session && this.data.session.length > 0) {
            this.data.session.forEach(s => {
                totalWins += Math.round(s.trades * s.win_rate);
            });
        }
        
        const overallWinrate = totalTrades > 0 ? (totalWins / totalTrades) * 100 : 0;
        
        const winrateEl = document.getElementById('winrate-overall');
        if (winrateEl) winrateEl.textContent = overallWinrate.toFixed(1) + '%';
        
        const expectancyEl = document.getElementById('expectancy');
        if (expectancyEl) expectancyEl.textContent = (this.data.overall_expectancy || 0).toFixed(2) + 'R';
        
        const avgREl = document.getElementById('avg-r');
        if (avgREl) avgREl.textContent = (this.data.overall_expectancy || 0).toFixed(2) + 'R';
        
        const totalEl = document.getElementById('total-trades');
        if (totalEl) totalEl.textContent = totalTrades;
        
        const bestEl = document.getElementById('best-session');
        if (bestEl && this.data.best_session) {
            bestEl.textContent = this.data.best_session.session || '--';
        }
    }
    
    renderSessionAnalysis() {
        if (!this.data || !this.data.session) return;
        
        console.log('📊 Session Analysis:', this.data.session);
        
        // Render session cards in both grids
        const winrateContainer = document.getElementById('session-winrate-cards');
        const expectancyContainer = document.getElementById('session-expectancy-cards');
        
        if (winrateContainer) {
            winrateContainer.innerHTML = '';
            this.data.session.forEach(sessionData => {
                const card = this.createSessionCard(sessionData, 'winrate');
                winrateContainer.appendChild(card);
            });
        }
        
        if (expectancyContainer) {
            expectancyContainer.innerHTML = '';
            this.data.session.forEach(sessionData => {
                const card = this.createSessionCard(sessionData, 'expectancy');
                expectancyContainer.appendChild(card);
            });
        }
    }
    
    createSessionCard(sessionData, type) {
        const card = document.createElement('div');
        card.className = 'session-card';
        
        const value = type === 'winrate' 
            ? (sessionData.win_rate * 100).toFixed(1) + '%'
            : sessionData.expectancy.toFixed(2) + 'R';
        
        card.innerHTML = `
            <div class="session-title">${sessionData.session}</div>
            <div class="session-value">${value}</div>
            <div class="session-metric">Trades: ${sessionData.trades}</div>
            <div class="session-hotspot-row">
                <div class="hot-label">Hot Hours:</div>
                <div class="hot-values" data-hot-hours-for="${sessionData.session}">--</div>
            </div>
            <div class="session-hotspot-row">
                <div class="cold-label">Cold Hour:</div>
                <div class="cold-values" data-cold-hours-for="${sessionData.session}">--</div>
            </div>
        `;
        
        return card;
    }
    
    renderHourlyAnalysis() {
        if (!this.data || !this.data.hourly) return;
        
        console.log('📊 Hourly Analysis:', this.data.hourly);
        // Placeholder for hourly visualization
        // Can be enhanced with charts in future iterations
    }
    
    renderDayAnalysis() {
        if (!this.data || !this.data.day_of_week) return;
        
        console.log('📊 Day Analysis:', this.data.day_of_week);
        // Placeholder for day-of-week visualization
        // Can be enhanced with charts in future iterations
    }
    
    renderSessionHotspots() {
        if (!this.data || !this.data.session_hotspots || !this.data.session_hotspots.sessions) {
            console.log('📊 Session Hotspots: No data available');
            return;
        }
        
        const sessions = this.data.session_hotspots.sessions;
        console.log('🔥 Session Hotspots:', sessions);
        
        // Log detailed hotspot information for each session
        Object.entries(sessions).forEach(([sessionName, hotspotData]) => {
            console.log(`  ${sessionName}:`, {
                hot_hours: hotspotData.hot_hours,
                cold_hours: hotspotData.cold_hours,
                avg_r: hotspotData.avg_r,
                win_rate: (hotspotData.win_rate * 100).toFixed(1) + '%',
                density: hotspotData.density + ' trades/hour',
                total_trades: hotspotData.total_trades
            });
        });
        
        // Store for potential Main Dashboard consumption
        window.sessionHotspots = sessions;
    }
    
    renderHotColdHours() {
        if (!this.data || !this.data.session_hotspots || !this.data.session_hotspots.sessions) {
            return;
        }
        
        const hotspots = this.data.session_hotspots.sessions;
        
        Object.keys(hotspots).forEach(sessionName => {
            const sessionData = hotspots[sessionName];
            const hotHours = sessionData.hot_hours || [];
            const coldHours = sessionData.cold_hours || [];
            
            const hotEls = document.querySelectorAll(`[data-hot-hours-for="${sessionName}"]`);
            const coldEls = document.querySelectorAll(`[data-cold-hours-for="${sessionName}"]`);
            
            hotEls.forEach(el => el.textContent = hotHours.length ? hotHours.join(', ') : '--');
            coldEls.forEach(el => el.textContent = coldHours.length ? coldHours.join(', ') : '--');
        });
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    window.timeAnalysis = new TimeAnalysis();
});

console.log('✅ Time Analysis JS Module loaded (H1.3 - Canonical API)');
