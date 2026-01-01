// ============================================================================
// MODULE 17 - TIME ANALYSIS (H1.3 - Canonical API)
// Uses /api/time-analysis as single source of truth
// ============================================================================

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
        
        // Build scatter data: one square per (session, hour)
        const points = [];
        sessionRows.forEach((name, yIndex) => {
            const s = sessions[name];
            if (!s) return;
            
            const hotHours = (s.hot_hours || []).map(h => {
                const parts = (h || '').split(':');
                return parseInt(parts[0], 10);
            });
            
            hotHours.forEach(hour => {
                const val = s.avg_r || 0;
                points.push({
                    x: hour,
                    y: yIndex,
                    r: 8,    // marker radius (square size)
                    v: val,  // used for color mapping
                    session: name
                });
            });
        });
        
        // If no points, skip rendering gracefully
        if (!points.length) {
            console.warn("⚠️ No hotspot data for heatmap — nothing to render.");
            return;
        }
        
        const ctx = canvas.getContext('2d');
        
        if (this.sessionHeatmapChart) {
            this.sessionHeatmapChart.destroy();
        }
        
        this.sessionHeatmapChart = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Session × Hour R',
                    data: points,
                    pointRadius: ctx => ctx.raw.r,
                    pointHoverRadius: 10,
                    pointBackgroundColor: ctx => this.getHeatColor(ctx.raw.v),
                    pointStyle: 'rectRounded',
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        min: 0,
                        max: 23,
                        ticks: {
                            stepSize: 1,
                            callback: v => `${v}:00`
                        },
                        grid: { color: '#1f2933' }
                    },
                    y: {
                        type: 'linear',
                        min: -0.5,
                        max: sessionRows.length - 0.5,
                        ticks: {
                            stepSize: 1,
                            callback: v => sessionRows[v] || ''
                        },
                        grid: { color: '#1f2933' }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: ctx => {
                                const rowName = ctx.raw.session;
                                const h = ctx.raw.x;
                                const val = ctx.raw.v?.toFixed ? ctx.raw.v.toFixed(2) : ctx.raw.v;
                                return `${rowName} ${h}:00 — ${val}R`;
                            }
                        }
                    }
                }
            }
        });
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

// ============================================================================
// TEMPORAL EDGE V1 - TRUSTED SIGNALS ONLY
// Uses /api/signals/v1/all with strict filtering
// ============================================================================

async function loadTemporalEdgeV1() {
    try {
        console.log('[TE-V1] Loading Temporal Edge V1...');
        
        // Fetch canonical signals
        const resp = await fetch('/api/signals/v1/all?symbol=GLBX.MDP3:NQ&limit=2000', { cache: 'no-store' });
        const data = await resp.json();
        const allSignals = data.rows || [];
        
        // CRITICAL FILTERING: Valid + Metrics Present
        const validSignals = allSignals.filter(s => s.valid_market_window === true);
        const computableSignals = validSignals.filter(s => 
            s.metrics_source === 'event' || s.metrics_source === 'computed'
        );
        
        console.log(`[TE-V1] Total: ${allSignals.length}, Valid: ${validSignals.length}, Computable: ${computableSignals.length}`);
        
        // ========================================
        // BLOCK A: Session Transition Sensitivity
        // ========================================
        renderSessionTransitions(computableSignals);
        
        // ========================================
        // BLOCK B: Time-to-1R / Time-in-Trade
        // ========================================
        renderTimeTo1R(computableSignals);
        
        // ========================================
        // BLOCK C: Signal Age Decay
        // ========================================
        renderSignalAgeDecay(computableSignals);
        
        console.log('[TE-V1] Temporal Edge V1 loaded successfully');
        
    } catch (error) {
        console.error('[TE-V1] Error loading Temporal Edge V1:', error);
    }
}

function renderSessionTransitions(signals) {
    // Session classification based on signal_bar_open_ts
    const classifySession = (signal) => {
        if (!signal.signal_bar_open_ts) return 'UNKNOWN';
        
        const dt = new Date(signal.signal_bar_open_ts);
        const hour = dt.getUTCHours();
        const minute = dt.getUTCMinutes();
        const dayOfWeek = dt.getUTCDay(); // 0=Sunday, 5=Friday
        
        // NY Open is 14:30 UTC (9:30 AM ET)
        const totalMinutes = hour * 60 + minute;
        const nyOpenMinutes = 14 * 60 + 30; // 14:30 UTC
        
        // NY Open -30 to 0 minutes (14:00-14:30 UTC)
        if (totalMinutes >= nyOpenMinutes - 30 && totalMinutes < nyOpenMinutes) {
            return 'NY Open -30 to 0';
        }
        
        // NY Open 0 to +30 minutes (14:30-15:00 UTC)
        if (totalMinutes >= nyOpenMinutes && totalMinutes < nyOpenMinutes + 30) {
            return 'NY Open 0 to +30';
        }
        
        // NY AM after +30 minutes (15:00-17:00 UTC)
        if (totalMinutes >= nyOpenMinutes + 30 && totalMinutes < 17 * 60) {
            return 'NY AM after +30';
        }
        
        // London→NY overlap (12:00-14:30 UTC)
        if (totalMinutes >= 12 * 60 && totalMinutes < nyOpenMinutes) {
            return 'London→NY overlap';
        }
        
        // Friday PM (17:00-20:00 UTC on Friday)
        if (dayOfWeek === 5 && totalMinutes >= 17 * 60 && totalMinutes < 20 * 60) {
            return 'Friday PM';
        }
        
        return 'Other';
    };
    
    // Bucket signals
    const buckets = {};
    signals.forEach(s => {
        const session = classifySession(s);
        if (!buckets[session]) {
            buckets[session] = [];
        }
        buckets[session].push(s);
    });
    
    // Calculate metrics per bucket
    const calcMetrics = (signals) => {
        const noBeMfes = signals.map(s => parseFloat(s.no_be_mfe)).filter(v => !isNaN(v));
        const beMfes = signals.map(s => parseFloat(s.be_mfe)).filter(v => !isNaN(v));
        
        const avgNoBeMfe = noBeMfes.length > 0 ? (noBeMfes.reduce((a,b) => a+b, 0) / noBeMfes.length).toFixed(2) + 'R' : '--';
        const avgBeMfe = beMfes.length > 0 ? (beMfes.reduce((a,b) => a+b, 0) / beMfes.length).toFixed(2) + 'R' : '--';
        const winCount = noBeMfes.filter(v => v >= 1.0).length;
        const winPct = noBeMfes.length > 0 ? ((winCount / noBeMfes.length) * 100).toFixed(1) + '%' : '--%';
        
        return { count: signals.length, avgNoBeMfe, avgBeMfe, winPct };
    };
    
    // Render table
    const bucketOrder = ['NY Open -30 to 0', 'NY Open 0 to +30', 'NY AM after +30', 'London→NY overlap', 'Friday PM', 'Other'];
    let html = `
        <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
            <thead>
                <tr style="border-bottom: 1px solid rgba(148,163,184,0.2);">
                    <th style="text-align: left; padding: 8px; color: #94a3b8;">Session Bucket</th>
                    <th style="text-align: right; padding: 8px; color: #94a3b8;">Count</th>
                    <th style="text-align: right; padding: 8px; color: #94a3b8;">Avg NoBE MFE</th>
                    <th style="text-align: right; padding: 8px; color: #94a3b8;">Avg BE MFE</th>
                    <th style="text-align: right; padding: 8px; color: #94a3b8;">Win Proxy (≥1R)</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    bucketOrder.forEach(bucket => {
        if (buckets[bucket] && buckets[bucket].length > 0) {
            const metrics = calcMetrics(buckets[bucket]);
            html += `
                <tr style="border-bottom: 1px solid rgba(148,163,184,0.1);">
                    <td style="padding: 8px; color: #e2e8f0;">${bucket}</td>
                    <td style="padding: 8px; text-align: right; color: #e2e8f0;">${metrics.count}</td>
                    <td style="padding: 8px; text-align: right; color: #e2e8f0;">${metrics.avgNoBeMfe}</td>
                    <td style="padding: 8px; text-align: right; color: #e2e8f0;">${metrics.avgBeMfe}</td>
                    <td style="padding: 8px; text-align: right; color: #e2e8f0;">${metrics.winPct}</td>
                </tr>
            `;
        }
    });
    
    html += '</tbody></table>';
    document.getElementById('te-session-transitions-table').innerHTML = html;
}

function renderTimeTo1R(signals) {
    // Best-effort time-to-1R calculation
    const timeTo1RData = [];
    const timeInTradeData = [];
    
    signals.forEach(s => {
        // Time to 1R (if BE triggered)
        if (s.entry_bar_open_ts && s.be_trigger_bar_open_ts) {
            const entryTime = new Date(s.entry_bar_open_ts).getTime();
            const beTime = new Date(s.be_trigger_bar_open_ts).getTime();
            const minutes = Math.round((beTime - entryTime) / (1000 * 60));
            if (minutes >= 0) {
                timeTo1RData.push(minutes);
            }
        }
        
        // Time in trade (if exited)
        if (s.entry_bar_open_ts && s.exit_bar_open_ts) {
            const entryTime = new Date(s.entry_bar_open_ts).getTime();
            const exitTime = new Date(s.exit_bar_open_ts).getTime();
            const minutes = Math.round((exitTime - entryTime) / (1000 * 60));
            if (minutes >= 0) {
                timeInTradeData.push(minutes);
            }
        }
    });
    
    const bucketize = (minutes) => {
        if (minutes <= 5) return '≤5';
        if (minutes <= 15) return '5-15';
        if (minutes <= 30) return '15-30';
        return '30+';
    };
    
    const createDistribution = (data, label) => {
        if (data.length === 0) {
            return `<div style="color: #94a3b8; font-size: 12px; margin-bottom: 16px;">
                <strong>${label}:</strong> N/A (requires ${label === 'Time-to-1R' ? 'be_trigger_bar_open_ts' : 'exit_bar_open_ts'})
            </div>`;
        }
        
        const buckets = {'≤5': 0, '5-15': 0, '15-30': 0, '30+': 0};
        data.forEach(m => {
            const bucket = bucketize(m);
            buckets[bucket]++;
        });
        
        let html = `<div style="margin-bottom: 20px;">
            <div style="color: #e2e8f0; font-size: 14px; margin-bottom: 8px;"><strong>${label}</strong> (${data.length} signals)</div>
            <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
                <thead>
                    <tr style="border-bottom: 1px solid rgba(148,163,184,0.2);">
                        <th style="text-align: left; padding: 6px; color: #94a3b8;">Minutes</th>
                        <th style="text-align: right; padding: 6px; color: #94a3b8;">Count</th>
                        <th style="text-align: right; padding: 6px; color: #94a3b8;">%</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        for (const [bucket, count] of Object.entries(buckets)) {
            const pct = ((count / data.length) * 100).toFixed(1);
            html += `
                <tr style="border-bottom: 1px solid rgba(148,163,184,0.1);">
                    <td style="padding: 6px; color: #e2e8f0;">${bucket} min</td>
                    <td style="padding: 6px; text-align: right; color: #e2e8f0;">${count}</td>
                    <td style="padding: 6px; text-align: right; color: #e2e8f0;">${pct}%</td>
                </tr>
            `;
        }
        
        html += '</tbody></table></div>';
        return html;
    };
    
    const html = createDistribution(timeTo1RData, 'Time-to-1R') + createDistribution(timeInTradeData, 'Time-in-Trade');
    document.getElementById('te-time-to-1r-content').innerHTML = html;
}

function renderSignalAgeDecay(signals) {
    // Calculate minutes between signal and entry
    const ageData = [];
    
    signals.forEach(s => {
        if (s.signal_bar_open_ts && s.entry_bar_open_ts) {
            const signalTime = new Date(s.signal_bar_open_ts).getTime();
            const entryTime = new Date(s.entry_bar_open_ts).getTime();
            const minutes = Math.round((entryTime - signalTime) / (1000 * 60));
            if (minutes >= 0) {
                ageData.push({ minutes, signal: s });
            }
        }
    });
    
    const bucketize = (minutes) => {
        if (minutes <= 5) return '0-5';
        if (minutes <= 15) return '5-15';
        if (minutes <= 30) return '15-30';
        return '30+';
    };
    
    // Bucket signals by age
    const buckets = {'0-5': [], '5-15': [], '15-30': [], '30+': []};
    ageData.forEach(item => {
        const bucket = bucketize(item.minutes);
        buckets[bucket].push(item.signal);
    });
    
    // Calculate metrics per bucket
    const calcMetrics = (signals) => {
        const noBeMfes = signals.map(s => parseFloat(s.no_be_mfe)).filter(v => !isNaN(v));
        const avgNoBeMfe = noBeMfes.length > 0 ? (noBeMfes.reduce((a,b) => a+b, 0) / noBeMfes.length).toFixed(2) + 'R' : '--';
        const winCount = noBeMfes.filter(v => v >= 1.0).length;
        const winPct = noBeMfes.length > 0 ? ((winCount / noBeMfes.length) * 100).toFixed(1) + '%' : '--%';
        return { count: signals.length, avgNoBeMfe, winPct };
    };
    
    // Render table
    let html = `
        <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
            <thead>
                <tr style="border-bottom: 1px solid rgba(148,163,184,0.2);">
                    <th style="text-align: left; padding: 8px; color: #94a3b8;">Signal Age (minutes)</th>
                    <th style="text-align: right; padding: 8px; color: #94a3b8;">Count</th>
                    <th style="text-align: right; padding: 8px; color: #94a3b8;">Avg NoBE MFE</th>
                    <th style="text-align: right; padding: 8px; color: #94a3b8;">Win Proxy (≥1R)</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    const bucketOrder = ['0-5', '5-15', '15-30', '30+'];
    bucketOrder.forEach(bucket => {
        if (buckets[bucket].length > 0) {
            const metrics = calcMetrics(buckets[bucket]);
            html += `
                <tr style="border-bottom: 1px solid rgba(148,163,184,0.1);">
                    <td style="padding: 8px; color: #e2e8f0;">${bucket} min</td>
                    <td style="padding: 8px; text-align: right; color: #e2e8f0;">${metrics.count}</td>
                    <td style="padding: 8px; text-align: right; color: #e2e8f0;">${metrics.avgNoBeMfe}</td>
                    <td style="padding: 8px; text-align: right; color: #e2e8f0;">${metrics.winPct}</td>
                </tr>
            `;
        }
    });
    
    html += '</tbody></table>';
    
    if (ageData.length === 0) {
        html = '<div style="color: #94a3b8; font-size: 12px;">N/A (requires signal_bar_open_ts and entry_bar_open_ts)</div>';
    }
    
    document.getElementById('te-signal-age-table').innerHTML = html;
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    window.timeAnalysis = new TimeAnalysis();
    
    // Load Temporal Edge V1
    loadTemporalEdgeV1();
});

console.log('✅ Time Analysis JS Module loaded (H1.3 - Canonical API)');
