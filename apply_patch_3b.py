#!/usr/bin/env python3
"""
PATCH 3B: Ultra JS fixes for times, setup, strength, final R, exit, chart labels
"""

def apply_patch_3b():
    """Apply all 4 parts of Patch 3B"""
    with open('static/js/automated_signals_ultra.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # PART 1: Fix time column
    old_time = '''        // Time formatting
        const ts = t.timestamp ? new Date(t.timestamp) : null;
        const timeStr = ts
            ? ts.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            : '';'''
    
    new_time = '''        // PATCH 3B PART 1: Fix time column
        const timeStr = t.time_et
            ? t.time_et
            : (t.last_event_time
                ? new Date(t.last_event_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                : '');'''
    
    content = content.replace(old_time, new_time)
    
    # PART 2: Comprehensive normalization before building row
    old_section = '''        // Session pill
        const sessionPill = `<span class="pill pill-session">${t.session}</span>`;
        
        // FIX 1: Entry & exit normalisation
        const entry = t.entry_price ?? t.entry ?? null;
        const exit = t.exit_price ?? t.exit ?? null;
        
        // FIX 2: Strength bar not rendering
        const strength = t.setup?.signal_strength ?? t.signal_strength ?? null;
        const strengthFill = strength != null
            ? `<div class="as-strength-bar-fill" style="width:${Math.min(100, Math.max(0, strength))}%;"></div>`
            : '';'''
    
    new_section = '''        // Session pill
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
            : '';'''
    
    content = content.replace(old_section, new_section)
    
    # PART 2: Update row HTML cells
    old_row = '''            <td>${t.setup?.id || t.setup?.setup_id || '--'}</td>
            <td><div class="as-strength-bar">${strengthFill}</div></td>
            <td>${fmtR(mfeCombined)}</td>
            <td>${fmtR(t.no_be_mfe_R)}</td>
            <td>${fmtR(t.final_mfe)}</td>
            <td>${entry != null ? entry.toFixed(2) : '--'}</td>
            <td>${exit != null ? exit.toFixed(2) : '--'}</td>'''
    
    new_row = '''            <td>${setupName || ''}</td>
            <td><div class="as-strength-bar">${strengthFill}</div></td>
            <td>${fmtR(currentMfe)}</td>
            <td>${fmtR(noBeMfe)}</td>
            <td>${fmtR(finalMfe)}</td>
            <td>${entry != null ? entry.toFixed(2) : ''}</td>
            <td>${exit != null ? exit.toFixed(2) : ''}</td>'''
    
    content = content.replace(old_row, new_row)
    
    # PART 3: Fix summary using final_mfe_R
    old_summary = '''        const finals = completed.map(t => (t.final_mfe != null ? Number(t.final_mfe) : null)).filter(v => v != null);'''
    
    new_summary = '''        // PATCH 3B PART 3: Use final_mfe_R
        const finals = completed.map(t => (t.final_mfe_R != null ? Number(t.final_mfe_R) : null)).filter(v => v != null);'''
    
    content = content.replace(old_summary, new_summary)
    
    # PART 4: Chart x-axis label formatting
    old_chart_label = '''        const timeStr = ts
            ? new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
            : `Event ${index + 1}`;'''
    
    new_chart_label = '''        // PATCH 3B PART 4: Shorter chart labels
        const timeStr = ts
            ? new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            : `E${index + 1}`;'''
    
    content = content.replace(old_chart_label, new_chart_label)
    
    # PART 4: Update chart x-axis config
    old_chart_config = '''                x: {
                    ticks: { maxRotation: 0, autoSkip: true, maxTicksLimit: 10 },
                    title: { display: true, text: 'Time' }
                },'''
    
    new_chart_config = '''                x: {
                    ticks: { maxRotation: 45, autoSkip: true, maxTicksLimit: 8 },
                    title: { display: true, text: 'Time' }
                },'''
    
    content = content.replace(old_chart_config, new_chart_config)
    
    with open('static/js/automated_signals_ultra.js', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ PATCH 3B APPLIED SUCCESSFULLY")
    print("\nPart 1: Time column fixed (uses time_et → last_event_time)")
    print("Part 2: Setup, strength, MFE, entry/exit normalized")
    print("Part 3: Summary uses final_mfe_R")
    print("Part 4: Chart labels shortened (HH:MM, E1, E2...)")


if __name__ == "__main__":
    print("🚀 APPLYING PATCH 3B")
    print("=" * 70)
    apply_patch_3b()
    print("=" * 70)
    print("\nFile modified: static/js/automated_signals_ultra.js")
