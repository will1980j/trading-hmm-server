// Advanced D3.js Chart Library for Trading Dashboard
class D3Charts {
    constructor() {
        this.charts = {};
        this.tooltip = this.createTooltip();
        this.updateInterval = null;
    }

    createTooltip() {
        return d3.select("body").append("div")
            .attr("class", "d3-tooltip")
            .style("position", "absolute")
            .style("background", "rgba(0,0,0,0.9)")
            .style("color", "white")
            .style("padding", "8px")
            .style("border-radius", "4px")
            .style("font-size", "12px")
            .style("pointer-events", "none")
            .style("opacity", 0)
            .style("z-index", 1000);
    }

    createGradient(svg, id, color) {
        const defs = svg.select("defs").empty() ? svg.append("defs") : svg.select("defs");
        const gradient = defs.append("linearGradient")
            .attr("id", id)
            .attr("gradientUnits", "userSpaceOnUse")
            .attr("x1", 0).attr("y1", 0)
            .attr("x2", 0).attr("y2", "100%");
        gradient.append("stop")
            .attr("offset", "0%")
            .attr("stop-color", color)
            .attr("stop-opacity", 0.8);
        gradient.append("stop")
            .attr("offset", "100%")
            .attr("stop-color", color)
            .attr("stop-opacity", 0.1);
        return `url(#${id})`;
    }

    createLineChart(containerId, data, color = '#00ff88', labels = null) {
        const container = d3.select(`#${containerId}`);
        container.selectAll("*").remove();

        const margin = { top: 20, right: 30, bottom: 40, left: 50 };
        const width = container.node().getBoundingClientRect().width - margin.left - margin.right;
        const height = 250 - margin.top - margin.bottom;

        const svg = container.append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom);

        const clipPath = svg.append("defs").append("clipPath")
            .attr("id", `clip-${containerId}`)
            .append("rect")
            .attr("width", width)
            .attr("height", height);

        const g = svg.append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        const xScale = d3.scaleLinear().domain([0, data.length - 1]).range([0, width]);
        const yScale = d3.scaleLinear().domain(d3.extent(data)).nice().range([height, 0]);

        // Zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.5, 10])
            .extent([[0, 0], [width, height]])
            .on("zoom", (event) => {
                const newXScale = event.transform.rescaleX(xScale);
                const newYScale = event.transform.rescaleY(yScale);
                
                g.select(".line").attr("d", line.x((d, i) => newXScale(i)).y(d => newYScale(d)));
                g.select(".area").attr("d", area.x((d, i) => newXScale(i)).y1(d => newYScale(d)));
                g.select(".x-axis").call(d3.axisBottom(newXScale));
                g.select(".y-axis").call(d3.axisLeft(newYScale));
            });

        svg.call(zoom);

        const line = d3.line().x((d, i) => xScale(i)).y(d => yScale(d)).curve(d3.curveMonotoneX);
        const area = d3.area().x((d, i) => xScale(i)).y0(height).y1(d => yScale(d)).curve(d3.curveMonotoneX);

        const gradientId = `gradient-${containerId}`;
        const gradientUrl = this.createGradient(svg, gradientId, color);

        // Area with gradient
        const areaPath = g.append("path")
            .datum(data)
            .attr("class", "area")
            .attr("fill", gradientUrl)
            .attr("clip-path", `url(#clip-${containerId})`)
            .attr("d", area)
            .style("opacity", 0)
            .transition()
            .duration(1000)
            .style("opacity", 1);

        // Line with animation
        const linePath = g.append("path")
            .datum(data)
            .attr("class", "line")
            .attr("fill", "none")
            .attr("stroke", color)
            .attr("stroke-width", 2)
            .attr("clip-path", `url(#clip-${containerId})`)
            .attr("d", line);

        const totalLength = linePath.node().getTotalLength();
        linePath
            .attr("stroke-dasharray", totalLength + " " + totalLength)
            .attr("stroke-dashoffset", totalLength)
            .transition()
            .duration(2000)
            .ease(d3.easeLinear)
            .attr("stroke-dashoffset", 0);

        // Interactive dots
        const dots = g.selectAll(".dot")
            .data(data)
            .enter().append("circle")
            .attr("class", "dot")
            .attr("cx", (d, i) => xScale(i))
            .attr("cy", d => yScale(d))
            .attr("r", 0)
            .attr("fill", color)
            .style("opacity", 0)
            .on("mouseover", (event, d, i) => {
                const index = data.indexOf(d);
                this.tooltip.transition().duration(200).style("opacity", .9);
                this.tooltip.html(`Point ${index + 1}<br/>Value: ${d.toFixed(2)}`)
                    .style("left", (event.pageX + 10) + "px")
                    .style("top", (event.pageY - 28) + "px");
                d3.select(event.target).transition().duration(100).attr("r", 6);
            })
            .on("mouseout", (event) => {
                this.tooltip.transition().duration(500).style("opacity", 0);
                d3.select(event.target).transition().duration(100).attr("r", 3);
            })
            .transition()
            .delay((d, i) => i * 50)
            .duration(500)
            .attr("r", 3)
            .style("opacity", 0.7);

        // Brush for selection
        const brush = d3.brushX()
            .extent([[0, 0], [width, height]])
            .on("brush end", (event) => {
                if (!event.selection) return;
                const [x0, x1] = event.selection;
                const i0 = Math.round(xScale.invert(x0));
                const i1 = Math.round(xScale.invert(x1));
                console.log(`Selected range: ${i0} to ${i1}`);
            });

        g.append("g")
            .attr("class", "brush")
            .call(brush);

        // Axes
        g.append("g")
            .attr("class", "x-axis")
            .attr("transform", `translate(0,${height})`)
            .call(d3.axisBottom(xScale))
            .selectAll("text")
            .style("fill", "white");

        g.append("g")
            .attr("class", "y-axis")
            .call(d3.axisLeft(yScale))
            .selectAll("text")
            .style("fill", "white");

        this.charts[containerId] = { svg, g, xScale, yScale, data, zoom, brush };
    }

    createBarChart(containerId, data, labels, colors) {
        const container = d3.select(`#${containerId}`);
        container.selectAll("*").remove();

        const margin = { top: 20, right: 30, bottom: 40, left: 50 };
        const width = container.node().getBoundingClientRect().width - margin.left - margin.right;
        const height = 250 - margin.top - margin.bottom;

        const svg = container.append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom);

        const g = svg.append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        const xScale = d3.scaleBand().domain(labels).range([0, width]).padding(0.1);
        const yScale = d3.scaleLinear().domain([0, d3.max(data)]).nice().range([height, 0]);

        // Zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.5, 5])
            .extent([[0, 0], [width, height]])
            .on("zoom", (event) => {
                const newXScale = event.transform.rescaleX(xScale);
                const newYScale = event.transform.rescaleY(yScale);
                
                g.selectAll(".bar")
                    .attr("x", (d, i) => newXScale(labels[i]))
                    .attr("width", newXScale.bandwidth())
                    .attr("y", d => newYScale(d))
                    .attr("height", d => height - newYScale(d));
                
                g.select(".x-axis").call(d3.axisBottom(newXScale));
                g.select(".y-axis").call(d3.axisLeft(newYScale));
            });

        svg.call(zoom);

        // Create gradients for bars
        colors?.forEach((color, i) => {
            this.createGradient(svg, `bar-gradient-${containerId}-${i}`, color);
        });

        // Bars with animation and interactivity
        const bars = g.selectAll(".bar")
            .data(data)
            .enter().append("rect")
            .attr("class", "bar")
            .attr("x", (d, i) => xScale(labels[i]))
            .attr("width", xScale.bandwidth())
            .attr("y", height)
            .attr("height", 0)
            .attr("fill", (d, i) => colors ? `url(#bar-gradient-${containerId}-${i})` : '#00ff88')
            .on("mouseover", (event, d, i) => {
                const index = data.indexOf(d);
                this.tooltip.transition().duration(200).style("opacity", .9);
                this.tooltip.html(`${labels[index]}<br/>Value: ${d.toFixed(2)}`)
                    .style("left", (event.pageX + 10) + "px")
                    .style("top", (event.pageY - 28) + "px");
                d3.select(event.target)
                    .transition().duration(100)
                    .attr("stroke", "white")
                    .attr("stroke-width", 2);
            })
            .on("mouseout", (event) => {
                this.tooltip.transition().duration(500).style("opacity", 0);
                d3.select(event.target)
                    .transition().duration(100)
                    .attr("stroke", "none");
            })
            .transition()
            .delay((d, i) => i * 100)
            .duration(800)
            .attr("y", d => yScale(d))
            .attr("height", d => height - yScale(d));

        // Brush for selection
        const brush = d3.brushX()
            .extent([[0, 0], [width, height]])
            .on("brush end", (event) => {
                if (!event.selection) return;
                const [x0, x1] = event.selection;
                const selectedBars = [];
                bars.each(function(d, i) {
                    const barX = xScale(labels[i]);
                    if (barX >= x0 && barX <= x1) {
                        selectedBars.push({label: labels[i], value: d});
                    }
                });
                console.log('Selected bars:', selectedBars);
            });

        g.append("g")
            .attr("class", "brush")
            .call(brush);

        // Axes
        g.append("g")
            .attr("class", "x-axis")
            .attr("transform", `translate(0,${height})`)
            .call(d3.axisBottom(xScale))
            .selectAll("text")
            .style("fill", "white");

        g.append("g")
            .attr("class", "y-axis")
            .call(d3.axisLeft(yScale))
            .selectAll("text")
            .style("fill", "white");

        this.charts[containerId] = { svg, g, xScale, yScale, data, labels, zoom, brush };
    }

    // Real-time update method
    updateChart(containerId, newData, labels = null) {
        const chart = this.charts[containerId];
        if (!chart) return;

        const { svg, g, xScale, yScale } = chart;
        
        if (chart.data) {
            // Line chart update
            const line = d3.line().x((d, i) => xScale(i)).y(d => yScale(d)).curve(d3.curveMonotoneX);
            const area = d3.area().x((d, i) => xScale(i)).y0(yScale.range()[0]).y1(d => yScale(d)).curve(d3.curveMonotoneX);
            
            yScale.domain(d3.extent(newData)).nice();
            
            g.select(".line")
                .datum(newData)
                .transition()
                .duration(500)
                .attr("d", line);
                
            g.select(".area")
                .datum(newData)
                .transition()
                .duration(500)
                .attr("d", area);
                
            g.select(".y-axis")
                .transition()
                .duration(500)
                .call(d3.axisLeft(yScale));
                
            chart.data = newData;
        } else if (chart.labels) {
            // Bar chart update
            yScale.domain([0, d3.max(newData)]).nice();
            
            g.selectAll(".bar")
                .data(newData)
                .transition()
                .duration(500)
                .attr("y", d => yScale(d))
                .attr("height", d => yScale.range()[0] - yScale(d));
                
            g.select(".y-axis")
                .transition()
                .duration(500)
                .call(d3.axisLeft(yScale));
                
            chart.data = newData;
        }
    }

    // Start real-time updates
    startRealTimeUpdates(interval = 5000) {
        if (this.updateInterval) clearInterval(this.updateInterval);
        this.updateInterval = setInterval(() => {
            if (typeof updateD3Charts === 'function') {
                updateD3Charts();
            }
        }, interval);
    }

    // Stop real-time updates
    stopRealTimeUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }
}

// Initialize all D3 charts with advanced features
function initD3Charts() {
    if (typeof d3 === 'undefined') {
        console.warn('D3.js not loaded');
        return;
    }

    window.d3Charts = new D3Charts();
    
    // Add CSS for enhanced styling
    const style = document.createElement('style');
    style.textContent = `
        .d3-tooltip {
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            border: 1px solid #333;
        }
        .brush .selection {
            fill: rgba(0, 255, 136, 0.2);
            stroke: #00ff88;
        }
        .bar:hover {
            filter: brightness(1.2);
        }
        .dot {
            cursor: pointer;
        }
        svg {
            cursor: grab;
        }
        svg:active {
            cursor: grabbing;
        }
    `;
    document.head.appendChild(style);
    
    console.log('Advanced D3 charts initialized with interactive features');
    
    // Start real-time updates
    window.d3Charts.startRealTimeUpdates();
}

// Update all D3 charts with current data
function updateD3Charts() {
    if (!window.d3Charts || !window.trades || window.trades.length === 0) return;

    const filteredTrades = getFilteredTrades();
    const rTargetElement = document.getElementById('rTargetFilter');
    const rTarget = rTargetElement ? parseInt(rTargetElement.value) : 1;

    // Equity Chart
    let cumulative = 0;
    const equityData = filteredTrades.map(trade => {
        cumulative += getRValue(trade, rTarget);
        return cumulative;
    });
    window.d3Charts.createLineChart('d3EquityChart', equityData, '#00ff88');

    // Daily Equity
    const dailyData = {};
    filteredTrades.forEach(trade => {
        const date = trade.date;
        if (!dailyData[date]) dailyData[date] = 0;
        dailyData[date] += getRValue(trade, rTarget);
    });
    const dailyLabels = Object.keys(dailyData).sort();
    let dailyCumulative = 0;
    const dailyEquityData = dailyLabels.map(date => {
        dailyCumulative += dailyData[date];
        return dailyCumulative;
    });
    window.d3Charts.createLineChart('d3DailyEquityChart', dailyEquityData, '#ffa502');

    // Weekly Equity
    const weeklyData = {};
    filteredTrades.forEach(trade => {
        const date = new Date(trade.date);
        const weekStr = getWeekString(date);
        if (!weeklyData[weekStr]) weeklyData[weekStr] = 0;
        weeklyData[weekStr] += getRValue(trade, rTarget);
    });
    const weeklyLabels = Object.keys(weeklyData).sort();
    let weeklyCumulative = 0;
    const weeklyEquityData = weeklyLabels.map(week => {
        weeklyCumulative += weeklyData[week];
        return weeklyCumulative;
    });
    window.d3Charts.createLineChart('d3WeeklyEquityChart', weeklyEquityData, '#3742fa');

    // Monthly Equity
    const monthlyData = {};
    filteredTrades.forEach(trade => {
        const monthStr = trade.date.slice(0, 7);
        if (!monthlyData[monthStr]) monthlyData[monthStr] = 0;
        monthlyData[monthStr] += getRValue(trade, rTarget);
    });
    const monthlyLabels = Object.keys(monthlyData).sort();
    let monthlyCumulative = 0;
    const monthlyEquityData = monthlyLabels.map(month => {
        monthlyCumulative += monthlyData[month];
        return monthlyCumulative;
    });
    window.d3Charts.createLineChart('d3MonthlyEquityChart', monthlyEquityData, '#ff4757');

    // R-Score Distribution - Fixed to capture all R values
    const rValues = filteredTrades.map(trade => getRValue(trade, rTarget));
    const maxR = Math.max(...rValues, 50); // Ensure we capture high R values
    const minR = Math.min(...rValues, -5);
    
    const rDistribution = new Array(maxR - minR + 1).fill(0);
    rValues.forEach(rValue => {
        const index = Math.floor(rValue) - minR;
        if (index >= 0 && index < rDistribution.length) {
            rDistribution[index]++;
        }
    });
    
    const rLabels = [];
    const rColors = [];
    for (let i = minR; i <= maxR; i++) {
        rLabels.push(i + 'R');
        if (i < 0) rColors.push('#ff4757');
        else if (i === 0) rColors.push('#ffa502');
        else {
            const hue = Math.min(120 + (i * 8), 180);
            rColors.push(`hsl(${hue}, 70%, 50%)`);
        }
    }
    // Filter out empty buckets for cleaner display
    const nonZeroIndices = rDistribution.map((count, i) => count > 0 ? i : -1).filter(i => i !== -1);
    const filteredRDist = nonZeroIndices.map(i => rDistribution[i]);
    const filteredRLabels = nonZeroIndices.map(i => rLabels[i]);
    const filteredRColors = nonZeroIndices.map(i => rColors[i]);
    
    window.d3Charts.createBarChart('d3RScoreChart', filteredRDist, filteredRLabels, filteredRColors);

    // Day of Week
    const dayPerf = analyzeDayOfWeek(filteredTrades, rTarget);
    const dayLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];
    const dayColors = ['#ff6b7a', '#ffa502', '#00ff88', '#00d4aa', '#3742fa'];
    window.d3Charts.createBarChart('d3DayOfWeekChart', dayPerf.expectancy, dayLabels, dayColors);

    // Seasonality
    const seasonalData = analyzeSeasonality(filteredTrades, rTarget);
    window.d3Charts.createLineChart('d3SeasonalityChart', seasonalData, '#00ff88');

    // Rolling Performance
    const rollingData = calculateRollingPerformance(filteredTrades, rTarget, 30);
    window.d3Charts.createLineChart('d3RollingChart', rollingData.values, '#ffa502');

    // Session Heatmap
    const sessionPerf = analyzeSessionPerformance(filteredTrades, rTarget);
    const sessionLabels = ['Asia', 'London', 'NY Pre', 'NY AM', 'NY Lunch', 'NY PM'];
    const sessionColors = ['#ff4757', '#ffa502', '#00ff88', '#00d4aa', '#3742fa', '#5f27cd'];
    window.d3Charts.createBarChart('d3SessionHeatmapChart', sessionPerf, sessionLabels, sessionColors);
}

// Global exports
window.initD3Charts = initD3Charts;
window.updateD3Charts = updateD3Charts;
window.D3Charts = D3Charts;

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initD3Charts);
} else {
    initD3Charts();
}