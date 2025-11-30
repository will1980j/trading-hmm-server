/**
 * AUTOMATED SIGNALS ULTRA - H1.4A FOUNDATIONAL DATA PIPELINE
 * Production-safe implementation with real endpoints only
 */

// Script loaded successfully
console.log("[ASE] ========== SCRIPT LOADED ==========");

// Define globally on window to ensure accessibility
window.AutomatedSignalsUltra = {
    data: null,
    timer: null,
    lastDetail: null
};

// Local reference for convenience
const AutomatedSignalsUltra = window.AutomatedSignalsUltra;

AutomatedSignalsUltra.currentMonth = new Date();
AutomatedSignalsUltra.calendarData = [];
AutomatedSignalsUltra.selectedDate = null;
AutomatedSignalsUltra.filters = {
    session: 'ALL',
    direction: 'ALL',
    state: 'ALL',
    searchId: ''
};

AutomatedSignalsUltra.init = function() {
    console.log("[ASE] Initializing Automated Signals Engine dashboard...");
    
    // First load
    AutomatedSignalsUltra.fetchDashboardData();
    AutomatedSignalsUltra.fetchCalendarData();
    
    // Wire calendar navigation
    const prevBtn = document.getElementById('ase-calendar-prev');
    const nextBtn = document.getElementById('ase-calendar-next');
    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            AutomatedSignalsUltra.currentMonth.setMonth(AutomatedSignalsUltra.currentMonth.getMonth() - 1);
            AutomatedSignalsUltra.renderCalendar();
        });
    }
    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            AutomatedSignalsUltra.currentMonth.setMonth(AutomatedSignalsUltra.currentMonth.getMonth() + 1);
            AutomatedSignalsUltra.renderCalendar();
        });
    }
    
    // Wire filter buttons
    AutomatedSignalsUltra.wireFilters();
    
    // Poll every 7 seconds
    if (AutomatedSignalsUltra.timer) {
        clearInterval(AutomatedSignalsUltra.timer);
    }
    AutomatedSignalsUltra.timer = setInterval(() => {
        AutomatedSignalsUltra.fetchDashboardData();
    }, 7000);
};

AutomatedSignalsUltra.wireFilters = function() {
    // Session filter
    document.querySelectorAll('#ase-session-filter .btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('#ase-session-filter .btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            AutomatedSignalsUltra.filters.session = btn.dataset.session;
            AutomatedSignalsUltra.renderSignalsTable();
        });
    });
    
    // Direction filter
    document.querySelectorAll('#ase-direction-filter .btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('#ase-direction-filter .btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            AutomatedSignalsUltra.filters.direction = btn.dataset.direction;
            AutomatedSignalsUltra.renderSignalsTable();
        });
    });
    
    // State filter
    document.querySelectorAll('#ase-state-filter .btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('#ase-state-filter .btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            AutomatedSignalsUltra.filters.state = btn.dataset.state;
            AutomatedSignalsUltra.renderSignalsTable();
        });
    });
    
    // Search input
    const searchInput = document.getElementById('ase-search-trade-id');
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            AutomatedSignalsUltra.filters.searchId = searchInput.value.trim().toLowerCase();
            AutomatedSignalsUltra.renderSignalsTable();
        });
    }
    
    // Clear filters button
    const clearBtn = document.getElementById('ase-clear-filters');
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            AutomatedSignalsUltra.clearAllFilters();
        });
    }
};

AutomatedSignalsUltra.clearAllFilters = function() {
    AutomatedSignalsUltra.filters = { session: 'ALL', direction: 'ALL', state: 'ALL', searchId: '' };
    AutomatedSignalsUltra.selectedDate = null;
    
    // Reset button states
    document.querySelectorAll('#ase-session-filter .btn').forEach(b => {
        b.classList.toggle('active', b.dataset.session === 'ALL');
    });
    document.querySelectorAll('#ase-direction-filter .btn').forEach(b => {
        b.classList.toggle('active', b.dataset.direction === 'ALL');
    });
    document.querySelectorAll('#ase-state-filter .btn').forEach(b => {
        b.classList.toggle('active', b.dataset.state === 'ALL');
    });
    
    const searchInput = document.getElementById('ase-search-trade-id');
    if (searchInput) searchInput.value = '';
    
    const dateLabel = document.getElementById('ase-selected-date-label');
    if (dateLabel) dateLabel.textContent = 'Click a day to filter';
    
    AutomatedSignalsUltra.renderCalendar();
    AutomatedSignalsUltra.renderSignalsTable();
};

AutomatedSignalsUltra.fetchDashboardData = async function() {
    try {
        const resp = await fetch('/api/automated-signals/dashboard-data', {
            cache: 'no-store'
        });
        const json = await resp.json();
        
        AutomatedSignalsUltra.data = json;
        AutomatedSignalsUltra.renderHeaderStats();
        AutomatedSignalsUltra.renderSignalsTable();
        AutomatedSignalsUltra.renderSummaryStats();
    } catch (err) {
        console.error("[ASE] Error fetching dashboard data:", err);
        const pill = document.getElementById('ase-health-pill');
        if (pill) {
            pill.textContent = "Error";
            pill.style.backgroundColor = "#ff4757";
        }
    }
};

AutomatedSignalsUltra.renderHeaderStats = function() {
    const stats = AutomatedSignalsUltra.data?.stats || {};
    const lastTs = stats.last_webhook_timestamp;
    const deltaSec = stats.seconds_since_last_webhook;
    
    // Header fields
    const lastEl = document.getElementById('ase-last-webhook');
    const sigTodayEl = document.getElementById('ase-signals-today');
    const activeEl = document.getElementById('ase-active-count');
    const pill = document.getElementById('ase-health-pill');
    
    if (lastEl) {
        if (lastTs) {
            const d = new Date(lastTs);
            lastEl.textContent = d.toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit', 
                second: '2-digit' 
            });
        } else {
            lastEl.textContent = "--:--:--";
        }
    }
    
    if (sigTodayEl) {
        sigTodayEl.textContent = stats.today_count ?? stats.total_signals ?? 0;
    }
    
    if (activeEl) {
        activeEl.textContent = stats.active_count ?? 0;
    }
    
    // Health pill logic
    if (pill) {
        let statusText = "Unknown";
        let color = "#999";
        
        if (deltaSec !== null && deltaSec < 90) {
            statusText = "Healthy";
            color = "#00ff88";
        }
        else if (deltaSec >= 90 && deltaSec < 180) {
            statusText = "Delayed";
            color = "#ffaa00";
        }
        else if (deltaSec >= 180) {
            statusText = "Stale";
            color = "#ff4757";
        }
        else {
            statusText = "No Signals";
            color = "#ff4757";
        }
        
        pill.textContent = "Engine: " + statusText;
        pill.style.backgroundColor = color;
        pill.style.color = "#000";
    }
};

AutomatedSignalsUltra.renderSignalsTable = function() {
    const tbody = document.getElementById('ase-signals-tbody');
    const counter = document.getElementById('ase-table-count');
    
    if (!tbody) return;
    
    const active = AutomatedSignalsUltra.data?.active_trades ?? [];
    const completed = AutomatedSignalsUltra.data?.completed_trades ?? [];
    const pending = AutomatedSignalsUltra.data?.pending_trades ?? [];
    
    // Combine all rows
    let rows = [];
    
    for (const sig of pending) {
        rows.push({ status: "PENDING", ...sig });
    }
    for (const sig of active) {
        rows.push({ status: "ACTIVE", ...sig });
    }
    for (const sig of completed) {
        rows.push({ status: "COMPLETED", ...sig });
    }
    
    // Apply filters
    const f = AutomatedSignalsUltra.filters;
    
    rows = rows.filter(row => {
        // Date filter (from calendar click)
        if (AutomatedSignalsUltra.selectedDate) {
            const rowDate = row.signal_date || (row.timestamp ? row.timestamp.split('T')[0] : null);
            if (rowDate !== AutomatedSignalsUltra.selectedDate) return false;
        }
        
        // Session filter
        if (f.session !== 'ALL' && row.session !== f.session) return false;
        
        // Direction filter
        if (f.direction !== 'ALL' && row.direction !== f.direction) return false;
        
        // State filter
        if (f.state !== 'ALL' && row.status !== f.state) return false;
        
        // Search filter
        if (f.searchId && row.trade_id && !row.trade_id.toLowerCase().includes(f.searchId)) return false;
        
        return true;
    });
    
    // Clear table
    tbody.innerHTML = "";
    
    if (rows.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="text-center ultra-muted py-3">No signals match filters.</td></tr>`;
        if (counter) counter.textContent = "0 rows";
        return;
    }
    
    // Populate rows
    for (const row of rows) {
        const tr = document.createElement('tr');
        tr.style.cursor = 'pointer';
        
        const dir = row.direction || "--";
        const entry = row.entry_price ? parseFloat(row.entry_price).toFixed(2) : "N/A";
        const sl = row.stop_loss ? parseFloat(row.stop_loss).toFixed(2) : "N/A";
        const mfeNoBE = row.no_be_mfe != null ? parseFloat(row.no_be_mfe).toFixed(2) : "N/A";
        const mfeBE = row.be_mfe != null ? parseFloat(row.be_mfe).toFixed(2) : "N/A";
        
        // Status badge styling
        let statusClass = 'ultra-badge-blue';
        if (row.status === 'ACTIVE') statusClass = 'ultra-badge-green';
        else if (row.status === 'COMPLETED') statusClass = 'ultra-badge-amber';
        else if (row.status === 'PENDING') statusClass = 'ultra-badge-blue';
        
        // Direction badge
        let dirClass = dir === 'Bullish' ? 'ultra-badge-green' : dir === 'Bearish' ? 'ultra-badge-red' : 'ultra-muted';
        
        // MFE coloring
        let mfeClass = 'ultra-text';
        const mfeVal = parseFloat(mfeNoBE);
        if (!isNaN(mfeVal)) {
            if (mfeVal >= 1) mfeClass = 'ultra-badge-green';
            else if (mfeVal >= 0) mfeClass = 'ultra-badge-amber';
            else mfeClass = 'ultra-badge-red';
        }
        
        // Age calculation
        let ageStr = "--";
        if (row.timestamp) {
            const t = new Date(row.timestamp);
            const diffSec = (Date.now() - t.getTime()) / 1000;
            const mins = Math.floor(diffSec / 60);
            const secs = Math.floor(diffSec % 60);
            ageStr = `${mins}m ${secs}s`;
        }
        
        // Time display
        let timeStr = "--";
        if (row.timestamp) {
            const t = new Date(row.timestamp);
            timeStr = t.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }
        
        tr.innerHTML = `
            <td><span class="${statusClass}">${row.status}</span></td>
            <td class="ultra-muted">${timeStr}</td>
            <td><span class="${dirClass}">${dir}</span></td>
            <td class="ultra-muted">${row.session ?? "--"}</td>
            <td>${entry}</td>
            <td>${sl}</td>
            <td><span class="${mfeClass}">${mfeNoBE}R</span></td>
            <td class="ultra-muted">${ageStr}</td>
        `;
        
        // Click → detail loader
        tr.addEventListener('click', () => {
            AutomatedSignalsUltra.loadTradeDetail(row.trade_id);
        });
        
        tbody.appendChild(tr);
    }
    
    if (counter) counter.textContent = `${rows.length} rows`;
};

AutomatedSignalsUltra.loadTradeDetail = async function(trade_id) {
    if (!trade_id) return;
    
    console.log("[ASE] Loading trade detail for:", trade_id);
    
    const statusBadge = document.getElementById('ase-detail-status');
    const placeholder = document.getElementById('ase-trade-detail-placeholder');
    const container = document.getElementById('ase-trade-detail-container');
    const expandBtn = document.getElementById('ase-lifecycle-expand');
    
    if (statusBadge) {
        statusBadge.textContent = "Loading...";
        statusBadge.classList.remove('bg-secondary', 'bg-success', 'bg-danger');
        statusBadge.classList.add('bg-secondary');
    }
    
    try {
        const resp = await fetch(`/api/automated-signals/trade-detail/${encodeURIComponent(trade_id)}`, {
            cache: 'no-store'
        });
        const json = await resp.json();
        
        if (!json.success || !json.data) {
            throw new Error(json.error || "Trade detail fetch failed");
        }
        
        const detail = json.data;
        
        // Side panel render
        AutomatedSignalsUltra.renderSideDetail(detail);
        
        // Overlay data prep
        AutomatedSignalsUltra.renderLifecycleOverlay(detail);
        
        if (statusBadge) {
            statusBadge.textContent = detail.status || "Loaded";
            statusBadge.classList.remove('bg-secondary', 'bg-success', 'bg-danger');
            if (detail.status === 'COMPLETED') {
                statusBadge.classList.add('bg-success');
            } else {
                statusBadge.classList.add('bg-secondary');
            }
        }
        
        if (placeholder && container) {
            placeholder.style.display = 'none';
            container.style.display = 'block';
        }
        
        if (expandBtn) {
            expandBtn.disabled = false;
            expandBtn.onclick = () => {
                AutomatedSignalsUltra.showLifecycleOverlay();
            };
        }
        
        // Store last detail for overlay reopen
        AutomatedSignalsUltra.lastDetail = detail;
        
    } catch (err) {
        console.error("[ASE] Error loading trade detail:", err);
        if (statusBadge) {
            statusBadge.textContent = "Error";
            statusBadge.classList.remove('bg-secondary');
            statusBadge.classList.add('bg-danger');
        }
    }
};

AutomatedSignalsUltra.renderSideDetail = function(detail) {
    const container = document.getElementById('ase-trade-detail-container');
    if (!container) return;
    
    const direction = detail.direction || 'UNKNOWN';
    const session = detail.session || 'N/A';
    const entry = detail.entry_price != null ? parseFloat(detail.entry_price).toFixed(2) : 'N/A';
    const sl = detail.stop_loss != null ? parseFloat(detail.stop_loss).toFixed(2) : 'N/A';
    const currentMFE = detail.current_mfe != null ? detail.current_mfe.toFixed(2) + 'R' : 'N/A';
    const finalMFE = detail.final_mfe != null ? detail.final_mfe.toFixed(2) + 'R' : 'N/A';
    const exitPrice = detail.exit_price != null ? parseFloat(detail.exit_price).toFixed(2) : 'N/A';
    
    container.innerHTML = `
        <div class="small text-muted mb-2">Trade ID: ${detail.trade_id || 'N/A'}</div>
        <div class="mb-2">
            <span class="badge me-1 ${direction === 'Bullish' ? 'bg-info' : direction === 'Bearish' ? 'bg-danger' : 'bg-secondary'}">${direction}</span>
            <span class="badge bg-dark text-uppercase">${session}</span>
        </div>
        <div class="row g-2 small">
            <div class="col-6">
                <div class="text-muted">Entry</div>
                <div>${entry}</div>
            </div>
            <div class="col-6">
                <div class="text-muted">Stop Loss</div>
                <div>${sl}</div>
            </div>
            <div class="col-6">
                <div class="text-muted">Current MFE</div>
                <div>${currentMFE}</div>
            </div>
            <div class="col-6">
                <div class="text-muted">Final MFE</div>
                <div>${finalMFE}</div>
            </div>
            <div class="col-6">
                <div class="text-muted">Exit Price</div>
                <div>${exitPrice}</div>
            </div>
            <div class="col-6">
                <div class="text-muted">Exit Reason</div>
                <div>${detail.exit_reason || 'N/A'}</div>
            </div>
        </div>
    `;
};

AutomatedSignalsUltra.renderLifecycleOverlay = function(detail) {
    const titleEl = document.getElementById('ase-lifecycle-title');
    const subtitleEl = document.getElementById('ase-lifecycle-subtitle');
    const timelineEl = document.getElementById('ase-lifecycle-timeline');
    const eventsEl = document.getElementById('ase-lifecycle-events');
    const metricsEl = document.getElementById('ase-lifecycle-metrics');
    
    if (!timelineEl || !eventsEl || !metricsEl) return;
    
    if (titleEl) {
        titleEl.textContent = `Trade Journey — ${detail.trade_id || 'N/A'}`;
    }
    
    if (subtitleEl) {
        subtitleEl.textContent = `${detail.direction || 'UNKNOWN'} • ${detail.session || 'N/A'} • Status: ${detail.status || 'N/A'}`;
    }
    
    // Events timeline
    const events = detail.events || [];
    if (events.length === 0) {
        timelineEl.innerHTML = `<div class="text-muted small">No lifecycle events available.</div>`;
        eventsEl.innerHTML = '';
    } else {
        // Simple linear node rendering
        const nodes = events.map((ev, idx) => {
            const etype = ev.event_type || 'EVENT';
            let color = '#7f8c8d';
            if (etype === 'ENTRY' || etype === 'SIGNAL_CREATED') color = '#00aaff';
            else if (etype === 'BE_TRIGGERED') color = '#ffd93d';
            else if (etype.startsWith('EXIT')) color = '#ff4757';
            else if (etype === 'MFE_UPDATE') color = '#21e6c1';
            
            return `<div class="text-center" style="flex:1;">
                <div style="width: 12px; height: 12px; border-radius: 999px; margin: 0 auto 4px auto; background:${color};"></div>
                <div class="small text-muted" style="font-size: 10px;">${etype}</div>
            </div>`;
        }).join('');
        
        timelineEl.innerHTML = `<div class="d-flex align-items-center justify-content-between" style="gap: 8px;">${nodes}</div>`;
        
        // Event list
        const evRows = events.map(ev => {
            const ts = ev.timestamp ? new Date(ev.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : '--:--:--';
            const mfeR = ev.mfe != null ? `${parseFloat(ev.mfe).toFixed(2)}R` : (ev.telemetry?.mfe_R != null ? `${parseFloat(ev.telemetry.mfe_R).toFixed(2)}R` : 'N/A');
            
            return `<div class="d-flex justify-content-between small mb-1">
                <span class="text-muted">${ts}</span>
                <span>${ev.event_type || 'EVENT'}</span>
                <span class="text-muted">${mfeR}</span>
            </div>`;
        }).join('');
        
        eventsEl.innerHTML = evRows;
    }
    
    // Metrics
    const entry = detail.entry_price != null ? parseFloat(detail.entry_price).toFixed(2) : 'N/A';
    const sl = detail.stop_loss != null ? parseFloat(detail.stop_loss).toFixed(2) : 'N/A';
    const currentMFE = detail.current_mfe != null ? detail.current_mfe.toFixed(2) + 'R' : 'N/A';
    const finalMFE = detail.final_mfe != null ? detail.final_mfe.toFixed(2) + 'R' : 'N/A';
    const exitPrice = detail.exit_price != null ? parseFloat(detail.exit_price).toFixed(2) : 'N/A';
    
    metricsEl.innerHTML = `
        <div class="small text-muted mb-2">Core Metrics</div>
        <div class="small mb-1"><span class="text-muted">Entry:</span> ${entry}</div>
        <div class="small mb-1"><span class="text-muted">Stop Loss:</span> ${sl}</div>
        <div class="small mb-1"><span class="text-muted">Current MFE:</span> ${currentMFE}</div>
        <div class="small mb-1"><span class="text-muted">Final MFE:</span> ${finalMFE}</div>
        <div class="small mb-1"><span class="text-muted">Exit Price:</span> ${exitPrice}</div>
    `;
};

AutomatedSignalsUltra.showLifecycleOverlay = function() {
    const overlay = document.getElementById('ase-lifecycle-overlay');
    if (!overlay) return;
    overlay.style.display = 'block';
};

AutomatedSignalsUltra.hideLifecycleOverlay = function() {
    const overlay = document.getElementById('ase-lifecycle-overlay');
    if (!overlay) return;
    overlay.style.display = 'none';
};

AutomatedSignalsUltra.renderSummaryStats = function() {
    const stats = AutomatedSignalsUltra.data?.stats ?? {};
    
    const map = {
        summarySignalsToday: "ase-summary-signals-today",
        summaryConfirmed: "ase-summary-confirmed",
        summaryWinrate: "ase-summary-winrate",
        summaryAvgMFE: "ase-summary-avgmfe",
        summaryBE: "ase-summary-be-count",
        summarySL: "ase-summary-sl-count"
    };
    
    const el1 = document.getElementById(map.summarySignalsToday);
    if (el1) el1.textContent = stats.today_count ?? stats.total_signals ?? 0;
    
    const el2 = document.getElementById(map.summaryConfirmed);
    if (el2) el2.textContent = stats.completed_count ?? 0;
    
    const el3 = document.getElementById(map.summaryWinrate);
    if (el3) {
        if (typeof stats.win_rate === "number") {
            el3.textContent = stats.win_rate.toFixed(1) + "%";
        } else {
            el3.textContent = "--%";
        }
    }
    
    const el4 = document.getElementById(map.summaryAvgMFE);
    if (el4) {
        if (typeof stats.avg_mfe === "number") {
            el4.textContent = stats.avg_mfe.toFixed(2) + "R";
        } else {
            el4.textContent = "0.00R";
        }
    }
    
    const el5 = document.getElementById(map.summaryBE);
    if (el5) el5.textContent = stats.be_triggered_count ?? 0;
    
    const el6 = document.getElementById(map.summarySL);
    if (el6) el6.textContent = stats.sl_count ?? 0;
};

AutomatedSignalsUltra.fetchCalendarData = async function() {
    try {
        const resp = await fetch('/api/automated-signals/daily-calendar', {
            cache: 'no-store'
        });
        const json = await resp.json();
        
        // Handle response format with completed_count and active_count
        if (json.success && json.daily_data) {
            AutomatedSignalsUltra.calendarData = Object.entries(json.daily_data).map(([date, data]) => ({
                date: date,
                completed_count: data.completed_count || 0,
                active_count: data.active_count || 0,
                trade_count: data.trade_count || 0,
                avg_mfe: data.avg_mfe || 0
            }));
        } else if (Array.isArray(json)) {
            AutomatedSignalsUltra.calendarData = json;
        } else {
            AutomatedSignalsUltra.calendarData = [];
        }
        
        console.log("[ASE] Calendar data loaded:", AutomatedSignalsUltra.calendarData.length, "days");
        AutomatedSignalsUltra.renderCalendar();
    } catch (err) {
        console.error("[ASE] Error fetching calendar data:", err);
        AutomatedSignalsUltra.calendarData = [];
        AutomatedSignalsUltra.renderCalendar();
    }
};

AutomatedSignalsUltra.renderCalendar = function() {
    const container = document.getElementById('ase-calendar-container');
    const monthLabel = document.getElementById('ase-calendar-month');
    
    if (!container) return;
    
    const year = AutomatedSignalsUltra.currentMonth.getFullYear();
    const month = AutomatedSignalsUltra.currentMonth.getMonth();
    
    // Update month label
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    if (monthLabel) {
        monthLabel.textContent = `${monthNames[month]} ${year}`;
    }
    
    // Build calendar grid
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    
    // Create lookup for calendar data - count completed and active per day
    const dataByDate = {};
    
    // Process calendar data from API
    for (const item of AutomatedSignalsUltra.calendarData) {
        const dateKey = item.date || item.signal_date;
        if (dateKey) {
            dataByDate[dateKey] = {
                completed: item.completed_count || 0,
                active: item.active_count || 0
            };
        }
    }
    
    const today = new Date();
    const todayStr = today.toISOString().split('T')[0];
    
    let html = `<table class="ultra-calendar"><thead><tr>
        <th>S</th><th>M</th><th>T</th><th>W</th><th>T</th><th>F</th><th>S</th>
    </tr></thead><tbody>`;
    
    let dayCount = 1;
    
    for (let week = 0; week < 6; week++) {
        if (dayCount > daysInMonth) break;
        
        html += '<tr>';
        for (let dow = 0; dow < 7; dow++) {
            if ((week === 0 && dow < firstDay) || dayCount > daysInMonth) {
                html += '<td><div class="calendar-day-empty"></div></td>';
            } else {
                const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(dayCount).padStart(2, '0')}`;
                const dayData = dataByDate[dateStr] || { completed: 0, active: 0 };
                
                let classes = 'calendar-day';
                if (dateStr === todayStr) classes += ' today';
                if (dateStr === AutomatedSignalsUltra.selectedDate) classes += ' selected';
                
                const completedBadge = dayData.completed > 0 
                    ? `<span class="calendar-completed-badge">${dayData.completed}</span>` 
                    : '';
                const activeBadge = dayData.active > 0 
                    ? `<span class="calendar-active-badge">${dayData.active}</span>` 
                    : '';
                
                html += `<td>
                    <div class="${classes}" data-date="${dateStr}">
                        <div class="calendar-day-num">${dayCount}</div>
                        ${completedBadge}
                        ${activeBadge}
                    </div>
                </td>`;
                dayCount++;
            }
        }
        html += '</tr>';
    }
    
    html += '</tbody></table>';
    container.innerHTML = html;
    
    // Wire click handlers for calendar days
    container.querySelectorAll('.calendar-day').forEach(dayEl => {
        dayEl.addEventListener('click', () => {
            const clickedDate = dayEl.dataset.date;
            AutomatedSignalsUltra.selectCalendarDate(clickedDate);
        });
    });
};

AutomatedSignalsUltra.selectCalendarDate = function(dateStr) {
    const dateLabel = document.getElementById('ase-selected-date-label');
    
    // Toggle selection
    if (AutomatedSignalsUltra.selectedDate === dateStr) {
        AutomatedSignalsUltra.selectedDate = null;
        if (dateLabel) dateLabel.textContent = 'Click a day to filter';
    } else {
        AutomatedSignalsUltra.selectedDate = dateStr;
        if (dateLabel) {
            const d = new Date(dateStr + 'T12:00:00');
            dateLabel.textContent = `Showing: ${d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;
        }
    }
    
    AutomatedSignalsUltra.renderCalendar();
    AutomatedSignalsUltra.renderSignalsTable();
};

// DOM ready hook
document.addEventListener('DOMContentLoaded', () => {
    console.log("[ASE] DOMContentLoaded fired");
    console.log("[ASE] AutomatedSignalsUltra exists:", !!window.AutomatedSignalsUltra);
    console.log("[ASE] init is function:", typeof AutomatedSignalsUltra.init === 'function');
    
    if (window.AutomatedSignalsUltra && typeof AutomatedSignalsUltra.init === 'function') {
        console.log("[ASE] Calling init()...");
        AutomatedSignalsUltra.init();
    } else {
        console.error("[ASE] FAILED to call init - object or function missing!");
    }
    
    // Wire Close button for lifecycle overlay
    const closeBtn = document.getElementById('ase-lifecycle-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            AutomatedSignalsUltra.hideLifecycleOverlay();
        });
    }
});
