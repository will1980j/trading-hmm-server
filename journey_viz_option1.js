// Option 1: Clean Price Line Chart with Event Markers
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
    
    // Extract trade data
    const direction = trade.direction;
    const entryPrice = trade.entry_price;
    const stopLoss = trade.stop_loss;
    let riskDistance = trade.risk_distance;
    const noBeRR = trade.no_be_mfe || 0;
    const beRR = trade.be_mfe || 0;
    const isActive = !trade.latest_event_type || !trade.latest_event_type.startsWith('EXIT_');
    const isBullish = direction === 'Bullish';
    
    // Ensure riskDistance is always positive (distance, not direction)
    if (riskDistance < 0) {
        riskDistance = Math.abs(riskDistance);
    }
    // If risk distance is missing or zero, calculate it
    if (!riskDistance || riskDistance === 0) {
        riskDistance = Math.abs(entryPrice - stopLoss);
    }
    
    // If incomplete data, show simple MFE bars
    if (!direction || !entryPrice || !stopLoss || !riskDistance) {
        renderSimpleMFEBars(container, trade, noBeRR, beRR, isActive);
        return;
    }
    
    // Filter and prepare key events only
    const keyEvents = [];
    
    // 1. Find ENTRY event
    const entryEvent = trade.events.find(e => e.event_type === 'ENTRY' || e.event_type === 'SIGNAL_CREATED');
    if (entryEvent) {
        keyEvents.push({
            type: 'ENTRY',
            event: entryEvent,
            mfe: 0,
            price: entryPrice,
            label: 'ENTRY',
            icon: '▶',
            color: '#00d4ff'
        });
    }
    
    // 2. Find first MFE update (if exists)
    const mfeUpdates = trade.events.filter(e => e.event_type === 'MFE_UPDATE');
    if (mfeUpdates.length > 0) {
        const firstMFE = mfeUpdates[0];
        const firstMFEPrice = isBullish ? 
            entryPrice + (firstMFE.no_be_mfe || 0) * riskDistance :
            entryPrice - (firstMFE.no_be_mfe || 0) * riskDistance;
        
        keyEvents.push({
            type: 'FIRST_MFE',
            event: firstMFE,
            mfe: firstMFE.no_be_mfe || 0,
            price: firstMFEPrice,
            label: 'First Move',
            icon: '📊',
            color: '#3b82f6'
        });
    }
    
    // 3. Find BE_TRIGGERED event (if exists)
    const beEvent = trade.events.find(e => e.event_type === 'BE_TRIGGERED');
    if (beEvent) {
        const bePrice = isBullish ? entryPrice + riskDistance : entryPrice - riskDistance;
        keyEvents.push({
            type: 'BE_TRIGGERED',
            event: beEvent,
            mfe: 1.0,
            price: bePrice,
            label: 'Break Even',
            icon: '⚡',
            color: '#fbbf24'
        });
    }
    
    // 4. Find peak MFE
    if (mfeUpdates.length > 0) {
        let peakMFE = mfeUpdates[0];
        mfeUpdates.forEach(e => {
            if ((e.no_be_mfe || 0) > (peakMFE.no_be_mfe || 0)) {
                peakMFE = e;
            }
        });
        
        // Only add if different from first and not the last
        if (peakMFE !== mfeUpdates[0] && peakMFE !== mfeUpdates[mfeUpdates.length - 1]) {
            const peakPrice = isBullish ?
                entryPrice + (peakMFE.no_be_mfe || 0) * riskDistance :
                entryPrice - (peakMFE.no_be_mfe || 0) * riskDistance;
            
            keyEvents.push({
                type: 'PEAK_MFE',
                event: peakMFE,
                mfe: peakMFE.no_be_mfe || 0,
                price: peakPrice,
                label: 'Peak MFE',
                icon: '🎯',
                color: '#10b981'
            });
        }
    }
    
    // 5. Find EXIT event (if exists)
    const exitEvent = trade.events.find(e => e.event_type.startsWith('EXIT_'));
    if (exitEvent) {
        const exitPrice = exitEvent.event_type === 'EXIT_STOP_LOSS' ? stopLoss : entryPrice;
        keyEvents.push({
            type: exitEvent.event_type,
            event: exitEvent,
            mfe: exitEvent.no_be_mfe || 0,
            price: exitPrice,
            label: exitEvent.event_type === 'EXIT_STOP_LOSS' ? 'Stop Loss' : 'BE Exit',
            icon: '🛑',
            color: exitEvent.event_type === 'EXIT_STOP_LOSS' ? '#ef4444' : '#8b5cf6'
        });
    } else if (mfeUpdates.length > 0) {
        // If active, add current MFE as last point
        const currentMFE = mfeUpdates[mfeUpdates.length - 1];
        const currentPrice = isBullish ?
            entryPrice + (currentMFE.no_be_mfe || 0) * riskDistance :
            entryPrice - (currentMFE.no_be_mfe || 0) * riskDistance;
        
        keyEvents.push({
            type: 'CURRENT',
            event: currentMFE,
            mfe: currentMFE.no_be_mfe || 0,
            price: currentPrice,
            label: 'Current',
            icon: '📈',
            color: '#4ade80'
        });
    }
    
    // Chart dimensions
    const width = container.node().offsetWidth || 600;
    const height = 400;
    const margin = {top: 60, right: 60, bottom: 60, left: 80};
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;
    
    // Create SVG
    const svg = container.append('svg')
        .attr('width', width)
        .attr('height', height)
        .style('background', 'rgba(255,255,255,0.02)')
        .style('border-radius', '8px');
    
    const chart = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // Calculate price range
    const prices = keyEvents.map(e => e.price);
    const minPrice = Math.min(...prices, stopLoss);
    const maxPrice = Math.max(...prices, entryPrice + 3 * riskDistance);
    const priceRange = maxPrice - minPrice;
    const pricePadding = priceRange * 0.1;
    
    // Scales
    const xScale = d3.scaleLinear()
        .domain([0, keyEvents.length - 1])
        .range([0, chartWidth]);
    
    const yScale = d3.scaleLinear()
        .domain([minPrice - pricePadding, maxPrice + pricePadding])
        .range([chartHeight, 0]);
    
    // Background gradient (profit/loss zones)
    const gradient = svg.append('defs')
        .append('linearGradient')
        .attr('id', 'profitGradient')
        .attr('x1', '0%')
        .attr('x2', '0%')
        .attr('y1', '0%')
        .attr('y2', '100%');
    
    gradient.append('stop')
        .attr('offset', '0%')
        .attr('stop-color', isBullish ? '#10b981' : '#ef4444')
        .attr('stop-opacity', 0.1);
    
    gradient.append('stop')
        .attr('offset', '50%')
        .attr('stop-color', '#00d4ff')
        .attr('stop-opacity', 0.05);
    
    gradient.append('stop')
        .attr('offset', '100%')
        .attr('stop-color', isBullish ? '#ef4444' : '#10b981')
        .attr('stop-opacity', 0.1);
    
    chart.append('rect')
        .attr('width', chartWidth)
        .attr('height', chartHeight)
        .attr('fill', 'url(#profitGradient)');
    
    // Draw horizontal reference lines
    // Entry line
    chart.append('line')
        .attr('x1', 0)
        .attr('x2', chartWidth)
        .attr('y1', yScale(entryPrice))
        .attr('y2', yScale(entryPrice))
        .attr('stroke', '#00d4ff')
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', '5,5')
        .attr('opacity', 0.6);
    
    chart.append('text')
        .attr('x', -10)
        .attr('y', yScale(entryPrice))
        .attr('text-anchor', 'end')
        .attr('alignment-baseline', 'middle')
        .attr('fill', '#00d4ff')
        .attr('font-size', '11px')
        .text(`Entry: ${entryPrice.toFixed(2)}`);
    
    // Stop loss line
    chart.append('line')
        .attr('x1', 0)
        .attr('x2', chartWidth)
        .attr('y1', yScale(stopLoss))
        .attr('y2', yScale(stopLoss))
        .attr('stroke', '#ef4444')
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', '3,3')
        .attr('opacity', 0.6);
    
    chart.append('text')
        .attr('x', -10)
        .attr('y', yScale(stopLoss))
        .attr('text-anchor', 'end')
        .attr('alignment-baseline', 'middle')
        .attr('fill', '#ef4444')
        .attr('font-size', '11px')
        .text(`SL: ${stopLoss.toFixed(2)}`);
    
    // +1R line (BE trigger)
    const bePrice = isBullish ? entryPrice + riskDistance : entryPrice - riskDistance;
    chart.append('line')
        .attr('x1', 0)
        .attr('x2', chartWidth)
        .attr('y1', yScale(bePrice))
        .attr('y2', yScale(bePrice))
        .attr('stroke', '#fbbf24')
        .attr('stroke-width', 1)
        .attr('stroke-dasharray', '2,2')
        .attr('opacity', 0.4);
    
    chart.append('text')
        .attr('x', -10)
        .attr('y', yScale(bePrice))
        .attr('text-anchor', 'end')
        .attr('alignment-baseline', 'middle')
        .attr('fill', '#fbbf24')
        .attr('font-size', '10px')
        .text('+1R');
    
    // Draw price line
    const line = d3.line()
        .x((d, i) => xScale(i))
        .y(d => yScale(d.price))
        .curve(d3.curveMonotoneX);
    
    const priceColor = noBeRR >= 0 ? '#4ade80' : '#ef4444';
    
    chart.append('path')
        .datum(keyEvents)
        .attr('fill', 'none')
        .attr('stroke', priceColor)
        .attr('stroke-width', 3)
        .attr('d', line)
        .attr('opacity', 0.8);
    
    // Draw event markers
    keyEvents.forEach((event, i) => {
        const group = chart.append('g')
            .attr('transform', `translate(${xScale(i)},${yScale(event.price)})`);
        
        // Event circle
        group.append('circle')
            .attr('r', event.type === 'ENTRY' || event.type.startsWith('EXIT_') ? 10 : 7)
            .attr('fill', event.color)
            .attr('stroke', '#0a0e27')
            .attr('stroke-width', 2)
            .style('cursor', 'pointer');
        
        // Event icon
        group.append('text')
            .attr('text-anchor', 'middle')
            .attr('alignment-baseline', 'middle')
            .attr('fill', '#0a0e27')
            .attr('font-size', event.type === 'ENTRY' || event.type.startsWith('EXIT_') ? '12px' : '10px')
            .attr('font-weight', '700')
            .text(event.icon);
        
        // Event label
        group.append('text')
            .attr('y', -20)
            .attr('text-anchor', 'middle')
            .attr('fill', event.color)
            .attr('font-size', '11px')
            .attr('font-weight', '600')
            .text(event.label);
        
        // MFE value
        if (event.mfe !== 0) {
            group.append('text')
                .attr('y', 25)
                .attr('text-anchor', 'middle')
                .attr('fill', '#94a3b8')
                .attr('font-size', '10px')
                .text(`${event.mfe.toFixed(2)}R`);
        }
        
        // Hover effect
        group.on('mouseover', function() {
            d3.select(this).select('circle')
                .transition()
                .duration(200)
                .attr('r', event.type === 'ENTRY' || event.type.startsWith('EXIT_') ? 14 : 10);
        })
        .on('mouseout', function() {
            d3.select(this).select('circle')
                .transition()
                .duration(200)
                .attr('r', event.type === 'ENTRY' || event.type.startsWith('EXIT_') ? 10 : 7);
        });
    });
    
    // Title
    svg.append('text')
        .attr('x', width / 2)
        .attr('y', 30)
        .attr('text-anchor', 'middle')
        .attr('fill', '#00d4ff')
        .attr('font-size', '16px')
        .attr('font-weight', '600')
        .text(`${direction} Trade Journey - ${isActive ? 'ACTIVE' : 'COMPLETED'}`);
    
    // Final MFE display
    svg.append('text')
        .attr('x', width / 2)
        .attr('y', height - 15)
        .attr('text-anchor', 'middle')
        .attr('fill', noBeRR >= 0 ? '#4ade80' : '#ef4444')
        .attr('font-size', '14px')
        .attr('font-weight', '600')
        .text(`Final MFE: ${noBeRR.toFixed(2)}R`);
    
    // Status indicator
    svg.append('circle')
        .attr('cx', width - 30)
        .attr('cy', 30)
        .attr('r', 8)
        .attr('fill', isActive ? '#4ade80' : '#8b5cf6');
}

// Helper function for simple MFE bars (when data is incomplete)
function renderSimpleMFEBars(container, trade, noBeRR, beRR, isActive) {
    const width = container.node().offsetWidth || 600;
    const height = 250;
    
    const svg = container.append('svg')
        .attr('width', width)
        .attr('height', height)
        .style('background', 'rgba(255,255,255,0.02)')
        .style('border-radius', '8px');
    
    // Title
    svg.append('text')
        .attr('x', width / 2)
        .attr('y', 30)
        .attr('text-anchor', 'middle')
        .attr('fill', '#00d4ff')
        .attr('font-size', '16px')
        .attr('font-weight', '600')
        .text(`Trade ${trade.trade_id || 'Unknown'} - ${isActive ? 'ACTIVE' : 'COMPLETED'}`);
    
    // MFE bars
    const barY = height / 2;
    const maxBarWidth = width - 200;
    const maxMFE = Math.max(noBeRR, beRR, 1);
    
    // No BE MFE bar
    const noBeWidth = (noBeRR / maxMFE) * maxBarWidth;
    svg.append('rect')
        .attr('x', 100)
        .attr('y', barY - 40)
        .attr('width', noBeWidth)
        .attr('height', 30)
        .attr('fill', noBeRR > 0 ? '#4ade80' : '#ef4444')
        .attr('opacity', 0.7);
    
    svg.append('text')
        .attr('x', 90)
        .attr('y', barY - 20)
        .attr('text-anchor', 'end')
        .attr('fill', '#e0e6ed')
        .attr('font-size', '12px')
        .text('No BE:');
    
    svg.append('text')
        .attr('x', 110 + noBeWidth)
        .attr('y', barY - 20)
        .attr('fill', '#4ade80')
        .attr('font-size', '14px')
        .attr('font-weight', '600')
        .text(`${noBeRR.toFixed(2)}R`);
    
    // BE=1 MFE bar
    const beWidth = (beRR / maxMFE) * maxBarWidth;
    svg.append('rect')
        .attr('x', 100)
        .attr('y', barY + 10)
        .attr('width', beWidth)
        .attr('height', 30)
        .attr('fill', beRR > 0 ? '#fbbf24' : '#ef4444')
        .attr('opacity', 0.7);
    
    svg.append('text')
        .attr('x', 90)
        .attr('y', barY + 30)
        .attr('text-anchor', 'end')
        .attr('fill', '#e0e6ed')
        .attr('font-size', '12px')
        .text('BE=1:');
    
    svg.append('text')
        .attr('x', 110 + beWidth)
        .attr('y', barY + 30)
        .attr('fill', '#fbbf24')
        .attr('font-size', '14px')
        .attr('font-weight', '600')
        .text(`${beRR.toFixed(2)}R`);
    
    // Status indicator
    svg.append('circle')
        .attr('cx', width - 30)
        .attr('cy', 30)
        .attr('r', 8)
        .attr('fill', isActive ? '#4ade80' : '#8b5cf6');
    
    // Info message
    svg.append('text')
        .attr('x', width / 2)
        .attr('y', height - 20)
        .attr('text-anchor', 'middle')
        .attr('fill', '#94a3b8')
        .attr('font-size', '11px')
        .text(`${trade.events ? trade.events.length : 0} events • ${trade.direction || 'Direction unknown'}`);
}
