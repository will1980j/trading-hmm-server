// Dashboard fixes - real data only, correct sessions

function updateMarketStatus() {
    const now = new Date();
    const utcHour = now.getUTCHours();
    const utcMinute = now.getUTCMinutes();
    const currentUTCTime = utcHour * 60 + utcMinute;
    
    const markets = [
        { name: 'ASIA', open: 22 * 60, close: 7 * 60, timezone: 'Asia' },
        { name: 'LONDON', open: 7 * 60, close: 16 * 60, timezone: 'London' },
        { name: 'NY PRE', open: 8 * 60, close: 13 * 60 + 30, timezone: 'NY Pre Market' },
        { name: 'NY AM', open: 13 * 60 + 30, close: 17 * 60, timezone: 'NY AM' },
        { name: 'NY LUNCH', open: 17 * 60, close: 18 * 60, timezone: 'NY Lunch' },
        { name: 'NY PM', open: 18 * 60, close: 20 * 60, timezone: 'NY PM' }
    ];
    
    let marketHTML = '';
    
    markets.forEach(market => {
        let isOpen = false;
        let nextEvent = '';
        let timeToEvent = 0;
        
        if (market.name === 'ASIA') {
            isOpen = currentUTCTime >= market.open || currentUTCTime < market.close;
            if (isOpen) {
                timeToEvent = market.close > currentUTCTime ? market.close - currentUTCTime : (24 * 60) - currentUTCTime + market.close;
                nextEvent = 'Closes in';
            } else {
                timeToEvent = currentUTCTime < market.open ? market.open - currentUTCTime : (24 * 60) - currentUTCTime + market.open;
                nextEvent = 'Opens in';
            }
        } else {
            isOpen = currentUTCTime >= market.open && currentUTCTime < market.close;
            if (isOpen) {
                timeToEvent = market.close - currentUTCTime;
                nextEvent = 'Closes in';
            } else {
                if (currentUTCTime < market.open) {
                    timeToEvent = market.open - currentUTCTime;
                } else {
                    timeToEvent = (24 * 60) - currentUTCTime + market.open;
                }
                nextEvent = 'Opens in';
            }
        }
        
        const hours = Math.floor(timeToEvent / 60);
        const minutes = timeToEvent % 60;
        const timeString = `${hours}h ${minutes}m`;
        
        const glowClass = isOpen ? 'open' : '';
        
        marketHTML += `
            <div class="market-widget ${glowClass}">
                <div class="market-name">${market.name}</div>
                <div class="market-status ${isOpen ? 'market-open' : 'market-closed'}">
                    ${isOpen ? 'OPEN' : 'CLOSED'}
                </div>
                <div class="market-timer">${nextEvent}</div>
                <div class="market-timer" style="font-weight: 600; color: ${isOpen ? '#00ff88' : '#ffa502'};">${timeString}</div>
            </div>
        `;
    });
    
    const marketElement = document.getElementById('marketStatus');
    if (marketElement) {
        marketElement.innerHTML = marketHTML;
    }
}

async function loadTradesFromDB() {
    try {
        const response = await fetch('/api/trades');
        const data = await response.json();
        if (data.trades && data.trades.length > 0) {
            window.trades = data.trades.map(t => ({
                date: t.created_at ? t.created_at.split('T')[0] : '2024-08-06',
                bias: t.bias || 'LONG',
                session: extractSession(t.reason) || 'LONDON',
                breakeven: extractBreakeven(t.reason),
                rScore: extractRScore(t.reason),
                pnl: parseFloat(t.pnl) || 0,
                entry_price: parseFloat(t.entry_price) || 0,
                exit_price: parseFloat(t.exit_price) || 0,
                quantity: parseInt(t.quantity) || 1
            }));
            console.log('Loaded', window.trades.length, 'trades from database');
            updateCharts();
        } else {
            console.log('No trades found in database');
            window.trades = [];
            updateCharts();
        }
    } catch (error) {
        console.error('Failed to load trades from database:', error);
        window.trades = [];
        updateCharts();
    }
}

function calculateMaxDrawdown(trades) {
    let peak = 0;
    let maxDD = 0;
    let cumulative = 0;
    
    trades.forEach(trade => {
        cumulative += trade.rScore;
        if (cumulative > peak) peak = cumulative;
        const drawdown = peak - cumulative;
        if (drawdown > maxDD) maxDD = drawdown;
    });
    
    return -maxDD;
}

function calculateSharpeRatio(trades) {
    if (trades.length < 2) return 0;
    const returns = trades.map(t => t.rScore);
    const mean = returns.reduce((a, b) => a + b, 0) / returns.length;
    const variance = returns.reduce((sum, r) => sum + Math.pow(r - mean, 2), 0) / (returns.length - 1);
    const stdDev = Math.sqrt(variance);
    return stdDev > 0 ? mean / stdDev : 0;
}

function calculateKellyPercent(trades) {
    const wins = trades.filter(t => t.rScore > 0);
    const losses = trades.filter(t => t.rScore < 0);
    
    if (wins.length === 0 || losses.length === 0) return 0;
    
    const winRate = wins.length / trades.length;
    const avgWin = wins.reduce((sum, t) => sum + t.rScore, 0) / wins.length;
    const avgLoss = Math.abs(losses.reduce((sum, t) => sum + t.rScore, 0) / losses.length);
    
    return ((winRate * avgWin) - ((1 - winRate) * avgLoss)) / avgWin * 100;
}

function updateCharts() {
    const filteredTrades = getFilteredTrades();
    
    document.getElementById('filteredTrades').textContent = filteredTrades.length;
    
    const wins = filteredTrades.filter(t => t.rScore >= 1 || t.breakeven).length;
    const winRate = filteredTrades.length > 0 ? (wins / filteredTrades.length * 100).toFixed(1) : '0.0';
    document.getElementById('filteredWinRate').textContent = winRate + '%';
    
    const totalR = filteredTrades.reduce((sum, t) => sum + t.rScore, 0);
    const expectancy = filteredTrades.length > 0 ? (totalR / filteredTrades.length).toFixed(2) : '0.00';
    document.getElementById('expectancy').textContent = expectancy + 'R';
    
    const profits = filteredTrades.filter(t => t.rScore > 0);
    const losses = filteredTrades.filter(t => t.rScore < 0);
    const avgWin = profits.length > 0 ? profits.reduce((sum, t) => sum + t.rScore, 0) / profits.length : 0;
    const avgLoss = losses.length > 0 ? Math.abs(losses.reduce((sum, t) => sum + t.rScore, 0) / losses.length) : 0;
    const profitFactor = losses.length > 0 ? (avgWin * profits.length / (avgLoss * losses.length)).toFixed(2) : 'Infinity';
    document.getElementById('profitFactor').textContent = profitFactor;
    
    const maxDrawdown = calculateMaxDrawdown(filteredTrades);
    document.getElementById('maxDrawdown').textContent = maxDrawdown.toFixed(2) + 'R';
    
    const sharpe = calculateSharpeRatio(filteredTrades);
    document.getElementById('sharpeRatio').textContent = sharpe.toFixed(2);
    
    const kelly = calculateKellyPercent(filteredTrades);
    document.getElementById('kellyPercent').textContent = kelly.toFixed(1) + '%';
    
    const recovery = totalR > 0 && maxDrawdown < 0 ? (totalR / Math.abs(maxDrawdown)).toFixed(2) : '0.00';
    document.getElementById('recoveryFactor').textContent = recovery;
    
    if (typeof updateD3Charts === 'function') {
        updateD3Charts();
    }
}

if (typeof window !== 'undefined') {
    window.updateMarketStatus = updateMarketStatus;
    window.loadTradesFromDB = loadTradesFromDB;
    window.updateCharts = updateCharts;
}