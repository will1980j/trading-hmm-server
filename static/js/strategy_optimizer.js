// ============================================
// STRATEGY OPTIMIZER - PHASE 1 MOCK DATA
// ============================================

// MOCK DATA MODEL
const mockOptimizerData = {
    configurations: [
        {
            id: 'config_1',
            name: 'NY AM + Low Vol',
            winrate: 52.3,
            expectancy: 2.45,
            avgR: 1.87,
            trades: 1898,
            sessions: {
                ASIA: 4.14,
                LONDON: 2.87,
                NY_AM: 3.21,
                NY_PM: 2.14
            }
        },
        {
            id: 'config_2',
            name: 'Conservative',
            winrate: 58.7,
            expectancy: 2.87,
            avgR: 2.14,
            trades: 842,
            sessions: {
                ASIA: 4.14,
                LONDON: 3.12,
                NY_AM: 2.98,
                NY_PM: 2.45
            }
        }
    ],
    variants: [
        {
            id: 'baseline',
            name: 'Baseline Strategy',
            winrate: 52.3,
            expectancy: 2.45,
            trades: 1898,
            avgR: 1.87,
            description: 'Standard configuration with all sessions and default parameters'
        },
        {
            id: 'conservative',
            name: 'Conservative Strategy',
            winrate: 58.7,
            expectancy: 2.87,
            trades: 842,
            avgR: 2.14,
            description: 'Higher confirmation requirements, lower volatility sessions only'
        },
        {
            id: 'aggressive',
            name: 'Aggressive Strategy',
            winrate: 48.2,
            expectancy: 3.12,
            trades: 2456,
            avgR: 2.45,
            description: 'Lower confirmation requirements, all sessions, higher R targets'
        },
        {
            id: 'volatility',
            name: 'Volatility Strategy',
            winrate: 54.1,
            expectancy: 2.68,
            trades: 1234,
            avgR: 1.98,
            description: 'Adapts parameters based on real-time volatility conditions'
        },
        {
            id: 'session',
            name: 'Session Strategy',
            winrate: 61.4,
            expectancy: 4.14,
            trades: 364,
            avgR: 3.21,
            description: 'Optimized for ASIA session only with custom parameters'
        },
        {
            id: 'ny-only',
            name: 'NY-Only Strategy',
            winrate: 50.8,
            expectancy: 2.34,
            trades: 987,
            avgR: 1.76,
            description: 'NY AM and NY PM sessions only, optimized for US market hours'
        }
    ],
    charts: {
        expectancy_curve: [
            { x: 0, baseline: 0, conservative: 0, aggressive: 0 },
            { x: 100, baseline: 245, conservative: 287, aggressive: 312 },
            { x: 200, baseline: 490, conservative: 574, aggressive: 624 }
        ],
        r_distribution: [
            { r: '0-1R', count: 450 },
            { r: '1-2R', count: 380 },
            { r: '2-3R', count: 290 },
            { r: '3-4R', count: 210 },
            { r: '4-5R', count: 150 }
        ],
        equity_curve: [
            { trade: 0, equity: 0 },
            { trade: 100, equity: 245 },
            { trade: 200, equity: 490 },
            { trade: 300, equity: 735 }
        ]
    }
};

// CURRENT STATE
let currentMode = 'configuration';
let currentConfig = mockOptimizerData.configurations[0];
let selectedVariants = ['baseline', 'conservative', 'aggressive'];

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('Strategy Optimizer initialized');
    
    initializeTabSwitcher();
    initializeSliders();
    initializeConfigControls();
    initializeVariantCards();
    
    // Load initial data
    loadConfigurationData();
    loadVariantData();
    
    console.log('Mock data loaded successfully');
});

// ============================================
// TAB SWITCHING
// ============================================

function initializeTabSwitcher() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    
    tabButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const mode = this.getAttribute('data-mode');
            switchMode(mode);
        });
    });
}

function switchMode(mode) {
    currentMode = mode;
    
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-mode') === mode) {
            btn.classList.add('active');
        }
    });
    
    // Show/hide sections
    const configSection = document.getElementById('configurationSection');
    const variantSection = document.getElementById('variantSection');
    
    if (mode === 'configuration') {
        configSection.classList.remove('hidden');
        variantSection.classList.add('hidden');
    } else {
        configSection.classList.add('hidden');
        variantSection.classList.remove('hidden');
    }
    
    console.log(`Switched to ${mode} mode`);
}

// ============================================
// SLIDER CONTROLS
// ============================================

function initializeSliders() {
    // Volatility slider
    const volatilitySlider = document.getElementById('volatilitySlider');
    const volatilityValue = document.getElementById('volatilityValue');
    
    if (volatilitySlider) {
        volatilitySlider.addEventListener('input', function() {
            volatilityValue.textContent = this.value;
        });
    }
    
    // Time slider
    const timeSlider = document.getElementById('timeSlider');
    const timeValue = document.getElementById('timeValue');
    
    if (timeSlider) {
        timeSlider.addEventListener('input', function() {
            timeValue.textContent = this.value;
        });
    }
    
    // Min R slider
    const minRSlider = document.getElementById('minRSlider');
    const minRValue = document.getElementById('minRValue');
    
    if (minRSlider) {
        minRSlider.addEventListener('input', function() {
            minRValue.textContent = parseFloat(this.value).toFixed(1);
        });
    }
    
    // Max R slider
    const maxRSlider = document.getElementById('maxRSlider');
    const maxRValue = document.getElementById('maxRValue');
    
    if (maxRSlider) {
        maxRSlider.addEventListener('input', function() {
            maxRValue.textContent = this.value;
        });
    }
}

// ============================================
// CONFIGURATION CONTROLS
// ============================================

function initializeConfigControls() {
    const applyBtn = document.querySelector('.apply-config-btn');
    
    if (applyBtn) {
        applyBtn.addEventListener('click', function() {
            applyConfiguration();
        });
    }
}

function applyConfiguration() {
    console.log('Applying configuration...');
    
    // Get selected values
    const confirmationType = document.getElementById('confirmationType').value;
    const stopLossLogic = document.getElementById('stopLossLogic').value;
    const selectedSessions = getSelectedSessions();
    const volatility = document.getElementById('volatilitySlider').value;
    const timeOfDay = document.getElementById('timeSlider').value;
    const minR = document.getElementById('minRSlider').value;
    const maxR = document.getElementById('maxRSlider').value;
    
    console.log('Configuration:', {
        confirmationType,
        stopLossLogic,
        selectedSessions,
        volatility,
        timeOfDay,
        minR,
        maxR
    });
    
    // Update results with mock data
    updateConfigurationResults();
    
    // Show feedback
    showConfigurationFeedback();
}

function getSelectedSessions() {
    const checkboxes = document.querySelectorAll('.session-checkboxes input[type="checkbox"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

function updateConfigurationResults() {
    // Update metrics with mock data
    document.getElementById('configWinrate').textContent = '52.3%';
    document.getElementById('configExpectancy').textContent = '2.45R';
    document.getElementById('configAvgR').textContent = '1.87R';
    
    console.log('Configuration results updated');
}

function showConfigurationFeedback() {
    const btn = document.querySelector('.apply-config-btn');
    const originalText = btn.textContent;
    
    btn.textContent = 'Configuration Applied ✓';
    btn.style.background = 'linear-gradient(135deg, #10B981, #059669)';
    
    setTimeout(() => {
        btn.textContent = originalText;
        btn.style.background = 'linear-gradient(135deg, var(--accent-start), var(--accent-end))';
    }, 2000);
}

// ============================================
// CONFIGURATION DATA LOADING
// ============================================

function loadConfigurationData() {
    const config = mockOptimizerData.configurations[0];
    
    // Update metric summary
    document.getElementById('bestConfig').textContent = config.name;
    document.getElementById('highestExpectancy').textContent = `${config.expectancy}R`;
    
    // Update results
    document.getElementById('configWinrate').textContent = `${config.winrate}%`;
    document.getElementById('configExpectancy').textContent = `${config.expectancy}R`;
    document.getElementById('configAvgR').textContent = `${config.avgR}R`;
    
    console.log('Configuration data loaded');
}

// ============================================
// VARIANT CARDS
// ============================================

function initializeVariantCards() {
    const variantCards = document.querySelectorAll('.variant-card');
    
    variantCards.forEach(card => {
        card.addEventListener('click', function() {
            const variantId = this.getAttribute('data-variant');
            toggleVariantSelection(variantId, this);
        });
    });
}

function toggleVariantSelection(variantId, cardElement) {
    const index = selectedVariants.indexOf(variantId);
    
    if (index > -1) {
        // Deselect
        selectedVariants.splice(index, 1);
        cardElement.style.borderColor = 'var(--border-color)';
    } else {
        // Select
        selectedVariants.push(variantId);
        cardElement.style.borderColor = 'var(--accent-start)';
    }
    
    console.log('Selected variants:', selectedVariants);
    updateVariantComparison();
}

function updateVariantComparison() {
    console.log('Updating variant comparison for:', selectedVariants);
    // Comparison charts would be updated here in Phase 2+
}

// ============================================
// VARIANT DATA LOADING
// ============================================

function loadVariantData() {
    // Update metric summary
    const bestVariant = mockOptimizerData.variants.find(v => v.id === 'session');
    document.getElementById('bestVariant').textContent = bestVariant.name.replace(' Strategy', '');
    
    // Update stability metrics
    document.querySelector('.stability-value').textContent = '0.82';
    
    console.log('Variant data loaded');
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

console.log('Strategy Optimizer JS loaded successfully');
console.log('Mock data available:', mockOptimizerData);
console.log('No backend calls - Phase 1 mock data only');
