"""
Create a price chart visualization for trade journey instead of abstract nodes
Shows actual price movement with entry, stop loss, and MFE levels
"""

chart_visualization_js = """
function renderPriceChartJourney(trade) {
    console.log('renderPriceChartJourney called with trade:', trade);
    
    const container = d3.select('#journeyViz');
    container.selectAll('*').remove();
    
    if (!trade || !trade.events || trade.events.length === 0) {
        container.append('div')
            .style('text-align', 'center')
            .style('padding', '40px')
            .style('color', '#94a3b8')
            .text('No event data available for visualization');
        return;
    }
    
    // Extract price data from events
    const direction = trade.direction;
    const entryPrice = trade.entry_price;
    const stopLoss = trade.stop_loss;
    const riskDistance = trade.risk_distance;
    
    // Calculate price levels
    const isBullish = direction === 'Bullish';
    const target1R = isBullish ? entryPrice + riskDistance : entryPrice - riskDistance;
    const target2R = isBullish ? entryPrice + (2 * riskDistance) : entryPrice - (2 * riskDistance);
    const target3R = isBullish ? entryPrice + (3 * riskDistance) : entryPrice - (3 * riskDistance);
    
    // Get MFE values from events
    const mfeEvents = trade.events.filter(e => e.event_type === 'MFE_UPDATE' || e.event_type === 'SIGNAL_CREATED');
    const maxMFE = Math.max(...trade.events.map(e => e.no_be_mfe || 0));
    const maxPrice = isBullish ? entryPrice + (maxMFE * riskDistance) : entryPrice - (maxMFE * riskDistance);
    
    // Determine price range for chart
    const priceMin = Math.min(stopLoss, entryPrice, maxPrice) - riskDistance;
    const priceMax = Math.max(stopLoss, entryPrice, maxPrice, target3R) + riskDistance;
    
    // Chart dimensions
    const margin = {top: 40, right: 80, bottom: 60, left: 80};
    const width = container.node().offsetWidth - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;
    
    // Create SVG
    const svg = container.append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // Scales
    const xScale = d3.scaleLinear()
        .domain([0, mfeEvents.length - 1])
        .range([0, width]);
    
    const yScale = d3.scaleLinear()
        .domain([priceMin, priceMax])
        .range([height, 0]);
    
    // Create price path data
    const priceData = mfeEvents.map((event, i) => {
        const mfe = event.no_be_mfe || 0;
        const price = isBullish ? entryPrice + (mfe * riskDistance) : entryPrice - (mfe * riskDistance);
        return {x: i, price: price, event: event};
    });
    
    // Draw background zones
    const zones = [
        {label: 'Stop Loss', price: stopLoss, color: '#ef4444', dash: '5,5'},
        {label: 'Entry', price: entryPrice, color: '#00d4ff', dash: 'none'},
        {label: '+1R', price: target1R, color: '#4ade80', dash: '3,3'},
        {label: '+2R', price: target2R, color: '#4ade80', dash: '3,3'},
        {label: '+3R', price: target3R, color: '#4ade80', dash: '3,3'}
    ];
    
    // Draw horizontal reference lines
    zones.forEach(zone => {
        svg.append('line')
            .attr('x1', 0)
            .attr('x2', width)
            .attr('y1', yScale(zone.price))
            .attr('y2', yScale(zone.price))
            .attr('stroke', zone.color)
            .attr('stroke-width', 2)
            .attr('stroke-dasharray', zone.dash)
            .attr('opacity', 0.5);
        
        // Label
        svg.append('text')
            .attr('x', width + 10)
            .attr('y', yScale(zone.price))
            .attr('dy', '0.35em')
            .attr('fill', zone.color)
            .attr('font-size', '11px')
            .attr('font-weight', '600')
            .text(`${zone.label} (${zone.price.toFixed(2)})`);
    });
    
    // Draw price path
    const line = d3.line()
        .x(d => xScale(d.x))
        .y(d => yScale(d.price))
        .curve(d3.curveMonotoneX);
    
    // Price area fill
    const area = d3.area()
        .x(d => xScale(d.x))
        .y0(yScale(entryPrice))
        .y1(d => yScale(d.price))
        .curve(d3.curveMonotoneX);
    
    svg.append('path')
        .datum(priceData)
        .attr('fill', isBullish ? 'rgba(74, 222, 128, 0.1)' : 'rgba(239, 68, 68, 0.1)')
        .attr('d', area);
    
    // Price line
    svg.append('path')
        .datum(priceData)
        .attr('fill', 'none')
        .attr('stroke', isBullish ? '#4ade80' : '#ef4444')
        .attr('stroke-width', 3)
        .attr('d', line);
    
    // Draw price points
    svg.selectAll('.price-point')
        .data(priceData)
        .enter()
        .append('circle')
        .attr('class', 'price-point')
        .attr('cx', d => xScale(d.x))
        .attr('cy', d => yScale(d.price))
        .attr('r', 5)
        .attr('fill', isBullish ? '#4ade80' : '#ef4444')
        .attr('stroke', '#0a0e27')
        .attr('stroke-width', 2)
        .style('cursor', 'pointer')
        .on('mouseover', function(event, d) {
            d3.select(this)
                .transition()
                .duration(200)
                .attr('r', 8);
            
            // Show tooltip
            const tooltip = svg.append('g')
                .attr('class', 'price-tooltip')
                .attr('transform', `translate(${xScale(d.x)},${yScale(d.price) - 20})`);
            
            const text = tooltip.append('text')
                .attr('text-anchor', 'middle')
                .attr('fill', '#e0e6ed')
                .attr('font-size', '12px')
                .attr('font-weight', '600')
                .text(`${d.price.toFixed(2)} (${d.event.no_be_mfe.toFixed(2)}R)`);
            
            const bbox = text.node().getBBox();
            tooltip.insert('rect', 'text')
                .attr('x', bbox.x - 5)
                .attr('y', bbox.y - 2)
                .attr('width', bbox.width + 10)
                .attr('height', bbox.height + 4)
                .attr('fill', 'rgba(0, 0, 0, 0.8)')
                .attr('rx', 4);
        })
        .on('mouseout', function() {
            d3.select(this)
                .transition()
                .duration(200)
                .attr('r', 5);
            
            svg.selectAll('.price-tooltip').remove();
        });
    
    // Add axes
    const xAxis = d3.axisBottom(xScale)
        .ticks(Math.min(mfeEvents.length, 10))
        .tickFormat(d => `Event ${Math.floor(d) + 1}`);
    
    const yAxis = d3.axisLeft(yScale)
        .ticks(8)
        .tickFormat(d => d.toFixed(2));
    
    svg.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(xAxis)
        .attr('color', '#94a3b8')
        .selectAll('text')
        .attr('font-size', '10px');
    
    svg.append('g')
        .call(yAxis)
        .attr('color', '#94a3b8')
        .selectAll('text')
        .attr('font-size', '10px');
    
    // Chart title
    svg.append('text')
        .attr('x', width / 2)
        .attr('y', -20)
        .attr('text-anchor', 'middle')
        .attr('fill', '#00d4ff')
        .attr('font-size', '14px')
        .attr('font-weight', '600')
        .text(`${direction} Trade Price Journey - Max MFE: ${maxMFE.toFixed(2)}R`);
    
    // Status indicator
    const isActive = !trade.events[trade.events.length - 1].event_type.startsWith('EXIT_');
    svg.append('text')
        .attr('x', width / 2)
        .attr('y', -5)
        .attr('text-anchor', 'middle')
        .attr('fill', isActive ? '#4ade80' : '#8b5cf6')
        .attr('font-size', '12px')
        .text(isActive ? '● ACTIVE' : '● COMPLETED');
}
"""

# Read the current dashboard HTML
with open('automated_signals_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the renderTradeJourney function
import re

# Find the function definition
pattern = r'function renderTradeJourney\(trade\) \{.*?\n\s*\}'
match = re.search(pattern, content, re.DOTALL)

if match:
    # Replace with new price chart version
    content = content.replace(match.group(0), chart_visualization_js.strip())
    
    with open('automated_signals_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Replaced abstract journey visualization with price chart")
    print("\nNew features:")
    print("- Actual price movement chart")
    print("- Entry, stop loss, and target levels marked")
    print("- Price path shows trade progression")
    print("- Hover over points to see exact prices and MFE")
    print("- Color-coded zones (red=stop, blue=entry, green=targets)")
    print("- Shows if trade is active or completed")
else:
    print("❌ Could not find renderTradeJourney function")
