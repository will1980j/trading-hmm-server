// D3.js Chart Library for Trading Dashboard
class D3Charts {
    constructor() {
        this.charts = {};
    }

    createLineChart(containerId, data, color = '#00ff88') {
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

        const xScale = d3.scaleLinear().domain([0, data.length - 1]).range([0, width]);
        const yScale = d3.scaleLinear().domain(d3.extent(data)).nice().range([height, 0]);

        const line = d3.line().x((d, i) => xScale(i)).y(d => yScale(d)).curve(d3.curveMonotoneX);
        const area = d3.area().x((d, i) => xScale(i)).y0(height).y1(d => yScale(d)).curve(d3.curveMonotoneX);

        g.append("path").datum(data).attr("fill", color + '20').attr("d", area);
        g.append("path").datum(data).attr("fill", "none").attr("stroke", color).attr("stroke-width", 2).attr("d", line);

        g.append("g").attr("transform", `translate(0,${height})`).call(d3.axisBottom(xScale)).selectAll("text").style("fill", "white");
        g.append("g").call(d3.axisLeft(yScale)).selectAll("text").style("fill", "white");

        this.charts[containerId] = { svg, g, xScale, yScale };
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

        g.selectAll(".bar").data(data).enter().append("rect")
            .attr("class", "bar")
            .attr("x", (d, i) => xScale(labels[i]))
            .attr("width", xScale.bandwidth())
            .attr("y", d => yScale(d))
            .attr("height", d => height - yScale(d))
            .attr("fill", (d, i) => colors ? colors[i] : '#00ff88');

        g.append("g").attr("transform", `translate(0,${height})`).call(d3.axisBottom(xScale)).selectAll("text").style("fill", "white");
        g.append("g").call(d3.axisLeft(yScale)).selectAll("text").style("fill", "white");

        this.charts[containerId] = { svg, g, xScale, yScale };
    }
}

// Initialize all D3 charts
function initD3Charts() {
    if (typeof d3 === 'undefined') {
        console.warn('D3.js not loaded');
        return;
    }

    window.d3Charts = new D3Charts();
    console.log('D3 charts initialized');
}

// Update all D3 charts with current data
function updateD3Charts() {
    if (!window.d3Charts || !window.trades || window.trades.length === 0) return;

    const filteredTrades = getFilteredTrades();
    const rTarget = parseInt(document.getElementById('rTargetFilter').value);

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

window.initD3Charts = initD3Charts;
window.updateD3Charts = updateD3Charts;