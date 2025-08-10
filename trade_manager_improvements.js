// Trade Manager JavaScript Improvements

// 1. Fix performance issues in data processing
function optimizedUpdateD3Charts(data) {
    // Single pass data processing instead of multiple loops
    const processedData = data.reduce((acc, trade) => {
        acc.totalR += trade.rScore || 0;
        acc.winCount += (trade.rScore > 0 || trade.breakeven) ? 1 : 0;
        acc.sessions[trade.session] = (acc.sessions[trade.session] || 0) + 1;
        return acc;
    }, { totalR: 0, winCount: 0, sessions: {} });
    
    return processedData;
}

// 2. Improve error handling with specific error types
async function safeApiCall(url, options = {}) {
    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        if (error instanceof TypeError) {
            console.error('Network error:', error.message);
            throw new Error('Network connection failed');
        } else if (error instanceof SyntaxError) {
            console.error('JSON parsing error:', error.message);
            throw new Error('Invalid server response');
        } else {
            console.error('API call failed:', error.message);
            throw error;
        }
    }
}

// 3. Enhanced trade validation
function validateTradeInput(trade) {
    const errors = [];
    
    if (!trade.date || isNaN(Date.parse(trade.date))) {
        errors.push('Valid date is required');
    }
    
    if (!['LONG', 'SHORT'].includes(trade.bias)) {
        errors.push('Bias must be LONG or SHORT');
    }
    
    if (trade.rScore !== undefined && (!isFinite(trade.rScore) || isNaN(trade.rScore))) {
        errors.push('R Score must be a valid number');
    }
    
    if (trade.entryPrice !== undefined && (!isFinite(trade.entryPrice) || trade.entryPrice < 0)) {
        errors.push('Entry price must be a positive number');
    }
    
    return errors;
}

// 4. Optimized context determination
const CONTEXT_MAP = {
    'risk': 'RISK_MANAGEMENT',
    'position': 'POSITION_SIZING',
    'entry': 'ENTRY_ANALYSIS',
    'exit': 'EXIT_STRATEGY',
    'session': 'SESSION_ANALYSIS'
};

function determineContextOptimized(prompt) {
    const lowerPrompt = prompt.toLowerCase();
    
    for (const [keyword, context] of Object.entries(CONTEXT_MAP)) {
        if (lowerPrompt.includes(keyword)) {
            return context;
        }
    }
    
    return 'GENERAL_TRADING';
}

// 5. Constants for magic numbers
const TRADING_CONSTANTS = {
    MIN_TRADES_FOR_SESSION_ANALYSIS: 3,
    NQ_POINT_VALUE: 20,
    MAX_DISPLAYED_TRADES: 50,
    DEFAULT_ACCOUNT_SIZE: 50000,
    UPDATE_INTERVAL_MS: 30000
};

// 6. Improved bulk operations with progress tracking
async function bulkOperationWithProgress(trades, operation, progressCallback) {
    const total = trades.length;
    const results = [];
    
    for (let i = 0; i < total; i++) {
        try {
            const result = await operation(trades[i]);
            results.push(result);
            
            if (progressCallback) {
                progressCallback(i + 1, total, `Processing trade ${i + 1}/${total}`);
            }
        } catch (error) {
            console.error(`Failed to process trade ${i + 1}:`, error);
            results.push({ error: error.message });
        }
    }
    
    return results;
}

// 7. Enhanced data sanitization
function sanitizeTradeData(trade) {
    return {
        id: parseInt(trade.id) || Date.now(),
        date: trade.date?.toString().substring(0, 10) || '',
        bias: ['LONG', 'SHORT'].includes(trade.bias) ? trade.bias : 'LONG',
        session: trade.session?.toString().substring(0, 20) || 'LONDON',
        breakeven: Boolean(trade.breakeven),
        rScore: isFinite(trade.rScore) ? Number(trade.rScore) : 0,
        entryPrice: isFinite(trade.entryPrice) ? Number(trade.entryPrice) : 0,
        exitPrice: isFinite(trade.exitPrice) ? Number(trade.exitPrice) : 0,
        stopLoss: isFinite(trade.stopLoss) ? Number(trade.stopLoss) : 0,
        positionSize: Math.max(1, parseInt(trade.positionSize) || 1),
        commission: Math.max(0, parseFloat(trade.commission) || 0)
    };
}