"""
Enhance the price chart to show different node types for different events
- SIGNAL_CREATED: Large star
- MFE_UPDATE: Regular circles
- BE_TRIGGERED: Special marker
- EXIT_SL: Final marker
"""

enhancement_code = """
    // Draw price points with different styles based on event type
    svg.selectAll('.price-point')
        .data(priceData)
        .enter()
        .append('g')
        .attr('class', 'price-point-group')
        .attr('transform', d => `translate(${xScale(d.x)},${yScale(d.price)})`)
        .each(function(d) {
            const group = d3.select(this);
            const eventType = d.event.event_type;
            
            // Different shapes for different event types
            if (eventType === 'SIGNAL_CREATED') {
                // Entry point - large star
                const starPath = d3.symbol().type(d3.symbolStar).size(200);
                group.append('path')
                    .attr('d', starPath)
                    .attr('fill', '#00d4ff')
                    .attr('stroke', '#0a0e27')
                    .attr('stroke-width', 2)
                    .attr('class', 'event-marker');
                
                // Label
                group.append('text')
                    .attr('y', -15)
                    .attr('text-anchor', 'middle')
                    .attr('fill', '#00d4ff')
                    .attr('font-size', '10px')
                    .attr('font-weight', '700')
                    .text('ENTRY');
                    
            } else if (eventType === 'BE_TRIGGERED') {
                // BE trigger - diamond
                const diamondPath = d3.symbol().type(d3.symbolDiamond).size(150);
                group.append('path')
                    .attr('d', diamondPath)
                    .attr('fill', '#fbbf24')
                    .attr('stroke', '#0a0e27')
                    .attr('stroke-width', 2)
                    .attr('class', 'event-marker');
                
                // Label
                group.append('text')
                    .attr('y', -15)
                    .attr('text-anchor', 'middle')
                    .attr('fill', '#fbbf24')
                    .attr('font-size', '10px')
                    .attr('font-weight', '700')
                    .text('BE +1R');
                    
            } else if (eventType.startsWith('EXIT_')) {
                // Exit point - square
                const squarePath = d3.symbol().type(d3.symbolSquare).size(150);
                group.append('path')
                    .attr('d', squarePath)
                    .attr('fill', '#ef4444')
                    .attr('stroke', '#0a0e27')
                    .attr('stroke-width', 2)
                    .attr('class', 'event-marker');
                
                // Label
                group.append('text')
                    .attr('y', -15)
                    .attr('text-anchor', 'middle')
                    .attr('fill', '#ef4444')
                    .attr('font-size', '10px')
                    .attr('font-weight', '700')
                    .text('EXIT');
                    
            } else {
                // MFE update - regular circle
                group.append('circle')
                    .attr('r', 5)
                    .attr('fill', isBullish ? '#4ade80' : '#ef4444')
                    .attr('stroke', '#0a0e27')
                    .attr('stroke-width', 2)
                    .attr('class', 'event-marker');
            }
            
            // Make interactive
            group.style('cursor', 'pointer')
                .on('mouseover', function(event) {
                    d3.select(this).select('.event-marker')
                        .transition()
                        .duration(200)
                        .attr('transform', 'scale(1.5)');
                    
                    // Show detailed tooltip
                    const tooltip = svg.append('g')
                        .attr('class', 'price-tooltip')
                        .attr('transform', `translate(${xScale(d.x)},${yScale(d.price) - 40})`);
                    
                    const tooltipText = [
                        `${d.event.event_type}`,
                        `Price: ${d.price.toFixed(2)}`,
                        `MFE: ${(d.event.no_be_mfe || 0).toFixed(2)}R`,
                        `Time: ${d.event.signal_time || 'N/A'}`
                    ];
                    
                    const textGroup = tooltip.append('text')
                        .attr('text-anchor', 'middle')
                        .attr('fill', '#e0e6ed')
                        .attr('font-size', '11px');
                    
                    tooltipText.forEach((line, i) => {
                        textGroup.append('tspan')
                            .attr('x', 0)
                            .attr('dy', i === 0 ? 0 : 14)
                            .attr('font-weight', i === 0 ? '700' : '400')
                            .text(line);
                    });
                    
                    const bbox = textGroup.node().getBBox();
                    tooltip.insert('rect', 'text')
                        .attr('x', bbox.x - 8)
                        .attr('y', bbox.y - 4)
                        .attr('width', bbox.width + 16)
                        .attr('height', bbox.height + 8)
                        .attr('fill', 'rgba(0, 0, 0, 0.9)')
                        .attr('rx', 6)
                        .attr('stroke', '#00d4ff')
                        .attr('stroke-width', 1);
                })
                .on('mouseout', function() {
                    d3.select(this).select('.event-marker')
                        .transition()
                        .duration(200)
                        .attr('transform', 'scale(1)');
                    
                    svg.selectAll('.price-tooltip').remove();
                });
        });
"""

# Read current file
with open('automated_signals_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the price points section
old_points = """    // Draw price points
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
        });"""

if old_points in content:
    content = content.replace(old_points, enhancement_code.strip())
    
    with open('automated_signals_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Enhanced MFE nodes with event-specific markers")
    print("\nNew node types:")
    print("⭐ SIGNAL_CREATED - Blue star (Entry point)")
    print("💎 BE_TRIGGERED - Yellow diamond (Breakeven at +1R)")
    print("⬛ EXIT_SL - Red square (Stop loss hit)")
    print("🔵 MFE_UPDATE - Green/Red circles (Price updates)")
    print("\nFeatures:")
    print("- Different shapes for different events")
    print("- Color-coded by event type")
    print("- Labeled for easy identification")
    print("- Enhanced tooltips with full event details")
    print("- Smooth hover animations")
else:
    print("❌ Could not find price points section to replace")
    print("The code may have already been updated or structure changed")
