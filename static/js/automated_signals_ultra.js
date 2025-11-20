/* Ultra Premium Automated Signals Hub Controller
SEGMENT 1 of 6
*/

const AS = {
    state: {
        trades: [],
        filteredTrades: [],
        calendar: [],
        selectedDate: null,
        filters: {
            session: 'ALL',
            direction: 'ALL',
            status: 'ALL',
            setupFamily: 'ALL',
            trend: 'ALL',
            minStrength: 0
        },
        tradeDetail: null,
        chart: null
    }
};

// Fetch hub data from backend
async function asFetchHubData() {
    const params = new URLSearchParams();
    const f = AS.state.filters;
    if (f.session !== 'ALL') params.set('session', f.session);
    if (f.direction !== 'ALL') params.set('direction', f.direction);
    if (f.status !== 'ALL') params.set('status', f.status);
    const url = '/api/automated-signals/hub-data?' + params.toString();
    try {
        const res = await fetch(url);
        if (!res.ok) {
            console.error('Failed to fetch hub data', res.status);
            return;
        }
        const json = await res.json();
        let calendar = [];
        let trades = [];
        // Support both {calendar, trades} and {data:{calendar, trades}}
        if (Array.isArray(json.trades)) {
            calendar = json.calendar || [];
            trades = json.trades;
        } else if (json.data && Array.isArray(json.data.trades)) {
            calendar = json.data.calendar || [];
            trades = json.data.trades;
        }
        AS.state.trades = trades;
        AS.state.calendar = calendar;
        asBuildFilterOptions();
        asApplyFilters();
        asRenderCalendar();
        asUpdateSummary();
        const lastRefreshEl = document.getElementById('as-last-refresh');
        const countBadge = document.getElementById('as-total-count-badge');
        if (lastRefreshEl) lastRefreshEl.textContent = new Date().toLocaleTimeString();
        if (countBadge) countBadge.textContent = `${AS.state.trades.length} trades`;
    } catch (err) {
        console.error('Error fetching hub data:', err);
    }
}

// Build setup family filter options based on loaded trades
function asBuildFilterOptions() {
    const famSelect = document.getElementById('as-filter-setup-family');
    if (!famSelect) return;
    const families = new Set();
    AS.state.trades.forEach(t => {
        if (t.setup && t.setup.setup_family) {
            families.add(t.setup.setup_family);
        }
    });
    const current = AS.state.filters.setupFamily;
    famSelect.innerHTML = '<option value="ALL">All</option>';
    [...families].sort().forEach(f => {
        const opt = document.createElement('option');
        opt.value = f;
        opt.textContent = f;
        famSelect.appendChild(opt);
    });
    if (current !== 'ALL') {
        famSelect.value = current;
    }
}


/* SEGMENT 2 of 6
Filters + Calendar Rendering + Utility Formatting
*/

// Apply filters to trades and update UI
function asApplyFilters() {
    const f = AS.state.filters;
    const date = AS.state.selectedDate;
    const filtered = AS.state.trades.filter(t => {
        // Session filter
        if (f.session !== 'ALL' && t.session !== f.session) return false;
        // Direction filter
        if (f.direction !== 'ALL' && t.direction !== f.direction) return false;
        // Status filter
        if (f.status !== 'ALL' && t.status !== f.status) return false;
        // Setup family filter
        if (f.setupFamily !== 'ALL') {
            if (!t.setup || t.setup.setup_family !== f.setupFamily) return false;
        }
        // Trend regime filter
        if (f.trend !== 'ALL') {
            const tr = t.market_state?.trend_regime;
            if (!tr || tr !== f.trend) return false;
        }
        // Signal strength filter
        if (f.minStrength > 0) {
            const s = t.setup?.signal_strength;
            if (typeof s === 'number' && s < f.minStrength) return false;
        }
        // Date (calendar day) filter
        if (date && t.date !== date) return false;
        return true;
    });
    AS.state.filteredTrades = filtered;
    // FIX 3: Sort newest trades first
    AS.state.filteredTrades.sort((a, b) => {
        const timeA = new Date(a.last_event_time || 0);
        const timeB = new Date(b.last_event_time || 0);
        return timeB - timeA;
    });
    asRenderTradesTable();
    asUpdateSummary();
}

// Render the calendar grid
function asRenderCalendar() {
    const wrap = document.getElementById('as-calendar-grid');
    if (!wrap) return;
    const calendar = AS.state.calendar || [];
    wrap.innerHTML = '';
    if (!calendar.length) {
        wrap.innerHTML = '<p class="text-muted small">No calendar data.</p>';
        document.getElementById('as-calendar-month-label').textContent = '';
        return;
    }
    const firstDate = calendar[0].date;
    const monthLabel = new Date(firstDate).toLocaleString('en-US', { month: 'short', year: 'numeric' });
    document.getElementById('as-calendar-month-label').textContent = monthLabel;
    calendar.forEach(day => {
        const el = document.createElement('div');
        el.className = 'as-calendar-day';
        if (AS.state.selectedDate === day.date) {
            el.classList.add('active');
        }
        // Day number
        const dt = document.createElement('div');
        dt.className = 'as-calendar-day-date';
        dt.textContent = new Date(day.date).getDate();
        // Meta: trade count + avg R
        const meta = document.createElement('div');
        meta.className = 'as-calendar-day-meta';
        const avg = day.avg_no_be_mfe_R != null ? day.avg_no_be_mfe_R.toFixed(2) : '–';
        meta.textContent = `${day.trade_count} trades • avg ${avg}R`;
        el.appendChild(dt);
        el.appendChild(meta);
        // Click handler (toggle selected date)
        el.onclick = () => {
            AS.state.selectedDate = (AS.state.selectedDate === day.date ? null : day.date);
            asApplyFilters();
            asRenderCalendar();
        };
        wrap.appendChild(el);
    });
}

// Format an R-value with colored classes
function fmtR(v) {
    if (v == null) return '<span class="as-event-mfe-neutral">–</span>';
    if (v > 0) return `<span class="as-event-mfe-positive">+${v.toFixed(2)}</span>`;
    if (v < 0) return `<span class="as-event-mfe-negative">${v.toFixed(2)}</span>`;
    return '<span class="as-event-mfe-neutral">0.00</span>';
}


/* SEGMENT 3 of 6
Trades Table Rendering + Summary Calculation
*/

// Render the main trades table
function asRenderTradesTable() {
    const tbody = document.getElementById('as-trades-tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    const trades = AS.state.filteredTrades;
    if (!trades.length) {
        tbody.innerHTML = `<tr><td colspan="11" class="text-center text-muted py-3">No trades match the current filters.</td></tr>`;
        return;
    }
    trades.forEach(t => {
        const tr = document.createElement('tr');
        tr.dataset.tradeId = t.trade_id;
        
        // FIX 2: Correct combined MFE logic
        const mfeCombined = Math.max(
            Number(t.be_mfe_R ?? -Infinity),
            Number(t.no_be_mfe_R ?? -Infinity)
        );
        
        // Time formatting
        const ts = t.timestamp ? new Date(t.timestamp) : null;
        const timeStr = ts
            ? ts.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            : '';
        // Direction pill
        const dirPill =
            t.direction === 'Bullish'
                ? '<span class="pill pill-long">LONG</span>'
                : '<span class="pill pill-short">SHORT</span>';
        // Status pill
        const statusClass =
            t.status === 'ACTIVE' ? 'pill-active' :
            t.status === 'BE_PROTECTED' ? 'pill-be-protected' :
            t.status === 'COMPLETED' ? 'pill-completed' :
            'pill-cancelled';
        const statusPill = `<span class="pill ${statusClass}">${t.status}</span>`;
        // Session pill
        const sessionPill = `<span class="pill pill-session">${t.session}</span>`;
        
        // FIX 1: Entry & exit normalisation
        const entry = t.entry_price ?? t.entry ?? null;
        const exit = t.exit_price ?? t.exit ?? null;
        
        // FIX 2: Strength bar not rendering
        const strength = t.setup?.signal_strength ?? t.signal_strength ?? null;
        const strengthFill = strength != null
            ? `<div class="as-strength-bar-fill" style="width:${Math.min(100, Math.max(0, strength))}%;"></div>`
            : '';
        // Build row
        tr.innerHTML = `
            <td>${timeStr}</td>
            <td>${dirPill}</td>
            <td>${sessionPill}</td>
            <td>${statusPill}</td>
            <td>${t.setup?.id || t.setup?.setup_id || '--'}</td>
            <td><div class="as-strength-bar">${strengthFill}</div></td>
            <td>${fmtR(mfeCombined)}</td>
            <td>${fmtR(t.no_be_mfe_R)}</td>
            <td>${fmtR(t.final_mfe)}</td>
            <td>${entry != null ? entry.toFixed(2) : '--'}</td>
            <td>${exit != null ? exit.toFixed(2) : '--'}</td>
        `;
        // Click handler for details modal
        tr.onclick = () => asOpenTradeDetail(t.trade_id);
        tbody.appendChild(tr);
    });
}

// Update summary cards
function asUpdateSummary() {
    const trades = AS.state.filteredTrades;
    const count = trades.length;
    // Completed trades for final R stats
    const completed = trades.filter(t => t.status === 'COMPLETED');
    const finals = completed.map(t => (t.final_mfe != null ? Number(t.final_mfe) : null)).filter(v => v != null);
    const avgR =
        finals.length > 0
            ? finals.reduce((a, b) => a + b, 0) / finals.length
            : null;
    const winCount = finals.filter(v => v > 0).length;
    const winRate =
        finals.length > 0 ? (winCount / finals.length) * 100 : null;
    // Signal strength average
    const strengths = trades.map(t => t.setup?.signal_strength).filter(v => v != null);
    const avgStrength =
        strengths.length > 0
            ? strengths.reduce((a, b) => a + b, 0) / strengths.length
            : null;
    // Update UI
    const t1 = document.getElementById('as-summary-trades');
    const t2 = document.getElementById('as-summary-avg-r');
    const t3 = document.getElementById('as-summary-winrate');
    const t4 = document.getElementById('as-summary-strength');
    if (t1) t1.textContent = count;
    if (t2) t2.textContent = avgR != null ? avgR.toFixed(2) : '–';
    if (t3) t3.textContent = winRate != null ? winRate.toFixed(0) + '%' : '–';
    if (t4) t4.textContent = avgStrength != null ? avgStrength.toFixed(0) : '–';
}


/* SEGMENT 4 of 6
Trade Detail: Fetch + Modal Header + Meta + Setup + Market State
*/

// Fetch full trade detail (timeline, telemetry, setup, market state)
async function asOpenTradeDetail(tradeId) {
    try {
        const res = await fetch(`/api/automated-signals/trade/${encodeURIComponent(tradeId)}`);
        if (!res.ok) {
            console.error('Failed to fetch trade detail:', res.status);
            return;
        }
        // Some backends return { success:true, data:{... } }
        // Others return { ... }
        const json = await res.json();
        const detail = json.data || json;
        AS.state.tradeDetail = detail;
        asRenderTradeDetail(detail);
    } catch (err) {
        console.error('Error fetching trade detail:', err);
    }
}

// Render the trade detail modal (header, meta, setup, market state)
function asRenderTradeDetail(detail) {
    // Elements
    const titleEl = document.getElementById('as-trade-modal-title');
    const subEl = document.getElementById('as-trade-modal-subtitle');
    const metaEl = document.getElementById('as-trade-meta');
    const setupEl = document.getElementById('as-trade-setup');
    const marketEl = document.getElementById('as-trade-market');
    if (!titleEl || !metaEl || !setupEl || !marketEl) {
        console.error('Trade detail modal elements missing in DOM.');
        return;
    }
    // ---- Header ----
    titleEl.textContent = `${detail.direction || ''} ${detail.trade_id || ''}`;
    subEl.textContent = `${detail.session || ''} • Status: ${detail.status || ''}`;
    // ---- Meta Block ----
    const finalR =
        detail.final_mfe_R != null
            ? detail.final_mfe_R
            : detail.final_mfe != null
            ? detail.final_mfe
            : null;
    metaEl.innerHTML = `
        <div class="mb-1"><span class="as-badge-soft">Entry</span> ${detail.entry_price != null ? detail.entry_price.toFixed(2) : '–'}</div>
        <div class="mb-1"><span class="as-badge-soft">Stop</span> ${detail.stop_loss != null ? detail.stop_loss.toFixed(2) : '–'}</div>
        <div class="mb-1"><span class="as-badge-soft">Exit</span> ${detail.exit_price != null ? detail.exit_price.toFixed(2) : '–'} (${detail.exit_reason || ''})</div>
        <div class="mb-1"><span class="as-badge-soft">Final R</span> ${finalR != null ? finalR.toFixed(2) : '–'}</div>
    `;
    // ---- Setup Block ----
    if (detail.setup) {
        const s = detail.setup;
        const t = detail.targets || {};
        setupEl.innerHTML = `
            <div class="mb-1"><strong>Family:</strong> ${s.setup_family || s.family || '–'}</div>
            <div class="mb-1"><strong>Variant:</strong> ${s.setup_variant || s.variant || '–'}</div>
            <div class="mb-1"><strong>Signal Strength:</strong> ${s.signal_strength != null ? s.signal_strength.toFixed(0) : '–'}</div>
            <hr>
            <div class="mb-1"><strong>TP1:</strong> ${t.tp1_price != null ? t.tp1_price.toFixed(2) : '–'} ${t.target_Rs?.[0] != null ? `(${t.target_Rs[0].toFixed(2)}R)` : ''}</div>
            <div class="mb-1"><strong>TP2:</strong> ${t.tp2_price != null ? t.tp2_price.toFixed(2) : '–'} ${t.target_Rs?.[1] != null ? `(${t.target_Rs[1].toFixed(2)}R)` : ''}</div>
            <div class="mb-1"><strong>TP3:</strong> ${t.tp3_price != null ? t.tp3_price.toFixed(2) : '–'} ${t.target_Rs?.[2] != null ? `(${t.target_Rs[2].toFixed(2)}R)` : ''}</div>
        `;
    } else {
        setupEl.innerHTML = '<span class="text-muted small">No setup/target data.</span>';
    }
    // ---- Market State Block ----
    if (detail.market_state_entry) {
        const ms = detail.market_state_entry;
        marketEl.innerHTML = `
            <div class="mb-1"><strong>Trend:</strong> ${ms.trend_regime || '–'} ${ms.trend_score != null ? '(' + (ms.trend_score * 100).toFixed(0) + '%)' : ''}</div>
            <div class="mb-1"><strong>Volatility:</strong> ${ms.volatility_regime || '–'}</div>
            <div class="mb-1"><strong>Swing:</strong> ${ms.structure?.swing_state || '–'}</div>
            <div class="mb-1"><strong>Structure:</strong> ${ms.structure?.bos_choch_signal || '–'}</div>
            <div class="mb-1"><strong>Liquidity:</strong> ${ms.structure?.liquidity_context || '–'}</div>
        `;
    } else {
        marketEl.innerHTML = '<span class="text-muted small">No market state data.</span>';
    }
    // NOTE: Timeline + Chart will be appended in Segment 5
    // Here we only open the modal
    new bootstrap.Modal(document.getElementById('as-trade-modal')).show();
}


/* SEGMENT 5 of 6
Event Timeline + MFE Journey Chart (Chart.js)
*/

// Render timeline & chart inside the trade detail modal
function asRenderTradeTimelineAndChart(detail) {
    const eventsEl = document.getElementById('as-trade-events');
    const canvas = document.getElementById('as-trade-chart');
    if (!eventsEl || !canvas) {
        console.error('Timeline/chart elements missing.');
        return;
    }
    eventsEl.innerHTML = '';
    const events = detail.events || [];
    const labels = [];
    const mfeData = [];
    events.forEach((ev, index) => {
        // FIX 4: Robust timestamp parsing
        const ts = ev.timestamp
            ? (Date.parse(ev.timestamp.replace(" ", "T")) || null)
            : null;
        const timeStr = ts
            ? new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
            : `Event ${index + 1}`;
        // Correct: Use telemetry MFE first, fall back to direct
        const effMfe =
            ev.telemetry?.mfe_R != null
                ? Number(ev.telemetry.mfe_R)
                : ev.mfe_R != null
                ? Number(ev.mfe_R)
                : null;
        const mfeClass =
            effMfe > 0 ? 'as-event-mfe-positive' :
            effMfe < 0 ? 'as-event-mfe-negative' :
            'as-event-mfe-neutral';
        // Build timeline row
        const row = document.createElement('div');
        row.className = 'as-event-item';
        row.innerHTML = `
            <div><span class="as-event-type">${ev.event_type}</span>
            <span class="text-muted">${timeStr}</span></div>
            <div class="${mfeClass}">MFE: ${effMfe != null ? effMfe.toFixed(2) + 'R' : '–'}</div>
        `;
        eventsEl.appendChild(row);
        // FIX 4: Add to chart data (filter out null/NaN)
        if (Number.isFinite(effMfe)) {
            labels.push(timeStr);
            mfeData.push(effMfe);
        }
    });
    // Render chart
    const ctx = canvas.getContext('2d');
    // Destroy old chart if exists
    if (AS.state.chart) {
        AS.state.chart.destroy();
    }
    AS.state.chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'MFE (R)',
                data: mfeData,
                borderColor: '#38bdf8',
                backgroundColor: 'rgba(56,189,248,0.20)',
                borderWidth: 2,
                tension: 0.25,
                pointRadius: 3,
                pointHoverRadius: 5
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    ticks: { maxRotation: 0, autoSkip: true, maxTicksLimit: 10 },
                    title: { display: true, text: 'Time' }
                },
                y: {
                    title: { display: true, text: 'R' },
                    zeroLineColor: '#475569'
                }
            }
        }
    });
}

// Patch trade detail render function to include timeline+chart
// (we call this at the end of asRenderTradeDetail)
const _asRenderTradeDetail_original = asRenderTradeDetail;
asRenderTradeDetail = function(detail) {
    _asRenderTradeDetail_original(detail);
    // Render timeline + chart after base rendering
    asRenderTradeTimelineAndChart(detail);
};


/* SEGMENT 6 of 6
Event Handlers + Initialization
*/

// Event handlers for filters and controls
function asSetupEventHandlers() {
    // Session filter
    const sessionSelect = document.getElementById('as-filter-session');
    if (sessionSelect) {
        sessionSelect.onchange = () => {
            AS.state.filters.session = sessionSelect.value;
            asApplyFilters();
        };
    }
    // Direction filter
    const directionSelect = document.getElementById('as-filter-direction');
    if (directionSelect) {
        directionSelect.onchange = () => {
            AS.state.filters.direction = directionSelect.value;
            asApplyFilters();
        };
    }
    // Status filter
    const statusSelect = document.getElementById('as-filter-status');
    if (statusSelect) {
        statusSelect.onchange = () => {
            AS.state.filters.status = statusSelect.value;
            asApplyFilters();
        };
    }
    // Setup family filter
    const setupFamilySelect = document.getElementById('as-filter-setup-family');
    if (setupFamilySelect) {
        setupFamilySelect.onchange = () => {
            AS.state.filters.setupFamily = setupFamilySelect.value;
            asApplyFilters();
        };
    }
    // Trend regime filter
    const trendSelect = document.getElementById('as-filter-trend');
    if (trendSelect) {
        trendSelect.onchange = () => {
            AS.state.filters.trend = trendSelect.value;
            asApplyFilters();
        };
    }
    // Signal strength slider
    const strengthSlider = document.getElementById('as-filter-strength');
    const strengthValue = document.getElementById('as-filter-strength-value');
    if (strengthSlider && strengthValue) {
        strengthSlider.oninput = () => {
            const val = parseInt(strengthSlider.value);
            AS.state.filters.minStrength = val;
            strengthValue.textContent = val;
            asApplyFilters();
        };
    }
    // Clear day button
    const clearDayBtn = document.getElementById('as-clear-day');
    if (clearDayBtn) {
        clearDayBtn.onclick = () => {
            AS.state.selectedDate = null;
            asApplyFilters();
            asRenderCalendar();
        };
    }
    // Refresh button
    const refreshBtn = document.getElementById('as-refresh-btn');
    if (refreshBtn) {
        refreshBtn.onclick = () => {
            asFetchHubData();
        };
    }
}

// Initialize the dashboard when DOM is ready
function asInit() {
    console.log('🚀 Ultra Automated Signals Dashboard initializing...');
    asSetupEventHandlers();
    asFetchHubData();
    // Auto-refresh every 30 seconds
    setInterval(() => {
        asFetchHubData();
    }, 30000);
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', asInit);
} else {
    asInit();
}

// FIX 4: Auto-refresh every 60 seconds
setInterval(() => {
    console.log("🔄 Auto-refreshing Ultra Dashboard...");
    asFetchHubData();
}, 60000);
