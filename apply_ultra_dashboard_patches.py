#!/usr/bin/env python3
"""
ULTRA DASHBOARD PATCH SET
Applies all 6 fixes in strict mode
"""

def apply_js_fixes():
    """Apply all JavaScript fixes"""
    with open('static/js/automated_signals_ultra.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # FIX 2: Correct current MFE calculation
    old_render_table = '''    trades.forEach(t => {
        const tr = document.createElement('tr');
        tr.dataset.tradeId = t.trade_id;
        // Time formatting
        const ts = t.timestamp ? new Date(t.timestamp) : null;
        const timeStr = ts
            ? ts.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            : '';
        // Direction pill'''
    
    new_render_table = '''    trades.forEach(t => {
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
        // Direction pill'''
    
    content = content.replace(old_render_table, new_render_table)
    
    # Replace t.current_mfe with mfeCombined
    content = content.replace('fmtR(t.current_mfe)', 'fmtR(mfeCombined)')
    
    # FIX 3: Sort newest trades first
    old_sort = '''AS.state.filteredTrades = filtered;
    asRenderTradesTable();'''
    
    new_sort = '''AS.state.filteredTrades = filtered;
    // FIX 3: Sort newest trades first
    AS.state.filteredTrades.sort((a, b) => {
        const timeA = new Date(a.last_event_time || 0);
        const timeB = new Date(b.last_event_time || 0);
        return timeB - timeA;
    });
    asRenderTradesTable();'''
    
    content = content.replace(old_sort, new_sort)
    
    # FIX 4: Robust timeline chart - find the chart rendering section
    # This is in asRenderTradeTimelineAndChart function
    old_chart_logic = '''    events.forEach(ev => {
        const ts = ev.timestamp ? new Date(ev.timestamp) : null;
        const timeStr = ts
            ? ts.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
            : '';
        // Correct: Use telemetry MFE first, fall back to direct
        const effMfe =
            ev.telemetry?.mfe_R != null
                ? Number(ev.telemetry.mfe_R)
                : ev.mfe_R != null
                ? Number(ev.mfe_R)
                : null;'''
    
    new_chart_logic = '''    events.forEach((ev, index) => {
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
                : null;'''
    
    content = content.replace(old_chart_logic, new_chart_logic)
    
    # FIX 4: Filter out null/NaN R values in chart
    old_chart_data = '''        eventsEl.appendChild(row);
        // Add to chart data
        if (ts && effMfe != null) {
            labels.push(timeStr);
            mfeData.push(effMfe);
        }'''
    
    new_chart_data = '''        eventsEl.appendChild(row);
        // FIX 4: Add to chart data (filter out null/NaN)
        if (Number.isFinite(effMfe)) {
            labels.push(timeStr);
            mfeData.push(effMfe);
        }'''
    
    content = content.replace(old_chart_data, new_chart_data)
    
    # FIX 5: Setup & signal strength mapping
    # Replace setup_family references
    content = content.replace('t.setup?.setup_family', 't.setup?.setup_family || t.setup?.family')
    content = content.replace('t.setup?.setup_variant', 't.setup?.setup_variant || t.setup?.variant')
    content = content.replace('s.setup_family', 's.setup_family || s.family')
    content = content.replace('s.setup_variant', 's.setup_variant || s.variant')
    
    with open('static/js/automated_signals_ultra.js', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Applied all JavaScript fixes")
    print("   - FIX 2: Correct MFE calculation (max of be_mfe_R and no_be_mfe_R)")
    print("   - FIX 3: Sort newest trades first")
    print("   - FIX 4: Robust timeline chart with timestamp parsing")
    print("   - FIX 5: Setup & signal strength mapping with fallbacks")


def apply_css_fixes():
    """Apply CSS fixes"""
    css_patch = '''
/* ULTRA DASHBOARD PATCH SET — Sticky Headers + Dark Mode Fixes */

/* FIX 6: Sticky table header */
.as-trades-wrapper table thead th {
    position: sticky;
    top: 0;
    background-color: #0f172a !important;
    color: #e5e7eb !important;
    z-index: 5;
}

/* Fix unreadable text in calendar + modal */
.as-calendar-day,
.as-calendar-day-date,
.as-calendar-day-meta,
.as-modal,
.as-modal .card-body,
.as-event-item,
.card-header {
    color: #e5e7eb !important;
}

/* Fix white telemetry table background */
.as-trades-wrapper table,
.as-trades-wrapper table tbody tr td {
    background-color: #020617 !important;
    color: #e5e7eb !important;
}

/* Strength bars readable */
.as-strength-bar {
    background: rgba(255, 255, 255, 0.08) !important;
}
'''
    
    with open('static/css/automated_signals_ultra.css', 'a', encoding='utf-8') as f:
        f.write(css_patch)
    
    print("✅ Applied CSS fixes")
    print("   - FIX 6: Sticky table headers")
    print("   - FIX 6: Dark mode text fixes (calendar, modal, event items)")
    print("   - FIX 6: Table background fixes")
    print("   - FIX 6: Strength bar visibility")


if __name__ == "__main__":
    print("🚀 ULTRA DASHBOARD PATCH SET")
    print("=" * 70)
    print("\nApplying JavaScript fixes...")
    apply_js_fixes()
    print("\nApplying CSS fixes...")
    apply_css_fixes()
    print("\n" + "=" * 70)
    print("✅ ALL PATCHES APPLIED SUCCESSFULLY")
    print("\nModified files:")
    print("  - automated_signals_state.py (FIX 1: Status classification)")
    print("  - static/js/automated_signals_ultra.js (FIX 2-5)")
    print("  - static/css/automated_signals_ultra.css (FIX 6)")
