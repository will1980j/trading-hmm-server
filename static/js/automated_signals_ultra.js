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

// Initialize currentMonth to NY timezone current date
// Store as object with year/month to avoid timezone conversion issues
AutomatedSignalsUltra.currentMonth = (() => {
    const now = new Date();
    const nyFormatter = new Intl.DateTimeFormat('en-US', { 
        timeZone: 'America/New_York',
        year: 'numeric',
        month: 'numeric',
        day: 'numeric'
    });
    const parts = nyFormatter.formatToParts(now);
    const year = parseInt(parts.find(p => p.type === 'year').value);
    const month = parseInt(parts.find(p => p.type === 'month').value) - 1; // 0-indexed
    
    // Return a Date object but ensure it represents the NY date
    const d = new Date(year, month, 1);
    return d;
})();
AutomatedSignalsUltra.calendarData = [];
AutomatedSignalsUltra.selectedDate = null;
AutomatedSignalsUltra.rawPayload = null;  // Store raw payload for debug tab
AutomatedSignalsUltra.filters = {
    session: 'ALL',
    direction: 'ALL',
    state: 'ALL',
    searchId: ''
};

// ────────────────
// Backend Echo API
// ────────────────
AutomatedSignalsUltra.echo = {
    enabled: true,     // set to false if you want to hide panel
    lastJson: null
};

AutomatedSignalsUltra.copyEcho = function() {
    if (!AutomatedSignalsUltra.echo.lastJson) return;
    navigator.clipboard.writeText(JSON.stringify(AutomatedSignalsUltra.echo.lastJson, null, 2));
};

document.addEventListener("DOMContentLoaded", () => {
    const copyBtn = document.querySelector("#ase-backend-echo-copy");
    if (copyBtn) copyBtn.onclick = AutomatedSignalsUltra.copyEcho;
});

// ────────────────────
// Signal Integrity API
// ────────────────────
AutomatedSignalsUltra.integrity = {
    enabled: true,
    last: []
};

AutomatedSignalsUltra.loadIntegrity = async function() {
    try {
        const r = await fetch("/api/automated-signals/integrity-v2");
        const j = await r.json();
        AutomatedSignalsUltra.integrity.last = j.issues || [];
        const panel = document.getElementById("ase-integrity-panel");
        const area = document.getElementById("ase-integrity-log");
        if (panel && area) {
            panel.style.display = "block";
            area.textContent = (j.issues || []).length
                ? j.issues.join("\n")
                : "No issues detected.";
        }
    } catch (err) {
        console.error("[INTEGRITY] Error:", err);
    }
};

document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("ase-integrity-refresh");
    if (btn) btn.onclick = AutomatedSignalsUltra.loadIntegrity;
});

// --- GLOBAL TIMEZONE HELPERS ---
AutomatedSignalsUltra.toNY = function(isoString) {
    try {
        if (!isoString) return null;
        const dateUtc = new Date(isoString); // interpreted as UTC
        return dateUtc.toLocaleString("en-US", {
            timeZone: "America/New_York",
            hour12: false
        });
    } catch (err) {
        console.error("[ASE] NY time conversion failed:", err, isoString);
        return isoString;
    }
};

AutomatedSignalsUltra.toNYTime = function(isoString) {
    try {
        const dateUtc = new Date(isoString);
        return dateUtc.toLocaleTimeString("en-US", {
            timeZone: "America/New_York",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
            hour12: false
        });
    } catch (err) {
        return "--:--:--";
    }
};

AutomatedSignalsUltra.toNYDate = function(isoString) {
    try {
        const dateUtc = new Date(isoString);
        return dateUtc.toLocaleDateString("en-US", {
            timeZone: "America/New_York",
            year: "numeric",
            month: "2-digit",
            day: "2-digit"
        });
    } catch (err) {
        return "--/--/----";
    }
};

AutomatedSignalsUltra.toUTC = function(isoString) {
    try {
        if (!isoString) return null;
        const d = new Date(isoString);
        return d.toISOString().replace("T", " ").replace("Z", "");
    } catch (err) {
        console.error("[ASE] Failed UTC convert:", err);
        return isoString;
    }
};

AutomatedSignalsUltra.computeLatencyMs = function(payloadTs, dbTs) {
    try {
        if (!payloadTs || !dbTs) return null;
        const p = new Date(payloadTs);
        const d = new Date(dbTs);
        return d - p; // milliseconds
    } catch {
        return null;
    }
};

AutomatedSignalsUltra.describeLatency = function(ms) {
    if (ms == null) return "";
    if (ms < 0) return `⚠ clock drift (db < payload by ${Math.abs(ms)} ms)`;
    if (ms < 500) return `${ms} ms`;
    if (ms < 2000) return `${(ms/1000).toFixed(2)}s`;
    return `${(ms/1000).toFixed(1)}s`;
};

// Universal NY time converter
AutomatedSignalsUltra.formatSignalDateTime = function(row) {
    // PRIORITY 1: Extract signal time from trade_id (most reliable source)
    // Trade ID format: YYYYMMDD_HHMMSS000_DIRECTION
    if (row && row.trade_id) {
        try {
            const parts = row.trade_id.split('_');
            if (parts.length >= 2) {
                const dateStr = parts[0]; // YYYYMMDD
                const timeStr24 = parts[1].substring(0, 6); // HHMMSS (strip trailing 000)
                
                // Parse date
                const year = dateStr.substring(0, 4);
                const month = parseInt(dateStr.substring(4, 6));
                const day = dateStr.substring(6, 8);
                
                // Parse time
                const hour24 = parseInt(timeStr24.substring(0, 2));
                const minute = parseInt(timeStr24.substring(2, 4));
                
                // Convert to 12-hour format
                const hour12 = hour24 % 12 || 12;
                const ampm = hour24 >= 12 ? "PM" : "AM";
                
                // Format: "Dec 08, 9:39 AM" (signal candle time from trade_id)
                const monthNames = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
                const result = `${monthNames[month-1]} ${day}, ${hour12}:${minute.toString().padStart(2,'0')} ${ampm}`;
                console.log(`[ASE] Parsed ${row.trade_id} → ${result}`);
                return result;
            }
        } catch (e) {
            console.error("[ASE] Failed to parse trade_id timestamp:", row.trade_id, e);
        }
    }
    
    // FALLBACK: Use event_ts or signal_date/signal_time
    const src = row.event_ts || (row.signal_date + "T" + row.signal_time);
    if (!src) return "--";
    
    // Ensure UTC
    const dt = new Date(src + "Z");
    
    // Convert to NY
    const ny = dt.toLocaleString("en-US", {
        timeZone: "America/New_York",
        year: "numeric",
        month: "short",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        hour12: true
    });
    
    return ny;
};

// Legacy wrapper for backward compatibility
AutomatedSignalsUltra.formatDateTime = function(dateStr, timeStr) {
    return AutomatedSignalsUltra.formatSignalDateTime({ signal_date: dateStr, signal_time: timeStr });
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

// Toggle Signal Integrity Monitor panel
document.addEventListener("click", (e) => {
    const t = e.target.closest("#ase-signal-monitor-toggle");
    if (!t) return;
    
    const panel = document.getElementById("ase-signal-monitor-panel");
    const open = panel.style.display !== "none";
    
    panel.style.display = open ? "none" : "block";
    t.textContent = (open ? "▼" : "▲") + " Signal Integrity Monitor";
    
    if (!open) {
        AutomatedSignalsUltra.loadSignalIntegrityMonitor();
    }
});

// Signal Integrity Monitor loader - now accepts optional trade_id to filter
AutomatedSignalsUltra.loadSignalIntegrityMonitor = function (trade_id = null) {
    const panel = document.getElementById("ase-signal-monitor-panel");
    if (!panel) return;
    
    panel.textContent = "Loading…";
    
    fetch("/api/automated-signals/integrity-v2")
        .then(r => r.json())
        .then(data => {
            if (!data || !data.issues) {
                panel.textContent = "No integrity data available.";
                return;
            }
            
            // Format the integrity report
            let issues = data.issues;
            
            // If trade_id provided, filter to just that trade
            if (trade_id) {
                issues = issues.filter(i => i.trade_id === trade_id);
                
                if (issues.length === 0) {
                    panel.textContent = `No integrity data found for trade: ${trade_id}`;
                    return;
                }
            }
            
            if (issues.length === 0) {
                panel.textContent = "✓ All trades healthy - no integrity issues detected.";
                return;
            }
            
            // Build formatted report
            const lines = [];
            issues.forEach(issue => {
                const status = issue.healthy ? "✓" : "✗";
                const failCount = issue.failures ? issue.failures.length : 0;
                
                if (trade_id) {
                    // Single trade view - show more detail
                    lines.push(`Trade: ${issue.trade_id}`);
                    lines.push(`Status: ${status} ${issue.healthy ? 'Healthy' : 'Has Issues'}`);
                    lines.push(`Issues Found: ${failCount}`);
                    lines.push("");
                    
                    if (!issue.healthy && issue.failures) {
                        lines.push("Integrity Failures:");
                        issue.failures.forEach(f => {
                            lines.push(`  • ${f}`);
                        });
                    } else {
                        lines.push("✓ No integrity issues detected for this trade.");
                    }
                } else {
                    // All trades view - compact format
                    lines.push(`${status} ${issue.trade_id} - ${failCount} issue(s)`);
                    
                    if (!issue.healthy && issue.failures) {
                        issue.failures.forEach(f => {
                            lines.push(`  - ${f}`);
                        });
                    }
                }
            });
            
            panel.textContent = lines.join("\n");
        })
        .catch((err) => {
            console.error("[INTEGRITY] Error:", err);
            panel.textContent = "Error loading monitor data.";
        });
};

// ============================================================================
// DIAGNOSIS LOADER - Fetches and displays trade lifecycle diagnosis
// ============================================================================
AutomatedSignalsUltra.loadDiagnosis = async function(tradeId) {
    console.log("[ASE] Loading diagnosis for trade:", tradeId);
    try {
        const res = await fetch(`/api/automated-signals/diagnosis/${tradeId}`, { cache: "no-store" });
        const diag = await res.json();
        
        const setText = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.textContent = val || "";
        };
        
        // Build pipeline map from db_events
        const pipelineEl = document.getElementById("ase-pipeline-map");
        if (pipelineEl && diag.db_events) {
            const events = diag.db_events;
            const lines = [];
            const ok = t => `🟢 ${t}`;
            const warn = t => `🟡 ${t}`;
            const fail = t => `🔴 ${t}`;
            
            const hasEntry = events.some(e => e.event_type === "ENTRY");
            const mfeUpdates = events.filter(e => e.event_type === "MFE_UPDATE");
            const hasExitBe = events.some(e => e.event_type === "EXIT_BE" || e.event_type === "EXIT_BREAK_EVEN");
            const hasExitSl = events.some(e => e.event_type === "EXIT_SL" || e.event_type === "EXIT_STOP_LOSS");
            const hasBeTrigger = events.some(e => e.event_type === "BE_TRIGGERED");
            
            lines.push(hasEntry ? ok("ENTRY Event Present") : fail("Missing ENTRY Event"));
            lines.push(mfeUpdates.length > 0 ? ok(`MFE_UPDATE Events: ${mfeUpdates.length}`) : warn("No MFE_UPDATE Events"));
            if (hasBeTrigger) lines.push(ok("BE_TRIGGERED Event Present"));
            if (hasExitBe || hasExitSl) {
                const arr = [];
                if (hasExitBe) arr.push("EXIT_BE");
                if (hasExitSl) arr.push("EXIT_SL");
                lines.push(ok("Exit Events: " + arr.join(", ")));
            } else {
                lines.push(warn("No Exit Events"));
            }
            lines.push(diag.logs && diag.logs.length > 20 ? ok("Backend Logs Present") : warn("No Backend Logs"));
            
            pipelineEl.textContent = lines.join("\n");
        }
        
        // Raw payload
        const payloadEl = document.getElementById("ase-raw-payload");
        if (payloadEl) {
            if (diag.payload) {
                try {
                    const parsed = typeof diag.payload === 'string' ? JSON.parse(diag.payload) : diag.payload;
                    payloadEl.textContent = JSON.stringify(parsed, null, 2);
                } catch {
                    payloadEl.textContent = diag.payload;
                }
            } else {
                payloadEl.textContent = "No payload available";
            }
        }
        
        if (diag.db_events) {
            const enriched = diag.db_events.map(ev => {
                const utc = AutomatedSignalsUltra.toUTC(ev.timestamp);
                const ny  = AutomatedSignalsUltra.toNY(ev.timestamp);
                const payloadTs = ev.raw_payload && ev.raw_payload.event_timestamp
                    ? ev.raw_payload.event_timestamp
                    : (ev.event_timestamp || null);
                const latency = AutomatedSignalsUltra.computeLatencyMs(payloadTs, ev.timestamp);
                return {
                    ...ev,
                    timestamp_utc: utc,
                    timestamp_ny: ny,
                    payload_timestamp: payloadTs,
                    latency_ms: latency,
                    latency_human: AutomatedSignalsUltra.describeLatency(latency)
                };
            });
            setText("ase-raw-db-events", JSON.stringify(enriched, null, 2));
        } else {
            setText("ase-raw-db-events", "No DB events available.");
        }
        setText("ase-backend-logs", diag.logs || "No logs available");
        if (diag.summary_rows) {
            const pretty = diag.summary_rows.map(r => {
                const utc = AutomatedSignalsUltra.toUTC(r.timestamp);
                const ny  = AutomatedSignalsUltra.toNY(r.timestamp);
                return `${r.timestamp}  (NY: ${ny})  –  ${r.event_type}  –  MFE=${r.mfe} / NoBE=${r.no_be_mfe} / MAE=${r.mae}`;
            }).join("\n");
            setText("ase-lifecycle-summary", pretty);
        } else {
            setText("ase-lifecycle-summary", diag.summary || "No summary available");
        }
        let driftNote = "";
        if (diag.db_events && diag.db_events.length > 0) {
            const drifts = diag.db_events.filter(ev => {
                const payloadTs = ev.raw_payload && ev.raw_payload.event_timestamp
                    ? ev.raw_payload.event_timestamp
                    : (ev.event_timestamp || null);
                if (!payloadTs) return false;
                const diff = AutomatedSignalsUltra.computeLatencyMs(payloadTs, ev.timestamp);
                return diff < -500; // drift > 500 ms backwards
            });
            if (drifts.length > 0) {
                driftNote = `\n⚠ Clock drift detected in ${drifts.length} events (db timestamp earlier than payload timestamp).`;
            }
        }
        setText("ase-diagnosis-report",
            (diag.discrepancy || "No discrepancy analysis available") + driftNote);
        
        // BE / No-BE lifecycle cues (if backend provided them)
        if (diag.be_state || diag.no_be_state || diag.next_exit) {
            const extra = [];
            extra.push("------ BE / No-BE Lifecycle ------");
            if (diag.be_state)    extra.push("BE leg:  " + diag.be_state);
            if (diag.no_be_state) extra.push("No-BE leg: " + diag.no_be_state);
            if (diag.next_exit)   extra.push("Next exit: " + diag.next_exit);
            
            const summaryEl = document.getElementById("ase-lifecycle-summary");
            if (summaryEl) {
                const current = summaryEl.textContent || "";
                summaryEl.textContent = (current ? current + "\n\n" : "") + extra.join("\n");
            }
        }
        
        // --- MAE DIAGNOSIS ---
        if (diag.db_events && diag.db_events.length > 0) {
            let maes = diag.db_events.map(e => parseFloat(e.mae_global_r)).filter(v => !isNaN(v));
            let minMae = Math.min(...maes);
            let maxMae = Math.max(...maes);
            let maeReport = "";
            maeReport += "MAE Range: " + minMae.toFixed(4) + " → " + maxMae.toFixed(4) + "\n";
            if (maxMae > 0) {
                maeReport += "❌ MAE polarity violation detected (positive MAE value).\n";
            }
            const maePanel = document.getElementById("ase-diagnosis-report");
            if (maePanel) {
                maePanel.textContent += "\n" + maeReport;
            }
        }
        
        // Load Stream Monitor Issues
        fetch(`/api/automated-signals/stream-monitor/${tradeId}`)
            .then(r => r.json())
            .then(d => {
                const box = document.getElementById("ase-stream-monitor-report");
                if (!box) return;
                
                if (!d || Object.keys(d).length === 0) {
                    box.textContent = "No stream data available.";
                    return;
                }
                
                let msg = "";
                msg += `Last Event: ${d.last_event_type || "--"}\n`;
                msg += `Last Timestamp: ${d.last_event_ts || "--"}\n`;
                msg += `Last MFE: ${d.last_mfe ?? "--"}\n`;
                msg += `Last MAE: ${d.last_mae ?? "--"}\n`;
                msg += `BE Triggered: ${d.be_triggered ? "YES" : "NO"}\n`;
                msg += `\nIssues (${d.issue_count}):\n`;
                
                if (d.issues && d.issues.length > 0) {
                    msg += d.issues.map(x => "- " + (typeof x === 'string' ? x : x.issue || JSON.stringify(x))).join("\n");
                } else {
                    msg += "None detected.";
                }
                
                box.textContent = msg;
            })
            .catch(() => {
                const box = document.getElementById("ase-stream-monitor-report");
                if (box) box.textContent = "Stream monitor unavailable.";
            });
        
        console.log(`[ASE] Diagnosis loaded for trade ${tradeId}`);
    } catch (err) {
        console.error("[ASE] Diagnosis load failed:", err);
        const pipelineEl = document.getElementById("ase-pipeline-map");
        if (pipelineEl) {
            pipelineEl.textContent = `🔴 Failed to load diagnosis: ${err.message}`;
        }
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
        
        // ─────────────────────────────────────────────
        // PHASE 7 — Timestamp Diagnostics
        // ─────────────────────────────────────────────
        console.group("[TS-DIAG] Timestamp Validation");
        // Raw payload timestamps
        console.log("RAW ACTIVE TRADES:", json.active_trades);
        // Validate each timestamp for parse correctness
        json.active_trades.forEach((t, idx) => {
            const ts = t.event_ts;
            const iso = ts ? (ts.includes("Z") ? ts : ts.replace(" ", "T") + "Z") : null;
            const parsed = iso ? new Date(iso) : null;
            const valid = parsed && !Number.isNaN(parsed.getTime());
            console.log(`ROW ${idx}`, {
                event_ts: t.event_ts,
                entry_ts: t.entry_ts,
                exit_ts: t.exit_ts,
                timestamp_utc: t.timestamp_utc,
                timestamp_ny: t.timestamp_ny,
                parsed_ok: valid,
                parsed_date: parsed,
            });
        });
        // Check sorting results
        console.log("[TS-SORT] Current sort keys:",
            json.active_trades.map(t => t.event_ts));
        // Check human-rendered times in DOM after next paint
        setTimeout(() => {
            console.group("[TS-DIAG] DOM Rendered Timestamps");
            document.querySelectorAll("#ase-signals-tbody tr").forEach((row, idx) => {
                console.log(`DOM ROW ${idx}:`, row.innerText);
            });
            console.groupEnd();
        }, 250);
        console.groupEnd();
        // ─────────────────────────────────────────────
        
        // ─────────────────────────────────────────────
        // BACKEND ECHO PANEL (Collapsed by default)
        // ─────────────────────────────────────────────
        AutomatedSignalsUltra.echo.lastJson = json;
        const echoArea = document.getElementById("ase-backend-echo-content");
        if (AutomatedSignalsUltra.echo.enabled && echoArea) {
            echoArea.textContent = JSON.stringify(json, null, 2);
        }
        // ─────────────────────────────────────────────
        
        // ─────────────────────────────────────────────
        // SIGNAL INTEGRITY CHECK
        // ─────────────────────────────────────────────
        await AutomatedSignalsUltra.loadIntegrity();
        // ─────────────────────────────────────────────
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
            lastEl.textContent = AutomatedSignalsUltra.toNYTime(lastTs);
        } else {
            lastEl.textContent = "--:--:--";
        }
    }
    
    if (sigTodayEl) {
        sigTodayEl.textContent = stats.today_count ?? stats.total_signals ?? 0;
    }
    
    if (activeEl) {
        // Calculate active count based on BE/NoBE status logic
        // A trade is "active" if BE is ACTIVE OR NoBE is ACTIVE
        const activeTrades = AutomatedSignalsUltra.data?.active_trades ?? [];
        const completedTrades = AutomatedSignalsUltra.data?.completed_trades ?? [];
        const allTrades = [...activeTrades, ...completedTrades];
        
        // Count trades where at least one strategy is still active
        const activeCount = allTrades.filter(t => {
            // Determine BE and NoBE status based on event_type
            let beStatus = 'ACTIVE';
            let noBeStatus = 'ACTIVE';
            
            if (t.event_type === 'EXIT_BE') {
                beStatus = 'COMPLETE';  // BE=1 exited at entry
                noBeStatus = 'ACTIVE';  // No BE still running
            } else if (t.event_type === 'EXIT_SL') {
                beStatus = 'COMPLETE';  // Both done
                noBeStatus = 'COMPLETE';
            } else if (t.status === 'COMPLETED') {
                // Fallback for older data without event_type
                beStatus = 'COMPLETE';
                noBeStatus = 'COMPLETE';
            }
            
            // Trade is active if either strategy is still active
            return beStatus === 'ACTIVE' || noBeStatus === 'ACTIVE';
        }).length;
        
        activeEl.textContent = activeCount;
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

// Helper functions to determine BE and No-BE status (matches table rendering logic)
AutomatedSignalsUltra.getBEStatus = function(row) {
    if (row.event_type === 'EXIT_BE') return 'COMPLETE';
    if (row.event_type === 'EXIT_SL') return 'COMPLETE';
    if (row.status === 'COMPLETED') return 'COMPLETE';
    return 'ACTIVE';
};

AutomatedSignalsUltra.getNoBeStatus = function(row) {
    if (row.event_type === 'EXIT_SL') return 'COMPLETE';
    if (row.event_type === 'EXIT_BE') return 'ACTIVE';
    if (row.status === 'COMPLETED') return 'COMPLETE';
    return 'ACTIVE';
};

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
    
    // --- HEALTH INDEX MAP ---
    // Build a quick lookup for integrity issues per trade_id.
    const healthMap = {};
    if (AutomatedSignalsUltra.integrity?.last) {
        for (const issue of AutomatedSignalsUltra.integrity.last) {
            const tid = (issue.trade_id || issue.id || issue).toString();
            if (!healthMap[tid]) healthMap[tid] = [];
            healthMap[tid].push(issue);
        }
    }
    
    // Health scoring logic:
    function getHealthStatus(tradeId) {
        const issues = healthMap[tradeId] || [];
        if (issues.length === 0) return { icon: "🟢", label: "Healthy" };
        
        // If missing MFE_UPDATE OR missing MAE → critical
        if (issues.some(x => x.toString().includes("Missing MFE_UPDATE")
            || x.toString().includes("No MAE")
            || x.toString().includes("Too few lifecycle"))) {
            return { icon: "🔴", label: "Critical" };
        }
        
        // Otherwise warning
        return { icon: "🟡", label: "Warning" };
    }
    
    for (const sig of pending) {
        rows.push({ status: "PENDING", ...sig });
    }
    for (const sig of active) {
        rows.push({ status: "ACTIVE", ...sig });
    }
    for (const sig of completed) {
        rows.push({ status: "COMPLETED", ...sig });
    }
    
    // --- FRONTEND DEDUPE SAFETY NET ---
    // Ensures only one row per trade_id is shown in the dashboard.
    const deduped = {};
    for (const r of rows) {
        deduped[r.trade_id] = r;
    }
    rows = Object.values(deduped);
    // ------------------------------------
    
    // Apply filters
    const f = AutomatedSignalsUltra.filters;
    
    rows = rows.filter(row => {
        if (AutomatedSignalsUltra.selectedDate) {
            const rowDate = row.signal_date
                || (row.event_ts ? row.event_ts.split("T")[0] : null);
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
        
        // State filter: ACTIVE = at least one strategy active, COMPLETED = both strategies complete
        if (f.state !== 'ALL') {
            const beStatus = AutomatedSignalsUltra.getBEStatus(row);
            const noBeStatus = AutomatedSignalsUltra.getNoBeStatus(row);
            
            if (f.state === 'ACTIVE') {
                // Show if No-BE is active (regardless of BE status)
                if (noBeStatus !== 'ACTIVE') return false;
            } else if (f.state === 'COMPLETED') {
                // Show only if both are complete
                if (beStatus !== 'COMPLETE' || noBeStatus !== 'COMPLETE') return false;
            }
        }
        if (f.searchId && row.trade_id && !row.trade_id.toLowerCase().includes(f.searchId)) return false;
        return true;
    });
    
    // Sort rows by timestamp (newest first)
    const parseTs = (row) => {
        if (row.event_ts) {
            // Handle both ISO format (2025-12-06T08:30:00+00:00) and space-separated (2025-12-06 08:30:00)
            let tsStr = row.event_ts.replace(" ", "T");
            // Only add Z if no timezone info present
            if (!tsStr.includes("+") && !tsStr.includes("Z") && !tsStr.match(/[+-]\d{2}:\d{2}$/)) {
                tsStr += "Z";
            }
            return new Date(tsStr).getTime();
        }
        return 0;
    };
    rows.sort((a, b) => parseTs(b) - parseTs(a));
    
    tbody.innerHTML = "";
    
    if (rows.length === 0) {
        tbody.innerHTML = `<tr><td colspan="11" class="text-center ultra-muted py-3">No signals match filters.</td></tr>`;
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
        
        // Helper to format duration (smart units)
        const formatDuration = (diffSec) => {
            const s = Math.max(0, Math.floor(diffSec));
            if (s < 60) {
                return `${s}s`;
            }
            const m = Math.floor(s / 60);
            const remS = s % 60;
            if (m < 60) {
                return `${m}m${remS > 0 ? ` ${remS}s` : ""}`;
            }
            const h = Math.floor(m / 60);
            const remM = m % 60;
            if (h < 48) {
                return `${h}h${remM > 0 ? ` ${remM}m` : ""}`;
            }
            const d = Math.floor(h / 24);
            const remH = h % 24;
            return `${d}d${remH > 0 ? ` ${remH}h` : ""}`;
        };
        
        // Age = time from entry to exit (completed trades) OR entry to now (active trades)
        let ageStr = "--";
        const entryTs = row.entry_ts || row.event_ts;   // event_ts is the ENTRY event for active trades
        const exitTs = row.exit_ts || null;             // completed trades have exit_ts
        const parseTs = (ts) => {
            if (!ts) return null;
            try {
                const iso = ts.includes("Z") ? ts : ts.replace(" ", "T") + "Z";
                const d = new Date(iso);
                return isNaN(d.getTime()) ? null : d;
            } catch (e) {
                console.error("[ASE] Failed to parse timestamp:", ts, e);
                return null;
            }
        };
        const entryDate = parseTs(entryTs);
        const exitDate  = parseTs(exitTs);
        if (entryDate) {
            let diffSeconds;
            if (exitDate) {
                // COMPLETED → use entry → exit
                diffSeconds = Math.max(0, (exitDate - entryDate) / 1000);
            } else {
                // ACTIVE → use entry → NOW
                diffSeconds = Math.max(0, (Date.now() - entryDate.getTime()) / 1000);
            }
            ageStr = formatDuration(diffSeconds);
        }
        
        // Extract signal time from trade_id (most reliable source)
        // Trade ID format: YYYYMMDD_HHMMSS000_DIRECTION
        let timeStr = "--";
        if (row.trade_id) {
            try {
                const parts = row.trade_id.split('_');
                if (parts.length >= 2) {
                    const dateStr = parts[0]; // YYYYMMDD
                    const timeStr24 = parts[1].substring(0, 6); // HHMMSS (strip trailing 000)
                    
                    // Parse date
                    const year = dateStr.substring(0, 4);
                    const month = parseInt(dateStr.substring(4, 6));
                    const day = dateStr.substring(6, 8);
                    
                    // Parse time
                    const hour24 = parseInt(timeStr24.substring(0, 2));
                    const minute = parseInt(timeStr24.substring(2, 4));
                    
                    // Convert to 12-hour format
                    const hour12 = hour24 % 12 || 12;
                    const ampm = hour24 >= 12 ? "PM" : "AM";
                    
                    // Format: "Dec 09, 2025, 10:04 AM"
                    const monthNames = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
                    timeStr = `${monthNames[month-1]} ${day}, ${year}, ${hour12}:${minute.toString().padStart(2,'0')} ${ampm}`;
                }
            } catch (e) {
                console.error("[ASE] Failed to parse trade_id timestamp:", row.trade_id, e);
                timeStr = "--";
            }
        } else if (row.event_ts) {
            // Fallback: use DB event timestamp
            const iso = row.event_ts.includes("Z")
                ? row.event_ts
                : row.event_ts.replace(" ", "T") + "Z";
            const d = new Date(iso);
            timeStr = d.toLocaleString("en-US", {
                timeZone: "America/New_York",
                year: "numeric",
                month: "short",
                day: "2-digit",
                hour: "2-digit",
                minute: "2-digit",
                hour12: true,
            });
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
        
        // MAE (Maximum Adverse Excursion) - worst drawdown in R
        // MAE uses backend field "mae_global_r" (lowercase r)
        const rawMae = row.mae_global_r ?? row.mae_global_R ?? row.mae ?? null;
        const maeVal = rawMae != null
            ? parseFloat(rawMae).toFixed(2)
            : "0.00";
        
        tr.innerHTML = `
            <td><input type="checkbox" class="trade-checkbox trade-row-checkbox" data-trade-id="${row.trade_id}" ${isChecked ? 'checked' : ''}></td>
            <td class="health-cell">${(() => {
                const h = getHealthStatus(row.trade_id);
                return `<span title="${h.label}">${h.icon}</span>`;
            })()}</td>
            <td class="dual-status-cell">
                <span class="dual-status-badge ${beStatusClass}" title="Break-Even at 1R Strategy">BE=1: ${beStatus}</span>
                <span class="dual-status-badge ${noBeStatusClass}" title="No Break-Even Strategy">No-BE: ${noBeStatus}</span>
            </td>
            <td class="ultra-muted">${AutomatedSignalsUltra.formatSignalDateTime(row)}</td>
            <td><span class="${dirBadgeClass}">${dir}</span></td>
            <td class="ultra-muted">${row.session ?? "--"}</td>
            <td>${entry}</td>
            <td>${sl}</td>
            <td><span class="${getMfeClass(mfeBE)}">${beMfeDisplay}</span></td>
            <td><span class="${getMfeClass(mfeNoBE)}">${noBeMfeDisplay}</span></td>
            <td><span class="ultra-badge-red">${maeVal}R</span></td>
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
        
        // Load diagnosis panel data using namespace method
        if (typeof AutomatedSignalsUltra.loadDiagnosis === 'function') {
            AutomatedSignalsUltra.loadDiagnosis(trade_id);
        }
        
        // Load Signal Integrity Monitor for this specific trade
        if (typeof AutomatedSignalsUltra.loadSignalIntegrityMonitor === 'function') {
            AutomatedSignalsUltra.loadSignalIntegrityMonitor(trade_id);
        }
        
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
    const maeVal = detail.mae_global_R != null ? parseFloat(detail.mae_global_R).toFixed(2) + 'R' : 'N/A';
    
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
                <div class="ultra-muted">MAE (Worst)</div>
                <div class="ultra-badge-red">${maeVal}</div>
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
            const ts = ev.timestamp ? AutomatedSignalsUltra.toNYTime(ev.timestamp)
                : '--:--:--';
            const date = ev.timestamp ? AutomatedSignalsUltra.toNYDate(ev.timestamp)
                : '';
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
    const maeMetric = detail.mae_global_R != null ? parseFloat(detail.mae_global_R).toFixed(2) : 'N/A';
    
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
            <div style="background:rgba(239,68,68,0.15); padding:10px; border-radius:8px;">
                <div style="color:#64748b; font-size:11px; text-transform:uppercase;">MAE (Worst)</div>
                <div style="color:#ef4444; font-size:16px; font-weight:600;">${maeMetric}R</div>
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
        tbody.innerHTML = `<tr><td colspan="7" class="text-center ultra-muted py-3">No cancelled signals recorded.</td></tr>`;
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
        
        // Parse timestamp for display using event_ts
        const ts = row.event_ts;
        let timeStr = "--:--:--";
        if (ts) {
            // Handle both ISO format (2025-12-06T08:30:00+00:00) and space-separated (2025-12-06 08:30:00)
            let tsStr = ts.replace(" ", "T");
            // Only add Z if no timezone info present
            if (!tsStr.includes("+") && !tsStr.includes("Z") && !tsStr.match(/[+-]\d{2}:\d{2}$/)) {
                tsStr += "Z";
            }
            const d = new Date(tsStr);
            timeStr = d.toLocaleTimeString("en-US", {
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
                hour12: true,
                timeZone: "America/New_York"
            });
        }
        
        const dir = row.direction || "--";
        const session = row.session || "--";
        const reason = "Not confirmed";  // Detailed reasons available via Raw Payload
        const age = fmtAge(row.age_seconds);
        
        // Direction badge styling
        const dirBadgeClass = dir === 'Bullish' ? 'direction-badge-bullish' : 
                              dir === 'Bearish' ? 'direction-badge-bearish' : 'ultra-muted';
        
        tr.innerHTML = `
            <td><input type="checkbox" class="cancelled-checkbox cancelled-row-checkbox" data-trade-id="${row.trade_id}"></td>
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

// ============================================================================
// TRADE LIFECYCLE DIAGNOSIS FUNCTIONS
// ============================================================================

function copyDiagnosis(id) {
    const el = document.getElementById(id);
    if (!el) return;
    navigator.clipboard.writeText(el.innerText || "");
}

function copyFullDiagnosis() {
    const ids = [
        "ase-pipeline-map",
        "ase-raw-payload",
        "ase-raw-db-events",
        "ase-backend-logs",
        "ase-lifecycle-summary",
        "ase-diagnosis-report"
    ];
    let buf = [];
    ids.forEach(id => {
        const el = document.getElementById(id);
        if (el && el.innerText) {
            buf.push("=== " + id + " ===");
            buf.push(el.innerText);
            buf.push("");
        }
    });
    navigator.clipboard.writeText(buf.join("\n"));
}

// =====================================================
// DIAGNOSIS PANEL - Global helpers for copy buttons
// The main diagnosis loading is handled by AutomatedSignalsUltra.loadDiagnosis()
// which is called from loadTradeDetail() when a trade row is clicked.
// =====================================================

// Expose namespace method globally for any external callers
window.loadTradeDiagnosis = function(tradeId) {
    if (typeof AutomatedSignalsUltra !== 'undefined' && AutomatedSignalsUltra.loadDiagnosis) {
        AutomatedSignalsUltra.loadDiagnosis(tradeId);
    }
};

// =====================================================
// SIMPLE DIAGNOSIS DROPDOWN TOGGLE (FINAL WORKING VERSION)
// =====================================================
document.addEventListener("click", function(e) {
    const header = e.target.closest(".diagnosis-header");
    if (!header) return;
    const section = header.closest(".diagnosis-section");
    if (!section) return;
    const content = section.querySelector(".diagnosis-content");
    if (!content) return;
    // Toggle panel
    const open = content.style.display !== "none" && content.style.display !== "";
    content.style.display = open ? "none" : "block";
});

// =====================================================
// BACKEND DATA ECHO COLLAPSE LOGIC
// =====================================================
document.addEventListener("DOMContentLoaded", () => {
    const header = document.getElementById("ase-backend-echo-header");
    const body = document.getElementById("ase-backend-echo-body");

    if (header && body) {
        header.addEventListener("click", () => {
            const open = body.style.display !== "none";
            body.style.display = open ? "none" : "block";
            header.textContent = (open ? "▶" : "▼") + " Backend Data Echo";
        });
    }
});


// Cancelled signals delete functionality
AutomatedSignalsUltra.selectedCancelledSignals = new Set();

AutomatedSignalsUltra.wireCancelledCheckboxes = function() {
    const selectAll = document.getElementById('ase-select-all-cancelled');
    const deleteBtn = document.getElementById('ase-delete-cancelled-selected');
    
    if (selectAll) {
        selectAll.addEventListener('change', (e) => {
            const checkboxes = document.querySelectorAll('.cancelled-row-checkbox');
            checkboxes.forEach(cb => {
                cb.checked = e.target.checked;
                const tradeId = cb.dataset.tradeId;
                if (e.target.checked) {
                    AutomatedSignalsUltra.selectedCancelledSignals.add(tradeId);
                } else {
                    AutomatedSignalsUltra.selectedCancelledSignals.delete(tradeId);
                }
            });
            AutomatedSignalsUltra.updateCancelledDeleteButton();
        });
    }
    
    if (deleteBtn) {
        deleteBtn.addEventListener('click', () => {
            AutomatedSignalsUltra.deleteCancelledSignals();
        });
    }
    
    // Wire individual checkboxes
    document.addEventListener('change', (e) => {
        if (e.target.classList.contains('cancelled-row-checkbox')) {
            const tradeId = e.target.dataset.tradeId;
            if (e.target.checked) {
                AutomatedSignalsUltra.selectedCancelledSignals.add(tradeId);
            } else {
                AutomatedSignalsUltra.selectedCancelledSignals.delete(tradeId);
            }
            AutomatedSignalsUltra.updateCancelledDeleteButton();
        }
    });
};

AutomatedSignalsUltra.updateCancelledDeleteButton = function() {
    const deleteBtn = document.getElementById('ase-delete-cancelled-selected');
    if (deleteBtn) {
        const count = AutomatedSignalsUltra.selectedCancelledSignals.size;
        deleteBtn.disabled = count === 0;
        deleteBtn.textContent = count > 0 ? `🗑 Delete (${count})` : '🗑 Delete';
    }
};

AutomatedSignalsUltra.deleteCancelledSignals = async function() {
    const tradeIds = Array.from(AutomatedSignalsUltra.selectedCancelledSignals);
    if (tradeIds.length === 0) return;
    
    if (!confirm(`Delete ${tradeIds.length} cancelled signal(s)? This cannot be undone.`)) return;
    
    try {
        const resp = await fetch('/api/automated-signals/bulk-delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ trade_ids: tradeIds })
        });
        
        const result = await resp.json();
        
        if (resp.ok && result.success) {
            console.log(`[ASE] Deleted ${result.deleted_count || tradeIds.length} cancelled signals`);
        } else {
            console.error('[ASE] Delete failed:', result.error || 'Unknown error');
            alert('Delete failed: ' + (result.error || 'Unknown error'));
        }
    } catch (err) {
        console.error('[ASE] Delete error:', err);
        alert('Delete failed: ' + err.message);
    }
    
    AutomatedSignalsUltra.selectedCancelledSignals.clear();
    AutomatedSignalsUltra.updateCancelledDeleteButton();
    AutomatedSignalsUltra.fetchCancelledSignals();
};

// Wire cancelled checkboxes on init
document.addEventListener("DOMContentLoaded", () => {
    AutomatedSignalsUltra.wireCancelledCheckboxes();
});


// ============================================================================
// ALL SIGNALS TAB - Shows every triangle (SIGNAL_CREATED events)
// ============================================================================

AutomatedSignalsUltra.renderAllSignalsTable = async function() {
    try {
        const resp = await fetch('/api/automated-signals/all-signals', { cache: 'no-store' });
        const data = await resp.json();
        
        if (!data.success) {
            console.error('All Signals API error:', data.error);
            return;
        }
        
        const tbody = document.getElementById('ase-all-signals-tbody');
        const counter = document.getElementById('ase-all-signals-count');
        
        if (!tbody) return;
        
        const signals = data.signals || [];
        const summary = data.summary || {};
        
        // Update counter
        if (counter) {
            counter.textContent = summary.total || 0;
        }
        
        if (signals.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" class="text-center ultra-muted py-4">No signals yet</td></tr>';
            return;
        }
        
        // Render table with complete professional formatting
        let html = '';
        for (const signal of signals) {
            const direction = signal.direction || 'UNKNOWN';
            const directionIcon = direction === 'Bullish' || direction === 'LONG' ? '🔵' : '🔴';
            
            // Status badge with better styling
            let statusBadge = '';
            if (signal.status === 'CONFIRMED') {
                statusBadge = '<span class="badge bg-success" style="font-size: 10px; padding: 3px 8px;">✓ CONF</span>';
            } else if (signal.status === 'CANCELLED') {
                statusBadge = '<span class="badge bg-danger" style="font-size: 10px; padding: 3px 8px;">✗ CANC</span>';
            } else {
                statusBadge = '<span class="badge bg-warning text-dark" style="font-size: 10px; padding: 3px 8px;">⏳ PEND</span>';
            }
            
            // HTF badges - bold and readable
            const htf = signal.htf_alignment || {};
            const htfBadge = (bias) => {
                if (!bias || bias === 'Neutral') return '<span style="color: #6b7280; font-size: 18px; font-weight: 900;">—</span>';
                return bias === 'Bullish' ? '<span style="color: #3b82f6; font-size: 18px; font-weight: 900;">▲</span>' : 
                                            '<span style="color: #ef4444; font-size: 18px; font-weight: 900;">▼</span>';
            };
            
            // Calculate risk with color coding
            let riskDisplay = '--';
            if (signal.entry_price && signal.stop_loss) {
                const riskVal = Math.abs(signal.entry_price - signal.stop_loss);
                const riskColor = riskVal > 30 ? '#ef4444' : riskVal > 20 ? '#f59e0b' : '#10b981';
                riskDisplay = `<span style="color: ${riskColor}; font-weight: 500;">${riskVal.toFixed(2)}</span>`;
            }
            
            // Format date as DD-Mon-YY (e.g., 12-Dec-25)
            let dateStr = '--';
            if (signal.signal_date) {
                const d = new Date(signal.signal_date);
                const day = d.getDate();
                const month = d.toLocaleString('en-US', { month: 'short' });
                const year = d.getFullYear().toString().substring(2);
                dateStr = `${day}-${month}-${year}`;
            }
            
            html += `
                <tr>
                    <td><input type="checkbox" class="form-check-input" data-trade-id="${signal.trade_id}" onchange="updateAllSignalsDeleteButton()"></td>
                    <td class="ultra-muted small">${dateStr}</td>
                    <td class="ultra-muted">${signal.signal_time_str || '--'}</td>
                    <td class="text-center">${directionIcon}</td>
                    <td class="ultra-muted small">${signal.session || '--'}</td>
                    <td class="text-center">${statusBadge}</td>
                    <td class="ultra-muted">${signal.entry_price ? signal.entry_price.toFixed(2) : '--'}</td>
                    <td class="ultra-muted">${signal.stop_loss ? signal.stop_loss.toFixed(2) : '--'}</td>
                    <td class="text-center">${riskDisplay}</td>
                    <td class="ultra-muted text-center">${signal.bars_to_confirmation || '--'}</td>
                    <td class="text-center">${htfBadge(htf.daily)}</td>
                    <td class="text-center">${htfBadge(htf.h4)}</td>
                    <td class="text-center">${htfBadge(htf.h1)}</td>
                    <td class="text-center">${htfBadge(htf.m15)}</td>
                    <td class="text-center">${htfBadge(htf.m5)}</td>
                    <td class="ultra-muted small">${signal.trade_id}</td>
                </tr>
            `;
        }
        
        tbody.innerHTML = html;
        
    } catch (error) {
        console.error('Error rendering All Signals:', error);
    }
};

// Load All Signals when tab is shown
document.addEventListener('DOMContentLoaded', function() {
    const allSignalsTab = document.getElementById('all-signals-tab');
    if (allSignalsTab) {
        allSignalsTab.addEventListener('shown.bs.tab', function() {
            AutomatedSignalsUltra.renderAllSignalsTable();
        });
    }
});


// ============================================================================
// CANCELLED SIGNALS TAB
// ============================================================================

AutomatedSignalsUltra.renderCancelledSignalsTable = async function() {
    try {
        const resp = await fetch('/api/automated-signals/cancelled-signals', { cache: 'no-store' });
        const data = await resp.json();
        
        if (!data.success) {
            console.error('Cancelled Signals API error:', data.error);
            return;
        }
        
        const tbody = document.getElementById('ase-cancelled-tbody');
        const counter = document.getElementById('ase-cancelled-count');
        
        if (!tbody) return;
        
        const signals = data.signals || [];
        
        // Update counter
        if (counter) {
            counter.textContent = signals.length;
        }
        
        if (signals.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center ultra-muted py-4">No cancelled signals</td></tr>';
            return;
        }
        
        // Render table
        let html = '';
        for (const signal of signals) {
            const direction = signal.direction || 'UNKNOWN';
            const directionClass = direction === 'Bullish' || direction === 'LONG' ? 'ultra-bullish' : 'ultra-bearish';
            const directionIcon = direction === 'Bullish' || direction === 'LONG' ? '🔵' : '🔴';
            
            const signalTime = signal.signal_time_str || '--';
            const cancelTime = signal.cancelled_time ? new Date(signal.cancelled_time).toLocaleTimeString() : '--';
            const reason = signal.cancel_reason || 'Opposite signal';
            
            html += `
                <tr>
                    <td class="ultra-muted">${signalTime}</td>
                    <td class="${directionClass}">${directionIcon} ${direction}</td>
                    <td class="ultra-muted">${signal.session || '--'}</td>
                    <td class="ultra-muted">${cancelTime}</td>
                    <td class="ultra-muted">${reason}</td>
                    <td class="ultra-muted">${signal.bars_pending || '--'}</td>
                    <td>
                        <button class="btn btn-sm ultra-btn-danger" onclick="AutomatedSignalsUltra.deleteSignal('${signal.trade_id}')">
                            🗑
                        </button>
                    </td>
                </tr>
            `;
        }
        
        tbody.innerHTML = html;
        
    } catch (error) {
        console.error('Error rendering Cancelled Signals:', error);
    }
};

// Load Cancelled Signals when tab is shown
document.addEventListener('DOMContentLoaded', function() {
    const cancelledTab = document.getElementById('cancelled-tab');
    if (cancelledTab) {
        cancelledTab.addEventListener('shown.bs.tab', function() {
            AutomatedSignalsUltra.renderCancelledSignalsTable();
        });
    }
});


// ============================================================================
// BULK DELETE FOR ALL SIGNALS TAB
// ============================================================================

// Select all checkbox for All Signals
document.addEventListener('DOMContentLoaded', () => {
    const selectAllAllSignals = document.getElementById('ase-select-all-all-signals');
    if (selectAllAllSignals) {
        selectAllAllSignals.addEventListener('change', (e) => {
            const checkboxes = document.querySelectorAll('#ase-all-signals-tbody input[type="checkbox"]');
            checkboxes.forEach(cb => cb.checked = e.target.checked);
            updateAllSignalsDeleteButton();
        });
    }
    
    // Delete button for All Signals
    const deleteAllSignalsBtn = document.getElementById('ase-bulk-delete-all-signals-btn');
    if (deleteAllSignalsBtn) {
        deleteAllSignalsBtn.addEventListener('click', async () => {
            const checkboxes = document.querySelectorAll('#ase-all-signals-tbody input[type="checkbox"]:checked');
            const tradeIds = Array.from(checkboxes).map(cb => cb.dataset.tradeId);
            
            if (tradeIds.length === 0) return;
            
            if (!confirm(`Delete ${tradeIds.length} selected signals? This will remove ALL events for these signals.`)) {
                return;
            }
            
            try {
                const response = await fetch('/api/automated-signals/bulk-delete', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({trade_ids: tradeIds})
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert(`✅ Deleted ${result.deleted_count} events for ${tradeIds.length} signals`);
                    // Reload All Signals tab
                    await loadAllSignals();
                } else {
                    alert(`❌ Delete failed: ${result.error}`);
                }
            } catch (error) {
                alert(`❌ Delete error: ${error.message}`);
            }
        });
    }
    
    // Delete button for Cancelled Signals
    const deleteCancelledBtn = document.getElementById('ase-delete-cancelled-selected');
    if (deleteCancelledBtn) {
        deleteCancelledBtn.addEventListener('click', async () => {
            const checkboxes = document.querySelectorAll('#ase-cancelled-tbody input[type="checkbox"]:checked');
            const tradeIds = Array.from(checkboxes).map(cb => cb.dataset.tradeId);
            
            if (tradeIds.length === 0) return;
            
            if (!confirm(`Delete ${tradeIds.length} cancelled signals?`)) {
                return;
            }
            
            try {
                const response = await fetch('/api/automated-signals/bulk-delete', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({trade_ids: tradeIds})
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert(`✅ Deleted ${result.deleted_count} events for ${tradeIds.length} signals`);
                    // Reload Cancelled Signals tab
                    await loadCancelledSignals();
                } else {
                    alert(`❌ Delete failed: ${result.error}`);
                }
            } catch (error) {
                alert(`❌ Delete error: ${error.message}`);
            }
        });
    }
    
    // Select all for Cancelled Signals
    const selectAllCancelled = document.getElementById('ase-select-all-cancelled');
    if (selectAllCancelled) {
        selectAllCancelled.addEventListener('change', (e) => {
            const checkboxes = document.querySelectorAll('#ase-cancelled-tbody input[type="checkbox"]');
            checkboxes.forEach(cb => cb.checked = e.target.checked);
            updateCancelledDeleteButton();
        });
    }
});

function updateAllSignalsDeleteButton() {
    const checkboxes = document.querySelectorAll('#ase-all-signals-tbody input[type="checkbox"]:checked');
    const deleteBtn = document.getElementById('ase-bulk-delete-all-signals-btn');
    const countSpan = document.getElementById('ase-all-signals-selected-count');
    
    if (deleteBtn && countSpan) {
        const count = checkboxes.length;
        countSpan.textContent = count;
        deleteBtn.style.display = count > 0 ? 'inline-block' : 'none';
    }
}

function updateCancelledDeleteButton() {
    const checkboxes = document.querySelectorAll('#ase-cancelled-tbody input[type="checkbox"]:checked');
    const deleteBtn = document.getElementById('ase-delete-cancelled-selected');
    
    if (deleteBtn) {
        deleteBtn.disabled = checkboxes.length === 0;
    }
}


// Update Cancelled Signals table rendering to include checkboxes
AutomatedSignalsUltra.renderCancelledSignalsTable = function(signals) {
    const tbody = document.getElementById('ase-cancelled-tbody');
    if (!tbody) return;
    
    if (!signals || signals.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center ultra-muted py-4">No cancelled signals</td></tr>';
        return;
    }
    
    let html = '';
    signals.forEach(signal => {
        html += `<tr>
            <td><input type="checkbox" class="form-check-input" data-trade-id="${signal.trade_id}" onchange="updateCancelledDeleteButton()"></td>
            <td class="ultra-muted">${signal.signal_time || '--'}</td>
            <td>${signal.direction === 'Bullish' ? '🔵' : '🔴'}</td>
            <td class="ultra-muted">${signal.session || '--'}</td>
            <td class="ultra-muted">${signal.cancellation_reason || 'Opposite signal'}</td>
            <td class="ultra-muted">${signal.age_before_cancel || '--'}</td>
            <td class="ultra-muted small">${signal.trade_id}</td>
        </tr>`;
    });
    
    tbody.innerHTML = html;
};


// ============================================================================
// LOAD ALL SIGNALS TAB
// ============================================================================

async function loadAllSignals() {
    try {
        const response = await fetch('/api/automated-signals/all-signals');
        const data = await response.json();
        
        if (data.success) {
            // Update count badge
            const countBadge = document.getElementById('ase-all-signals-count');
            if (countBadge) {
                countBadge.textContent = data.total || 0;
            }
            
            // Render table
            AutomatedSignalsUltra.renderAllSignalsTable(data.signals || []);
        } else {
            console.error('[ASE] All Signals API error:', data.error);
            const tbody = document.getElementById('ase-all-signals-tbody');
            if (tbody) {
                tbody.innerHTML = '<tr><td colspan="16" class="text-center text-danger py-4">Error loading signals</td></tr>';
            }
        }
    } catch (error) {
        console.error('[ASE] All Signals fetch error:', error);
        const tbody = document.getElementById('ase-all-signals-tbody');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="16" class="text-center text-danger py-4">Failed to load signals</td></tr>';
        }
    }
}

// Load All Signals when tab is clicked
document.addEventListener('DOMContentLoaded', () => {
    const allSignalsTab = document.getElementById('all-signals-tab');
    if (allSignalsTab) {
        allSignalsTab.addEventListener('shown.bs.tab', () => {
            loadAllSignals();
        });
        
        // Load immediately if it's the active tab
        if (allSignalsTab.classList.contains('active')) {
            loadAllSignals();
        }
    }
});
