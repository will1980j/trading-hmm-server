// D3 Chart Library for Trading Dashboard
class D3Charts {
    constructor() {
        this.margin = { top: 20, right: 30, bottom: 40, left: 50 };
    }

    createEquityChart(containerId, data) {
        const container = d3.select(`#${containerId}`);
        container.selectAll("*").remove();
        
        const width = container.node().getBoundingClientRect().width - this.margin.left - this.margin.right;
        const height = 280 - this.margin.top - this.margin.bottom;

        const svg = container.append("svg")
            .attr("width", width + this.margin.left + this.margin.right)
            .attr("height", height + this.margin.top + this.margin.bottom);

        const g = svg.append("g")
            .attr("transform", `translate(${this.margin.left},${this.margin.top})`);

        // Scales
        const xScale = d3.scaleLinear()
            .domain([0, data.length - 1])
            .range([0, width]);

        const yScale = d3.scaleLinear()
            .domain(d3.extent(data))
            .nice()
            .range([height, 0]);

        // Gradient
        const gradient = svg.append("defs")
            .append("linearGradient")
            .attr("id", "equity-gradient")
            .attr("gradientUnits", "userSpaceOnUse")
            .attr("x1", 0).attr("y1", height)
            .attr("x2", 0).attr("y2", 0);

        gradient.append("stop")
            .attr("offset", "0%")
            .attr("stop-color", "#00ff88")
            .attr("stop-opacity", 0);

        gradient.append("stop")
            .attr("offset", "100%")
            .attr("stop-color", "#00ff88")
            .attr("stop-opacity", 0.3);

        // Line generator
        const line = d3.line()
            .x((d, i) => xScale(i))
            .y(d => yScale(d))
            .curve(d3.curveCardinal);

        // Area generator
        const area = d3.area()
            .x((d, i) => xScale(i))
            .y0(height)
            .y1(d => yScale(d))
            .curve(d3.curveCardinal);

        // Add area
        g.append("path")
            .datum(data)
            .attr("fill", "url(#equity-gradient)")
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
            .call(d3.axisBottom(xScale).ticks(5))
            .selectAll("text")
            .style("fill", "white");

        g.append("g")
            .call(d3.axisLeft(yScale).ticks(5))
            .selectAll("text")
            .style("fill", "white");

        // Style axes
        g.selectAll(".domain, .tick line")
            .style("stroke", "rgba(255,255,255,0.2)");

        // Add hover effects
        const focus = g.append("g").style("display", "none");
        
        focus.append("circle")
            .attr("r", 4)
            .attr("fill", "#00ff88");

        focus.append("rect")
            .attr("class", "tooltip")
            .attr("width", 80)
            .attr("height", 30)
            .attr("x", -40)
            .attr("y", -40)
            .attr("rx", 4)
            .style("fill", "rgba(0,0,0,0.8)");

        focus.append("text")
            .attr("class", "tooltip-text")
            .attr("text-anchor", "middle")
            .attr("y", -20)
            .style("fill", "white")
            .style("font-size", "12px");

        svg.append("rect")
            .attr("class", "overlay")
            .attr("width", width)
            .attr("height", height)
            .attr("transform", `translate(${this.margin.left},${this.margin.top})`)
            .style("fill", "none")
            .style("pointer-events", "all")
            .on("mouseover", () => focus.style("display", null))
            .on("mouseout", () => focus.style("display", "none"))
            .on("mousemove", function(event) {
                const [x] = d3.pointer(event);
                const i = Math.round(xScale.invert(x));
                if (i >= 0 && i < data.length) {
                    focus.attr("transform", `translate(${xScale(i)},${yScale(data[i])})`);
                    focus.select(".tooltip-text").text(`${data[i].toFixed(2)}R`);
                }
            });
    }

    createBarChart(containerId, data, colors) {
        const container = d3.select(`#${containerId}`);
        container.selectAll("*").remove();
        
        const width = container.node().getBoundingClientRect().width - this.margin.left - this.margin.right;
        const height = 280 - this.margin.top - this.margin.bottom;

        const svg = container.append("svg")
            .attr("width", width + this.margin.left + this.margin.right)
            .attr("height", height + this.margin.top + this.margin.bottom);

        const g = svg.append("g")
            .attr("transform", `translate(${this.margin.left},${this.margin.top})`);

        const xScale = d3.scaleBand()
            .domain(data.map((d, i) => i))
            .range([0, width])
            .padding(0.1);

        const yScale = d3.scaleLinear()
            .domain([0, d3.max(data)])
            .nice()
            .range([height, 0]);

        // Bars
        g.selectAll(".bar")
            .data(data)
            .enter().append("rect")
            .attr("class", "bar")
            .attr("x", (d, i) => xScale(i))
            .attr("width", xScale.bandwidth())
            .attr("y", height)
            .attr("height", 0)
            .attr("fill", (d, i) => colors[i] || "#00ff88")
            .transition()
            .duration(800)
            .attr("y", d => yScale(d))
            .attr("height", d => height - yScale(d));

        // Axes
        g.append("g")
            .attr("transform", `translate(0,${height})`)
            .call(d3.axisBottom(xScale))
            .selectAll("text")
            .style("fill", "white");

        g.append("g")
            .call(d3.axisLeft(yScale))
            .selectAll("text")
            .style("fill", "white");

        g.selectAll(".domain, .tick line")
            .style("stroke", "rgba(255,255,255,0.2)");
    }
}

// Initialize D3 Charts
window.d3Charts = new D3Charts();

// Replace Chart.js equity chart with D3
function initD3EquityChart() {
    const equityContainer = document.getElementById('equityChart').parentElement;
    equityContainer.innerHTML = '<div id="d3-equity-chart"></div>';
    
    // Sample data - replace with your actual equity data
    const sampleData = [0, 1.5, 0.5, 2.1, 1.8, 3.2, 2.9, 4.1, 3.8, 5.2];
    window.d3Charts.createEquityChart('d3-equity-chart', sampleData);
}

// Update function for D3 charts
function updateD3Charts() {
    const filteredTrades = getFilteredTrades();
    const rTarget = parseInt(document.getElementById('rTargetFilter').value);
    
    // Calculate equity data
    let cumulative = 0;
    const equityData = filteredTrades.map(trade => {
        cumulative += getRValue(trade, rTarget);
        return cumulative;
    });
    
    if (equityData.length > 0) {
        window.d3Charts.createEquityChart('d3-equity-chart', equityData);
    }
}