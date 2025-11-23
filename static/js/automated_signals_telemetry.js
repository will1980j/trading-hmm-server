// static/js/automated_signals_telemetry.js
// Read-only telemetry dashboard for telemetry_automated_signals_log
// STRICT MODE: No writes, no mutations of trading tables.

(function () {
'use strict';

const state = {
    events: [],
    selectedId: null,
    isLoadingList: false,
    isLoadingDetail: false,
    lastLoadedId: null,
    pollIntervalMs: 15000,
    pollTimer: null
};

function $(id) {
    return document.getElementById(id);
}

function setStatus(text) {
    const badge = $('asTelemetryStatusBadge');
    if (!badge) return;
    badge.textContent = text;
}

function formatIso(dtString) {
    if (!dtString) return '—';
    try {
        const d = new Date(dtString);
        if (Number.isNaN(d.getTime())) return dtString;
        return d.toLocaleString();
    } catch (e) {
        return dtString;
    }
}

function formatMs(ms) {
    if (ms == null) return '—';
    const n = Number(ms);
    if (Number.isNaN(n)) return '—';
    return `${n} ms`;
}

function renderEventsTable() {
    const tbody = $('asTelemetryTableBody');
    const summary = $('asTelemetrySummary');
    if (!tbody) return;

    if (!state.events.length) {
        tbody.innerHTML = `<tr><td colspan="4" class="as-telemetry-empty">No telemetry events found yet.</td></tr>`;
        if (summary) summary.textContent = '0 events';
        return;
    }

    let html = '';
    state.events.forEach(ev => {
        const sel = state.selectedId === ev.id ? ' as-telemetry-row--selected' : '';
        const ms = ev.processing_time_ms || 0;
        const msClass = ms > 500 ? 'as-telemetry-ms as-telemetry-ms-bad' : 'as-telemetry-ms';
        const validationPill = ev.validation_error
            ? `<span class="as-telemetry-pill-err">Validation error</span>`
            : `<span class="as-telemetry-pill-ok">OK</span>`;

        html += `<tr class="as-telemetry-row${sel}" data-log-id="${ev.id}">
            <td><span class="as-telemetry-id">#${ev.id}</span></td>
            <td><span class="as-telemetry-time">${formatIso(ev.received_at)}</span></td>
            <td><span class="${msClass}">${formatMs(ms)}</span></td>
            <td>${validationPill}</td>
        </tr>`;
    });

    tbody.innerHTML = html;
    if (summary) summary.textContent = `${state.events.length} events`;

    // Attach click handlers
    Array.from(tbody.querySelectorAll('tr[data-log-id]')).forEach(row => {
        row.addEventListener('click', () => {
            const idStr = row.getAttribute('data-log-id');
            const id = idStr ? parseInt(idStr, 10) : null;
            if (!id || Number.isNaN(id)) return;
            state.selectedId = id;
            renderEventsTable();
            fetchTelemetryDetail(id);
        });
    });
}

function renderDetailPlaceholders() {
    const status = $('asTelemetryDetailStatus');
    const rawBox = $('asTelemetryRawBox');
    const fusedBox = $('asTelemetryFusedBox');
    const resultBox = $('asTelemetryResultBox');

    if (status) status.textContent = 'No event selected';
    if (rawBox) rawBox.textContent = '';
    if (fusedBox) fusedBox.textContent = '';
    if (resultBox) resultBox.textContent = '';
}

function prettyJson(value) {
    if (value == null) return '';
    try {
        return JSON.stringify(value, null, 2);
    } catch (e) {
        return String(value);
    }
}

function fetchTelemetryList(options) {
    if (state.isLoadingList) return;
    state.isLoadingList = true;
    setStatus('Loading telemetry…');

    const params = new URLSearchParams();
    params.set('limit', '50');
    if (options && options.afterId) {
        params.set('after_id', String(options.afterId));
    }

    fetch('/api/automated-signals/telemetry?' + params.toString(), {
        method: 'GET',
        credentials: 'include'
    })
    .then(res => res.json())
    .then(data => {
        if (!data || !data.success) {
            setStatus('Error loading telemetry');
            state.isLoadingList = false;
            return;
        }

        const events = Array.isArray(data.events) ? data.events : [];
        // Always replace list; we are not maintaining infinite history here.
        state.events = events.sort((a, b) => a.id - b.id);

        if (state.events.length) {
            state.lastLoadedId = state.events[state.events.length - 1].id;
        }

        renderEventsTable();
        setStatus('Telemetry loaded');
    })
    .catch(err => {
        console.error('Telemetry list error', err);
        setStatus('Error loading telemetry');
    })
    .finally(() => {
        state.isLoadingList = false;
    });
}

function fetchTelemetryDetail(id) {
    if (state.isLoadingDetail) return;
    state.isLoadingDetail = true;
    setStatus(`Loading detail for #${id}…`);

    const status = $('asTelemetryDetailStatus');
    if (status) status.textContent = `Loading #${id}…`;

    fetch(`/api/automated-signals/telemetry/${id}`, {
        method: 'GET',
        credentials: 'include'
    })
    .then(res => res.json())
    .then(data => {
        if (!data || !data.success || !data.event) {
            setStatus(`Detail not available for #${id}`);
            if (status) status.textContent = `Detail not available for #${id}`;
            return;
        }

        const ev = data.event;
        const rawBox = $('asTelemetryRawBox');
        const fusedBox = $('asTelemetryFusedBox');
        const resultBox = $('asTelemetryResultBox');

        if (rawBox) rawBox.textContent = prettyJson(ev.raw_payload);
        if (fusedBox) fusedBox.textContent = prettyJson(ev.fused_event);
        if (resultBox) resultBox.textContent = prettyJson(ev.handler_result);

        const label = ev.id ? `Event #${ev.id}` : `Event`;
        if (status) status.textContent = `${label} — received ${formatIso(ev.received_at)}`;
        setStatus('Telemetry detail loaded');
    })
    .catch(err => {
        console.error('Telemetry detail error', err);
        setStatus(`Error loading detail for #${id}`);
        const statusEl = $('asTelemetryDetailStatus');
        if (statusEl) statusEl.textContent = `Error loading detail for #${id}`;
    })
    .finally(() => {
        state.isLoadingDetail = false;
    });
}

function startPolling() {
    if (state.pollTimer) {
        clearInterval(state.pollTimer);
        state.pollTimer = null;
    }

    state.pollTimer = setInterval(() => {
        if (!state.lastLoadedId) {
            fetchTelemetryList();
        } else {
            fetchTelemetryList({ afterId: state.lastLoadedId });
        }
    }, state.pollIntervalMs);
}

function bindUi() {
    const root = $('asTelemetryRoot');
    if (!root) return;

    const btn = $('asTelemetryRefreshBtn');
    if (btn) {
        btn.addEventListener('click', () => {
            fetchTelemetryList();
        });
    }

    renderEventsTable();
    renderDetailPlaceholders();
}

// PATCH 7L START: Telemetry backfill handler
function asRunTelemetryBackfill(limit = 1000) {
    const btn = document.getElementById('as-telemetry-backfill-btn');
    if (!btn) {
        console.warn('7L: Backfill button not found in DOM');
        return;
    }
    
    btn.disabled = true;
    const originalText = btn.textContent;
    btn.textContent = 'Running backfill...';
    
    fetch('/api/automated-signals/telemetry/backfill', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ limit })
    })
        .then(res => res.json())
        .then(data => {
            console.log('7L backfill result:', data);
            if (!data.success) {
                alert('Backfill failed: ' + (data.error || 'Unknown error'));
            } else {
                alert(
                    'Backfill complete:\n' +
                    'Scanned: ' + data.scanned + '\n' +
                    'Inserted: ' + data.inserted
                );
                // Refresh telemetry list after backfill
                if (typeof fetchTelemetryList === 'function') {
                    fetchTelemetryList();
                }
            }
        })
        .catch(err => {
            console.error('7L backfill error:', err);
            alert('Backfill error: ' + err.message);
        })
        .finally(() => {
            btn.disabled = false;
            btn.textContent = originalText;
        });
}
// PATCH 7L END: Telemetry backfill handler

function init() {
    const root = $('asTelemetryRoot');
    if (!root) return; // Not on this page

    setStatus('Initializing…');
    bindUi();
    fetchTelemetryList();
    startPolling();
    
    // PATCH 7L: wire backfill button
    (function () {
        const backfillBtn = document.getElementById('as-telemetry-backfill-btn');
        if (backfillBtn) {
            backfillBtn.addEventListener('click', function () {
                asRunTelemetryBackfill(1000);
            });
        }
    })();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

})();
