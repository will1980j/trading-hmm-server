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
AutomatedSignalsUltra.rawPayload = null;  // Store raw payload for debug tab
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
    
    // Wire refresh button
    const refreshBtn = document.getElementById('ase-refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            AutomatedSignalsUltra.fetchDashboardData();
            AutomatedSignalsUltra.fetchCalendarData();
        });
    }
    
    // Poll every 7 seconds
    if (AutomatedSignalsUltra.timer) {
        clearInterval(AutomatedSignalsUltra.timer);
    }
    // Auto-refresh ALL dashboard components together (not just the table)
    AutomatedSignalsUltra.timer = setInterval(() => {
        AutomatedSignalsUltra.fetchDashboardData();
        AutomatedSignalsUltra.fetchCalendarData();
    }, 7000);
    
    // Wire Cancelled Signals tab - fetch data when tab is clicked
    const cancelledTab = document.getElementById('cancelled-tab');
    if (cancelledTab) {
        cancelledTab.addEventListener('click', () => {
            // Fetch cancelled signals when the Cancelled tab is activated
            AutomatedSignalsUltra.fetchCancelledSignals();
        });
    }
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
        const resp = await fetch(`/api/automated-signals/dashboard-data?_=${Date.now()}`, {
            cache: 'no-store',
            headers: {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
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
            // Parse UTC timestamp and convert to NY Eastern
            const utcDate = new Date(lastTs + (lastTs.includes('Z') ? '' : 'Z'));
            lastEl.textContent = utcDate.toLocaleTimeString('en-US', { 
                hour: '2-digit', 
                minute: '2-digit', 
                second: '2-digit',
                hour12: true,
                timeZone: 'America/New_York'
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

AutomatedSignalsUltra.selectedTrades = new Set();

AutomatedSignalsUltra.renderSignalsTable = function() {
    const tbody = document.getElementById('ase-signals-tbody');
    const counter = document.getElementById('ase-table-count');
    const dateLabel = document.getElementById('ase-table-date');
    
    if (!tbody) return;
    
    // Update date display - use NY Eastern timezone (handles DST automatically)
    if (dateLabel) {
        const today = new Date();
        dateLabel.textContent = `— ${today.toLocaleDateString('en-US', { 
            weekday: 'short', 
            month: 'short', 
            day: 'numeric',
            timeZone: 'America/New_York'
        })}`;
    }
    
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
        if (AutomatedSignalsUltra.selectedDate) {
            const rowDate = row.signal_date || (row.timestamp ? row.timestamp.split('T')[0] : null);
            if (rowDate !== AutomatedSignalsUltra.selectedDate) return false;
        }
        if (f.session !== 'ALL' && row.session !== f.session) return false;
        
        // Direction filter: normalize LONG/SHORT to Bullish/Bearish for comparison
        if (f.direction !== 'ALL') {
            let rowDir = row.direction || '';
            if (rowDir.toUpperCase() === 'LONG') rowDir = 'Bullish';
            else if (rowDir.toUpperCase() === 'SHORT') rowDir = 'Bearish';
            if (rowDir !== f.direction) return false;
        }
        
        if (f.state !== 'ALL' && row.status !== f.state) return false;
        if (f.searchId && row.trade_id && !row.trade_id.toLowerCase().includes(f.searchId)) return false;
        return true;
    });
    
    tbody.innerHTML = "";
    
    if (rows.length === 0) {
        tbody.innerHTML = `<tr><td colspan="10" class="text-center ultra-muted py-3">No signals match filters.</td></tr>`;
        if (counter) counter.textContent = "0 rows";
        return;
    }
    
    for (const row of rows) {
        const tr = document.createElement('tr');
        tr.dataset.tradeId = row.trade_id;
        
        // Normalize direction: API may return LONG/SHORT or Bullish/Bearish
        let dir = row.direction || "--";
        if (dir.toUpperCase() === 'LONG') dir = 'Bullish';
        else if (dir.toUpperCase() === 'SHORT') dir = 'Bearish';
        
        const entry = row.entry_price ? parseFloat(row.entry_price).toFixed(2) : "N/A";
        const sl = row.stop_loss ? parseFloat(row.stop_loss).toFixed(2) : "N/A";
        
        // API returns be_mfe and no_be_mfe (without _R suffix) - fix field names
        // Also check mfe as fallback for older data
        const beMfeVal = row.be_mfe ?? row.be_mfe_R ?? row.mfe ?? null;
        const noBeMfeVal = row.no_be_mfe ?? row.no_be_mfe_R ?? row.mfe ?? null;
        const mfeBE = beMfeVal != null ? parseFloat(beMfeVal).toFixed(2) + "R" : "--";
        const mfeNoBE = noBeMfeVal != null ? parseFloat(noBeMfeVal).toFixed(2) + "R" : "--";
        
        // DUAL STATUS LOGIC: Track BE=1 and No BE strategies separately
        // - EXIT_BE: BE=1 completed (hit entry after +1R), No BE still active
        // - EXIT_SL: Both strategies completed (original SL hit)
        // - ACTIVE: Both strategies still running
        let beStatus = 'ACTIVE';
        let noBeStatus = 'ACTIVE';
        
        if (row.event_type === 'EXIT_BE') {
            beStatus = 'COMPLETE';  // BE=1 exited at entry
            noBeStatus = 'ACTIVE';  // No BE still running
        } else if (row.event_type === 'EXIT_SL') {
            beStatus = 'COMPLETE';  // Both done
            noBeStatus = 'COMPLETE';
        } else if (row.status === 'COMPLETED') {
            // Fallback for older data without event_type
            beStatus = 'COMPLETE';
            noBeStatus = 'COMPLETE';
        }
        
        // MFE coloring for both columns
        const getMfeClass = (val) => {
            const v = parseFloat(val);
            if (isNaN(v)) return 'ultra-muted';
            if (v >= 1) return 'ultra-badge-green';
            if (v >= 0) return 'ultra-badge-amber';
            return 'ultra-badge-red';
        };
        
        // Age: Calculate from signal_date + signal_time (Eastern Time)
        let ageStr = "--";
        
        // Helper to format duration
        const formatDuration = (diffSec) => {
            if (diffSec < 60) return `${Math.floor(diffSec)}s`;
            if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ${Math.floor(diffSec % 60)}s`;
            return `${Math.floor(diffSec / 3600)}h ${Math.floor((diffSec % 3600) / 60)}m`;
        };
        
        if (row.status === 'ACTIVE' && row.signal_date && row.signal_time) {
            // Active trades: show live age since signal time
            // signal_date and signal_time are in Eastern Time from the API
            // We need to get current Eastern time and compare
            const now = new Date();
            const nowEastern = new Date(now.toLocaleString('en-US', { timeZone: 'America/New_York' }));
            
            // Parse signal time components
            const [year, month, day] = row.signal_date.split('-').map(Number);
            const timeParts = row.signal_time.split(':').map(Number);
            const signalHour = timeParts[0] || 0;
            const signalMin = timeParts[1] || 0;
            const signalSec = timeParts[2] || 0;
            
            // Create signal time as if it were in the same timezone as nowEastern
            const signalTimeEastern = new Date(year, month - 1, day, signalHour, signalMin, signalSec);
            
            // Calculate age in seconds
            const diffSec = Math.max(0, (nowEastern.getTime() - signalTimeEastern.getTime()) / 1000);
            ageStr = formatDuration(diffSec);
        } else if (row.status === 'COMPLETED') {
            // Completed trades: show duration from entry to exit
            if (row.duration_seconds) {
                ageStr = formatDuration(row.duration_seconds);
            } else if (row.exit_timestamp && row.signal_date && row.signal_time) {
                // Parse exit timestamp (ISO format with timezone)
                const exitTime = new Date(row.exit_timestamp);
                const exitEastern = new Date(exitTime.toLocaleString('en-US', { timeZone: 'America/New_York' }));
                
                // Parse signal time components
                const [year, month, day] = row.signal_date.split('-').map(Number);
                const timeParts = row.signal_time.split(':').map(Number);
                const signalHour = timeParts[0] || 0;
                const signalMin = timeParts[1] || 0;
                const signalSec = timeParts[2] || 0;
                
                const signalTimeEastern = new Date(year, month - 1, day, signalHour, signalMin, signalSec);
                const diffSec = Math.max(0, (exitEastern.getTime() - signalTimeEastern.getTime()) / 1000);
                ageStr = formatDuration(diffSec);
            } else {
                ageStr = "--";
            }
        }
        
        // Time display: Use signal_time from TradingView (already in Eastern Time)
        // CRITICAL FIX: Use the ORIGINAL signal_time, never derive from current time
        let timeStr = "--";
        const originalSignalTime = row.signal_time;  // Preserve original value
        if (originalSignalTime) {
            // signal_time is already in Eastern Time format like "05:28:00" or "07:01:00"
            // Parse and format nicely as HH:MM AM/PM
            const rawTime = String(originalSignalTime);
            const parts = rawTime.split(':');
            if (parts.length >= 2) {
                let hour = parseInt(parts[0], 10);
                const min = parts[1];
                const ampm = hour >= 12 ? 'PM' : 'AM';
                if (hour > 12) hour -= 12;
                if (hour === 0) hour = 12;
                timeStr = `${hour.toString().padStart(2, '0')}:${min} ${ampm}`;
            } else {
                timeStr = rawTime;
            }

        }
        
        const isChecked = AutomatedSignalsUltra.selectedTrades.has(row.trade_id);
        
        // Direction badge with Matrix/red-pill styling like Trade Lifecycle panel
        const dirBadgeClass = dir === 'Bullish' ? 'direction-badge-bullish' : 
                              dir === 'Bearish' ? 'direction-badge-bearish' : 'ultra-muted';
        
        // Build dual status badges - only highlight ACTIVE (green), COMPLETE is muted
        const beStatusClass = beStatus === 'ACTIVE' ? 'ultra-badge-green' : 'ultra-badge-muted';
        const noBeStatusClass = noBeStatus === 'ACTIVE' ? 'ultra-badge-green' : 'ultra-badge-muted';
        const beMfeDisplay = mfeBE;
        const noBeMfeDisplay = mfeNoBE;
        
        tr.innerHTML = `
            <td><input type="checkbox" class="trade-checkbox trade-row-checkbox" data-trade-id="${row.trade_id}" ${isChecked ? 'checked' : ''}></td>
            <td class="dual-status-cell">
                <span class="dual-status-badge ${beStatusClass}" title="BE=1 Strategy">BE: ${beStatus}</span>
                <span class="dual-status-badge ${noBeStatusClass}" title="No BE Strategy">NoBE: ${noBeStatus}</span>
            </td>
            <td class="ultra-muted">${timeStr}</td>
            <td><span class="${dirBadgeClass}">${dir}</span></td>
            <td class="ultra-muted">${row.session ?? "--"}</td>
            <td>${entry}</td>
            <td>${sl}</td>
            <td><span class="${getMfeClass(mfeBE)}">${beMfeDisplay}</span></td>
            <td><span class="${getMfeClass(mfeNoBE)}">${noBeMfeDisplay}</span></td>
            <td class="ultra-muted">${ageStr}</td>
        `;
        
        // Click on row (not checkbox) loads detail
        tr.addEventListener('click', (e) => {
            if (e.target.type !== 'checkbox') {
                AutomatedSignalsUltra.loadTradeDetail(row.trade_id);
            }
        });
        
        tbody.appendChild(tr);
    }
    
    if (counter) counter.textContent = `${rows.length} rows`;
    
    // Wire checkbox events
    AutomatedSignalsUltra.wireCheckboxes();
};

AutomatedSignalsUltra.wireCheckboxes = function() {
    const selectAll = document.getElementById('ase-select-all');
    const deleteBtn = document.getElementById('ase-delete-selected');
    
    // Select all checkbox
    if (selectAll) {
        selectAll.addEventListener('change', () => {
            const checkboxes = document.querySelectorAll('.trade-row-checkbox');
            checkboxes.forEach(cb => {
                cb.checked = selectAll.checked;
                if (selectAll.checked) {
                    AutomatedSignalsUltra.selectedTrades.add(cb.dataset.tradeId);
                } else {
                    AutomatedSignalsUltra.selectedTrades.delete(cb.dataset.tradeId);
                }
            });
            AutomatedSignalsUltra.updateDeleteButton();
        });
    }
    
    // Individual checkboxes
    document.querySelectorAll('.trade-row-checkbox').forEach(cb => {
        cb.addEventListener('change', () => {
            if (cb.checked) {
                AutomatedSignalsUltra.selectedTrades.add(cb.dataset.tradeId);
            } else {
                AutomatedSignalsUltra.selectedTrades.delete(cb.dataset.tradeId);
            }
            AutomatedSignalsUltra.updateDeleteButton();
        });
    });
    
    // Delete button
    if (deleteBtn) {
        deleteBtn.onclick = () => AutomatedSignalsUltra.deleteSelectedTrades();
    }
};

AutomatedSignalsUltra.updateDeleteButton = function() {
    const deleteBtn = document.getElementById('ase-delete-selected');
    if (deleteBtn) {
        const count = AutomatedSignalsUltra.selectedTrades.size;
        deleteBtn.disabled = count === 0;
        deleteBtn.textContent = count > 0 ? `🗑 Delete (${count})` : '🗑 Delete';
    }
};

AutomatedSignalsUltra.deleteSelectedTrades = async function() {
    const tradeIds = Array.from(AutomatedSignalsUltra.selectedTrades);
    if (tradeIds.length === 0) return;
    
    if (!confirm(`Delete ${tradeIds.length} trade(s)? This cannot be undone.`)) return;
    
    try {
        // Use bulk delete endpoint with POST
        const resp = await fetch('/api/automated-signals/bulk-delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ trade_ids: tradeIds })
        });
        
        const result = await resp.json();
        
        if (resp.ok && result.success) {
            console.log(`[ASE] Deleted ${result.deleted_count || tradeIds.length} trades`);
        } else {
            console.error('[ASE] Delete failed:', result.error || 'Unknown error');
            alert('Delete failed: ' + (result.error || 'Unknown error'));
        }
    } catch (err) {
        console.error('[ASE] Delete error:', err);
        alert('Delete failed: ' + err.message);
    }
    
    AutomatedSignalsUltra.selectedTrades.clear();
    AutomatedSignalsUltra.updateDeleteButton();
    
    // Refresh data
    AutomatedSignalsUltra.fetchDashboardData();
    AutomatedSignalsUltra.fetchCalendarData();
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
        // Correct endpoint: /api/automated-signals/trade/<trade_id>
        const resp = await fetch(`/api/automated-signals/trade/${encodeURIComponent(trade_id)}`, {
            cache: 'no-store'
        });
        const json = await resp.json();
        
        // The endpoint returns the detail directly (not wrapped in success/data)
        if (json.error) {
            throw new Error(json.error || "Trade detail fetch failed");
        }
        
        const detail = json;
        
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
    
    // Normalize direction: API may return LONG/SHORT or Bullish/Bearish
    let direction = detail.direction || 'UNKNOWN';
    if (direction.toUpperCase() === 'LONG') direction = 'Bullish';
    else if (direction.toUpperCase() === 'SHORT') direction = 'Bearish';
    
    const session = detail.session || 'N/A';
    const entry = detail.entry_price != null ? parseFloat(detail.entry_price).toFixed(2) : 'N/A';
    const sl = detail.stop_loss != null ? parseFloat(detail.stop_loss).toFixed(2) : 'N/A';
    // API returns no_be_mfe, be_mfe, final_mfe (without _R suffix) - fix field names
    const noBeMfeVal = detail.no_be_mfe ?? detail.no_be_mfe_R ?? detail.mfe ?? null;
    const beMfeVal = detail.be_mfe ?? detail.be_mfe_R ?? detail.mfe ?? null;
    const finalMfeVal = detail.final_mfe ?? detail.final_mfe_R ?? null;
    const currentMFE = noBeMfeVal != null ? parseFloat(noBeMfeVal).toFixed(2) + 'R' : 
                       (beMfeVal != null ? parseFloat(beMfeVal).toFixed(2) + 'R' : 'N/A');
    const finalMFE = finalMfeVal != null ? parseFloat(finalMfeVal).toFixed(2) + 'R' : 'N/A';
    const exitPrice = detail.exit_price != null ? parseFloat(detail.exit_price).toFixed(2) : 'N/A';
    
    container.innerHTML = `
        <div class="small ultra-muted mb-2">Trade ID: <span class="ultra-text">${detail.trade_id || 'N/A'}</span></div>
        <div class="mb-2">
            <span class="badge me-1 ${direction === 'Bullish' ? 'bg-info' : direction === 'Bearish' ? 'bg-danger' : 'bg-secondary'}">${direction}</span>
            <span class="badge bg-dark text-uppercase">${session}</span>
        </div>
        <div class="row g-2 small">
            <div class="col-6">
                <div class="ultra-muted">Entry</div>
                <div class="ultra-text">${entry}</div>
            </div>
            <div class="col-6">
                <div class="ultra-muted">Stop Loss</div>
                <div class="ultra-text">${sl}</div>
            </div>
            <div class="col-6">
                <div class="ultra-muted">Current MFE</div>
                <div class="ultra-badge-green">${currentMFE}</div>
            </div>
            <div class="col-6">
                <div class="ultra-muted">Final MFE</div>
                <div class="ultra-badge-green">${finalMFE}</div>
            </div>
            <div class="col-6">
                <div class="ultra-muted">Exit Price</div>
                <div class="ultra-text">${exitPrice}</div>
            </div>
            <div class="col-6">
                <div class="ultra-muted">Exit Reason</div>
                <div class="ultra-text">${detail.exit_reason || 'N/A'}</div>
            </div>
        </div>
    `;
};

AutomatedSignalsUltra.renderLifecycleOverlay = function(detail) {
    const titleEl = document.getElementById('ase-lifecycle-title');
    const subtitleEl = document.getElementById('ase-lifecycle-subtitle');
    const eventsEl = document.getElementById('ase-lifecycle-events');
    const metricsEl = document.getElementById('ase-lifecycle-metrics');
    const liveIndicator = document.getElementById('ase-chart-live-indicator');
    
    if (!eventsEl || !metricsEl) return;
    
    // Store raw payload for debug tab
    AutomatedSignalsUltra.rawPayload = detail || null;
    
    // Render raw payload JSON in debug panel
    const payloadEl = document.getElementById('ase-payload-json');
    if (payloadEl) {
        if (AutomatedSignalsUltra.rawPayload) {
            payloadEl.textContent = JSON.stringify(AutomatedSignalsUltra.rawPayload, null, 2);
        } else {
            payloadEl.textContent = 'No payload available.';
        }
    }
    
    // Normalize direction for display
    let displayDir = detail.direction || 'UNKNOWN';
    if (displayDir.toUpperCase() === 'LONG') displayDir = 'Bullish';
    else if (displayDir.toUpperCase() === 'SHORT') displayDir = 'Bearish';
    
    // Update header
    if (titleEl) {
        titleEl.textContent = `Trade Journey — ${detail.trade_id || 'N/A'}`;
    }
    if (subtitleEl) {
        const dirColor = displayDir === 'Bullish' ? '#22c55e' : displayDir === 'Bearish' ? '#ef4444' : '#94a3b8';
        subtitleEl.innerHTML = `<span style="color:${dirColor}">${displayDir}</span> • ${detail.session || 'N/A'} • Status: <span style="color:#3b82f6">${detail.status || 'N/A'}</span>`;
    }
    
    // Live indicator
    if (liveIndicator) {
        liveIndicator.style.color = detail.status === 'ACTIVE' ? '#22c55e' : '#64748b';
        liveIndicator.textContent = detail.status === 'ACTIVE' ? '● Live' : '○ Completed';
    }
    
    // Render D3 Chart
    AutomatedSignalsUltra.renderLifecycleChart(detail);
    
    // Render Events List
    const events = detail.events || [];
    if (events.length === 0) {
        eventsEl.innerHTML = `<div style="color:rgba(226,232,240,0.5); font-size:13px;">No lifecycle events available.</div>`;
    } else {
        const evRows = events.map(ev => {
            // Format time in NY Eastern timezone to match TradingView
            const ts = ev.timestamp ? new Date(ev.timestamp).toLocaleTimeString('en-US', { 
                hour: '2-digit', minute: '2-digit', second: '2-digit', 
                hour12: true, timeZone: 'America/New_York' 
            }) : '--:--:--';
            const date = ev.timestamp ? new Date(ev.timestamp).toLocaleDateString('en-US', { 
                month: 'short', day: 'numeric', timeZone: 'America/New_York' 
            }) : '';
            // API returns mfe, no_be_mfe, be_mfe (without _R suffix)
            const mfeR = ev.mfe != null ? parseFloat(ev.mfe).toFixed(2) : 
                        (ev.no_be_mfe != null ? parseFloat(ev.no_be_mfe).toFixed(2) : 
                        (ev.be_mfe != null ? parseFloat(ev.be_mfe).toFixed(2) : 
                        (ev.mfe_R != null ? parseFloat(ev.mfe_R).toFixed(2) : null)));
            
            let eventColor = '#94a3b8';
            const etype = ev.event_type || 'EVENT';
            if (etype === 'ENTRY' || etype === 'SIGNAL_CREATED') eventColor = '#3b82f6';
            else if (etype === 'BE_TRIGGERED') eventColor = '#eab308';
            else if (etype.startsWith('EXIT')) eventColor = '#ef4444';
            else if (etype === 'MFE_UPDATE') eventColor = '#22c55e';
            
            const mfeDisplay = mfeR !== null ? `<span style="color:${parseFloat(mfeR) >= 1 ? '#22c55e' : parseFloat(mfeR) >= 0 ? '#eab308' : '#ef4444'}">${mfeR}R</span>` : '<span style="color:#64748b">--</span>';
            
            return `<div style="display:flex; justify-content:space-between; align-items:center; padding:6px 8px; margin-bottom:4px; background:rgba(255,255,255,0.03); border-radius:6px; border-left:3px solid ${eventColor};">
                <span style="color:#94a3b8; font-size:12px;">${date} ${ts}</span>
                <span style="color:#e2e8f0; font-size:13px; font-weight:500;">${etype}</span>
                ${mfeDisplay}
            </div>`;
        }).join('');
        eventsEl.innerHTML = evRows;
    }
    
    // Render Metrics - API returns be_mfe and no_be_mfe (without _R suffix)
    const entry = detail.entry_price != null ? parseFloat(detail.entry_price).toFixed(2) : 'N/A';
    const sl = detail.stop_loss != null ? parseFloat(detail.stop_loss).toFixed(2) : 'N/A';
    const riskDist = detail.risk_distance != null ? parseFloat(detail.risk_distance).toFixed(2) : 'N/A';
    // Use correct field names from API: no_be_mfe and be_mfe (without _R suffix)
    const noBeMfeMetric = detail.no_be_mfe ?? detail.no_be_mfe_R ?? detail.mfe ?? null;
    const beMfeMetric = detail.be_mfe ?? detail.be_mfe_R ?? detail.mfe ?? null;
    const currentMFE = noBeMfeMetric != null ? parseFloat(noBeMfeMetric).toFixed(2) : 'N/A';
    const beMFE = beMfeMetric != null ? parseFloat(beMfeMetric).toFixed(2) : 'N/A';
    const exitPrice = detail.exit_price != null ? parseFloat(detail.exit_price).toFixed(2) : 'N/A';
    
    metricsEl.innerHTML = `
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
            <div style="background:rgba(59,130,246,0.1); padding:10px; border-radius:8px;">
                <div style="color:#64748b; font-size:11px; text-transform:uppercase;">Entry</div>
                <div style="color:#e2e8f0; font-size:16px; font-weight:600;">${entry}</div>
            </div>
            <div style="background:rgba(239,68,68,0.1); padding:10px; border-radius:8px;">
                <div style="color:#64748b; font-size:11px; text-transform:uppercase;">Stop Loss</div>
                <div style="color:#ef4444; font-size:16px; font-weight:600;">${sl}</div>
            </div>
            <div style="background:rgba(34,197,94,0.1); padding:10px; border-radius:8px;">
                <div style="color:#64748b; font-size:11px; text-transform:uppercase;">Current MFE</div>
                <div style="color:#22c55e; font-size:16px; font-weight:600;">${currentMFE}R</div>
            </div>
            <div style="background:rgba(234,179,8,0.1); padding:10px; border-radius:8px;">
                <div style="color:#64748b; font-size:11px; text-transform:uppercase;">BE MFE</div>
                <div style="color:#eab308; font-size:16px; font-weight:600;">${beMFE}R</div>
            </div>
            <div style="background:rgba(148,163,184,0.1); padding:10px; border-radius:8px;">
                <div style="color:#64748b; font-size:11px; text-transform:uppercase;">Risk (1R)</div>
                <div style="color:#94a3b8; font-size:16px; font-weight:600;">${riskDist} pts</div>
            </div>
            <div style="background:rgba(148,163,184,0.1); padding:10px; border-radius:8px;">
                <div style="color:#64748b; font-size:11px; text-transform:uppercase;">Exit Price</div>
                <div style="color:#94a3b8; font-size:16px; font-weight:600;">${exitPrice}</div>
            </div>
        </div>
    `;
};

// D3.js Chart Rendering
AutomatedSignalsUltra.renderLifecycleChart = function(detail) {
    const container = document.getElementById('ase-lifecycle-chart');
    const svg = d3.select('#ase-lifecycle-svg');
    if (!container || !svg) return;
    
    // Clear previous
    svg.selectAll('*').remove();
    
    const events = detail.events || [];
    if (events.length === 0) {
        svg.append('text')
            .attr('x', '50%')
            .attr('y', '50%')
            .attr('text-anchor', 'middle')
            .attr('fill', 'rgba(226,232,240,0.4)')
            .attr('font-size', '14px')
            .text('No MFE data available for chart');
        return;
    }
    
    // Chart dimensions
    const width = container.clientWidth || 800;
    const height = 320;
    const margin = { top: 30, right: 60, bottom: 50, left: 60 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;
    
    svg.attr('width', width).attr('height', height);
    
    // Parse data points with MFE values (API returns mfe, no_be_mfe, be_mfe without _R suffix)
    const dataPoints = events
        .filter(ev => ev.mfe != null || ev.no_be_mfe != null || ev.be_mfe != null || ev.mfe_R != null)
        .map(ev => ({
            time: new Date(ev.timestamp),
            mfe: ev.mfe != null ? parseFloat(ev.mfe) : 
                 (ev.no_be_mfe != null ? parseFloat(ev.no_be_mfe) : 
                 (ev.be_mfe != null ? parseFloat(ev.be_mfe) : 
                 (ev.mfe_R != null ? parseFloat(ev.mfe_R) : 0))),
            type: ev.event_type
        }))
        .sort((a, b) => a.time - b.time);
    
    if (dataPoints.length === 0) {
        svg.append('text')
            .attr('x', '50%')
            .attr('y', '50%')
            .attr('text-anchor', 'middle')
            .attr('fill', 'rgba(226,232,240,0.4)')
            .attr('font-size', '14px')
            .text('No MFE data points to display');
        return;
    }
    
    // Scales
    const xExtent = d3.extent(dataPoints, d => d.time);
    const xScale = d3.scaleTime()
        .domain([xExtent[0], new Date(Math.max(xExtent[1].getTime(), Date.now()))])
        .range([0, innerWidth]);
    
    const maxMFE = Math.max(3, d3.max(dataPoints, d => d.mfe) + 0.5);
    const minMFE = Math.min(-1.5, d3.min(dataPoints, d => d.mfe) - 0.5);
    const yScale = d3.scaleLinear()
        .domain([minMFE, maxMFE])
        .range([innerHeight, 0]);
    
    const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // Milestone lines (SL, Entry, BE, R1, R2, R3)
    const milestones = [
        { r: -1, label: 'SL (-1R)', color: '#ef4444', dash: '4,4' },
        { r: 0, label: 'ENTRY (0R)', color: '#3b82f6', dash: '0' },
        { r: 1, label: 'BE (+1R)', color: '#eab308', dash: '4,4' },
        { r: 2, label: '+2R', color: '#22c55e', dash: '4,4' },
        { r: 3, label: '+3R', color: '#22c55e', dash: '4,4' }
    ];
    
    milestones.forEach(m => {
        if (m.r >= minMFE && m.r <= maxMFE) {
            g.append('line')
                .attr('x1', 0)
                .attr('x2', innerWidth)
                .attr('y1', yScale(m.r))
                .attr('y2', yScale(m.r))
                .attr('stroke', m.color)
                .attr('stroke-width', m.r === 0 ? 1.5 : 1)
                .attr('stroke-dasharray', m.dash)
                .attr('opacity', 0.4);
            
            g.append('text')
                .attr('x', innerWidth + 5)
                .attr('y', yScale(m.r) + 4)
                .attr('fill', m.color)
                .attr('font-size', '10px')
                .attr('opacity', 0.7)
                .text(m.label);
        }
    });
    
    // Line generator
    const line = d3.line()
        .x(d => xScale(d.time))
        .y(d => yScale(d.mfe))
        .curve(d3.curveMonotoneX);
    
    // Gradient for area
    const gradient = svg.append('defs')
        .append('linearGradient')
        .attr('id', 'mfe-gradient')
        .attr('x1', '0%').attr('y1', '0%')
        .attr('x2', '0%').attr('y2', '100%');
    gradient.append('stop').attr('offset', '0%').attr('stop-color', '#22c55e').attr('stop-opacity', 0.3);
    gradient.append('stop').attr('offset', '100%').attr('stop-color', '#22c55e').attr('stop-opacity', 0.02);
    
    // Area under line
    const area = d3.area()
        .x(d => xScale(d.time))
        .y0(yScale(0))
        .y1(d => yScale(d.mfe))
        .curve(d3.curveMonotoneX);
    
    g.append('path')
        .datum(dataPoints)
        .attr('fill', 'url(#mfe-gradient)')
        .attr('d', area);
    
    // MFE Line
    g.append('path')
        .datum(dataPoints)
        .attr('fill', 'none')
        .attr('stroke', '#22c55e')
        .attr('stroke-width', 2.5)
        .attr('d', line);
    
    // Data points
    g.selectAll('.mfe-point')
        .data(dataPoints)
        .enter()
        .append('circle')
        .attr('class', 'mfe-point')
        .attr('cx', d => xScale(d.time))
        .attr('cy', d => yScale(d.mfe))
        .attr('r', d => d.type === 'ENTRY' || d.type.startsWith('EXIT') ? 6 : 4)
        .attr('fill', d => {
            if (d.type === 'ENTRY' || d.type === 'SIGNAL_CREATED') return '#3b82f6';
            if (d.type === 'BE_TRIGGERED') return '#eab308';
            if (d.type.startsWith('EXIT')) return '#ef4444';
            return '#22c55e';
        })
        .attr('stroke', '#0a1628')
        .attr('stroke-width', 2);
    
    // X Axis
    const xAxis = d3.axisBottom(xScale)
        .ticks(6)
        .tickFormat(d3.timeFormat('%H:%M'));
    
    g.append('g')
        .attr('transform', `translate(0,${innerHeight})`)
        .call(xAxis)
        .selectAll('text')
        .attr('fill', '#94a3b8')
        .attr('font-size', '11px');
    
    g.selectAll('.domain, .tick line').attr('stroke', 'rgba(148,163,184,0.3)');
    
    // Y Axis
    const yAxis = d3.axisLeft(yScale)
        .ticks(6)
        .tickFormat(d => d + 'R');
    
    g.append('g')
        .call(yAxis)
        .selectAll('text')
        .attr('fill', '#94a3b8')
        .attr('font-size', '11px');
    
    // Axis labels
    svg.append('text')
        .attr('x', width / 2)
        .attr('y', height - 8)
        .attr('text-anchor', 'middle')
        .attr('fill', '#64748b')
        .attr('font-size', '11px')
        .text('Time');
    
    svg.append('text')
        .attr('transform', 'rotate(-90)')
        .attr('x', -height / 2)
        .attr('y', 15)
        .attr('text-anchor', 'middle')
        .attr('fill', '#64748b')
        .attr('font-size', '11px')
        .text('MFE (R-Multiple)');
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
    
    // Get today's date in NY Eastern timezone (handles DST automatically)
    const today = new Date();
    const nyFormatter = new Intl.DateTimeFormat('en-CA', { 
        timeZone: 'America/New_York',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
    const todayStr = nyFormatter.format(today); // Returns YYYY-MM-DD format
    
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
                // Highlight today with special styling
                if (dateStr === todayStr) classes += ' calendar-today';
                if (dateStr === AutomatedSignalsUltra.selectedDate) classes += ' selected';
                
                // Show badges for completed (blue) and active (green) trades
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

AutomatedSignalsUltra.selectCalendarDate = async function(dateStr) {
    const dateLabel = document.getElementById('ase-selected-date-label');
    
    // Toggle selection
    if (AutomatedSignalsUltra.selectedDate === dateStr) {
        AutomatedSignalsUltra.selectedDate = null;
        if (dateLabel) dateLabel.textContent = 'Click a day to filter';
        // Reload default data (no date filter)
        await AutomatedSignalsUltra.fetchDashboardData();
    } else {
        AutomatedSignalsUltra.selectedDate = dateStr;
        if (dateLabel) {
            const d = new Date(dateStr + 'T12:00:00');
            dateLabel.textContent = `Showing: ${d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;
        }
        // Fetch data for the selected date
        await AutomatedSignalsUltra.loadDataForDate(dateStr);
    }
    
    AutomatedSignalsUltra.renderCalendar();
    AutomatedSignalsUltra.renderSignalsTable();
};

// Fetch data for a specific date
AutomatedSignalsUltra.loadDataForDate = async function(dateStr) {
    try {
        console.log('[ASE] Loading data for date:', dateStr);
        const resp = await fetch(`/api/automated-signals/dashboard-data?date=${dateStr}`, {
            credentials: 'same-origin'
        });
        if (!resp.ok) {
            console.error('[ASE] Failed to load data for date:', dateStr);
            return;
        }
        const json = await resp.json();
        AutomatedSignalsUltra.data = json;
        console.log('[ASE] Loaded', (json.active_trades?.length || 0) + (json.completed_trades?.length || 0), 'trades for', dateStr);
    } catch (err) {
        console.error('[ASE] Error loading data for date:', err);
    }
};

// ============================================================================
// CANCELLED SIGNALS TAB FUNCTIONS
// ============================================================================

AutomatedSignalsUltra.fetchCancelledSignals = async function() {
    try {
        const resp = await fetch(`/api/automated-signals/cancelled?_=${Date.now()}`, {
            cache: 'no-store',
            headers: {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        });
        const json = await resp.json();
        AutomatedSignalsUltra.renderCancelledSignals(json.cancelled || []);
    } catch (err) {
        console.error("[ASE] Error fetching cancelled signals:", err);
        AutomatedSignalsUltra.renderCancelledSignals([]);
    }
};

AutomatedSignalsUltra.renderCancelledSignals = function(rows) {
    const tbody = document.getElementById('ase-cancelled-tbody');
    const counter = document.getElementById('ase-cancelled-count');
    
    if (!tbody) return;
    
    tbody.innerHTML = "";
    
    if (!rows || rows.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center ultra-muted py-3">No cancelled signals recorded.</td></tr>`;
        if (counter) counter.textContent = "0";
        return;
    }
    
    // Helper to format age
    const fmtAge = (sec) => {
        if (sec == null) return "--";
        const s = Math.floor(sec);
        if (s < 60) return `${s}s`;
        const m = Math.floor(s / 60);
        const rem = s % 60;
        if (m < 60) return `${m}m ${rem}s`;
        const h = Math.floor(m / 60);
        const mm = m % 60;
        return `${h}h ${mm}m`;
    };
    
    rows.forEach(row => {
        const tr = document.createElement('tr');
        
        // Parse timestamp for display
        const ts = row.timestamp ? new Date(row.timestamp) : null;
        const timeStr = ts
            ? ts.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: true,
                timeZone: 'America/New_York'
            })
            : '--:--:--';
        
        const dir = row.direction || "--";
        const session = row.session || "--";
        const reason = "Not confirmed";  // Detailed reasons available via Raw Payload
        const age = fmtAge(row.age_seconds);
        
        // Direction badge styling
        const dirBadgeClass = dir === 'Bullish' ? 'direction-badge-bullish' : 
                              dir === 'Bearish' ? 'direction-badge-bearish' : 'ultra-muted';
        
        tr.innerHTML = `
            <td class="ultra-muted">${timeStr}</td>
            <td><span class="${dirBadgeClass}">${dir}</span></td>
            <td>${session}</td>
            <td class="ultra-muted">${reason}</td>
            <td class="ultra-muted">${age}</td>
            <td class="ultra-text small">${row.trade_id || ''}</td>
        `;
        
        tbody.appendChild(tr);
    });
    
    if (counter) counter.textContent = rows.length.toString();
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
    
    // Wire Tab Switching for Lifecycle Modal
    const chartBtn = document.getElementById('ase-tab-chart-btn');
    const detailsBtn = document.getElementById('ase-tab-details-btn');
    const rawBtn = document.getElementById('ase-tab-rawpay-btn');
    const chartContent = document.getElementById('ase-tab-chart-content');
    const detailsContent = document.getElementById('ase-tab-details-content');
    const rawPanel = document.getElementById('ase-raw-payload-panel');
    const lifecycleChart = document.getElementById('ase-lifecycle-chart');
    
    const setActiveTab = (activeBtn) => {
        [chartBtn, detailsBtn, rawBtn].forEach(btn => {
            if (btn) {
                btn.style.background = btn === activeBtn ? 'rgba(59,130,246,0.3)' : 'rgba(255,255,255,0.1)';
                btn.style.borderColor = btn === activeBtn ? 'rgba(59,130,246,0.4)' : 'rgba(255,255,255,0.2)';
            }
        });
    };
    
    if (chartBtn) {
        chartBtn.addEventListener('click', () => {
            setActiveTab(chartBtn);
            if (lifecycleChart) lifecycleChart.style.display = 'block';
            if (chartContent) chartContent.style.display = 'block';
            if (detailsContent) detailsContent.style.display = 'none';
            if (rawPanel) rawPanel.style.display = 'none';
        });
    }
    
    if (detailsBtn) {
        detailsBtn.addEventListener('click', () => {
            setActiveTab(detailsBtn);
            if (lifecycleChart) lifecycleChart.style.display = 'none';
            if (chartContent) chartContent.style.display = 'none';
            if (detailsContent) detailsContent.style.display = 'block';
            if (rawPanel) rawPanel.style.display = 'none';
        });
    }
    
    if (rawBtn) {
        rawBtn.addEventListener('click', () => {
            setActiveTab(rawBtn);
            if (lifecycleChart) lifecycleChart.style.display = 'none';
            if (chartContent) chartContent.style.display = 'none';
            if (detailsContent) detailsContent.style.display = 'none';
            if (rawPanel) rawPanel.style.display = 'block';
        });
    }
    
    // Wire Copy Payload button
    const copyBtn = document.getElementById('ase-copy-payload-btn');
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            if (!AutomatedSignalsUltra.rawPayload) return;
            const formatted = JSON.stringify(AutomatedSignalsUltra.rawPayload, null, 2);
            navigator.clipboard.writeText(formatted).then(() => {
                copyBtn.textContent = '✔ Copied!';
                setTimeout(() => {
                    copyBtn.textContent = '📋 Copy Payload';
                }, 1200);
            }).catch(() => {
                alert('Failed to copy payload.');
            });
        });
    }
});
