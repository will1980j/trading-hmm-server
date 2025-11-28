/**
 * AUTOMATED SIGNALS ULTRA - H1.4A FOUNDATIONAL DATA PIPELINE
 * Production-safe implementation with real endpoints only
 */

const AutomatedSignalsUltra = {
    data: null,
    timer: null,
};

AutomatedSignalsUltra.init = function() {
    console.log("[ASE] Initializing Automated Signals Engine dashboard...");
    
    // First load
    AutomatedSignalsUltra.fetchDashboardData();
    
    // Poll every 7 seconds
    if (AutomatedSignalsUltra.timer) {
        clearInterval(AutomatedSignalsUltra.timer);
    }
    AutomatedSignalsUltra.timer = setInterval(() => {
        AutomatedSignalsUltra.fetchDashboardData();
    }, 7000);
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
        sigTodayEl.textContent = stats.total_signals ?? 0;
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
    const pending = AutomatedSignalsUltra.data?.pending_trades ?? []; // If backend adds in future
    
    // Combine
    const rows = [];
    
    // Pending (optional)
    for (const sig of pending) {
        rows.push({
            status: "PENDING",
            ...sig
        });
    }
    
    // Active
    for (const sig of active) {
        rows.push({
            status: "ACTIVE",
            ...sig
        });
    }
    
    // Completed
    for (const sig of completed) {
        rows.push({
            status: "COMPLETED",
            ...sig
        });
    }
    
    // Clear table
    tbody.innerHTML = "";
    
    if (rows.length === 0) {
        tbody.innerHTML = `<tr><td colspan="11" class="text-center text-muted small py-3">No signals available.</td></tr>`;
        if (counter) counter.textContent = "0 rows";
        return;
    }
    
    // Populate rows
    for (const row of rows) {
        const tr = document.createElement('tr');
        const dir = row.direction || "--";
        const entry = row.entry_price ? parseFloat(row.entry_price).toFixed(2) : "N/A";
        const sl = row.stop_loss ? parseFloat(row.stop_loss).toFixed(2) : "N/A";
        const mfeNoBE = row.no_be_mfe ? parseFloat(row.no_be_mfe).toFixed(2) + "R" : "N/A";
        const mfeBE = row.be_mfe ? parseFloat(row.be_mfe).toFixed(2) + "R" : "N/A";
        
        // Age calculation
        let ageStr = "--";
        if (row.timestamp) {
            const t = new Date(row.timestamp);
            const diffSec = (Date.now() - t.getTime()) / 1000;
            const mins = Math.floor(diffSec / 60);
            const secs = Math.floor(diffSec % 60);
            ageStr = `${mins}m ${secs}s`;
        }
        
        tr.innerHTML = `
            <td>${row.status}</td>
            <td>${row.timestamp ?? "--"}</td>
            <td>${dir}</td>
            <td>${row.session ?? "--"}</td>
            <td>${entry}</td>
            <td>${sl}</td>
            <td>${mfeNoBE}</td>
            <td>${mfeBE}</td>
            <td>${row.no_be_mfe ?? 0}</td>
            <td>${ageStr}</td>
            <td>${row.trade_id ?? "--"}</td>
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
    if (el1) el1.textContent = stats.total_signals ?? 0;
    
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

// DOM ready hook
document.addEventListener('DOMContentLoaded', () => {
    if (window.AutomatedSignalsUltra && typeof AutomatedSignalsUltra.init === 'function') {
        AutomatedSignalsUltra.init();
    }
    
    // Wire Close button for lifecycle overlay
    const closeBtn = document.getElementById('ase-lifecycle-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            AutomatedSignalsUltra.hideLifecycleOverlay();
        });
    }
});
