/* Ultra Premium Automated Signals Hub Controller
SEGMENT 1 of 6
*/

// === Automated Signals Ultra - Trade Notebook State ===
let asNotebookState = {
    isOpen: false,
    tradeId: null,
    data: null,
    loading: false,
    error: null,
    rootEl: null
};

// === Automated Signals Ultra — Trade Timeline Styles ===
function asEnsureTimelineStyles() {
    if (document.getElementById("as-timeline-styles")) return;
    
    const css = `
        .as-timeline {
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 4px 0;
        }
        .as-timeline-step {
            display: flex;
            flex-direction: column;
            align-items: center;
            font-size: 11px;
            color: #ddd;
        }
        .as-timeline-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #555;
        }
        .as-timeline-dot.active {
            background: #00d37d;
        }
        .as-timeline-dot.mfe {
            background: #0aa0ff;
        }
        .as-timeline-dot.exit {
            background: #ff5d5d;
        }
        .as-timeline-bar {
            flex: 1;
            height: 3px;
            background: #444;
        }
        .as-timeline-bar.active {
            background: #00d37d;
        }
        .as-timeline-bar.exit {
            background: #ff5d5d;
        }
    `;
    
    const tag = document.createElement("style");
    tag.id = "as-timeline-styles";
    tag.textContent = css;
    document.head.appendChild(tag);
}

function asEnsureNotebookStyles() {
    if (document.getElementById('as-notebook-styles')) {
        return;
    }
    const style = document.createElement('style');
    style.id = 'as-notebook-styles';
    style.type = 'text/css';
    style.textContent = `
    .as-notebook-overlay {
        position: fixed;
        inset: 0;
        background: rgba(5, 10, 25, 0.88);
        backdrop-filter: blur(8px);
        display: none;
        align-items: stretch;
        justify-content: center;
        z-index: 9999;
    }
    .as-notebook-overlay.as-open {
        display: flex;
    }
    .as-notebook-shell {
        width: 100%;
        max-width: 1200px;
        margin: 32px auto;
        background: #050812;
        border-radius: 16px;
        border: 1px solid rgba(120, 130, 155, 0.35);
        box-shadow: 0 24px 80px rgba(0,0,0,0.65);
        display: flex;
        flex-direction: column;
        max-height: calc(100% - 64px);
        overflow: hidden;
    }
    .as-notebook-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 24px;
        border-bottom: 1px solid rgba(120,130,155,0.4);
        background: linear-gradient(90deg, rgba(10,25,56,0.9), rgba(10,10,24,0.95));
    }
    .as-notebook-title {
        font-size: 18px;
        font-weight: 600;
        color: #f5f7ff;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .as-notebook-subtitle {
        font-size: 13px;
        color: rgba(200, 210, 230, 0.8);
    }
    .as-notebook-close {
        border: none;
        background: transparent;
        color: #9ca3af;
        cursor: pointer;
        font-size: 20px;
        line-height: 1;
        padding: 4px 8px;
        border-radius: 999px;
        transition: background 0.15s ease, color 0.15s ease;
    }
    .as-notebook-close:hover {
        background: rgba(148,163,184,0.2);
        color: #f9fafb;
    }
    .as-notebook-body {
        display: grid;
        grid-template-columns: minmax(0, 2fr) minmax(0, 1.5fr);
        gap: 0;
        flex: 1;
        overflow: hidden;
    }
    .as-notebook-panel {
        padding: 16px 24px;
        overflow-y: auto;
    }
    .as-notebook-panel + .as-notebook-panel {
        border-left: 1px solid rgba(31,41,55,0.8);
    }
    .as-notebook-section {
        margin-bottom: 24px;
    }
    .as-notebook-section-title {
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: rgba(148,163,184,0.95);
        margin-bottom: 8px;
    }
    .as-notebook-kv {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 6px 18px;
        font-size: 13px;
    }
    .as-notebook-kv-label {
        color: rgba(156,163,175,0.95);
        text-transform: uppercase;
        font-size: 11px;
        letter-spacing: 0.08em;
    }
    .as-notebook-kv-value {
        color: #e5e7eb;
        font-weight: 500;
        text-align: right;
        word-break: break-word;
    }
    .as-notebook-timeline {
        margin-top: 8px;
        padding: 8px 0 0;
        border-top: 1px solid rgba(31,41,55,0.6);
    }
    .as-notebook-json {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
        font-size: 11px;
        background: #020617;
        border-radius: 8px;
        padding: 8px 10px;
        color: #e5e7eb;
        max-height: 260px;
        overflow: auto;
        border: 1px solid rgba(31,41,55,0.8);
        white-space: pre;
    }
    .as-notebook-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        background: rgba(15,23,42,0.9);
        border: 1px solid rgba(148,163,184,0.4);
    }
    .as-notebook-pill--active {
        border-color: rgba(34,197,94,0.8);
        color: #bbf7d0;
        background: rgba(22,163,74,0.2);
    }
    .as-notebook-pill--exited {
        border-color: rgba(248,113,113,0.85);
        color: #fecaca;
        background: rgba(127,29,29,0.25);
    }
    .as-notebook-loading {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 32px 0;
        color: #e5e7eb;
        font-size: 14px;
        gap: 10px;
    }
    .as-notebook-spinner {
        width: 18px;
        height: 18px;
        border-radius: 999px;
        border: 2px solid rgba(148,163,184,0.3);
        border-top-color: #38bdf8;
        animation: as-spin 0.7s linear infinite;
    }
    @keyframes as-spin {
        to { transform: rotate(360deg); }
    }
    `;
    document.head.appendChild(style);
}

function asEnsureNotebookContainer() {
    if (asNotebookState.rootEl && document.body.contains(asNotebookState.rootEl)) {
        return;
    }
    const existing = document.getElementById('as-trade-notebook-overlay');
    if (existing) {
        asNotebookState.rootEl = existing;
        return;
    }
    const overlay = document.createElement('div');
    overlay.id = 'as-trade-notebook-overlay';
    overlay.className = 'as-notebook-overlay';
    overlay.innerHTML = `
        <div class="as-notebook-shell" role="dialog" aria-modal="true" aria-label="Trade Notebook">
            <div class="as-notebook-header">
                <div>
                    <div class="as-notebook-title">
                        <span id="as-notebook-title-text">Trade Notebook</span>
                        <span id="as-notebook-lifecycle-pill" class="as-notebook-pill"></span>
                    </div>
                    <div id="as-notebook-subtitle" class="as-notebook-subtitle"></div>
                </div>
                <button type="button" class="as-notebook-close" id="as-notebook-close-btn" aria-label="Close trade notebook">×</button>
            </div>
            <div class="as-notebook-body">
                <div class="as-notebook-panel">
                    <div id="as-notebook-primary"></div>
                </div>
                <div class="as-notebook-panel">
                    <div id="as-notebook-secondary"></div>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);
    asNotebookState.rootEl = overlay;
    
    // Close on backdrop click
    overlay.addEventListener('click', function (evt) {
        if (evt.target === overlay) {
            asCloseTradeNotebook();
        }
    });
    
    // Close button
    const closeBtn = overlay.querySelector('#as-notebook-close-btn');
    if (closeBtn) {
        closeBtn.addEventListener('click', function () {
            asCloseTradeNotebook();
        });
    }
}

function asFormatValue(value) {
    if (value === null || value === undefined || value === '') {
        return '—';
    }
    if (typeof value === 'number') {
        return Number.isFinite(value) ? value.toString() : '—';
    }
    return String(value);
}

/**
 * Render the trade notebook content from detail JSON.
 * This MUST NOT assume any field exists. Always guard with `&&` and fallback to "—".
 */
function asRenderNotebookContent(detail) {
    if (!asNotebookState.rootEl) return;
    
    const primary = asNotebookState.rootEl.querySelector('#as-notebook-primary');
    const secondary = asNotebookState.rootEl.querySelector('#as-notebook-secondary');
    const titleEl = asNotebookState.rootEl.querySelector('#as-notebook-title-text');
    const subtitleEl = asNotebookState.rootEl.querySelector('#as-notebook-subtitle');
    const pillEl = asNotebookState.rootEl.querySelector('#as-notebook-lifecycle-pill');
    
    if (!primary || !secondary || !titleEl || !subtitleEl || !pillEl) {
        return;
    }
    
    // Basic identity fields - all optional, no assumptions
    const tradeId = detail.trade_id || detail.tradeId || detail.id || asNotebookState.tradeId || 'Unknown Trade';
    const direction = detail.direction || detail.bias || detail.side || '—';
    const session = detail.session || '—';
    const state = (detail.lifecycle_state || detail.trade_status || detail.status || '').toString().toUpperCase() || 'UNKNOWN';
    const lifecycleSeq = typeof detail.lifecycle_seq === 'number' ? detail.lifecycle_seq : null;
    const mfeBe = (typeof detail.be_mfe === 'number') ? detail.be_mfe : (typeof detail.mfe_be === 'number' ? detail.mfe_be : null);
    const mfeNoBe = (typeof detail.no_be_mfe === 'number' ? detail.no_be_mfe : (typeof detail.mfe_none === 'number' ? detail.mfe_none : (typeof detail.mfe === 'number' ? detail.mfe : null)));
    const entryPrice = detail.entry_price || detail.entry || null;
    const stopLoss = detail.stop_loss || detail.sl_price || null;
    const exitPrice = detail.exit_price || detail.resolution_price || null;
    
    titleEl.textContent = `Trade ${tradeId}`;
    const dirLabel = direction && direction !== '—' ? direction.toUpperCase() : 'N/A';
    const sessionLabel = session !== '—' ? `• ${session}` : '';
    subtitleEl.textContent = `${dirLabel} ${sessionLabel}`.trim();
    
    // Lifecycle pill
    let pillClass = 'as-notebook-pill';
    let pillText = 'LIFECYCLE UNKNOWN';
    if (state === 'ACTIVE') {
        pillClass += ' as-notebook-pill--active';
        pillText = 'ACTIVE';
    } else if (state === 'EXITED' || state.indexOf('EXIT') === 0) {
        pillClass += ' as-notebook-pill--exited';
        pillText = state;
    } else if (state === 'PENDING' || state === 'PENDING_CONFIRMATION') {
        pillText = 'PENDING';
    }
    if (lifecycleSeq !== null) {
        pillText += ` · #${lifecycleSeq}`;
    }
    pillEl.className = pillClass;
    pillEl.setAttribute && pillEl.setAttribute('data-lifecycle-state', state);
    pillEl.textContent = pillText;
    
    // Primary panel: core metrics & lifecycle timeline
    let primaryHtml = '';
    primaryHtml += `
        <div class="as-notebook-section">
            <div class="as-notebook-section-title">Snapshot</div>
            <div class="as-notebook-kv">
                <div>
                    <div class="as-notebook-kv-label">Direction</div>
                    <div class="as-notebook-kv-value">${asFormatValue(dirLabel)}</div>
                </div>
                <div>
                    <div class="as-notebook-kv-label">Session</div>
                    <div class="as-notebook-kv-value">${asFormatValue(session)}</div>
                </div>
                <div>
                    <div class="as-notebook-kv-label">Entry</div>
                    <div class="as-notebook-kv-value">${asFormatValue(entryPrice)}</div>
                </div>
                <div>
                    <div class="as-notebook-kv-label">Stop Loss</div>
                    <div class="as-notebook-kv-value">${asFormatValue(stopLoss)}</div>
                </div>
                <div>
                    <div class="as-notebook-kv-label">Exit Price</div>
                    <div class="as-notebook-kv-value">${asFormatValue(exitPrice)}</div>
                </div>
                <div>
                    <div class="as-notebook-kv-label">MFE (No BE)</div>
                    <div class="as-notebook-kv-value">${mfeNoBe !== null ? mfeNoBe.toFixed(2) + 'R' : '—'}</div>
                </div>
                <div>
                    <div class="as-notebook-kv-label">MFE (After BE)</div>
                    <div class="as-notebook-kv-value">${mfeBe !== null ? mfeBe.toFixed(2) + 'R' : '—'}</div>
                </div>
                <div>
                    <div class="as-notebook-kv-label">Lifecycle State</div>
                    <div class="as-notebook-kv-value">${asFormatValue(state)}</div>
                </div>
            </div>
        </div>
    `;
    
    // Timeline: prefer backend-provided data, fall back to existing timeline builder when safe
    primaryHtml += `<div class="as-notebook-section"><div class="as-notebook-section-title">Lifecycle Timeline</div><div class="as-notebook-timeline" id="as-notebook-timeline"></div></div>`;
    
    primary.innerHTML = primaryHtml;
    
    // If a backend timeline array is provided, render it; otherwise reuse asBuildTimeline if available
    (function renderTimeline() {
        const timelineHost = primary.querySelector('#as-notebook-timeline');
        if (!timelineHost) return;
        
        // If backend provided a structured timeline, render it
        const timelineEvents = Array.isArray(detail.timeline) ? detail.timeline : (Array.isArray(detail.events) ? detail.events : null);
        if (timelineEvents && timelineEvents.length) {
            const items = timelineEvents.map(function(ev, idx) {
                const label = asFormatValue(ev.label || ev.event_type || ev.type || `Step ${idx + 1}`);
                const at = ev.timestamp || ev.time || ev.at || null;
                const atStr = at ? asFormatValue(at) : '';
                const state = (ev.lifecycle_state || ev.state || '').toString().toUpperCase();
                const isExit = state.indexOf('EXIT') === 0 || (ev.type === 'EXIT' || ev.event_type === 'EXIT');
                const isEntry = (ev.type === 'ENTRY' || ev.event_type === 'ENTRY' || state === 'ENTRY');
                
                const baseCls = 'as-timeline-chip';
                let colorCls = 'as-timeline-chip--neutral';
                if (isEntry) colorCls = 'as-timeline-chip--entry';
                else if (isExit) colorCls = 'as-timeline-chip--exit';
                else if (state === 'ACTIVE' || state === 'MFE_UPDATE') colorCls = 'as-timeline-chip--active';
                
                return `
                    <div class="as-timeline-item">
                        <div class="${baseCls} ${colorCls}">
                            <span class="as-timeline-dot"></span>
                            <span class="as-timeline-label">${label}</span>
                            ${atStr ? `<span class="as-timeline-meta">${atStr}</span>` : ''}
                        </div>
                    </div>
                `;
            }).join('');
            
            timelineHost.innerHTML = `
                <div class="as-timeline">
                    ${items}
                </div>
            `;
            return;
        }
        
        // Fallback: if we have a summary trade row and asBuildTimeline exists, reuse it
        try {
            if (typeof asBuildTimeline === 'function' && detail.summary) {
                timelineHost.innerHTML = asBuildTimeline(detail.summary);
            } else if (typeof asBuildTimeline === 'function') {
                timelineHost.innerHTML = asBuildTimeline(detail);
            } else {
                timelineHost.textContent = 'Lifecycle timeline will appear here when available.';
            }
        } catch (timelineErr) {
            console.error('Error rendering notebook timeline', timelineErr);
            timelineHost.textContent = 'Timeline unavailable (see console for details).';
        }
    })();
    
    // Secondary panel: raw JSON + any extra sections
    let secondaryHtml = '';
    
    // Outcome / notes if present
    const outcome = detail.outcome || detail.resolution_type || detail.completion_reason || null;
    const notes = detail.notes || detail.comment || detail.analysis || null;
    if (outcome || notes) {
        secondaryHtml += `<div class="as-notebook-section"><div class="as-notebook-section-title">Outcome & Notes</div>`;
        secondaryHtml += `<div class="as-notebook-kv">`;
        secondaryHtml += `
            <div>
                <div class="as-notebook-kv-label">Outcome</div>
                <div class="as-notebook-kv-value">${asFormatValue(outcome)}</div>
            </div>
        `;
        secondaryHtml += `
            <div>
                <div class="as-notebook-kv-label">Notes</div>
                <div class="as-notebook-kv-value">${asFormatValue(notes)}</div>
            </div>
        `;
        secondaryHtml += `</div></div>`;
    }
    
    // Raw JSON (debug/forensics)
    secondaryHtml += `
        <div class="as-notebook-section">
            <div class="as-notebook-section-title">Raw Event Payload</div>
            <pre class="as-notebook-json">${asFormatValue(JSON.stringify(detail, null, 2))}</pre>
        </div>
    `;
    
    secondary.innerHTML = secondaryHtml;
}

function asShowNotebookOverlay() {
    if (!asNotebookState.rootEl) return;
    asNotebookState.rootEl.classList.add('as-open');
    asNotebookState.isOpen = true;
}

function asHideNotebookOverlay() {
    if (!asNotebookState.rootEl) return;
    asNotebookState.rootEl.classList.remove('as-open');
    asNotebookState.isOpen = false;
}

async function asOpenTradeNotebook(tradeId) {
    if (!tradeId) {
        console.warn('asOpenTradeNotebook: missing tradeId');
        return;
    }
    
    asEnsureNotebookStyles();
    asEnsureNotebookContainer();
    asShowNotebookOverlay();
    
    asNotebookState.tradeId = tradeId;
    asNotebookState.loading = true;
    asNotebookState.error = null;
    asNotebookState.data = null;
    
    const primary = asNotebookState.rootEl && asNotebookState.rootEl.querySelector('#as-notebook-primary');
    const secondary = asNotebookState.rootEl && asNotebookState.rootEl.querySelector('#as-notebook-secondary');
    const titleEl = asNotebookState.rootEl && asNotebookState.rootEl.querySelector('#as-notebook-title-text');
    const subtitleEl = asNotebookState.rootEl && asNotebookState.rootEl.querySelector('#as-notebook-subtitle');
    const pillEl = asNotebookState.rootEl && asNotebookState.rootEl.querySelector('#as-notebook-lifecycle-pill');
    
    if (primary) {
        primary.innerHTML = `
            <div class="as-notebook-loading">
                <div class="as-notebook-spinner"></div>
                <div>Loading trade details…</div>
            </div>
        `;
    }
    if (secondary) {
        secondary.innerHTML = '';
    }
    if (titleEl) {
        titleEl.textContent = `Trade ${tradeId}`;
    }
    if (subtitleEl) {
        subtitleEl.textContent = 'Fetching full lifecycle and metrics…';
    }
    if (pillEl) {
        pillEl.className = 'as-notebook-pill';
        pillEl.textContent = 'LOADING…';
    }
    
    try {
        const resp = await fetch(`/api/automated-signals/trade/${encodeURIComponent(tradeId)}`, {
            method: 'GET',
            credentials: 'same-origin',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!resp.ok) {
            const text = await resp.text();
            asNotebookState.loading = false;
            asNotebookState.error = `HTTP ${resp.status}: ${text || 'Unknown error'}`;
            if (primary) {
                primary.innerHTML = `
                    <div class="as-notebook-loading">
                        <span>Unable to load trade details.</span>
                        <span style="opacity:0.7;">${escapeHtml(asNotebookState.error)}</span>
                    </div>
                `;
            }
            if (pillEl) {
                pillEl.className = 'as-notebook-pill';
                pillEl.textContent = 'ERROR';
            }
            return;
        }
        
        let detail = null;
        try {
            detail = await resp.json();
        } catch (parseErr) {
            asNotebookState.loading = false;
            asNotebookState.error = 'Failed to parse response JSON';
            if (primary) {
                primary.innerHTML = `
                    <div class="as-notebook-loading">
                        <span>Unable to parse trade detail response.</span>
                    </div>
                    <pre class="as-notebook-json">${escapeHtml(String(parseErr))}</pre>
                `;
            }
            if (pillEl) {
                pillEl.className = 'as-notebook-pill';
                pillEl.textContent = 'ERROR';
            }
            return;
        }
        
        asNotebookState.loading = false;
        asNotebookState.data = detail;
        asRenderNotebookContent(detail);
    } catch (err) {
        asNotebookState.loading = false;
        asNotebookState.error = String(err);
        if (primary) {
            primary.innerHTML = `
                <div class="as-notebook-loading">
                    <span>Connection error while loading trade details.</span>
                    <span style="opacity:0.7;">${escapeHtml(String(err))}</span>
                </div>
            `;
        }
        if (pillEl) {
            pillEl.className = 'as-notebook-pill';
            pillEl.textContent = 'ERROR';
        }
        console.error('asOpenTradeNotebook error', err);
    }
}

function asCloseTradeNotebook() {
    asNotebookState.isOpen = false;
    asNotebookState.tradeId = null;
    asNotebookState.data = null;
    asNotebookState.loading = false;
    asNotebookState.error = null;
    asHideNotebookOverlay();
}

// Simple HTML escaper for debug output
function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

const AS = {
    state: {
        trades: [],
        filteredTrades: [],
        calendar: [],
        selectedDate: null,
        selectedTrades: new Set(),
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
        // LIFECYCLE PATCH: Filter to only ENTRY or EXIT_* events (no MFE_UPDATE rows)
        trades = trades.filter(t => {
            const evt = (t.event_type || '').toString().toUpperCase();
            return evt === 'ENTRY' || evt.startsWith('EXIT_');
        });
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

// Format lifecycle state for display (LIFECYCLE PATCH)
function formatLifecycleState(trade) {
    const rawState = (trade.lifecycle_state || '').toString().trim().toUpperCase();
    let state;
    if (rawState === 'ACTIVE' || rawState === 'EXITED') {
        state = rawState;
    } else {
        // Fallback based on event_type if lifecycle_state is missing for older rows
        const evt = (trade.event_type || '').toString().toUpperCase();
        if (evt.startsWith('EXIT_')) {
            state = 'EXITED';
        } else if (evt === 'ENTRY' || evt === 'MFE_UPDATE' || evt === 'BE_TRIGGERED') {
            state = 'ACTIVE';
        } else {
            state = 'UNKNOWN';
        }
    }
    const seq = (typeof trade.lifecycle_seq === 'number' && !isNaN(trade.lifecycle_seq))
        ? `#${trade.lifecycle_seq}`
        : '';
    // Example: "ACTIVE · #3" or just "ACTIVE"
    return seq ? `${state} · ${seq}` : state;
}

// ANIMATION PATCH: Inject lifecycle animation CSS
function asEnsureLifecycleAnimationStyles() {
    var styleId = 'automated-signals-lifecycle-animations';
    if (document.getElementById(styleId)) {
        return;
    }
    var style = document.createElement('style');
    style.id = styleId;
    style.type = 'text/css';
    style.textContent = `
        .as-row-anim-entry {
            animation: as-entry-flash 0.6s ease-out;
        }
        .as-row-anim-mfe {
            animation: as-mfe-pulse 0.6s ease-out;
        }
        .as-row-anim-exit {
            animation: as-exit-fade 0.7s ease-out forwards;
        }
        
        @keyframes as-entry-flash {
            0%   { box-shadow: 0 0 0 rgba(0, 255, 128, 0); background-color: inherit; }
            20%  { box-shadow: 0 0 12px rgba(0, 255, 128, 0.7); background-color: rgba(0, 255, 128, 0.08); }
            100% { box-shadow: 0 0 0 rgba(0, 255, 128, 0); background-color: inherit; }
        }
        
        @keyframes as-mfe-pulse {
            0%   { transform: scale(1); box-shadow: 0 0 0 rgba(0, 192, 255, 0); }
            40%  { transform: scale(1.01); box-shadow: 0 0 8px rgba(0, 192, 255, 0.5); }
            100% { transform: scale(1); box-shadow: 0 0 0 rgba(0, 192, 255, 0); }
        }
        
        @keyframes as-exit-fade {
            0%   { opacity: 1; transform: translateY(0); }
            40%  { opacity: 0.7; transform: translateY(-2px); }
            100% { opacity: 0.2; transform: translateY(-4px); }
        }
    `;
    document.head.appendChild(style);
}

// ANIMATION PATCH: Apply lifecycle animation to a trade row
function asApplyLifecycleAnimation(eventType, tradeId) {
    try {
        if (!tradeId) return;
        var row = document.querySelector('[data-trade-id="' + tradeId + '"]');
        if (!row) return;
        
        // Decide which class to apply based on event type
        var cls;
        var t = (eventType || '').toUpperCase();
        if (t === 'ENTRY') {
            cls = 'as-row-anim-entry';
        } else if (t === 'MFE_UPDATE') {
            cls = 'as-row-anim-mfe';
        } else if (t.indexOf('EXIT') === 0) {
            cls = 'as-row-anim-exit';
        } else {
            return;
        }
        
        // Remove any existing animation classes first
        row.classList.remove('as-row-anim-entry', 'as-row-anim-mfe', 'as-row-anim-exit');
        
        // Force reflow to restart animation if the same class is re-applied
        // eslint-disable-next-line no-unused-expressions
        void row.offsetWidth;
        
        row.classList.add(cls);
        
        // Clean up the class after animation ends
        window.requestAnimationFrame(function () {
            setTimeout(function () {
                if (row && row.classList) {
                    row.classList.remove(cls);
                }
            }, 700);
        });
    } catch (err) {
        // Do not throw; just log minimally without breaking flow
        console.warn('asApplyLifecycleAnimation error:', err && err.message ? err.message : err);
    }
}

// TIMELINE PATCH: Build timeline component for a trade
function asBuildTimeline(trade) {
    const seq = trade.lifecycle_seq || 1;
    const state = (trade.lifecycle_state || '').toUpperCase();
    
    const steps = [];
    
    // Entry dot always present
    steps.push(`<div class="as-timeline-step">
                    <div class="as-timeline-dot active"></div>
                    <div>ENTRY</div>
                </div>`);
    
    // MFE dots (sequence 2 to N-1)
    if (seq > 2 && state !== 'EXITED') {
        const mfeCount = seq - 1;
        for (let i = 0; i < mfeCount - 1; i++) {
            steps.push(`<div class="as-timeline-bar active"></div>`);
            steps.push(`<div class="as-timeline-step">
                            <div class="as-timeline-dot mfe"></div>
                            <div>MFE</div>
                        </div>`);
        }
    }
    
    // EXIT dot (final)
    if (state === 'EXITED') {
        steps.push(`<div class="as-timeline-bar exit"></div>`);
        steps.push(`<div class="as-timeline-step">
                        <div class="as-timeline-dot exit"></div>
                        <div>EXIT</div>
                    </div>`);
    }
    
    return `<div class="as-timeline">${steps.join("")}</div>`;
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
        
        // PATCH 4C: Check if trade is selected
        const isSelected = AS.state.selectedTrades.has(t.trade_id);
        
        // FIX 2: Correct combined MFE logic
        const mfeCombined = Math.max(
            Number(t.be_mfe_R ?? -Infinity),
            Number(t.no_be_mfe_R ?? -Infinity)
        );
        
        // PATCH 3B PART 1: Fix time column
        const timeStr = t.time_et
            ? t.time_et
            : (t.last_event_time
                ? new Date(t.last_event_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                : '');
        // Direction pill
        const dirPill =
            t.direction === 'Bullish'
                ? '<span class="pill pill-long">LONG</span>'
                : '<span class="pill pill-short">SHORT</span>';
        // LIFECYCLE PATCH: Lifecycle state badge
        const lifecycleLabel = formatLifecycleState(t);
        const lifecycleClass = lifecycleLabel.startsWith('ACTIVE')
            ? 'pill pill-active'
            : lifecycleLabel.startsWith('EXITED')
            ? 'pill pill-completed'
            : 'pill pill-cancelled';
        const lifecyclePill = `<span class="${lifecycleClass}">${lifecycleLabel}</span>`;
        // Session pill
        const sessionPill = `<span class="pill pill-session">${t.session}</span>`;
        
        // PATCH 3B PART 2: Comprehensive normalization
        // Normalize setup and strength
        const setupObj = t.setup || {};
        const setupName = setupObj.id ||
            setupObj.setup_id ||
            (setupObj.setup_family || setupObj.family || '') +
            (setupObj.setup_variant || setupObj.variant
                ? ' · ' + (setupObj.setup_variant || setupObj.variant)
                : '');
        const strength = typeof setupObj.signal_strength === 'number'
            ? setupObj.signal_strength
            : null;
        
        // Normalize prices
        const entry = t.entry_price != null ? Number(t.entry_price) : null;
        const exit = t.exit_price != null ? Number(t.exit_price) : null;
        
        // Combined MFE logic
        const beMfe = t.be_mfe_R != null ? Number(t.be_mfe_R) : null;
        const noBeMfe = t.no_be_mfe_R != null ? Number(t.no_be_mfe_R) : null;
        const finalMfe = t.final_mfe_R != null ? Number(t.final_mfe_R) : null;
        const currentMfe = (function() {
            const vals = [beMfe, noBeMfe].filter(v => typeof v === 'number' && !Number.isNaN(v));
            if (!vals.length) return null;
            return Math.max.apply(null, vals);
        })();
        
        const strengthFill = strength != null
            ? `<div class="as-strength-fill" style="width:${Math.min(100, Math.max(0, strength))}%;"></div>`
            : '';
        // Build row - PATCH 4C: Add checkbox as first column, LIFECYCLE PATCH: Use lifecycle pill
        tr.innerHTML = `
            <td><input type="checkbox" class="as-select-trade" data-id="${t.trade_id}" ${isSelected ? 'checked' : ''}></td>
            <td>${timeStr}</td>
            <td>${dirPill}</td>
            <td>${sessionPill}</td>
            <td>${lifecyclePill}</td>
            <td>${setupName || ''}</td>
            <td><div class="as-strength-bar">${strengthFill}</div></td>
            <td>${fmtR(currentMfe)}</td>
            <td>${fmtR(noBeMfe)}</td>
            <td>${fmtR(finalMfe)}</td>
            <td>${entry != null ? entry.toFixed(2) : ''}</td>
            <td>${exit != null ? exit.toFixed(2) : ''}</td>
        `;
        // Click handler for details modal - but not on checkbox
        tr.onclick = (e) => {
            if (e.target.type !== 'checkbox') {
                asOpenTradeDetail(t.trade_id);
            }
        };
        tbody.appendChild(tr);
        
        // Attach click handler to open Trade Notebook (full-screen modal)
        (function attachNotebookHandler(r, trade) {
            try {
                const tradeId = trade.trade_id || trade.tradeId || trade.id || r.getAttribute('data-trade-id');
                if (!tradeId) {
                    return;
                }
                r.style.cursor = 'pointer';
                r.addEventListener('click', function (evt) {
                    // Avoid interfering with buttons/links inside the row
                    const target = evt.target;
                    if (target && (target.closest('button') || target.closest('a') || target.closest('[data-as-ignore-click="true"]') || target.type === 'checkbox')) {
                        return;
                    }
                    asOpenTradeNotebook(tradeId);
                });
            } catch (err) {
                console.warn('Failed to attach Trade Notebook click handler', err);
            }
        })(tr, t);
        
        // TIMELINE PATCH: Add timeline row
        const timelineHtml = asBuildTimeline(t);
        const timelineRow = document.createElement('tr');
        timelineRow.className = 'as-timeline-row';
        timelineRow.innerHTML = `<td colspan="12">${timelineHtml}</td>`;
        tbody.appendChild(timelineRow);
    });
    
    // PATCH 4C PART 3: Wire up checkbox event handlers
    document.querySelectorAll('.as-select-trade').forEach(cb => {
        cb.addEventListener('change', e => {
            const id = e.target.dataset.id;
            if (e.target.checked) {
                AS.state.selectedTrades.add(id);
            } else {
                AS.state.selectedTrades.delete(id);
            }
        });
    });
    
    // PATCH 4C: Master checkbox handler
    const master = document.querySelector('#as-select-all-checkbox');
    if (master) {
        master.checked = false;
        master.addEventListener('change', e => {
            const checked = e.target.checked;
            AS.state.selectedTrades.clear();
            document.querySelectorAll('.as-select-trade').forEach(cb => {
                cb.checked = checked;
                if (checked) AS.state.selectedTrades.add(cb.dataset.id);
            });
        });
    }
}

// Update summary cards
function asUpdateSummary() {
    const trades = AS.state.filteredTrades;
    const count = trades.length;
    // LIFECYCLE PATCH: Use lifecycle_state or event_type to determine completed trades
    const completed = trades.filter(t => {
        const lifecycleState = (t.lifecycle_state || '').toString().toUpperCase();
        const eventType = (t.event_type || '').toString().toUpperCase();
        return lifecycleState === 'EXITED' || eventType.startsWith('EXIT_') || t.status === 'COMPLETED';
    });
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
        // PATCH 3B PART 4: Shorter chart labels
        const timeStr = ts
            ? new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            : `E${index + 1}`;
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
                    ticks: { maxRotation: 45, autoSkip: true, maxTicksLimit: 8 },
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
    
    // PATCH 4C PART 4: Delete Selected button
    const deleteBtn = document.getElementById('as-delete-selected-btn');
    if (deleteBtn) {
        deleteBtn.onclick = async () => {
            if (AS.state.selectedTrades.size === 0) {
                alert("No trades selected.");
                return;
            }
            if (!confirm(`Delete ${AS.state.selectedTrades.size} trades? This cannot be undone.`)) {
                return;
            }
            const trade_ids = Array.from(AS.state.selectedTrades);
            try {
                const resp = await fetch('/api/automated-signals/delete-trades', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ trade_ids })
                });
                const data = await resp.json();
                if (!data.success) throw new Error(data.error);
                alert(`Deleted ${data.deleted} records.`);
                AS.state.selectedTrades.clear();
                await asFetchHubData();
                asApplyFilters();
            } catch (err) {
                console.error("Bulk delete failed:", err);
                alert("Bulk delete failed. Check console.");
            }
        };
    }

    // PATCH 5C: Purge Legacy Trades button
    const purgeBtn = document.querySelector('#as-purge-ghosts-btn');
    if (purgeBtn) {
        purgeBtn.addEventListener('click', async () => {
            if (!confirm('This will purge legacy/malformed trades (trade_ids with commas or null). Continue?')) {
                return;
            }
            try {
                const resp = await fetch('/api/automated-signals/purge-ghosts', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                const data = await resp.json();
                if (!data.success) {
                    console.error('Ghost purge failed:', data.error);
                    alert('Ghost purge failed: ' + data.error);
                    return;
                }
                alert(`Ghost purge complete. Deleted ${data.deleted} rows.`);
                AS.state.selectedTrades.clear();
                await asFetchHubData();
                asApplyFilters();
            } catch (err) {
                console.error('Ghost purge request error:', err);
                alert('Ghost purge request error. Check console.');
            }
        });
    }
}

function asInitLifecycleWebSocketStream() {
    try {
        // Reuse existing global socket if available
        var sock = window.socket || window.asSocket || window.tradingSocket || null;
        if (!sock || typeof sock.on !== 'function') {
            console.warn('[AS ULTRA] lifecycle WS: no global socket available, skipping stream init');
            return;
        }
        // Avoid double-binding
        if (sock.__asLifecycleStreamBound) {
            return;
        }
        sock.__asLifecycleStreamBound = true;
        sock.on('trade_lifecycle', function (payload) {
            try {
                if (!payload || !payload.trade_id || !payload.event_type) {
                    return;
                }
                var tradeId = payload.trade_id;
                var eventType = payload.event_type;
                // 1) Apply row animation (already implemented)
                if (typeof asApplyLifecycleAnimation === 'function') {
                    asApplyLifecycleAnimation(eventType, tradeId);
                }
                // 2) Optionally trigger a debounced refresh so data stays accurate
                if (typeof asScheduleLifecycleRefresh === 'function') {
                    asScheduleLifecycleRefresh();
                }
            } catch (innerErr) {
                console.error('[AS ULTRA] lifecycle WS handler error', innerErr);
            }
        });
        console.info('[AS ULTRA] lifecycle WebSocket stream initialized');
    } catch (err) {
        console.error('[AS ULTRA] lifecycle WS init failed', err);
    }
}

var asLifecycleRefreshTimer = null;
function asScheduleLifecycleRefresh() {
    try {
        if (asLifecycleRefreshTimer) {
            clearTimeout(asLifecycleRefreshTimer);
        }
        asLifecycleRefreshTimer = setTimeout(function () {
            asLifecycleRefreshTimer = null;
            if (typeof asFetchHubData === 'function') {
                asFetchHubData();
            }
        }, 1500); // 1.5s debounce to avoid hammering the API
    } catch (err) {
        console.error('[AS ULTRA] lifecycle refresh scheduling error', err);
    }
}

// Initialize the dashboard when DOM is ready
function asInit() {
    console.log('🚀 Ultra Automated Signals Dashboard initializing...');
    asEnsureLifecycleAnimationStyles();
    asEnsureTimelineStyles();
    asEnsureNotebookStyles();
    asEnsureNotebookContainer();
    asInitLifecycleWebSocketStream();
    asSetupEventHandlers();
    asFetchHubData();
    // Auto-refresh every 30 seconds
    setInterval(() => {
        asFetchHubData();
    }, 30000);
    
    // Close Trade Notebook on ESC
    try {
        window.addEventListener('keydown', function (evt) {
            if (!asNotebookState || !asNotebookState.isOpen) return;
            if (evt.key === 'Escape' || evt.key === 'Esc') {
                evt.preventDefault();
                asCloseTradeNotebook && asCloseTradeNotebook();
            }
        });
    } catch (err) {
        console.warn('Failed to bind notebook ESC handler', err);
    }

    // PATCH 7K: update telemetry status indicator if present
    (function () {
        try {
            var statusEl = document.getElementById('as-telemetry-status');
            if (statusEl) {
                statusEl.textContent = 'Telemetry: live (7K)';
            }
        } catch (e) {
            // never break init if anything goes wrong
        }
    }());
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
