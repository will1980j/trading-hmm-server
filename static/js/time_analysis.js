// ============================================================================
// MODULE 17 - TIME ANALYSIS (H1.3 - Canonical API)
// Uses /api/time-analysis as single source of truth
// ============================================================================

// ===== Register Matrix Controller for Chart.js 4 =====
if (window.Chart && window.Chart.controllers && window.Chart.registry) {
    const keys = Object.keys(window).filter(k => k.toLowerCase().includes('matrix'));
    for (const k of keys) {
        const obj = window[k];
        if (!obj) continue;
        
        // Register all matrix exports (controllers, elements, scales)
        Object.values(obj).forEach(item => {
            try {
                Chart.register(item);
            } catch (e) {
                // ignore non-Chart components
            }
        });
    }
}

class TimeAnalysis {
    constructor() {
        this.isLoading = false;
        this.data = null;
        this.sessionHeatmapChart = null;
        
        this.init();
    }
    
    normalizeSession(name) {
        const map = {
            "Asia": "ASIA",
            "ASIA": "ASIA",
            "London": "LONDON",
            "LONDON": "LONDON",
            "NY Pre Market": "NY PRE",
            "NY PRE": "NY PRE",
            "NY AM": "NY AM",
            "NY Lunch": "NY LUNCH",
            "NY LUNCH": "NY LUNCH",
            "NY PM": "NY PM"
        };
        return map[name] || name;
    }
    
    async init() {
        console.log('🚀 Time Analysis - H1.3 Initialized (Canonical API)');
        
        this.setupFilters();
        await this.fetchAllData();
    }
    
    setupFilters() {
        const startInput = document.getElementById('startDateInput');
        const endInput = document.getElementById('endDateInput');
        const sessionFilter = document.getElementById('sessionFilter');
        const directionFilter = document.getElementById('directionFilter');
        
        const handler = () => {
            console.log('TODO: apply V2 filters', {
                start: startInput?.value,
                end: endInput?.value,
                session: sessionFilter?.value,
                direction: directionFilter?.value,
            });
            // Later: call fetchAllData with query params
        };
        
        [startInput, endInput, sessionFilter, directionFilter].forEach(el => {
            if (el) el.addEventListener('change', handler);
        });
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
        
        this.renderHeaderMetrics();
        this.renderSessionAnalysis();
        this.renderSessionHotspots();
        this.renderSessionHeatmap();
        this.renderHourlyAnalysis();
        this.renderHotColdHours();
        
        // CHUNK 7C: Temporal Analytics
        this.renderDayOfWeek();
        this.renderWeekOfMonth();
        this.renderMonthOfYear();
        this.renderMacroWindows();
        this.renderRDistribution();
    }
    
    renderEmpty() {
        const elements = [
            'winRateValue', 'expectancyValue', 'avgRValue', 'totalTradesValue', 'bestSessionValue'
        ];
        elements.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.textContent = '--';
        });
        
        console.log('📊 Time Analysis - No data available');
    }
    
    renderHeaderMetrics() {
        if (!this.data) return;
        
        const stats = this.data;
        
        // Get elements
        const winRateEl = document.getElementById('winRateValue');
        const expectancyEl = document.getElementById('expectancyValue');
        const avgREl = document.getElementById('avgRValue');
        const totalTradesEl = document.getElementById('totalTradesValue');
        const bestSessionEl = document.getElementById('bestSessionValue');
        
        // Parse V2 API response fields
        const winRate = (stats.overall_win_rate || 0) * 100;
        const expectancy = stats.overall_expectancy || 0;
        const avgR = stats.overall_avg_r || 0;
        const totalTrades = stats.total_trades || 0;
        const bestSession = stats.best_session && stats.best_session.session 
            ? stats.best_session.session 
            : 'N/A';
        
        // Update DOM with real data
        if (winRateEl) winRateEl.textContent = `${winRate.toFixed(1)}%`;
        if (expectancyEl) expectancyEl.textContent = `${expectancy.toFixed(2)}R`;
        if (avgREl) avgREl.textContent = `${avgR.toFixed(2)}R`;
        if (totalTradesEl) totalTradesEl.textContent = totalTrades;
        if (bestSessionEl) bestSessionEl.textContent = bestSession;
    }
    
    renderSessionAnalysis() {
        if (!this.data || !this.data.session) return;
        
        const grid = document.getElementById('sessionGrid');
        if (!grid) return;
        grid.innerHTML = '';
        
        const sessionRows = ["ASIA", "LONDON", "NY PRE", "NY AM", "NY LUNCH", "NY PM"];
        const sessions = this.data.session;
        const hotspots = (this.data.session_hotspots && this.data.session_hotspots.sessions) || {};
        
        sessionRows.forEach(name => {
            const rowData = sessions.find(s => s.session === name);
            const hotData = hotspots[name] || {};
            
            const card = this.createSessionCard(name, rowData, hotData);
            grid.appendChild(card);
        });
        
        console.log('📊 Session Analysis rendered:', sessions.length, 'sessions');
    }
    
    createSessionCard(sessionName, data, hotspot) {
        const card = document.createElement('div');
        card.className = 'session-card';
        
        const title = document.createElement('div');
        title.className = 'session-title';
        title.textContent = sessionName;
        card.appendChild(title);
        
        const metrics = document.createElement('div');
        metrics.className = 'session-metric';
        metrics.innerHTML = `<span>Trades</span><span>${data ? data.trades : '--'}</span>`;
        card.appendChild(metrics);
        
        const m2 = document.createElement('div');
        m2.className = 'session-metric';
        const avgR = data ? data.avg_r.toFixed(2) : '--';
        m2.innerHTML = `<span>Avg R</span><span>${avgR}</span>`;
        card.appendChild(m2);
        
        const m3 = document.createElement('div');
        m3.className = 'session-metric';
        const winRate = data ? `${(data.win_rate * 100).toFixed(1)}%` : '--';
        m3.innerHTML = `<span>Win Rate</span><span>${winRate}</span>`;
        card.appendChild(m3);
        
        const hrHot = document.createElement('div');
        hrHot.className = 'session-hotspot-row';
        hrHot.innerHTML = `<div class="hot-label">Hot Hours:</div><div class="hot-values" data-hot-hours-for="${sessionName}">--</div>`;
        card.appendChild(hrHot);
        
        const hrCold = document.createElement('div');
        hrCold.className = 'session-hotspot-row';
        hrCold.innerHTML = `<div class="cold-label">Cold Hour:</div><div class="cold-values" data-cold-hours-for="${sessionName}">--</div>`;
        card.appendChild(hrCold);
        
        return card;
    }
    
    renderSessionHeatmap() {
        if (!this.data || !this.data.session_hotspots || !this.data.session_hotspots.sessions) return;
        const canvas = document.getElementById('sessionHeatmapCanvas');
        if (!canvas) return;
        
        const sessions = this.data.session_hotspots.sessions;
        const sessionRows = ["ASIA", "LONDON", "NY PRE", "NY AM", "NY LUNCH", "NY PM"];
        
        const data = [];
        sessionRows.forEach((name, yIndex) => {
            const s = sessions[name];
            if (!s) return;
            
            const hotHours = (s.hot_hours || []).map(h => parseInt((h || '').split(':')[0], 10));
            const avgR = s.avg_r || 0;
            
            for (let hour = 0; hour < 24; hour++) {
                if (!hotHours.includes(hour)) continue;
                data.push({
                    x: hour,
                    y: yIndex,
                    v: avgR
                });
            }
        });
        
        // Correct Chart.js v4 detection for Matrix controller
        let matrixController = null;
        try {
            matrixController = Chart.registry.getController('matrix');
        } catch (e) {
            console.warn("⚠️ Matrix controller registry lookup failed — skipping heatmap");
            return;
        }
        
        if (!matrixController) {
            console.warn("⚠️ Matrix controller not registered — skipping heatmap");
            return;
        }
        
        if (!this.sessionHeatmapChart) {
            this.sessionHeatmapChart = new Chart(canvas.getContext('2d'), {
                type: 'matrix',
                data: {
                    datasets: [{
                        label: 'Session × Hour R',
                        data,
                        borderWidth: 1,
                        borderColor: '#1e293b',
                        backgroundColor: (ctx) => {
                            const value = ctx.raw.v || 0;
                            return this.getHeatColor(value);
                        },
                        width: ctx => 16,
                        height: ctx => 16,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            type: 'linear',
                            position: 'bottom',
                            ticks: {
                                stepSize: 1,
                                callback: v => `${v}:00`
                            },
                            grid: { color: '#1f2933' }
                        },
                        y: {
                            type: 'linear',
                            ticks: {
                                stepSize: 1,
                                callback: (v) => sessionRows[v] || ''
                            },
                            grid: { color: '#1f2933' }
                        }
                    },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: ctx => {
                                    const rowName = sessionRows[ctx.raw.y] || '';
                                    const h = ctx.raw.x;
                                    const val = ctx.raw.v.toFixed ? ctx.raw.v.toFixed(2) : ctx.raw.v;
                                    return `${rowName} ${h}:00 — ${val}R`;
                                }
                            }
                        },
                        title: {
                            display: false
                        }
                    }
                }
            });
        } else {
            this.sessionHeatmapChart.data.datasets[0].data = data;
            this.sessionHeatmapChart.update();
        }
        
        console.log('🔥 Session Heatmap rendered:', data.length, 'hot hour cells');
    }
    
    getHeatColor(value) {
        if (value <= 0) return 'rgba(15,23,42,0.4)'; // very dark navy for <=0
        if (value < 1) return '#1E293B';            // deep navy
        if (value < 3) return '#4C66FF';            // blue
        if (value < 5) return '#8E54FF';            // violet
        return '#FF00FF';                           // magenta for very hot
    }
    
    renderHourlyAnalysis() {
        if (!this.data || !this.data.hourly) return;
        const grid = document.getElementById('hourlyGrid');
        if (!grid) return;
        grid.innerHTML = '';
        
        this.data.hourly.forEach(h => {
            if (!h || h.trades === 0) return;
            const card = document.createElement('div');
            card.className = 'hour-card';
            
            const label = document.createElement('div');
            label.className = 'hour-label';
            label.textContent = `${h.hour}:00`;
            card.appendChild(label);
            
            const m1 = document.createElement('div');
            m1.textContent = `Avg R: ${h.avg_r.toFixed(2)}`;
            card.appendChild(m1);
            
            const m2 = document.createElement('div');
            m2.textContent = `Win Rate: ${(h.win_rate * 100).toFixed(1)}%`;
            card.appendChild(m2);
            
            const m3 = document.createElement('div');
            m3.textContent = `Trades: ${h.trades}`;
            card.appendChild(m3);
            
            grid.appendChild(card);
        });
        
        console.log('📊 Hourly Analysis rendered');
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
            const norm = this.normalizeSession(sessionName);
            const sessionData = hotspots[sessionName];
            const hotHours = sessionData.hot_hours || [];
            const coldHours = sessionData.cold_hours || [];
            
            // Use normalized name for data attribute lookup
            const hotEls = document.querySelectorAll(`[data-hot-hours-for="${norm}"]`);
            const coldEls = document.querySelectorAll(`[data-cold-hours-for="${norm}"]`);
            
            hotEls.forEach(el => el.textContent = hotHours.length ? hotHours.join(', ') : '--');
            coldEls.forEach(el => el.textContent = coldHours.length ? coldHours.join(', ') : '--');
        });
    }
    
    // ========================================================================
    // CHUNK 7C: TEMPORAL ANALYTICS RENDERERS
    // ========================================================================
    
    renderDayOfWeek() {
        if (!this.data || !this.data.day_of_week) return;
        const grid = document.getElementById('dayOfWeekGrid');
        if (!grid) return;
        grid.innerHTML = '';
        
        this.data.day_of_week.forEach((d, idx) => {
            const card = document.createElement('div');
            card.className = 'dow-card';
            
            const exp = d.expectancy ?? 0;
            const winRate = d.win_rate ?? 0;
            const trades = d.trades ?? 0;
            
            card.innerHTML = `
                <div class="card-title">${d.day}</div>
                <div>Expectancy: ${exp.toFixed(2)}R</div>
                <div>Win Rate: ${(winRate * 100).toFixed(1)}%</div>
                <div>Trades: ${trades}</div>
                <canvas class="mini-chart" id="dowMini${idx}"></canvas>
            `;
            
            grid.appendChild(card);
            
            const canvas = document.getElementById(`dowMini${idx}`);
            if (!canvas) return;
            
            const ctx = canvas.getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [0, 1, 2],
                    datasets: [{
                        data: [0, d.avg_r ?? 0, exp],
                        borderColor: '#4C66FF',
                        borderWidth: 2,
                        pointRadius: 0,
                        tension: 0.3
                    }]
                },
                options: {
                    responsive: false,
                    plugins: { legend: { display: false } },
                    scales: { x: { display: false }, y: { display: false } }
                }
            });
        });
    }
    
    renderWeekOfMonth() {
        if (!this.data || !this.data.week_of_month) return;
        const grid = document.getElementById('weekOfMonthGrid');
        if (!grid) return;
        grid.innerHTML = '';
        
        this.data.week_of_month.forEach((w, idx) => {
            const card = document.createElement('div');
            card.className = 'wom-card';
            
            const exp = w.expectancy ?? 0;
            const winRate = w.win_rate ?? 0;
            const trades = w.trades ?? 0;
            
            card.innerHTML = `
                <div class="card-title">Week ${w.week}</div>
                <div>Expectancy: ${exp.toFixed(2)}R</div>
                <div>Win Rate: ${(winRate * 100).toFixed(1)}%</div>
                <div>Trades: ${trades}</div>
                <canvas class="mini-chart" id="womMini${idx}"></canvas>
            `;
            
            grid.appendChild(card);
            
            const canvas = document.getElementById(`womMini${idx}`);
            if (!canvas) return;
            const ctx = canvas.getContext('2d');
            
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [0, 1, 2],
                    datasets: [{
                        data: [0, w.avg_r ?? 0, exp],
                        borderColor: '#8E54FF',
                        borderWidth: 2,
                        pointRadius: 0,
                        tension: 0.3
                    }]
                },
                options: {
                    responsive: false,
                    plugins: { legend: { display: false } },
                    scales: { x: { display: false }, y: { display: false } }
                }
            });
        });
    }
    
    renderMonthOfYear() {
        if (!this.data || !this.data.monthly) return;
        const grid = document.getElementById('monthOfYearGrid');
        if (!grid) return;
        grid.innerHTML = '';
        
        this.data.monthly.forEach((m, idx) => {
            const card = document.createElement('div');
            card.className = 'moy-card';
            
            const exp = m.expectancy ?? 0;
            const winRate = m.win_rate ?? 0;
            const trades = m.trades ?? 0;
            
            card.innerHTML = `
                <div class="card-title">${m.month}</div>
                <div>Expectancy: ${exp.toFixed(2)}R</div>
                <div>Win Rate: ${(winRate * 100).toFixed(1)}%</div>
                <div>Trades: ${trades}</div>
                <canvas class="mini-chart" id="moyMini${idx}"></canvas>
            `;
            
            grid.appendChild(card);
            
            const canvas = document.getElementById(`moyMini${idx}`);
            if (!canvas) return;
            const ctx = canvas.getContext('2d');
            
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [0, 1, 2],
                    datasets: [{
                        data: [0, m.avg_r ?? 0, exp],
                        borderColor: '#FF00FF',
                        borderWidth: 2,
                        pointRadius: 0,
                        tension: 0.3
                    }]
                },
                options: {
                    responsive: false,
                    plugins: { legend: { display: false } },
                    scales: { x: { display: false }, y: { display: false } }
                }
            });
        });
    }
    
    renderMacroWindows() {
        if (!this.data || !this.data.macro) return;
        const grid = document.getElementById('macroGrid');
        if (!grid) return;
        grid.innerHTML = '';
        
        this.data.macro.forEach(m => {
            const card = document.createElement('div');
            card.className = 'macro-card';
            
            const exp = m.expectancy ?? 0;
            const winRate = m.win_rate ?? 0;
            const trades = m.trades ?? 0;
            
            card.innerHTML = `
                <div class="card-title">${m.window}</div>
                <div>Expectancy: ${exp.toFixed(2)}R</div>
                <div>Win Rate: ${(winRate * 100).toFixed(1)}%</div>
                <div>Trades: ${trades}</div>
            `;
            
            grid.appendChild(card);
        });
    }
    
    renderRDistribution() {
        const canvas = document.getElementById('rDistCanvas');
        if (!canvas || !this.data) return;
        
        let rValues = [];
        if (this.data.hourly && this.data.hourly.length) {
            rValues = this.data.hourly
                .filter(h => h.trades > 0)
                .map(h => h.expectancy ?? 0);
        }
        
        if (!rValues.length) {
            return;
        }
        
        const ctx = canvas.getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: rValues.map((_, i) => `#${i+1}`),
                datasets: [{
                    data: rValues,
                    backgroundColor: '#4C66FF'
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { display: false }, grid: { display: false } },
                    y: { grid: { color: '#1f2933' } }
                }
            }
        });
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    window.timeAnalysis = new TimeAnalysis();
});

console.log('✅ Time Analysis JS Module loaded (H1.3 - Canonical API)');
