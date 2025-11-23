// ============================================
// COMPARE - PHASE 1 MOCK DATA
// ============================================

// MOCK DATA MODEL
const mockCompareData = {
    strategies: [
        {
            id: 'strategy_1',
            name: 'Baseline Strategy',
            winrate: 52.3,
            expectancy: 2.45,
            avgR: 1.87,
            trades: 1898,
            stability: 75,
            sessions: {
                ASIA: 4.14,
                LONDON: 2.87,
                NY_PRE: 2.45,
                NY_AM: 3.21,
                NY_LUNCH: 1.87,
                NY_PM: 2.14
            }
        },
        {
            id: 'strategy_2',
            name: 'Conservative Strategy',
            winrate: 58.7,
            expectancy: 2.87,
            avgR: 2.14,
            trades: 842,
            stability: 82,
            sessions: {
                ASIA: 4.14,
                LONDON: 3.12,
                NY_PRE: 2.78,
                NY_AM: 2.98,
                NY_LUNCH: 2.34,
                NY_PM: 2.45
            }
        },
        {
            id: 'strategy_3',
            name: 'Aggressive Strategy',
            winrate: 48.2,
            expectancy: 3.12,
            avgR: 2.45,
            trades: 2456,
            stability: 68,
            sessions: {
                ASIA: 3.87,
                LONDON: 2.56,
                NY_PRE: 2.12,
                NY_AM: 3.45,
                NY_LUNCH: 1.98,
                NY_PM: 2.87
            }
        },
        {
            id: 'strategy_4',
            name: 'Volatility Strategy',
            winrate: 54.1,
            expectancy: 2.68,
            avgR: 1.98,
            trades: 1234,
            stability: 78,
            sessions: {
                ASIA: 3.98,
                LONDON: 2.98,
                NY_PRE: 2.34,
                NY_AM: 3.12,
                NY_LUNCH: 2.01,
                NY_PM: 2.34
            }
        },
        {
            id: 'strategy_5',
            name: 'Session Strategy',
            winrate: 61.4,
            expectancy: 4.14,
            avgR: 3.21,
            trades: 364,
            stability: 88,
            sessions: {
                ASIA: 4.14,
                LONDON: 0,
                NY_PRE: 0,
                NY_AM: 0,
                NY_LUNCH: 0,
                NY_PM: 0
            }
        },
        {
            id: 'strategy_6',
            name: 'NY-Only Strategy',
            winrate: 50.8,
            expectancy: 2.34,
            avgR: 1.76,
            trades: 987,
            stability: 72,
            sessions: {
                ASIA: 0,
                LONDON: 0,
                NY_PRE: 0,
                NY_AM: 3.21,
                NY_LUNCH: 1.87,
                NY_PM: 2.14
            }
        }
    ],
    comparisonData: {
        expectancyCurve: [
            { trade: 0, strategy_1: 0, strategy_2: 0, strategy_3: 0 },
            { trade: 100, strategy_1: 245, strategy_2: 287, strategy_3: 312 },
            { trade: 200, strategy_1: 490, strategy_2: 574, strategy_3: 624 }
        ],
        rDistribution: [
            { range: '0-1R', strategy_1: 450, strategy_2: 380, strategy_3: 520 },
            { range: '1-2R', strategy_1: 380, strategy_2: 320, strategy_3: 440 },
            { range: '2-3R', strategy_1: 290, strategy_2: 250, strategy_3: 350 }
        ]
    }
};

// CURRENT STATE
let selectedStrategies = [];

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('Compare page initialized');
    
    initializeAddStrategyButton();
    initializeModal();
    
    console.log('Mock data loaded successfully');
});

// ============================================
// ADD STRATEGY FUNCTIONALITY
// ============================================

function initializeAddStrategyButton() {
    const addBtn = document.getElementById('addStrategyCard');
    
    if (addBtn) {
        addBtn.addEventListener('click', function() {
            openStrategyModal();
        });
    }
}

function openStrategyModal() {
    const modal = document.getElementById('strategyModal');
    const strategyList = document.getElementById('strategyList');
    
    // Clear existing list
    strategyList.innerHTML = '';
    
    // Populate with available strategies (exclude already selected)
    const availableStrategies = mockCompareData.strategies.filter(s => 
        !selectedStrategies.find(selected => selected.id === s.id)
    );
    
    if (availableStrategies.length === 0) {
        strategyList.innerHTML = '<div style="text-align: center; padding: 40px; color: var(--text-muted);">All strategies have been added</div>';
    } else {
        availableStrategies.forEach(strategy => {
            const option = document.createElement('div');
            option.className = 'strategy-option';
            option.innerHTML = `
                <div class="strategy-option-name">${strategy.name}</div>
                <div class="strategy-option-details">
                    <span>Win Rate: ${strategy.winrate}%</span>
                    <span>Expectancy: ${strategy.expectancy}R</span>
                    <span>Trades: ${strategy.trades}</span>
                </div>
            `;
            
            option.addEventListener('click', function() {
                addStrategy(strategy);
                closeStrategyModal();
            });
            
            strategyList.appendChild(option);
        });
    }
    
    modal.classList.add('active');
}

function closeStrategyModal() {
    const modal = document.getElementById('strategyModal');
    modal.classList.remove('active');
}

function initializeModal() {
    const modalClose = document.getElementById('modalClose');
    const modal = document.getElementById('strategyModal');
    
    if (modalClose) {
        modalClose.addEventListener('click', closeStrategyModal);
    }
    
    // Close on background click
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeStrategyModal();
            }
        });
    }
}

// ============================================
// STRATEGY MANAGEMENT
// ============================================

function addStrategy(strategy) {
    selectedStrategies.push(strategy);
    renderStrategyCards();
    updateDeltaMetrics();
    updateComparisonCharts();
    
    console.log('Strategy added:', strategy.name);
}

function removeStrategy(strategyId) {
    selectedStrategies = selectedStrategies.filter(s => s.id !== strategyId);
    renderStrategyCards();
    updateDeltaMetrics();
    updateComparisonCharts();
    
    console.log('Strategy removed:', strategyId);
}

function renderStrategyCards() {
    const container = document.getElementById('strategyCardsContainer');
    
    if (!container) return;
    
    container.innerHTML = '';
    
    selectedStrategies.forEach(strategy => {
        const card = createStrategyCard(strategy);
        container.appendChild(card);
    });
}

function createStrategyCard(strategy) {
    const card = document.createElement('div');
    card.className = 'strategy-card';
    card.setAttribute('data-strategy-id', strategy.id);
    
    // Calculate max session value for bar scaling
    const maxSessionValue = Math.max(...Object.values(strategy.sessions));
    
    card.innerHTML = `
        <div class="strategy-card-header">
            <h3 class="strategy-name">${strategy.name}</h3>
            <button class="remove-btn" onclick="removeStrategy('${strategy.id}')">&times;</button>
        </div>
        
        <div class="strategy-metrics">
            <div class="strategy-metric">
                <div class="strategy-metric-label">Win Rate</div>
                <div class="strategy-metric-value">${strategy.winrate}%</div>
            </div>
            <div class="strategy-metric">
                <div class="strategy-metric-label">Expectancy</div>
                <div class="strategy-metric-value">${strategy.expectancy}R</div>
            </div>
            <div class="strategy-metric">
                <div class="strategy-metric-label">Avg R</div>
                <div class="strategy-metric-value">${strategy.avgR}R</div>
            </div>
            <div class="strategy-metric">
                <div class="strategy-metric-label">Trades</div>
                <div class="strategy-metric-value">${strategy.trades}</div>
            </div>
            <div class="strategy-metric">
                <div class="strategy-metric-label">Stability</div>
                <div class="strategy-metric-value">${strategy.stability}</div>
            </div>
        </div>
        
        <div class="session-performance">
            <h4>Session Performance</h4>
            <div class="session-bars">
                ${Object.entries(strategy.sessions).map(([session, value]) => `
                    <div class="session-bar">
                        <span class="session-name">${session}</span>
                        <div class="bar-container">
                            <div class="bar-fill" style="width: ${maxSessionValue > 0 ? (value / maxSessionValue * 100) : 0}%"></div>
                        </div>
                        <span class="session-value">${value.toFixed(2)}R</span>
                    </div>
                `).join('')}
            </div>
        </div>
        
        <div class="chart-placeholders">
            <div class="mini-chart-placeholder">
                <div class="mini-placeholder-text">R-Distribution</div>
            </div>
            <div class="mini-chart-placeholder">
                <div class="mini-placeholder-text">Equity Curve</div>
            </div>
        </div>
    `;
    
    return card;
}

// ============================================
// DELTA METRICS
// ============================================

function updateDeltaMetrics() {
    if (selectedStrategies.length < 2) {
        // Reset to default if less than 2 strategies
        document.getElementById('deltaExpectancy').textContent = '--';
        document.getElementById('deltaWinrate').textContent = '--';
        document.getElementById('deltaAvgR').textContent = '--';
        document.getElementById('deltaTrades').textContent = '--';
        document.getElementById('deltaStability').textContent = '--';
        
        // Remove color classes
        ['deltaExpectancy', 'deltaWinrate', 'deltaAvgR', 'deltaTrades', 'deltaStability'].forEach(id => {
            const el = document.getElementById(id);
            el.classList.remove('positive', 'negative');
        });
        
        return;
    }
    
    // Calculate deltas between first and last strategy
    const first = selectedStrategies[0];
    const last = selectedStrategies[selectedStrategies.length - 1];
    
    const deltaExpectancy = last.expectancy - first.expectancy;
    const deltaWinrate = last.winrate - first.winrate;
    const deltaAvgR = last.avgR - first.avgR;
    const deltaTrades = last.trades - first.trades;
    const deltaStability = last.stability - first.stability;
    
    // Update display
    updateDeltaMetric('deltaExpectancy', deltaExpectancy, 'R');
    updateDeltaMetric('deltaWinrate', deltaWinrate, '%');
    updateDeltaMetric('deltaAvgR', deltaAvgR, 'R');
    updateDeltaMetric('deltaTrades', deltaTrades, '');
    updateDeltaMetric('deltaStability', deltaStability, '');
}

function updateDeltaMetric(elementId, value, suffix) {
    const element = document.getElementById(elementId);
    
    if (!element) return;
    
    const sign = value > 0 ? '+' : '';
    element.textContent = `${sign}${value.toFixed(2)}${suffix}`;
    
    // Add color class
    element.classList.remove('positive', 'negative');
    if (value > 0) {
        element.classList.add('positive');
    } else if (value < 0) {
        element.classList.add('negative');
    }
}

// ============================================
// COMPARISON CHARTS
// ============================================

function updateComparisonCharts() {
    console.log('Updating comparison charts for', selectedStrategies.length, 'strategies');
    
    // In Phase 1, charts are placeholders
    // Future phases will render actual charts here
}

// ============================================
// DATASET SELECTOR
// ============================================

const datasetSelect = document.getElementById('datasetSelect');
if (datasetSelect) {
    datasetSelect.addEventListener('change', function() {
        console.log('Dataset changed to:', this.value);
        // Would reload data in Phase 2+
    });
}

// ============================================
// DATE RANGE SELECTOR
// ============================================

const startDate = document.getElementById('startDate');
const endDate = document.getElementById('endDate');

if (startDate) {
    startDate.addEventListener('change', function() {
        console.log('Start date changed to:', this.value);
        // Would filter data in Phase 2+
    });
}

if (endDate) {
    endDate.addEventListener('change', function() {
        console.log('End date changed to:', this.value);
        // Would filter data in Phase 2+
    });
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function formatNumber(num, decimals = 2) {
    return num.toFixed(decimals);
}

function formatPercentage(num, decimals = 1) {
    return `${num.toFixed(decimals)}%`;
}

function formatR(num, decimals = 2) {
    return `${num.toFixed(decimals)}R`;
}

// ============================================
// CONSOLE LOG CONFIRMATION
// ============================================

console.log('Compare JS loaded successfully');
console.log('Mock data available:', mockCompareData);
console.log('No backend calls - Phase 1 mock data only');
