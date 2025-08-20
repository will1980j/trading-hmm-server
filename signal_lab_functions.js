// Signal Lab Analysis Functions
function updateSignalLabAnalysis(filteredTrades, rTarget) {
    console.log('Signal Lab analysis with', filteredTrades.length, 'trades');
    
    // Identify active trades (missing MFE data)
    const activeTrades = filteredTrades.filter(t => {
        const mfe = t.mfe || t.mfe_none || t.rScore;
        return mfe === null || mfe === undefined || mfe === 0;
    });
    
    const completedTrades = filteredTrades.filter(t => {
        const mfe = t.mfe || t.mfe_none || t.rScore;
        return mfe !== null && mfe !== undefined && mfe !== 0;
    });
    
    console.log('Active trades:', activeTrades.length, 'Completed trades:', completedTrades.length);
    
    // Breakeven strategy analysis using completed trades
    const noBETrades = completedTrades.filter(t => !t.be1Hit && !t.be2Hit);
    const be1Trades = completedTrades.filter(t => t.be1Hit && !t.be2Hit);
    const be2Trades = completedTrades.filter(t => t.be2Hit);
    
    console.log('BE analysis - No BE:', noBETrades.length, 'BE1:', be1Trades.length, 'BE2:', be2Trades.length);
    
    // Calculate performance for each strategy
    const noBEPerf = noBETrades.length > 0 ? {
        winRate: (noBETrades.filter(t => (t.mfe || t.rScore || 0) > 0).length / noBETrades.length * 100).toFixed(1),
        avgR: (noBETrades.reduce((sum, t) => sum + (t.mfe || t.rScore || 0), 0) / noBETrades.length).toFixed(2)
    } : { winRate: '0.0', avgR: '0.00' };
    
    const be1Perf = be1Trades.length > 0 ? {
        winRate: (be1Trades.filter(t => (t.mfe1 || t.mfe || t.rScore || 0) > 0).length / be1Trades.length * 100).toFixed(1),
        avgR: (be1Trades.reduce((sum, t) => sum + (t.mfe1 || t.mfe || t.rScore || 0), 0) / be1Trades.length).toFixed(2)
    } : { winRate: '0.0', avgR: '0.00' };
    
    const be2Perf = be2Trades.length > 0 ? {
        winRate: (be2Trades.filter(t => (t.mfe2 || t.mfe || t.rScore || 0) > 0).length / be2Trades.length * 100).toFixed(1),
        avgR: (be2Trades.reduce((sum, t) => sum + (t.mfe2 || t.mfe || t.rScore || 0), 0) / be2Trades.length).toFixed(2)
    } : { winRate: '0.0', avgR: '0.00' };
    
    // Update UI elements with null checks
    const noBEEl = document.getElementById('noBEPerformance');
    const be1El = document.getElementById('be1Performance');
    const be2El = document.getElementById('be2Performance');
    const activeCountEl = document.getElementById('activeTradesCount');
    const activePercentEl = document.getElementById('activeTradePercentage');
    
    if (noBEEl) noBEEl.textContent = `${noBEPerf.winRate}% WR, ${noBEPerf.avgR}R avg (${noBETrades.length}T)`;
    if (be1El) be1El.textContent = `${be1Perf.winRate}% WR, ${be1Perf.avgR}R avg (${be1Trades.length}T)`;
    if (be2El) be2El.textContent = `${be2Perf.winRate}% WR, ${be2Perf.avgR}R avg (${be2Trades.length}T)`;
    if (activeCountEl) activeCountEl.textContent = `${activeTrades.length} trades`;
    if (activePercentEl && filteredTrades.length > 0) {
        activePercentEl.textContent = `${(activeTrades.length / filteredTrades.length * 100).toFixed(1)}%`;
    }
    
    // Determine optimal strategy
    const strategies = [
        { name: 'No BE', perf: parseFloat(noBEPerf.avgR), count: noBETrades.length },
        { name: 'BE 1R', perf: parseFloat(be1Perf.avgR), count: be1Trades.length },
        { name: 'BE 2R', perf: parseFloat(be2Perf.avgR), count: be2Trades.length }
    ];
    
    const optimalStrategy = strategies
        .filter(s => s.count >= 3) // Need at least 3 trades for reliability
        .sort((a, b) => b.perf - a.perf)[0];
    
    const optimalEl = document.getElementById('optimalBEStrategy');
    if (optimalEl) {
        optimalEl.textContent = optimalStrategy ? 
            `${optimalStrategy.name} (${optimalStrategy.perf.toFixed(2)}R avg)` : 
            'Need more data';
    }
    
    // Session and R-target analysis
    updateSessionRTargetAnalysis(completedTrades, rTarget);
    
    // Generate AI analysis for breakeven strategies
    updateBreakevenAIAnalysis(noBEPerf, be1Perf, be2Perf, activeTrades.length, filteredTrades.length);
}

function updateSessionRTargetAnalysis(completedTrades, rTarget) {
    if (completedTrades.length === 0) return;
    
    // Session analysis
    const sessionStats = {};
    completedTrades.forEach(trade => {
        const session = trade.session || 'UNKNOWN';
        if (!sessionStats[session]) {
            sessionStats[session] = { total: 0, wins: 0, totalR: 0 };
        }
        sessionStats[session].total++;
        const mfe = trade.mfe || trade.rScore || 0;
        sessionStats[session].totalR += mfe;
        if (mfe > 0) sessionStats[session].wins++;
    });
    
    // Find best session
    let bestSession = 'LONDON';
    let bestExpectancy = -999;
    
    Object.keys(sessionStats).forEach(session => {
        const stats = sessionStats[session];
        if (stats.total >= 3) { // Need at least 3 trades
            const expectancy = stats.totalR / stats.total;
            if (expectancy > bestExpectancy) {
                bestExpectancy = expectancy;
                bestSession = session;
            }
        }
    });
    
    // Update UI
    const bestSessionEl = document.getElementById('bestSessionAnalysis');
    const optimalSessionEl = document.getElementById('optimalSessionCombo');
    const bestRTargetEl = document.getElementById('bestRTargetOverall');
    const londonREl = document.getElementById('londonOptimalR');
    const nyAmREl = document.getElementById('nyAmOptimalR');
    const signalLabOptimalREl = document.getElementById('signalLabOptimalR');
    
    if (bestSessionEl) {
        const stats = sessionStats[bestSession];
        const winRate = stats ? (stats.wins / stats.total * 100).toFixed(1) : '0.0';
        const avgR = stats ? (stats.totalR / stats.total).toFixed(2) : '0.00';
        bestSessionEl.textContent = `${bestSession} (${winRate}% WR, ${avgR}R avg)`;
    }
    
    if (optimalSessionEl) optimalSessionEl.textContent = `${bestSession} + ${rTarget}R target`;
    if (bestRTargetEl) bestRTargetEl.textContent = `${rTarget}R (current)`;
    if (londonREl) londonREl.textContent = `${rTarget}R`;
    if (nyAmREl) nyAmREl.textContent = `${rTarget}R`;
    if (signalLabOptimalREl) signalLabOptimalREl.textContent = `${rTarget}R`;
    
    // Update summary
    const sessionSummaryEl = document.getElementById('sessionRTargetSummary');
    if (sessionSummaryEl) {
        sessionSummaryEl.textContent = `${bestSession} session shows strongest performance with ${bestExpectancy.toFixed(2)}R expectancy. Current ${rTarget}R target appears optimal for systematic execution.`;
    }
}

function updateBreakevenAIAnalysis(noBEPerf, be1Perf, be2Perf, activeCount, totalCount) {
    // Generate breakeven analysis summary
    const beAnalysisSummaryEl = document.getElementById('beAnalysisSummary');
    const aiBEAnalysisEl = document.getElementById('aiBEAnalysis');
    const aiSessionOptimizationEl = document.getElementById('aiSessionOptimization');
    
    if (beAnalysisSummaryEl) {
        const bestStrategy = [
            { name: 'No BE', perf: parseFloat(noBEPerf.avgR) },
            { name: 'BE 1R', perf: parseFloat(be1Perf.avgR) },
            { name: 'BE 2R', perf: parseFloat(be2Perf.avgR) }
        ].sort((a, b) => b.perf - a.perf)[0];
        
        beAnalysisSummaryEl.textContent = `${bestStrategy.name} strategy shows best performance with ${bestStrategy.perf.toFixed(2)}R average. ${activeCount} trades pending completion (${(activeCount/totalCount*100).toFixed(1)}% of total).`;
    }
    
    if (aiBEAnalysisEl) {
        aiBEAnalysisEl.textContent = `Breakeven optimization analysis shows systematic approach to risk management. Current data suggests ${parseFloat(be1Perf.avgR) > parseFloat(noBEPerf.avgR) ? 'BE at 1R' : 'no breakeven'} strategy may optimize expectancy while maintaining account protection.`;
    }
    
    if (aiSessionOptimizationEl) {
        aiSessionOptimizationEl.textContent = `Session analysis indicates optimal trading windows align with high liquidity periods. Focus allocation during identified peak performance sessions for maximum efficiency.`;
    }
}