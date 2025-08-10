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

    // R-Score Distribution
    const rDistribution = new Array(23).fill(0);
    filteredTrades.forEach(trade => {
        const rValue = getRValue(trade, rTarget);
        if (rValue <= -2) rDistribution[0]++;
        else if (rValue <= -1) rDistribution[1]++;
        else if (rValue === 0) rDistribution[2]++;
        else if (rValue >= 1 && rValue <= 20) {
            const index = Math.floor(rValue) + 2;
            if (index < 23) rDistribution[index]++;
            else rDistribution[22]++;
        }
    });
    const rLabels = ['-2R', '-1R', '0R'];
    for (let i = 1; i <= 20; i++) rLabels.push(i + 'R');
    const rColors = ['#ff4757', '#ff6b7a', '#ffa502'];
    for (let i = 1; i <= 20; i++) {
        const hue = (i - 1) * 15;
        rColors.push(`hsl(${120 + hue}, 70%, 50%)`);
    }
    window.d3Charts.createBarChart('d3RScoreChart', rDistribution, rLabels, rColors);

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