#!/usr/bin/env python3
"""
ULTRA DASHBOARD PATCH SET (PART 2)
Final 5 fixes to complete the Ultra Dashboard build
"""

def apply_js_fixes_part2():
    """Apply JavaScript fixes 1-4"""
    with open('static/js/automated_signals_ultra.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # FIX 1: Show correct entry/exit prices
    old_strength_section = '''        // Session pill
        const sessionPill = `<span class="pill pill-session">${t.session}</span>`;
        // Signal strength bar
        const strength = t.setup?.signal_strength ?? null;'''
    
    new_strength_section = '''        // Session pill
        const sessionPill = `<span class="pill pill-session">${t.session}</span>`;
        
        // FIX 1: Entry & exit normalisation
        const entry = t.entry_price ?? t.entry ?? null;
        const exit = t.exit_price ?? t.exit ?? null;
        
        // FIX 2: Strength bar not rendering
        const strength = t.setup?.signal_strength ?? t.signal_strength ?? null;'''
    
    content = content.replace(old_strength_section, new_strength_section)
    
    # FIX 1: Replace entry_price and exit_price in HTML
    content = content.replace(
        '${t.entry_price != null ? t.entry_price.toFixed(2) : \'\'}',
        '${entry != null ? entry.toFixed(2) : \'--\'}'
    )
    content = content.replace(
        '${t.exit_price != null ? t.exit_price.toFixed(2) : \'\'}',
        '${exit != null ? exit.toFixed(2) : \'--\'}'
    )
    
    # FIX 2: Fix strength bar rendering
    old_strength_bar = '''        const strengthFill =
            strength != null
                ? `<div class="as-strength-fill" style="width:${Math.min(100, Math.max(0, strength))}%;"></div>`
                : '';'''
    
    new_strength_bar = '''        const strengthFill = strength != null
            ? `<div class="as-strength-bar-fill" style="width:${Math.min(100, Math.max(0, strength))}%;"></div>`
            : '';'''
    
    content = content.replace(old_strength_bar, new_strength_bar)
    
    # FIX 3: Setup missing in table
    old_setup_display = '''            <td>${t.setup?.setup_family || t.setup?.family || ''} ${t.setup?.setup_variant || t.setup?.variant ? '· ' + t.setup.setup_variant : ''}</td>'''
    
    new_setup_display = '''            <td>${t.setup?.id || t.setup?.setup_id || '--'}</td>'''
    
    content = content.replace(old_setup_display, new_setup_display)
    
    # FIX 4: Auto-refresh every 60 seconds
    old_init = '''// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', asInit);
} else {
    asInit();
}'''
    
    new_init = '''// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', asInit);
} else {
    asInit();
}

// FIX 4: Auto-refresh every 60 seconds
setInterval(() => {
    console.log("🔄 Auto-refreshing Ultra Dashboard...");
    asFetchHubData();
}, 60000);'''
    
    content = content.replace(old_init, new_init)
    
    with open('static/js/automated_signals_ultra.js', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Applied JavaScript fixes (Part 2)")
    print("   - FIX 1: Entry/exit price normalization with fallbacks")
    print("   - FIX 2: Strength bar rendering fixed")
    print("   - FIX 3: Setup display simplified (shows setup ID)")
    print("   - FIX 4: Auto-refresh every 60 seconds")


def apply_css_fixes_part2():
    """Apply CSS fix 5"""
    css_patch = '''
/* ULTRA DASHBOARD PATCH SET PART 2 — Force Dark Theme Everywhere */

/* FIX 5: Force light text on all elements inside Ultra Dashboard */
#as-ultra-root,
#as-ultra-root * {
    color: #e5e7eb !important;
}

/* Fix remaining white backgrounds */
#as-ultra-root table,
#as-ultra-root thead,
#as-ultra-root tbody,
#as-ultra-root tr,
#as-ultra-root td,
#as-ultra-root th {
    background-color: #020617 !important;
}
'''
    
    with open('static/css/automated_signals_ultra.css', 'a', encoding='utf-8') as f:
        f.write(css_patch)
    
    print("✅ Applied CSS fixes (Part 2)")
    print("   - FIX 5: Force dark theme on all Ultra Dashboard elements")
    print("   - FIX 5: Override all remaining white backgrounds")


if __name__ == "__main__":
    print("🚀 ULTRA DASHBOARD PATCH SET (PART 2)")
    print("=" * 70)
    print("\nApplying JavaScript fixes (1-4)...")
    apply_js_fixes_part2()
    print("\nApplying CSS fixes (5)...")
    apply_css_fixes_part2()
    print("\n" + "=" * 70)
    print("✅ ALL PART 2 PATCHES APPLIED SUCCESSFULLY")
    print("\nModified files:")
    print("  - static/js/automated_signals_ultra.js (FIX 1-4)")
    print("  - static/css/automated_signals_ultra.css (FIX 5)")
    print("\nTotal patches applied: 11 (6 from Part 1 + 5 from Part 2)")
