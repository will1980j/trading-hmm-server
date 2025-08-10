// D3.js Chart Library for Trading Dashboard
class D3Charts {
    constructor() {
        this.charts = {};
    }

    // Create enhanced equity chart with D3
    createEquityChart(containerId, data) {
        const container = d3.select(`#${containerId}`);
        container.selectAll("*").remove(); // Clear existing content

        const margin = { top: 20, right: 30, bottom: 40, left: 50 };
        const width = container.node().getBoundingClientRect().width - margin.left - margin.right;
        const height = 300 - margin.top - margin.bottom;

        const svg = container
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom);

        const g = svg.append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        // Create scales
        const xScale = d3.scaleLinear()
            .domain([0, data.length - 1])
            .range([0, width]);

        const yScale = d3.scaleLinear()
            .domain(d3.extent(data))
            .nice()
            .range([height, 0]);

        // Create line generator
        const line = d3.line()
            .x((d, i) => xScale(i))
            .y(d => yScale(d))
            .curve(d3.curveMonotoneX);

        // Create gradient
        const gradient = svg.append("defs")
            .append("linearGradient")
            .attr("id", "equityGradient")
            .attr("gradientUnits", "userSpaceOnUse")
            .attr("x1", 0).attr("y1", height)
            .attr("x2", 0).attr("y2", 0);

        gradient.append("stop")
            .attr("offset", "0%")
            .attr("stop-color", "#00ff88")
            .attr("stop-opacity", 0.1);

        gradient.append("stop")
            .attr("offset", "100%")
            .attr("stop-color", "#00ff88")
            .attr("stop-opacity", 0.8);

        // Create area
        const area = d3.area()
            .x((d, i) => xScale(i))
            .y0(height)
            .y1(d => yScale(d))
            .curve(d3.curveMonotoneX);

        // Add area
        g.append("path")
            .datum(data)
            .attr("fill", "url(#equityGradient)")
            .attr("d", area);

        // Add line
        g.append("path")
            .datum(data)
            .attr("fill", "none")
            .attr("stroke", "#00ff88")
            .attr("stroke-width", 2)
            .attr("d", line);

        // Add axes
        g.append("g")
            .attr("transform", `translate(0,${height})`)
            .call(d3.axisBottom(xScale).tickFormat(d => `T${d + 1}`))
            .selectAll("text")
            .style("fill", "white");

        g.append("g")
            .call(d3.axisLeft(yScale).tickFormat(d => `${d}R`))
            .selectAll("text")
            .style("fill", "white");

        // Add interactive dots
        g.selectAll(".dot")
            .data(data)
            .enter().append("circle")
            .attr("class", "dot")
            .attr("cx", (d, i) => xScale(i))
            .attr("cy", d => yScale(d))
            .attr("r", 3)
            .attr("fill", "#00ff88")
            .style("opacity", 0)
            .on("mouseover", function(event, d) {
                d3.select(this).style("opacity", 1);
                
                // Create tooltip
                const tooltip = d3.select("body").append("div")
                    .attr("class", "d3-tooltip")
                    .style("position", "absolute")
                    .style("background", "rgba(0,0,0,0.8)")
                    .style("color", "white")
                    .style("padding", "8px")
                    .style("border-radius", "4px")
                    .style("font-size", "12px")
                    .style("pointer-events", "none")
                    .style("z-index", "1000")
                    .html(`Trade ${data.indexOf(d) + 1}: ${d.toFixed(2)}R`)
                    .style("left", (event.pageX + 10) + "px")
                    .style("top", (event.pageY - 10) + "px");
            })
            .on("mouseout", function() {
                d3.select(this).style("opacity", 0);
                d3.selectAll(".d3-tooltip").remove();
            });

        this.charts[containerId] = { svg, g, xScale, yScale };
    }

    // Create enhanced bar chart
    createBarChart(containerId, data, labels) {
        const container = d3.select(`#${containerId}`);
        container.selectAll("*").remove();

        const margin = { top: 20, right: 30, bottom: 40, left: 50 };
        const width = container.node().getBoundingClientRect().width - margin.left - margin.right;
        const height = 300 - margin.top - margin.bottom;

        const svg = container
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom);

        const g = svg.append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        const xScale = d3.scaleBand()
            .domain(labels)
            .range([0, width])
            .padding(0.1);

        const yScale = d3.scaleLinear()
            .domain([0, d3.max(data)])
            .nice()
            .range([height, 0]);

        // Color scale
        const colorScale = d3.scaleSequential(d3.interpolateViridis)
            .domain([0, data.length - 1]);

        // Add bars
        g.selectAll(".bar")
            .data(data)
            .enter().append("rect")
            .attr("class", "bar")
            .attr("x", (d, i) => xScale(labels[i]))
            .attr("width", xScale.bandwidth())
            .attr("y", height)
            .attr("height", 0)
            .attr("fill", (d, i) => colorScale(i))
            .transition()
            .duration(800)
            .attr("y", d => yScale(d))
            .attr("height", d => height - yScale(d));

        // Add axes
        g.append("g")
            .attr("transform", `translate(0,${height})`)
            .call(d3.axisBottom(xScale))
            .selectAll("text")
            .style("fill", "white");

        g.append("g")
            .call(d3.axisLeft(yScale))
            .selectAll("text")
            .style("fill", "white");

        this.charts[containerId] = { svg, g, xScale, yScale };
    }

    // Update existing chart
    updateChart(containerId, newData) {
        if (!this.charts[containerId]) return;

        const chart = this.charts[containerId];
        // Implementation for updating charts would go here
        console.log(`Updating chart ${containerId} with new data`);
    }
}

// Initialize D3 charts when DOM is ready
function initD3EquityChart() {
    if (typeof d3 === 'undefined') {
        console.warn('D3.js not loaded, skipping D3 chart initialization');
        return;
    }

    const d3Charts = new D3Charts();
    
    // Example usage - you can integrate this with your existing data
    if (window.trades && window.trades.length > 0) {
        const rTarget = parseInt(document.getElementById('rTargetFilter')?.value || 1);
        let cumulative = 0;
        const equityData = window.trades.map(trade => {
            const rValue = getRValue ? getRValue(trade, rTarget) : (trade.rScore || 0);
            cumulative += rValue;
            return cumulative;
        });

        // Create a D3 equity chart in a new container (you'd need to add this to HTML)
        const d3Container = document.getElementById('d3EquityContainer');
        if (d3Container) {
            d3Charts.createEquityChart('d3EquityContainer', equityData);
        }
    }
}

// Make D3Charts available globally
window.d3Charts = new D3Charts();
window.initD3EquityChart = initD3EquityChart;