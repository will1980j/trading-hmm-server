# 🎲 Enhanced Monte Carlo Simulation with Equity Curves

## 🎯 Enhancement Goals

Transform the current Monte Carlo simulation from simple histograms to an interactive equity curve visualization with customizable simulation parameters.

## 📊 Current State

The existing Monte Carlo simulation shows:
- Final equity distribution histogram
- Max drawdown distribution histogram  
- Loss streak distribution histogram
- Summary statistics

## 🚀 Enhanced Features to Add

### 1. Interactive Simulation Options

Add controls BEFORE running simulation:

```html
<div class="simulation-options" style="background: var(--bg-tertiary); border-radius: 8px; padding: 16px; margin-bottom: 16px; border: 1px solid var(--border-color);">
    <h5 style="color: var(--text-primary); margin-bottom: 12px;">Simulation Parameters</h5>
    
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">
        <!-- Number of Simulations -->
        <div>
            <label style="font-size: 12px; color: var(--text-secondary); margin-bottom: 4px; display: block;">
                Number of Simulations
            </label>
            <select id="mcNumSimulations" style="width: 100%; padding: 8px; background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 4px; color: var(--text-primary);">
                <option value="100">100 (Fast)</option>
                <option value="500">500 (Balanced)</option>
                <option value="1000" selected>1,000 (Standard)</option>
                <option value="5000">5,000 (Detailed)</option>
                <option value="10000">10,000 (Comprehensive)</option>
            </select>
        </div>
        
        <!-- Trade Sequence Length -->
        <div>
            <label style="font-size: 12px; color: var(--text-secondary); margin-bottom: 4px; display: block;">
                Trades per Simulation
            </label>
            <select id="mcTradeLength" style="width: 100%; padding: 8px; background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 4px; color: var(--text-primary);">
                <option value="actual">Actual (${strategy.stats.total})</option>
                <option value="50">50 trades</option>
                <option value="100">100 trades</option>
                <option value="250" selected>250 trades</option>
                <option value="500">500 trades</option>
                <option value="1000">1,000 trades</option>
            </select>
        </div>
        
        <!-- Starting Capital -->
        <div>
            <label style="font-size: 12px; color: var(--text-secondary); margin-bottom: 4px; display: block;">
                Starting Capital ($)
            </label>
            <input type="number" id="mcStartingCapital" value="100000" min="1000" max="10000000" step="1000"
                   style="width: 100%; padding: 8px; background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 4px; color: var(--text-primary);">
        </div>
        
        <!-- Risk Per Trade -->
        <div>
            <label style="font-size: 12px; color: var(--text-secondary); margin-bottom: 4px; display: block;">
                Risk Per Trade (%)
            </label>
            <input type="number" id="mcRiskPercent" value="${strategy.riskPerTrade || 1}" min="0.1" max="5" step="0.1"
                   style="width: 100%; padding: 8px; background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 4px; color: var(--text-primary);">
        </div>
        
        <!-- Sampling Method -->
        <div>
            <label style="font-size: 12px; color: var(--text-secondary); margin-bottom: 4px; display: block;">
                Sampling Method
            </label>
            <select id="mcSamplingMethod" style="width: 100%; padding: 8px; background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 4px; color: var(--text-primary);">
                <option value="bootstrap" selected>Bootstrap (Resample actual trades)</option>
                <option value="parametric">Parametric (Use win rate & expectancy)</option>
                <option value="sequential">Sequential (Preserve order)</option>
            </select>
        </div>
        
        <!-- Show Options -->
        <div>
            <label style="font-size: 12px; color: var(--text-secondary); margin-bottom: 4px; display: block;">
                Display Options
            </label>
            <div style="display: flex; flex-direction: column; gap: 4px;">
                <label style="display: flex; align-items: center; gap: 6px; cursor: pointer;">
                    <input type="checkbox" id="mcShowPercentiles" checked style="accent-color: var(--accent-primary);">
                    <span style="font-size: 12px; color: var(--text-primary);">Show Percentile Bands</span>
                </label>
                <label style="display: flex; align-items: center; gap: 6px; cursor: pointer;">
                    <input type="checkbox" id="mcShowIndividual" style="accent-color: var(--accent-primary);">
                    <span style="font-size: 12px; color: var(--text-primary);">Show Individual Curves</span>
                </label>
            </div>
        </div>
    </div>
</div>
```

### 2. Equity Curve Visualization

Replace histograms with D3.js equity curve chart:

```javascript
function displayMonteCarloResults(results, options) {
    const resultsContainer = document.getElementById('monteCarloResults');
    resultsContainer.style.display = 'block';
    
    // Create main equity curve chart
    const chartHtml = `
        <div style="background: var(--bg-primary); border-radius: 8px; padding: 16px; margin-bottom: 16px; border: 1px solid var(--border-color);">
            <h5 style="color: var(--text-primary); margin-bottom: 12px;">Equity Curve Simulations</h5>
            <div id="mcEquityCurveChart" style="width: 100%; height: 400px;"></div>
        </div>
    `;
    
    resultsContainer.innerHTML = chartHtml + getStatisticsHtml(results);
    
    // Render D3 chart
    renderEquityCurveChart(results, options);
}

function renderEquityCurveChart(results, options) {
    const container = d3.select('#mcEquityCurveChart');
    container.selectAll('*').remove();
    
    const margin = {top: 20, right: 30, bottom: 40, left: 60};
    const width = container.node().getBoundingClientRect().width - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;
    
    const svg = container.append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // Calculate percentiles for each trade number
    const numTrades = results[0].equityCurve.length;
    const percentileData = [];
    
    for (let i = 0; i < numTrades; i++) {
        const values = results.map(r => r.equityCurve[i]).sort((a, b) => a - b);
        percentileData.push({
            trade: i,
            p5: d3.quantile(values, 0.05),
            p25: d3.quantile(values, 0.25),
            p50: d3.quantile(values, 0.50),
            p75: d3.quantile(values, 0.75),
            p95: d3.quantile(values, 0.95)
        });
    }
    
    // Scales
    const xScale = d3.scaleLinear()
        .domain([0, numTrades - 1])
        .range([0, width]);
    
    const allValues = results.flatMap(r => r.equityCurve);
    const yScale = d3.scaleLinear()
        .domain([d3.min(allValues) * 0.95, d3.max(allValues) * 1.05])
        .range([height, 0]);
    
    // Axes
    svg.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(xScale))
        .style('color', '#94a3b8');
    
    svg.append('g')
        .call(d3.axisLeft(yScale).tickFormat(d => '$' + (d/1000).toFixed(0) + 'K'))
        .style('color', '#94a3b8');
    
    // Grid lines
    svg.append('g')
        .attr('class', 'grid')
        .attr('opacity', 0.1)
        .call(d3.axisLeft(yScale)
            .tickSize(-width)
            .tickFormat(''));
    
    // Percentile bands
    if (options.showPercentiles) {
        // 5-95 percentile band (lightest)
        const area95 = d3.area()
            .x(d => xScale(d.trade))
            .y0(d => yScale(d.p5))
            .y1(d => yScale(d.p95))
            .curve(d3.curveMonotoneX);
        
        svg.append('path')
            .datum(percentileData)
            .attr('fill', '#3b82f6')
            .attr('fill-opacity', 0.1)
            .attr('d', area95);
        
        // 25-75 percentile band (darker)
        const area75 = d3.area()
            .x(d => xScale(d.trade))
            .y0(d => yScale(d.p25))
            .y1(d => yScale(d.p75))
            .curve(d3.curveMonotoneX);
        
        svg.append('path')
            .datum(percentileData)
            .attr('fill', '#3b82f6')
            .attr('fill-opacity', 0.2)
            .attr('d', area75);
    }
    
    // Median line (bold)
    const medianLine = d3.line()
        .x(d => xScale(d.trade))
        .y(d => yScale(d.p50))
        .curve(d3.curveMonotoneX);
    
    svg.append('path')
        .datum(percentileData)
        .attr('fill', 'none')
        .attr('stroke', '#00ff88')
        .attr('stroke-width', 3)
        .attr('d', medianLine);
    
    // Individual curves (if enabled)
    if (options.showIndividual) {
        const line = d3.line()
            .x((d, i) => xScale(i))
            .y(d => yScale(d))
            .curve(d3.curveMonotoneX);
        
        // Show max 50 individual curves to avoid clutter
        const sampled = results.slice(0, Math.min(50, results.length));
        
        sampled.forEach(result => {
            svg.append('path')
                .datum(result.equityCurve)
                .attr('fill', 'none')
                .attr('stroke', '#3b82f6')
                .attr('stroke-width', 0.5)
                .attr('stroke-opacity', 0.3)
                .attr('d', line);
        });
    }
    
    // Starting capital line
    svg.append('line')
        .attr('x1', 0)
        .attr('x2', width)
        .attr('y1', yScale(options.startingCapital))
        .attr('y2', yScale(options.startingCapital))
        .attr('stroke', '#f59e0b')
        .attr('stroke-width', 1)
        .attr('stroke-dasharray', '5,5')
        .attr('opacity', 0.5);
    
    // Labels
    svg.append('text')
        .attr('x', width / 2)
        .attr('y', height + 35)
        .attr('text-anchor', 'middle')
        .attr('fill', '#94a3b8')
        .style('font-size', '12px')
        .text('Trade Number');
    
    svg.append('text')
        .attr('transform', 'rotate(-90)')
        .attr('x', -height / 2)
        .attr('y', -45)
        .attr('text-anchor', 'middle')
        .attr('fill', '#94a3b8')
        .style('font-size', '12px')
        .text('Account Equity ($)');
    
    // Legend
    const legend = svg.append('g')
        .attr('transform', `translate(${width - 150}, 10)`);
    
    if (options.showPercentiles) {
        legend.append('rect')
            .attr('x', 0)
            .attr('y', 0)
            .attr('width', 20)
            .attr('height', 10)
            .attr('fill', '#3b82f6')
            .attr('opacity', 0.1);
        
        legend.append('text')
            .attr('x', 25)
            .attr('y', 9)
            .attr('fill', '#94a3b8')
            .style('font-size', '10px')
            .text('5-95 Percentile');
        
        legend.append('rect')
            .attr('x', 0)
            .attr('y', 15)
            .attr('width', 20)
            .attr('height', 10)
            .attr('fill', '#3b82f6')
            .attr('opacity', 0.2);
        
        legend.append('text')
            .attr('x', 25)
            .attr('y', 24)
            .attr('fill', '#94a3b8')
            .style('font-size', '10px')
            .text('25-75 Percentile');
    }
    
    legend.append('line')
        .attr('x1', 0)
        .attr('x2', 20)
        .attr('y1', 35)
        .attr('y2', 35)
        .attr('stroke', '#00ff88')
        .attr('stroke-width', 3);
    
    legend.append('text')
        .attr('x', 25)
        .attr('y', 39)
        .attr('fill', '#94a3b8')
        .style('font-size', '10px')
        .text('Median');
}
```

### 3. Enhanced Statistics Display

```javascript
function getStatisticsHtml(results) {
    const finalEquities = results.map(r => r.finalEquity).sort((a, b) => a - b);
    const maxDrawdowns = results.map(r => r.maxDrawdown).sort((a, b) => a - b);
    
    const profitable = results.filter(r => r.finalEquity > r.startingCapital).length;
    const profitablePercent = (profitable / results.length) * 100;
    
    return `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 16px; margin-bottom: 16px;">
            <!-- Final Equity Stats -->
            <div style="background: var(--bg-tertiary); border-radius: 8px; padding: 16px; border: 1px solid var(--border-color);">
                <h6 style="color: var(--text-secondary); margin: 0 0 12px 0; font-size: 12px; text-transform: uppercase;">Final Equity</h6>
                <div style="display: grid; gap: 8px;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-secondary); font-size: 12px;">Best Case (95%):</span>
                        <span style="color: #00ff88; font-weight: 600;">$${d3.quantile(finalEquities, 0.95).toFixed(0)}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-secondary); font-size: 12px;">Median (50%):</span>
                        <span style="color: var(--text-primary); font-weight: 600;">$${d3.quantile(finalEquities, 0.50).toFixed(0)}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-secondary); font-size: 12px;">Worst Case (5%):</span>
                        <span style="color: #ef4444; font-weight: 600;">$${d3.quantile(finalEquities, 0.05).toFixed(0)}</span>
                    </div>
                </div>
            </div>
            
            <!-- Drawdown Stats -->
            <div style="background: var(--bg-tertiary); border-radius: 8px; padding: 16px; border: 1px solid var(--border-color);">
                <h6 style="color: var(--text-secondary); margin: 0 0 12px 0; font-size: 12px; text-transform: uppercase;">Max Drawdown</h6>
                <div style="display: grid; gap: 8px;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-secondary); font-size: 12px;">Best Case (5%):</span>
                        <span style="color: #00ff88; font-weight: 600;">-${d3.quantile(maxDrawdowns, 0.05).toFixed(1)}%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-secondary); font-size: 12px;">Median (50%):</span>
                        <span style="color: var(--text-primary); font-weight: 600;">-${d3.quantile(maxDrawdowns, 0.50).toFixed(1)}%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-secondary); font-size: 12px;">Worst Case (95%):</span>
                        <span style="color: #ef4444; font-weight: 600;">-${d3.quantile(maxDrawdowns, 0.95).toFixed(1)}%</span>
                    </div>
                </div>
            </div>
            
            <!-- Success Rate -->
            <div style="background: var(--bg-tertiary); border-radius: 8px; padding: 16px; border: 1px solid var(--border-color);">
                <h6 style="color: var(--text-secondary); margin: 0 0 12px 0; font-size: 12px; text-transform: uppercase;">Success Rate</h6>
                <div style="text-align: center;">
                    <div style="font-size: 48px; font-weight: 700; color: ${profitablePercent >= 75 ? '#00ff88' : profitablePercent >= 50 ? '#f59e0b' : '#ef4444'};">
                        ${profitablePercent.toFixed(0)}%
                    </div>
                    <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">
                        ${profitable} of ${results.length} simulations profitable
                    </div>
                </div>
            </div>
        </div>
        
        <div style="padding: 16px; background: rgba(59, 130, 246, 0.05); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 8px;">
            <strong style="color: var(--accent-primary);">Monte Carlo Insight:</strong>
            <span style="color: var(--text-primary);">
                ${profitablePercent >= 80 ? 
                    `Excellent strategy - ${profitablePercent.toFixed(0)}% of simulations were profitable` :
                  profitablePercent >= 60 ?
                    `Good strategy - ${profitablePercent.toFixed(0)}% success rate with manageable risk` :
                  profitablePercent >= 40 ?
                    `Moderate strategy - ${profitablePercent.toFixed(0)}% success rate, consider risk management` :
                    `High risk strategy - only ${profitablePercent.toFixed(0)}% of simulations were profitable`
                }
            </span>
        </div>
    `;
}
```

### 4. Updated Simulation Logic

```javascript
function runMonteCarloSimulation(strategy, results, options) {
    const numSimulations = parseInt(options.numSimulations);
    const numTrades = options.tradeLength === 'actual' ? results.length : parseInt(options.tradeLength);
    const startingCapital = parseFloat(options.startingCapital);
    const riskPercent = parseFloat(options.riskPercent) / 100;
    const samplingMethod = options.samplingMethod;
    
    const simulations = [];
    
    for (let sim = 0; sim < numSimulations; sim++) {
        let equity = startingCapital;
        const equityCurve = [equity];
        let peak = equity;
        let maxDrawdown = 0;
        let maxConsecLosses = 0;
        let currentConsecLosses = 0;
        
        for (let trade = 0; trade < numTrades; trade++) {
            let tradeResult;
            
            // Sample based on method
            if (samplingMethod === 'bootstrap') {
                // Random sampling with replacement
                tradeResult = results[Math.floor(Math.random() * results.length)];
            } else if (samplingMethod === 'parametric') {
                // Generate based on win rate and expectancy
                const isWin = Math.random() < strategy.stats.winRate / 100;
                tradeResult = isWin ? 
                    (Math.random() * 2 + 1) : // Win: 1-3R
                    -1; // Loss: -1R
            } else {
                // Sequential (preserve order)
                tradeResult = results[trade % results.length];
            }
            
            // Apply trade result
            const positionSize = equity * riskPercent;
            const dollarResult = positionSize * tradeResult;
            equity += dollarResult;
            equityCurve.push(equity);
            
            // Track drawdown
            if (equity > peak) {
                peak = equity;
            }
            const currentDrawdown = ((peak - equity) / peak) * 100;
            maxDrawdown = Math.max(maxDrawdown, currentDrawdown);
            
            // Track loss streaks
            if (tradeResult < 0) {
                currentConsecLosses++;
                maxConsecLosses = Math.max(maxConsecLosses, currentConsecLosses);
            } else if (tradeResult > 0) {
                currentConsecLosses = 0;
            }
        }
        
        simulations.push({
            finalEquity: equity,
            equityCurve: equityCurve,
            maxDrawdown: maxDrawdown,
            maxConsecLosses: maxConsecLosses,
            startingCapital: startingCapital,
            returnPercent: ((equity - startingCapital) / startingCapital) * 100
        });
    }
    
    return simulations;
}
```

## 📝 Implementation Steps

1. Add simulation options HTML before the run button
2. Update button click handler to read options
3. Replace histogram rendering with equity curve D3 chart
4. Add percentile band calculations
5. Update statistics display with percentiles
6. Add legend and tooltips to chart
7. Test with different parameter combinations

## 🎨 Visual Improvements

- Percentile bands show probability distribution
- Median line shows expected outcome
- Individual curves (optional) show variability
- Color-coded statistics (green/yellow/red)
- Interactive legend
- Responsive design

## ✅ Benefits

1. **Visual Understanding:** See actual equity curve progression
2. **Risk Assessment:** Percentile bands show range of outcomes
3. **Customization:** Adjust parameters for different scenarios
4. **Scalability:** Test with different trade counts
5. **Comparison:** Compare different sampling methods

---

**Status:** Ready for implementation
**Complexity:** Medium (requires D3.js integration)
**Impact:** High (much better visualization and understanding)
