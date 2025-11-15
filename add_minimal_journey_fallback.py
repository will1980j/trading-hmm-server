"""
Add a minimal journey visualization that works even with just ENTRY event
Shows current status and what's expected next
"""

# Read dashboard
with open('automated_signals_dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the "no events" fallback with a minimal visualization
old_no_events = '''            // If no events, show message
            if (events.length === 0) {
                console.warn('No events found for trade');
                document.getElementById('journeyViz').innerHTML = '<div style="color: #fbbf24; text-align: center; padding: 40px;">No event data available for this trade</div>';
                return;
            }'''

new_no_events = '''            // If no events, show message
            if (events.length === 0) {
                console.warn('No events found for trade');
                document.getElementById('journeyViz').innerHTML = '<div style="color: #fbbf24; text-align: center; padding: 40px;">No event data available for this trade</div>';
                return;
            }
            
            // If only ENTRY event, create a minimal journey showing current state
            if (events.length === 1 && events[0].event_type === 'ENTRY') {
                console.log('Only ENTRY event found, creating minimal journey');
                renderMinimalJourney(trade, events[0]);
                return;
            }'''

html = html.replace(old_no_events, new_no_events)

# Add minimal journey function before renderTradeJourney
minimal_journey_function = '''
        // Minimal Journey for trades with only ENTRY event
        function renderMinimalJourney(trade, entryEvent) {
            const container = d3.select('#journeyViz');
            const width = container.node().getBoundingClientRect().width;
            const height = 400;
            
            const svg = container.append('svg')
                .attr('width', width)
                .attr('height', height);
            
            const centerY = height / 2;
            const spacing = width / 4;
            
            // Define minimal journey: ENTRY -> Waiting for MFE -> Potential Outcomes
            const nodes = [
                { x: spacing, y: centerY, label: 'Entry', sublabel: trade.entry_price ? trade.entry_price.toFixed(2) : 'N/A', color: '#4ade80', icon: '▶', status: 'completed' },
                { x: spacing * 2, y: centerY, label: 'Awaiting Updates', sublabel: 'No MFE data yet', color: '#fbbf24', icon: '⏳', status: 'current' },
                { x: spacing * 3, y: centerY, label: 'Potential Exit', sublabel: 'Stop or Target', color: '#94a3b8', icon: '🏁', status: 'potential' }
            ];
            
            // Draw lines
            for (let i = 0; i < nodes.length - 1; i++) {
                const source = nodes[i];
                const target = nodes[i + 1];
                
                svg.append('path')
                    .attr('class', i === 0 ? 'journey-link completed' : 'journey-link potential')
                    .attr('d', `M ${source.x},${source.y} L ${target.x},${target.y}`);
            }
            
            // Draw nodes
            const nodeGroups = svg.selectAll('.journey-node')
                .data(nodes)
                .enter()
                .append('g')
                .attr('class', 'journey-node')
                .attr('transform', d => `translate(${d.x},${d.y})`);
            
            nodeGroups.append('circle')
                .attr('class', d => d.status === 'current' ? 'node-circle current-indicator' : 'node-circle')
                .attr('r', d => d.status === 'current' ? 40 : 32)
                .attr('fill', d => d.color)
                .attr('opacity', d => d.status === 'potential' ? 0.3 : 0.9);
            
            nodeGroups.append('text')
                .attr('class', 'node-label')
                .attr('y', 6)
                .style('font-size', d => d.status === 'current' ? '24px' : '18px')
                .text(d => d.icon);
            
            nodeGroups.append('text')
                .attr('class', 'node-label')
                .attr('y', -50)
                .text(d => d.label);
            
            nodeGroups.append('text')
                .attr('class', 'node-value')
                .attr('y', 55)
                .text(d => d.sublabel);
            
            // Add note about missing data
            svg.append('text')
                .attr('x', width / 2)
                .attr('y', height - 30)
                .attr('text-anchor', 'middle')
                .attr('fill', '#94a3b8')
                .attr('font-size', '12px')
                .text('⚠️ Waiting for MFE updates from TradingView indicator');
        }

'''

# Insert before renderTradeJourney
html = html.replace('        // Trade Journey Visualization with D3.js\n        function renderTradeJourney(trade) {',
                    minimal_journey_function + '        // Trade Journey Visualization with D3.js\n        function renderTradeJourney(trade) {')

# Write updated file
with open('automated_signals_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ Added minimal journey fallback visualization")
print("\nNow trades with only ENTRY events will show:")
print("  Entry ▶ → Awaiting Updates ⏳ → Potential Exit 🏁")
print("\nThis makes it clear that the system is waiting for MFE updates from TradingView!")
