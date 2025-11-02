# 🚀 Monte Carlo Enhancement - Deployment Instructions

## Quick Start

This guide shows exactly what to change in `strategy_comparison.html` to add the enhanced Monte Carlo simulation with equity curves.

## Changes Required

### 1. Find the Monte Carlo HTML Section (Line ~2273)

**FIND THIS:**
```html
<!-- Monte Carlo Simulation -->
<div class="monte-carlo-section" style="position: relative; z-index: 1;">
    <div class="section-header" style="margin-bottom: 12px;">
        <h4 style="color: var(--accent-primary); margin: 0; display: flex; align-items: center; gap: 8px; font-size: 16px;">
            🎲 Monte Carlo Simulation
            <span style="font-size: 11px; color: var(--text-secondary); font-weight: normal;">1,000 Possible Futures</span>
        </h4>
    </div>
    <div class="monte-carlo-container" style="background: var(--bg-tertiary); border-radius: 8px; padding: 12px; border: 1px solid var(--border-color);">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
            <button id="runMonteCarloBtn" class="btn-primary" style="padding: 10px 20px; font-size: 13px; display: flex; align-items: center; gap: 6px;">
                <span>🚀</span>
                <span>Run 1,000 Simulations</span>
            </button>
```

**REPLACE WITH:**
```html
<!-- Monte Carlo Simulation -->
<div class="monte-carlo-section" style="position: relative; z-index: 1;">
    <div class="section-header" style="margin-bottom: 12px;">
        <h4 style="color: var(--accent-primary); margin: 0; display: flex; align-items: center; gap: 8px; font-size: 16px;">
            🎲 Monte Carlo Simulation
            <span style="font-size: 11px; color: var(--text-secondary); font-weight: normal;">Customizable Equity Curve Analysis</span>
        </h4>
    </div>
    <div class="monte-carlo-container" style="background: var(--bg-tertiary); border-radius: 8px; padding: 12px; border: 1px solid var(--border-color);">
        
        <!-- NEW: Simulation Options Panel -->
        <div class="simulation-options" style="background: rgba(59, 130, 246, 0.05); border-radius: 8px; padding: 16px; margin-bottom: 16px; border: 1px solid rgba(59, 130, 246, 0.2);">
            <h5 style="color: var(--text-primary); margin: 0 0 12px 0; font-size: 14px;">⚙️ Simulation Parameters</h5>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px;">
                <div>
                    <label style="font-size: 11px; color: var(--text-secondary); margin-bottom: 4px; display: block;">Simulations</label>
                    <select id="mcNumSimulations" style="width: 100%; padding: 6px; background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 4px; color: var(--text-primary); font-size: 12px;">
                        <option value="100">100 (Fast)</option>
                        <option value="500">500 (Balanced)</option>
                        <option value="1000" selected>1,000 (Standard)</option>
                        <option value="5000">5,000 (Detailed)</option>
                    </select>
                </div>
                
                <div>
                    <label style="font-size: 11px; color: var(--text-secondary); margin-bottom: 4px; display: block;">Trades per Sim</label>
                    <select id="mcTradeLength" style="width: 100%; padding: 6px; background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 4px; color: var(--text-primary); font-size: 12px;">
                        <option value="actual">Actual (${strategy.stats.total})</option>
                        <option value="100">100 trades</option>
                        <option value="250" selected>250 trades</option>
                        <option value="500">500 trades</option>
                    </select>
                </div>
                
                <div>
                    <label style="font-size: 11px; color: var(--text-secondary); margin-bottom: 4px; display: block;">Starting Capital</label>
                    <input type="number" id="mcStartingCapital" value="100000" min="1000" step="1000"
                           style="width: 100%; padding: 6px; background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 4px; color: var(--text-primary); font-size: 12px;">
                </div>
                
                <div>
                    <label style="font-size: 11px; color: var(--text-secondary); margin-bottom: 4px; display: block;">Risk Per Trade (%)</label>
                    <input type="number" id="mcRiskPercent" value="${strategy.riskPerTrade || 1}" min="0.1" max="5" step="0.1"
                           style="width: 100%; padding: 6px; background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 4px; color: var(--text-primary); font-size: 12px;">
                </div>
                
                <div>
                    <label style="font-size: 11px; color: var(--text-secondary); margin-bottom: 4px; display: block;">Sampling Method</label>
                    <select id="mcSamplingMethod" style="width: 100%; padding: 6px; background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 4px; color: var(--text-primary); font-size: 12px;">
                        <option value="bootstrap" selected>Bootstrap</option>
                        <option value="parametric">Parametric</option>
                    </select>
                </div>
                
                <div>
                    <label style="font-size: 11px; color: var(--text-secondary); margin-bottom: 4px; display: block;">Display</label>
                    <div style="display: flex; flex-direction: column; gap: 4px; padding-top: 2px;">
                        <label style="display: flex; align-items: center; gap: 6px; cursor: pointer;">
                            <input type="checkbox" id="mcShowPercentiles" checked style="accent-color: var(--accent-primary);">
                            <span style="font-size: 11px; color: var(--text-primary);">Percentile Bands</span>
                        </label>
                        <label style="display: flex; align-items: center; gap: 6px; cursor: pointer;">
                            <input type="checkbox" id="mcShowIndividual" style="accent-color: var(--accent-primary);">
                            <span style="font-size: 11px; color: var(--text-primary);">Individual Curves</span>
                        </label>
                    </div>
                </div>
            </div>
        </div>
        
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
            <button id="runMonteCarloBtn" class="btn-primary" style="padding: 10px 20px; font-size: 13px; display: flex; align-items: center; gap: 6px;">
                <span>🚀</span>
                <span>Run Simulation</span>
            </button>
```

### 2. Replace Results Display Section

**FIND THIS (around line 2292):**
```html
<div id="monteCarloResults" style="display: none;">
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 12px;">
        <div id="finalEquityChart" style="background: var(--bg-primary); border-radius: 6px; padding: 10px; border: 1px solid var(--border-color);">
            <h6 style="color: var(--text-primary); margin: 0 0 8px 0; font-size: 12px;">Final Equity Distribution</h6>
            <canvas id="equityHistogram" width="180" height="100"></canvas>
        </div>
```

**REPLACE WITH:**
```html
<div id="monteCarloResults" style="display: none;">
    <div style="background: var(--bg-primary); border-radius: 8px; padding: 16px; margin-bottom: 16px; border: 1px solid var(--border-color);">
        <h5 style="color: var(--text-primary); margin: 0 0 12px 0; font-size: 14px;">📈 Equity Curve Simulations</h5>
        <div id="mcEquityCurveChart" style="width: 100%; height: 400px;"></div>
    </div>
    <div id="mcStatistics"></div>
</div>
```

### 3. Update setupMonteCarloSimulation Function (around line 2873)

**FIND THIS:**
```javascript
function setupMonteCarloSimulation(strategy, winRate, results) {
    const runBtn = document.getElementById('runMonteCarloBtn');
    if (!runBtn) return;
```

**ADD THIS COMPLETE REPLACEMENT:**

See `MONTE_CARLO_ENHANCEMENT_SPEC.md` for the complete function code (too long for this summary).

Key changes:
- Read options from UI controls
- Pass options to simulation
- Update button text dynamically
- Show progress with simulation count

### 4. Add New renderEquityCurveChart Function

Add this new function after setupMonteCarloSimulation:

```javascript
function renderEquityCurveChart(results, options) {
    // See MONTE_CARLO_ENHANCEMENT_SPEC.md for complete code
    // This function creates the D3.js equity curve visualization
}
```

### 5. Update displayMonteCarloResults Function

Replace the existing function with enhanced version that:
- Calls renderEquityCurveChart
- Displays enhanced statistics
- Shows percentile information

## Testing Steps

1. **Open Strategy Comparison page**
2. **Run a comparison** to get strategies
3. **Click "View"** on any strategy
4. **Go to "Risk" tab**
5. **Scroll to Monte Carlo section**
6. **Verify options panel appears**
7. **Change some options**
8. **Click "Run Simulation"**
9. **Verify equity curve renders**
10. **Check statistics display**

## Expected Result

You should see:
- ✅ Options panel with 6 controls
- ✅ Equity curve chart with percentile bands
- ✅ Median line in green
- ✅ Statistics showing best/median/worst cases
- ✅ Success rate percentage
- ✅ Professional D3.js visualization

## Rollback Plan

If issues occur:
1. Revert to previous version via Git
2. Or comment out new options panel
3. Keep old histogram display as fallback

---

**Ready to Deploy!** 🚀

For complete code examples, see `MONTE_CARLO_ENHANCEMENT_SPEC.md`
