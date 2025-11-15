"""
Deploy D3.js Trade Journey Visualization to Dashboard
Creates a beautiful, animated visual representation of each trade's lifecycle
"""

# Read current dashboard
with open('automated_signals_dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add D3.js library before </head>
d3_library = '''    <script src="https://d3js.org/d3.v7.min.js"></script>
</head>'''

html = html.replace('</head>', d3_library)

# Add journey visualization styles to existing modal styles
journey_styles = '''
        /* Trade Journey Visualization */
        .journey-container {
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
            border-radius: 12px;
            padding: 30px;
            margin: 20px 0;
            border: 1px solid rgba(0, 212, 255, 0.2);
        }

        .journey-title {
            color: #00d4ff;
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 25px;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        #journeyViz {
            width: 100%;
            height: 400px;
            position: relative;
        }

        .journey-node {
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .journey-node:hover {
            transform: scale(1.1);
        }

        .journey-link {
            fill: none;
            stroke-width: 4px;
            opacity: 0.6;
            transition: all 0.3s ease;
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
            stroke-dasharray: 8,8;
            opacity: 0.3;
        }

        @keyframes pulse-line {
            0%, 100% { 
                opacity: 1;
                stroke-width: 4px;
            }
            50% { 
                opacity: 0.6;
                stroke-width: 6px;
            }
        }

        .node-circle {
            filter: drop-shadow(0 0 10px currentColor);
            transition: all 0.3s ease;
        }

        .journey-node:hover .node-circle {
            filter: drop-shadow(0 0 20px currentColor);
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
            font-size: 13px;
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
                filter: drop-shadow(0 0 12px #00d4ff) drop-shadow(0 0 20px #00d4ff);
            }
            50% {
                filter: drop-shadow(0 0 20px #00d4ff) drop-shadow(0 0 30px #00d4ff);
            }
        }

        .journey-legend {
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 25px;
            font-size: 12px;
            padding-top: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 10px;
            color: #94a3b8;
        }

        .legend-line {
            width: 35px;
            height: 4px;
            border-radius: 2px;
        }

        .legend-line.completed { background: #4ade80; }
        .legend-line.active { 
            background: #00d4ff;
            animation: pulse-legend 2s infinite;
        }
        .legend-line.potential { 
            background: #94a3b8; 
            opacity: 0.3;
        }

        @keyframes pulse-legend {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
'''

# Find where to insert journey styles (before closing style tag in modal section)
html = html.replace('        .clickable-row:hover {', journey_styles + '\n        .clickable-row:hover {')

# Add journey visualization JavaScript function
journey_js = '''
        // Trade Journey Visualization with D3.js
        function renderTradeJourney(trade) {
            // Clear existing visualization
            d3.select('#journeyViz').selectAll('*').remove();
            
            const events = trade.events;
            const latestEvent = events[events.length - 1];
            const isActive = !latestEvent.event_type.startsWith('EXIT_');
            
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
                    stage: 'EXIT',
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
                .attr('r', d => d.status === 'current' ? 40 : d.status === 'potential' ? 28 : 32)
                .attr('fill', d => d.color)
                .attr('opacity', d => d.status === 'potential' ? 0.3 : 0.9);
            
            // Node icons
            nodes.append('text')
                .attr('class', 'node-label')
                .attr('y', 6)
                .style('font-size', d => d.status === 'current' ? '24px' : '18px')
                .text(d => d.icon);
            
            // Node labels
            nodes.append('text')
                .attr('class', 'node-label')
                .attr('y', -50)
                .text(d => d.label);
            
            // Node sublabels (MFE values, etc.)
            nodes.filter(d => d.sublabel)
                .append('text')
                .attr('class', 'node-value')
                .attr('y', 55)
                .text(d => d.sublabel);
            
            // Node times
            nodes.filter(d => d.event)
                .append('text')
                .attr('class', 'node-time')
                .attr('y', 72)
                .text(d => {
                    if (d.event.signal_time) {
                        const time = d.event.signal_time.split('T')[1];
                        return time ? time.substring(0, 8) : '';
                    }
                    return '';
                });
        }

'''

# Insert journey JS before the closing script tag
html = html.replace('        // Trade Detail Modal Functions', journey_js + '\n        // Trade Detail Modal Functions')

# Update renderTradeDetail to include journey visualization
old_detail_section = '''                <div class="detail-section">
                    <h3>Trade Summary</h3>'''

new_detail_section = '''                <div class="journey-container">
                    <div class="journey-title">📍 Trade Journey Map</div>
                    <div id="journeyViz"></div>
                    <div class="journey-legend">
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
                            <span>Potential Next</span>
                        </div>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h3>Trade Summary</h3>'''

html = html.replace(old_detail_section, new_detail_section)

# Add call to renderTradeJourney at the end of renderTradeDetail
old_pre_close = '''            </div>
        `;
    }'''

new_pre_close = '''            </div>
        `;
        
        // Render the journey visualization
        setTimeout(() => renderTradeJourney(trade), 100);
    }'''

html = html.replace(old_pre_close, new_pre_close)

# Write updated dashboard
with open('automated_signals_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ Trade Journey Visualization Deployed!")
print("\nFeatures Added:")
print("━" * 80)
print("📍 Visual Journey Map - Shows complete trade lifecycle")
print("🎯 Key Milestones - Entry, First MFE, Peak MFE, Current, BE, Exit")
print("✨ Animated Current State - Pulsing glow on active position")
print("🔮 Potential Next States - Shows what could happen next")
print("🎨 Color-Coded Events - Green (completed), Blue (current), Gray (potential)")
print("📊 MFE Values - Displayed at each milestone")
print("⏰ Timestamps - Shows when each event occurred")
print("🖱️  Interactive - Hover for effects, click for details")
print("━" * 80)
print("\nThe journey visualization will appear at the top of the trade detail modal.")
print("It provides instant visual understanding of where the trade has been and where it's going!")
