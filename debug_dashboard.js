// Debug script to check dashboard data loading
console.log('=== DASHBOARD DEBUG SCRIPT ===');

// Check if Signal Lab functions are loaded
console.log('Signal Lab functions available:', typeof updateSignalLabAnalysis);

// Check data source
const dataSource = document.getElementById('dataSourceToggle')?.value || 'unknown';
console.log('Current data source:', dataSource);

// Check trades data
console.log('Window.trades length:', window.trades?.length || 0);
if (window.trades?.length > 0) {
    console.log('Sample trade:', window.trades[0]);
}

// Check filtered trades
function debugGetFilteredTrades() {
    const sessionCheckboxes = document.querySelectorAll('.session-filter:checked');
    const selectedSessions = Array.from(sessionCheckboxes).map(cb => cb.value);
    const biasFilter = document.getElementById('biasFilter')?.value || 'ALL';
    const breakevenFilter = document.getElementById('breakevenFilter')?.value || 'all';
    
    console.log('Filter settings:', {
        selectedSessions,
        biasFilter,
        breakevenFilter
    });
    
    const filtered = (window.trades || []).filter(trade => {
        if (selectedSessions.length > 0 && !selectedSessions.includes(trade.session)) return false;
        if (biasFilter !== 'ALL' && trade.bias !== biasFilter) return false;
        
        // Breakeven strategy filter
        if (breakevenFilter === 'no-be' && (trade.be1Hit || trade.be2Hit)) return false;
        if (breakevenFilter === 'be-1' && (!trade.be1Hit || trade.be2Hit)) return false;
        if (breakevenFilter === 'be-2' && !trade.be2Hit) return false;
        
        return true;
    });
    
    console.log('Filtered trades:', filtered.length);
    return filtered;
}

// Test getRValue function
function debugGetRValue(trade, rTarget) {
    const breakevenFilter = document.getElementById('breakevenFilter')?.value || 'all';
    
    console.log('getRValue debug:', {
        trade: {
            date: trade.date,
            mfe_none: trade.mfe_none,
            mfe: trade.mfe,
            rScore: trade.rScore,
            be1Hit: trade.be1Hit,
            be2Hit: trade.be2Hit
        },
        rTarget,
        breakevenFilter
    });
    
    // No BE strategy - use mfe_none
    if (breakevenFilter === 'no-be' || breakevenFilter === 'all') {
        const mfe = trade.mfe_none || trade.mfe || trade.rScore || 0;
        console.log('No BE strategy - MFE:', mfe);
        if (mfe <= 0) return -1; // Loss
        return mfe >= rTarget ? rTarget : -1; // Win at target or loss
    }
    
    // BE = 1 strategy - must hit BE1 and check mfe1
    if (breakevenFilter === 'be-1') {
        const be1Hit = trade.be1Hit || trade.be1_hit || false;
        console.log('BE1 strategy - BE1 Hit:', be1Hit);
        if (!be1Hit) return -1; // Didn't reach BE1, it's a loss
        
        const mfe1 = trade.mfe1 || 0;
        console.log('BE1 strategy - MFE1:', mfe1);
        if (mfe1 >= rTarget) return rTarget; // Win at target
        return 0; // Breakeven (hit BE1 but not target)
    }
    
    // BE = 2 strategy - must hit BE2 and check mfe2
    if (breakevenFilter === 'be-2') {
        const be2Hit = trade.be2Hit || trade.be2_hit || false;
        console.log('BE2 strategy - BE2 Hit:', be2Hit);
        if (!be2Hit) return -1; // Didn't reach BE2, it's a loss
        
        const mfe2 = trade.mfe2 || 0;
        console.log('BE2 strategy - MFE2:', mfe2);
        if (mfe2 >= rTarget) return rTarget; // Win at target
        return 0; // Breakeven (hit BE2 but not target)
    }
    
    return -1;
}

// Run debug tests
function runDebugTests() {
    console.log('\n=== RUNNING DEBUG TESTS ===');
    
    const filteredTrades = debugGetFilteredTrades();
    const rTarget = parseInt(document.getElementById('rTargetFilter')?.value || '1');
    
    console.log('R-Target:', rTarget);
    
    if (filteredTrades.length > 0) {
        console.log('\nTesting getRValue on first 3 trades:');
        filteredTrades.slice(0, 3).forEach((trade, index) => {
            console.log(`\nTrade ${index + 1}:`);
            const rValue = debugGetRValue(trade, rTarget);
            console.log('Calculated R-Value:', rValue);
        });
        
        // Test metrics calculation
        const rValues = filteredTrades.map(t => debugGetRValue(t, rTarget));
        console.log('\nAll R-Values:', rValues);
        
        const winsAndBreakevens = rValues.filter(r => r >= 0);
        const actualWins = rValues.filter(r => r > 0);
        const losses = rValues.filter(r => r < 0);
        
        console.log('Wins + Breakevens:', winsAndBreakevens.length);
        console.log('Actual Wins:', actualWins.length);
        console.log('Losses:', losses.length);
        
        const winRate = (winsAndBreakevens.length / filteredTrades.length * 100).toFixed(1);
        console.log('Calculated Win Rate:', winRate + '%');
    }
}

// Auto-run when script loads
setTimeout(runDebugTests, 2000);

// Make functions available globally for manual testing
window.debugGetFilteredTrades = debugGetFilteredTrades;
window.debugGetRValue = debugGetRValue;
window.runDebugTests = runDebugTests;

console.log('Debug functions available: debugGetFilteredTrades, debugGetRValue, runDebugTests');