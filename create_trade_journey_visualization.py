"""
Create D3.js-powered Trade Journey Visualization
Shows the complete lifecycle of a trade with beautiful graphics
"""

visualization_code = '''
<!-- Add D3.js library -->
<script src="https://d3js.org/d3.v7.min.js"></script>

<style>
/* Trade Journey Visualization Styles */
.journey-container {
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
    border-radius: 12px;
    padding: 30px;
    margin: 20px 0;
}

.journey-title {
    color: #00d4ff;
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 20px;
    text-align: center;
}

#journeyViz {
    width: 100%;
    height: 400px;
}

.journey-node {
    cursor: pointer;
    transition: all 0.3s ease;
}

.journey-node:hover {
    filter: brightness(1.3);
}

.journey-link {
    fill: none;
    stroke-width: 3px;
    opacity: 0.6;
}

.journey-link.completed {
    stroke: #4ade80;
    opacity: 0.8;
}

.journey-link.active {
    stroke: #00d4ff;
    opacity: 1;
    animation: pulse-line 2s infinite;
}

.journey-link.potential {
    stroke: #94a3b8;
    stroke-dasharray: 5,5;
    opacity: 0.4;
}

@keyframes pulse-line {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.node-circle {
    filter: drop-shadow(0 0 8px currentColor);
}

.node-label {
    font-size: 12px;
    font-weight: 600;
    fill: #e0e6ed;
    text-anchor: middle;
    pointer-events: none;
}

.node-time {
    font-size: 10px;
    fill: #94a3b8;
    text-anchor: middle;
    pointer-events: none;
}

.node-value {
    font-size: 11px;
    font-weight: 700;
    fill: #00d4ff;
    text-anchor: middle;
    pointer-events: none;
}

.current-indicator {
    animation: pulse-glow 2s infinite;
}

@keyframes pulse-glow {
    0%, 100% {
        filter: drop-shadow(0 0 8px #00d4ff) drop-shadow(0 0 16px #00d4ff);
    }
    50% {
        filter: drop-shadow(0 0 16px #00d4ff) drop-shadow(0 0 24px #00d4ff);
    }
}

.legend {
    display: flex;
    justify-content: center;
    gap: 30px;
    margin-top: 20px;
    font-size: 12px;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
}

.legend-line {
    width: 30px;
    height: 3px;
    border-radius: 2px;
}

.legend-line.completed { background: #4ade80; }
.legend-line.active { background: #00d4ff; }
.legend-line.potential { 
    background: #94a3b8; 
    opacity: 0.4;
}
</style>

<script>
function renderTradeJourney(trade) {
    // Clear existing visualization
    d3.select('#journeyViz').selectAll('*').remove();
    
    const events = trade.events;
    const isActive = !events[events.length - 1].event_type.startsWith('EXIT_');
    
    // Define the journey stages
    const stages = [
        { id: 'ENTRY', label: 'Entry', color: '#4ade80', icon: '▶' },
        { id: 'MFE_UPDATE', label: 'MFE Tracking', color: '#00d4ff', icon: '📈' },
        { id: 'BE_TRIGGERED', label: 'Break Even', color: '#fbbf24', icon: '⚡' },
        { id: 'EXIT_STOP_LOSS', label: 'Stop Loss', color: '#ef4444', icon: '🛑' },
        { id: 'EXIT_BREAK_EVEN', label: 'BE Exit', color: '#8b5cf6', icon: '↩' }
    ];
    
    // Build journey path based on actual events
    const journeyPath = [];
    const eventsByType = {};
    
    events.forEach(event => {
        if (!eventsByType[event.event_type]) {
            eventsByType[event.event_type] = [];
        }
        eventsByType[event.event_type].push(event);
    });
    
    // Add ENTRY
    if (eventsByType['ENTRY']) {
        journeyPath.push({
            stage: 'ENTRY',
            event: eventsByType['ENTRY'][0],
            status: 'completed',
            label: 'Entry',
            color: '#4ade80',
            icon: '▶'
        });
    }
    
    // Add MFE_UPDATE nodes (show first, peak, and latest)
    if (eventsByType['MFE_UPDATE']) {
        const mfeEvents = eventsByType['MFE_UPDATE'];
        
        // Find peak MFE
        let peakMfe = mfeEvents[0];
        mfeEvents.forEach(e => {
            if ((e.no_be_mfe || 0) > (peakMfe.no_be_mfe || 0)) {
                peakMfe = e;
            }
        });
        
        // Add first MFE
        journeyPath.push({
            stage: 'MFE_UPDATE',
            event: mfeEvents[0],
            status: 'completed',
            label: 'First MFE',
            sublabel: `${(mfeEvents[0].no_be_mfe || 0).toFixed(2)}R`,
            color: '#00d4ff',
            icon: '📊'
        });
        
        // Add peak MFE if different
        if (peakMfe !== mfeEvents[0] && peakMfe !== mfeEvents[mfeEvents.length - 1]) {
            journeyPath.push({
                stage: 'MFE_UPDATE',
                event: peakMfe,
                status: 'completed',
                label: 'Peak MFE',
                sublabel: `${(peakMfe.no_be_mfe || 0).toFixed(2)}R`,
                color: '#10b981',
                icon: '🎯'
            });
        }
        
        // Add latest MFE if active
        if (isActive && mfeEvents.length > 1) {
            journeyPath.push({
                stage: 'MFE_UPDATE',
                event: mfeEvents[mfeEvents.length - 1],
                status: 'current',
                label: 'Current MFE',
                sublabel: `${(mfeEvents[mfeEvents.length - 1].no_be_mfe || 0).toFixed(2)}R`,
                color: '#00d4ff',
                icon: '📈'
            });
        }
    }
    
    // Add BE_TRIGGERED if exists
    if (eventsByType['BE_TRIGGERED']) {
        journeyPath.push({
            stage: 'BE_TRIGGERED',
            event: eventsByType['BE_TRIGGERED'][0],
            status: 'completed',
            label: 'Break Even',
            sublabel: '+1R Achieved',
            color: '#fbbf24',
            icon: '⚡'
        });
    }
    
    // Add EXIT if exists
    if (eventsByType['EXIT_STOP_LOSS']) {
        journeyPath.push({
            stage: 'EXIT_STOP_LOSS',
            event: eventsByType['EXIT_STOP_LOSS'][0],
            status: 'completed',
            label: 'Stop Loss Hit',
            sublabel: `Final: ${(eventsByType['EXIT_STOP_LOSS'][0].no_be_mfe || 0).toFixed(2)}R`,
            color: '#ef4444',
            icon: '🛑'
        });
    } else if (eventsByType['EXIT_BREAK_EVEN']) {
        journeyPath.push({
            stage: 'EXIT_BREAK_EVEN',
            event: eventsByType['EXIT_BREAK_EVEN'][0],
            status: 'completed',
            label: 'BE Exit',
            sublabel: `Final: ${(eventsByType['EXIT_BREAK_EVEN'][0].be_mfe || 0).toFixed(2)}R`,
            color: '#8b5cf6',
            icon: '↩'
        });
    }
    
    // Add potential next states if active
    if (isActive) {
        if (!eventsByType['BE_TRIGGERED']) {
            journeyPath.push({
                stage: 'BE_TRIGGERED',
                status: 'potential',
                label: 'Potential BE',
                sublabel: 'If +1R reached',
                color: '#94a3b8',
                icon: '⚡'
            });
        }
        
        journeyPath.push({
            stage: 'EXIT_STOP_LOSS',
            status: 'potential',
            label: 'Potential Exit',
            sublabel: 'Stop or Target',
            color: '#94a3b8',
            icon: '🏁'
        });
    }
    
    // Set up SVG
    const container = d3.select('#journeyViz');
    const width = container.node().getBoundingClientRect().width;
    const height = 400;
    
    const svg = container.append('svg')
        .attr('width', width)
        .attr('height', height);
    
    // Calculate positions
    const nodeSpacing = width / (journeyPath.length + 1);
    const centerY = height / 2;
    
    journeyPath.forEach((node, i) => {
        node.x = nodeSpacing * (i + 1);
        node.y = centerY;
    });
    
    // Draw connecting lines
    for (let i = 0; i < journeyPath.length - 1; i++) {
        const source = journeyPath[i];
        const target = journeyPath[i + 1];
        
        let linkClass = 'journey-link ';
        if (source.status === 'completed' && target.status === 'completed') {
            linkClass += 'completed';
        } else if (source.status === 'current' || target.status === 'current') {
            linkClass += 'active';
        } else {
            linkClass += 'potential';
        }
        
        svg.append('path')
            .attr('class', linkClass)
            .attr('d', `M ${source.x},${source.y} L ${target.x},${target.y}`);
    }
    
    // Draw nodes
    const nodes = svg.selectAll('.journey-node')
        .data(journeyPath)
        .enter()
        .append('g')
        .attr('class', 'journey-node')
        .attr('transform', d => `translate(${d.x},${d.y})`);
    
    // Node circles
    nodes.append('circle')
        .attr('class', d => d.status === 'current' ? 'node-circle current-indicator' : 'node-circle')
        .attr('r', d => d.status === 'current' ? 35 : d.status === 'potential' ? 25 : 30)
        .attr('fill', d => d.color)
        .attr('opacity', d => d.status === 'potential' ? 0.3 : 0.9);
    
    // Node icons
    nodes.append('text')
        .attr('class', 'node-label')
        .attr('y', 5)
        .style('font-size', d => d.status === 'current' ? '20px' : '16px')
        .text(d => d.icon);
    
    // Node labels
    nodes.append('text')
        .attr('class', 'node-label')
        .attr('y', -45)
        .text(d => d.label);
    
    // Node sublabels (MFE values, etc.)
    nodes.filter(d => d.sublabel)
        .append('text')
        .attr('class', 'node-value')
        .attr('y', 50)
        .text(d => d.sublabel);
    
    // Node times
    nodes.filter(d => d.event)
        .append('text')
        .attr('class', 'node-time')
        .attr('y', 65)
        .text(d => d.event.signal_time ? d.event.signal_time.split('T')[1].substring(0, 8) : '');
    
    // Add click handlers for details
    nodes.filter(d => d.event)
        .on('click', function(event, d) {
            showEventDetail(d.event);
        });
}

function showEventDetail(event) {
    alert(`Event: ${event.event_type}\\nTime: ${event.signal_time}\\nBE MFE: ${event.be_mfe || 'N/A'}\\nNo BE MFE: ${event.no_be_mfe || 'N/A'}`);
}
</script>
'''

print("="*80)
print("TRADE JOURNEY VISUALIZATION CODE")
print("="*80)
print("\nAdd this to the modal in automated_signals_dashboard.html:")
print("\n1. Add D3.js library and styles to <head> or before </body>")
print("\n2. Update renderTradeDetail() function to include:")
print(visualization_code)
print("\n3. Add journey container to modal body:")
print('''
<div class="journey-container">
    <div class="journey-title">📍 Trade Journey Map</div>
    <div id="journeyViz"></div>
    <div class="legend">
        <div class="legend-item">
            <div class="legend-line completed"></div>
            <span>Completed</span>
        </div>
        <div class="legend-item">
            <div class="legend-line active"></div>
            <span>Current</span>
        </div>
        <div class="legend-item">
            <div class="legend-line potential"></div>
            <span>Potential</span>
        </div>
    </div>
</div>
''')
print("\n4. Call renderTradeJourney(trade) after rendering trade details")
print("\n" + "="*80)
print("\nFeatures:")
print("✓ Visual journey from ENTRY to current state")
print("✓ Shows first MFE, peak MFE, and current MFE")
print("✓ Highlights current position with pulsing glow")
print("✓ Shows potential next states (BE trigger, Exit)")
print("✓ Animated connections between states")
print("✓ Click nodes to see event details")
print("✓ Color-coded by event type")
print("✓ Compact, professional design")
print("="*80)
