// Trading Dashboard API Integration
class TradingDashboardAPI {
    constructor() {
        this.baseUrl = window.location.origin;
    }

    // Export data for external tools
    exportForGamma() {
        let trades = [];
        let propFirms = [];
        try {
            trades = JSON.parse(localStorage.getItem('tradingData') || '[]');
            propFirms = JSON.parse(localStorage.getItem('propFirmsV2_2024-01') || '[]');
        } catch (e) {
            console.error('Error parsing localStorage data:', e);
        }
        
        return {
            summary: this.generateSummary(trades, propFirms),
            charts: this.generateChartData(trades),
            metrics: this.calculateMetrics(trades, propFirms),
            timestamp: new Date().toISOString()
        };
    }

    generateSummary(trades, propFirms) {
        const fundedFirms = propFirms.filter(firm => firm.status === 'funded');
        const totalRiskRewardRatio = trades.reduce((sum, trade) => {
            try {
                if (trade.breakeven) return sum;
                const rTarget = parseFloat(trade.rTarget) || 1;
                
                // Validate numeric values
                if (!Number.isFinite(rTarget)) {
                    console.warn('Invalid rTarget value:', trade.rTarget);
                    return sum;
                }
                
                return sum + (trade.outcome === 'win' ? rTarget : (trade.outcome === 'loss' ? -1 : 0));
            } catch (error) {
                console.error('Error processing trade:', error);
                return sum;
            }
        }, 0);
        const winRate = trades.length > 0 ? ((trades.filter(t => t.outcome === 'win' || t.breakeven).length / trades.length) * 100).toFixed(1) : 0;
        
        return {
            totalTrades: trades.length,
            winRate: winRate + '%',
            totalR: totalRiskRewardRatio.toFixed(1) + 'R',
            fundedAccounts: fundedFirms.length,
            portfolioValue: fundedFirms.reduce((sum, f) => sum + f.accountSize, 0)
        };
    }

    generateChartData(trades) {
        let cumulative = 0;
        const equityData = trades.map((trade, index) => {
            cumulative += trade.profit || 0;
            return { x: index + 1, y: cumulative };
        });

        return {
            equity: equityData,
            monthlyPerformance: this.getMonthlyData(trades)
        };
    }

    calculateMetrics(trades, propFirms) {
        const fundedFirms = propFirms.filter(f => f.status === 'funded');
        const monthlyProfit = fundedFirms.reduce((sum, f) => sum + (f.monthlyProfit || 0), 0);
        
        return {
            expectancy: trades.length > 0 ? (trades.reduce((sum, t) => sum + (t.rScore || 0), 0) / trades.length).toFixed(2) : 0,
            monthlyProfit: monthlyProfit,
            successRate: propFirms.length > 0 ? ((fundedFirms.length / propFirms.length) * 100).toFixed(1) : 0
        };
    }

    getMonthlyData(trades) {
        const monthly = {};
        trades.forEach(trade => {
            try {
                if (trade && trade.date) {
                    const month = trade.date.substring(0, 7);
                    if (!monthly[month]) monthly[month] = 0;
                    const profit = trade.profit || 0;
                    if (Number.isFinite(profit)) {
                        monthly[month] += profit;
                    }
                }
            } catch (error) {
                console.error('Error processing trade data:', error);
                // Skip this trade and continue processing
            }
        });
        return monthly;
    }

    // Generate comprehensive AI-driven content for Gamma presentations
    generateGammaPresentation(reportType = 'comprehensive') {
        const trades = JSON.parse(localStorage.getItem('tradingData')) || [];
        const propFirms = JSON.parse(localStorage.getItem('propFirmsV2_2024-01')) || [];
        const insights = this.generateAIInsights(trades, propFirms, reportType);
        const data = this.exportForGamma();
        
        const presentations = {
            comprehensive: this.generateComprehensivePresentation(data, insights),
            investor: this.generateInvestorPresentation(data, insights),
            risk: this.generateRiskPresentation(data, insights),
            monthly: this.generateMonthlyPresentation(data, insights),
            strategy: this.generateStrategyPresentation(data, insights),
            quarterly: this.generateQuarterlyPresentation(data, insights)
        };
        
        return presentations[reportType] || presentations.comprehensive;
    }

    generateAIInsights(trades, propFirms, reportType) {
        const metrics = this.calculateAdvancedMetrics(trades, propFirms);
        
        return {
            executiveSummary: this.generateExecutiveSummary(metrics, reportType),
            keyFindings: this.generateKeyFindings(metrics, trades),
            recommendations: this.generateRecommendations(metrics, reportType),
            riskAssessment: this.generateRiskAssessment(metrics, trades),
            performanceAnalysis: this.generatePerformanceAnalysis(metrics, trades),
            marketOutlook: this.generateMarketOutlook(metrics, reportType),
            strategicInsights: this.generateStrategicInsights(metrics, trades, reportType)
        };
    }

    calculateAdvancedMetrics(trades, propFirms) {
        try {
            const fundedFirms = propFirms.filter(firm => firm.status === 'funded');
            const rValues = trades.map(trade => {
                if (trade.breakeven) return 0;
                const rTarget = parseFloat(trade.rTarget) || 1;
                return trade.outcome === 'win' ? rTarget : (trade.outcome === 'loss' ? -1 : 0);
            });
            const winningTrades = trades.filter(trade => trade.outcome === 'win');
            const losingTrades = trades.filter(trade => trade.outcome === 'loss');
        
        return {
            totalTrades: trades.length,
            winRate: trades.length ? (winningTrades.length / trades.length * 100) : 0,
            avgWin: winningTrades.length ? winningTrades.reduce((sum, t) => sum + (parseFloat(t.rTarget) || 1), 0) / winningTrades.length : 0,
            avgLoss: 1,
            totalR: rValues.reduce((sum, r) => sum + r, 0),
            maxDrawdown: this.calculateMaxDrawdown(rValues),
            sharpeRatio: this.calculateSharpeRatio(rValues),
            profitFactor: this.calculateProfitFactor(winningTrades, losingTrades),
            fundedAccounts: fundedFirms.length,
            totalCapital: fundedFirms.reduce((sum, f) => sum + f.accountSize, 0),
            monthlyProfit: fundedFirms.reduce((sum, f) => sum + (f.monthlyProfit || 0), 0),
            successRate: propFirms.length ? (fundedFirms.length / propFirms.length * 100) : 0
        };
        } catch (error) {
            console.error('Error calculating advanced metrics:', error);
            throw new Error('Failed to calculate trading metrics');
        }
    }

    generateExecutiveSummary(metrics, reportType) {
        const performance = metrics.totalR > 0 ? 'profitable' : 'developmental';
        const trend = metrics.winRate > 55 ? 'strong momentum' : metrics.winRate > 45 ? 'stable execution' : 'optimization phase';
        
        switch(reportType) {
            case 'investor':
                return `Our systematic trading approach demonstrates ${performance} performance with ${trend} across ${metrics.totalTrades} executed positions. Current portfolio metrics show ${metrics.winRate.toFixed(1)}% trade accuracy with ${metrics.fundedAccounts} funded accounts managing $${(metrics.totalCapital/1000).toFixed(0)}K in capital. Risk-adjusted returns maintain institutional standards with controlled drawdown parameters.`;
            case 'risk':
                return `Risk management framework maintains ${metrics.maxDrawdown.toFixed(2)}% maximum drawdown across ${metrics.totalTrades} positions. Portfolio diversification through ${metrics.fundedAccounts} funded accounts provides capital preservation with systematic risk controls. Current volatility metrics align with conservative institutional parameters.`;
            case 'monthly':
                return `Monthly trading operations generated ${metrics.totalR > 0 ? 'positive' : 'learning-focused'} results of ${metrics.totalR.toFixed(1)}R across ${metrics.totalTrades} positions. Win rate of ${metrics.winRate.toFixed(1)}% demonstrates ${trend} with systematic execution protocols. Risk management maintained drawdown within ${metrics.maxDrawdown.toFixed(2)}% parameters.`;
            default:
                return `Systematic trading strategy demonstrates ${performance} execution with ${trend}. Portfolio management across ${metrics.fundedAccounts} funded accounts shows disciplined risk management and consistent methodology application.`;
        }
    }

    generateKeyFindings(metrics, trades) {
        if (!metrics || !trades) {
            return ['⚠️ Insufficient data for analysis'];
        }
        
        const findings = [];
        
        if (metrics.winRate > 60) {
            findings.push(`Exceptional ${metrics.winRate.toFixed(1)}% win rate indicates superior market timing and entry criteria optimization`);
        } else if (metrics.winRate > 50) {
            findings.push(`Solid ${metrics.winRate.toFixed(1)}% win rate demonstrates consistent edge in systematic trade selection`);
        } else {
            findings.push(`${metrics.winRate.toFixed(1)}% win rate presents optimization opportunities in strategy refinement`);
        }
        
        if (metrics.profitFactor > 1.5) {
            findings.push(`Strong ${metrics.profitFactor.toFixed(2)} profit factor indicates effective risk-reward optimization`);
        }
        
        if (metrics.fundedAccounts > 3) {
            findings.push(`Portfolio diversification across ${metrics.fundedAccounts} funded accounts provides robust capital base`);
        }
        
        if (metrics.maxDrawdown < 10) {
            findings.push(`Excellent ${metrics.maxDrawdown.toFixed(2)}% drawdown control demonstrates disciplined risk management`);
        }
        
        if (metrics.successRate > 70) {
            findings.push(`${metrics.successRate.toFixed(1)}% prop firm success rate shows consistent evaluation performance`);
        }
        
        return findings;
    }

    generateRecommendations(metrics, reportType) {
        const recommendations = [];
        
        if (metrics.winRate < 50) {
            recommendations.push('Implement enhanced backtesting protocols for entry criteria optimization');
            recommendations.push('Consider position size reduction until win rate stabilizes above 55%');
        }
        
        if (metrics.maxDrawdown > 15) {
            recommendations.push('Strengthen stop-loss protocols and implement dynamic position sizing');
        }
        
        if (metrics.fundedAccounts < 3) {
            recommendations.push('Expand funded account portfolio for improved diversification and capital growth');
        }
        
        if (reportType === 'investor') {
            recommendations.push('Maintain systematic approach with quarterly performance reviews');
            recommendations.push('Consider capital allocation increase based on consistent risk-adjusted returns');
        }
        
        return recommendations;
    }

    generateRiskAssessment(metrics, trades) {
        const riskLevel = metrics.maxDrawdown > 20 ? 'Elevated' : metrics.maxDrawdown > 10 ? 'Moderate' : 'Conservative';
        return `Risk profile classified as ${riskLevel} with ${metrics.maxDrawdown.toFixed(2)}% maximum drawdown. Portfolio heat distribution across ${metrics.fundedAccounts} accounts provides adequate diversification. Current risk-adjusted returns via Sharpe ratio of ${metrics.sharpeRatio.toFixed(2)} ${metrics.sharpeRatio > 1 ? 'exceed' : 'meet'} institutional benchmarks.`;
    }

    generatePerformanceAnalysis(metrics, trades) {
        const consistency = metrics.winRate > 55 ? 'highly consistent' : 'developing';
        return `Performance analysis reveals ${consistency} execution with ${metrics.totalR.toFixed(1)}R total returns. Average winning trade of ${metrics.avgWin.toFixed(2)}R versus ${metrics.avgLoss.toFixed(2)}R average loss yields ${(metrics.avgWin/Math.abs(metrics.avgLoss) || 0).toFixed(2)}:1 reward-risk ratio. Profit factor of ${metrics.profitFactor.toFixed(2)} indicates ${metrics.profitFactor > 1.5 ? 'strong' : 'developing'} systematic edge.`;
    }

    generateMarketOutlook(metrics, reportType) {
        const trades = JSON.parse(localStorage.getItem('tradingData')) || [];
        const recentTrades = trades.slice(-10);
        const recentPerformance = recentTrades.length ? recentTrades.reduce((sum, t) => {
            if (t.breakeven) return sum;
            const rTarget = parseFloat(t.rTarget) || 1;
            return sum + (t.outcome === 'win' ? rTarget : (t.outcome === 'loss' ? -1 : 0));
        }, 0) : 0;
        const momentum = recentPerformance > 0 ? 'positive momentum' : 'consolidation phase';
        
        return `Market outlook based on recent performance indicators suggests ${momentum} with systematic strategy adaptation. Current execution patterns support ${reportType === 'investor' ? 'continued allocation confidence' : 'operational consistency'} with ${metrics.sharpeRatio > 0.8 ? 'strong' : 'developing'} risk-adjusted expectations.`;
    }

    generateStrategicInsights(metrics, trades, reportType) {
        const insights = [];
        
        if (metrics.winRate > 55 && metrics.profitFactor > 1.3) {
            insights.push('Strategy demonstrates institutional-grade metrics with sustainable competitive advantages');
        } else {
            insights.push('Strategy foundation shows promise with specific optimization opportunities identified');
        }
        
        if (metrics.fundedAccounts > 2) {
            insights.push('Multi-account portfolio structure provides robust capital base and risk diversification');
        }
        
        insights.push(`Current ${metrics.successRate.toFixed(1)}% prop firm success rate indicates ${metrics.successRate > 70 ? 'exceptional' : 'solid'} evaluation consistency`);
        
        return insights;
    }

    generateComprehensivePresentation(data, insights) {
        return {
            title: "Comprehensive Trading Performance Analysis",
            slides: [
                {
                    type: "title",
                    content: {
                        title: "Trading Performance Dashboard",
                        subtitle: insights.executiveSummary,
                        date: new Date().toLocaleDateString()
                    }
                },
                {
                    type: "insights",
                    content: {
                        title: "Key Performance Insights",
                        findings: insights.keyFindings,
                        analysis: insights.performanceAnalysis
                    }
                },
                {
                    type: "metrics",
                    content: {
                        title: "Advanced Analytics",
                        data: data.summary,
                        riskMetrics: insights.riskAssessment
                    }
                },
                {
                    type: "recommendations",
                    content: {
                        title: "Strategic Recommendations",
                        items: insights.recommendations,
                        outlook: insights.marketOutlook
                    }
                }
            ]
        };
    }

    generateInvestorPresentation(data, insights) {
        return {
            title: "Investor Performance Report",
            slides: [
                {
                    type: "executive",
                    content: {
                        title: "Executive Summary",
                        summary: insights.executiveSummary,
                        keyMetrics: data.summary
                    }
                },
                {
                    type: "performance",
                    content: {
                        title: "Risk-Adjusted Returns",
                        analysis: insights.performanceAnalysis,
                        charts: data.charts
                    }
                },
                {
                    type: "risk",
                    content: {
                        title: "Risk Management",
                        assessment: insights.riskAssessment,
                        controls: "Systematic position sizing and drawdown controls"
                    }
                },
                {
                    type: "outlook",
                    content: {
                        title: "Forward Outlook",
                        projection: insights.marketOutlook,
                        strategy: insights.strategicInsights
                    }
                }
            ]
        };
    }

    generateRiskPresentation(data, insights) {
        return {
            title: "Risk Assessment Report",
            slides: [
                {
                    type: "risk_overview",
                    content: {
                        title: "Risk Profile Overview",
                        assessment: insights.riskAssessment,
                        metrics: data.summary
                    }
                },
                {
                    type: "controls",
                    content: {
                        title: "Risk Controls & Mitigation",
                        findings: insights.keyFindings,
                        recommendations: insights.recommendations
                    }
                },
                {
                    type: "monitoring",
                    content: {
                        title: "Ongoing Risk Monitoring",
                        analysis: insights.performanceAnalysis,
                        outlook: insights.marketOutlook
                    }
                }
            ]
        };
    }

    generateMonthlyPresentation(data, insights) {
        return {
            title: "Monthly Performance Review",
            slides: [
                {
                    type: "monthly_summary",
                    content: {
                        title: "Monthly Performance Summary",
                        summary: insights.executiveSummary,
                        metrics: data.summary
                    }
                },
                {
                    type: "analysis",
                    content: {
                        title: "Performance Analysis",
                        findings: insights.keyFindings,
                        analysis: insights.performanceAnalysis
                    }
                },
                {
                    type: "next_month",
                    content: {
                        title: "Next Month Focus",
                        recommendations: insights.recommendations,
                        outlook: insights.marketOutlook
                    }
                }
            ]
        };
    }

    generateStrategyPresentation(data, insights) {
        return {
            title: "Strategy Performance Analysis",
            slides: [
                {
                    type: "strategy_overview",
                    content: {
                        title: "Strategy Performance Overview",
                        insights: insights.strategicInsights,
                        metrics: data.summary
                    }
                },
                {
                    type: "effectiveness",
                    content: {
                        title: "Strategy Effectiveness",
                        analysis: insights.performanceAnalysis,
                        findings: insights.keyFindings
                    }
                },
                {
                    type: "optimization",
                    content: {
                        title: "Strategy Optimization",
                        recommendations: insights.recommendations,
                        outlook: insights.marketOutlook
                    }
                }
            ]
        };
    }

    generateQuarterlyPresentation(data, insights) {
        return {
            title: "Quarterly Business Review",
            slides: [
                {
                    type: "quarterly_overview",
                    content: {
                        title: "Quarterly Performance Overview",
                        summary: insights.executiveSummary,
                        achievements: insights.keyFindings
                    }
                },
                {
                    type: "business_metrics",
                    content: {
                        title: "Business Performance Metrics",
                        analysis: insights.performanceAnalysis,
                        risk: insights.riskAssessment
                    }
                },
                {
                    type: "strategic_direction",
                    content: {
                        title: "Strategic Direction",
                        strategy: insights.strategicInsights,
                        recommendations: insights.recommendations
                    }
                },
                {
                    type: "next_quarter",
                    content: {
                        title: "Next Quarter Outlook",
                        outlook: insights.marketOutlook,
                        objectives: "Maintain systematic approach with enhanced optimization"
                    }
                }
            ]
        };
    }

    // Helper calculation methods
    calculateMaxDrawdown(profits) {
        if (!profits || profits.length === 0) return 0;
        
        // Use reduce for better performance with large datasets
        const { maxDrawdown } = profits.reduce((acc, profit) => {
            acc.cumulative += profit;
            acc.peak = Math.max(acc.peak, acc.cumulative);
            const drawdown = acc.peak > 0 ? (acc.peak - acc.cumulative) / acc.peak * 100 : 0;
            acc.maxDrawdown = Math.max(acc.maxDrawdown, drawdown);
            return acc;
        }, { maxDrawdown: 0, peak: 0, cumulative: 0 });
        
        return maxDrawdown;
    }
    
    calculateSharpeRatio(profits) {
        if (!profits.length) return 0;
        const mean = profits.reduce((sum, p) => sum + p, 0) / profits.length;
        const variance = profits.reduce((sum, p) => sum + Math.pow(p - mean, 2), 0) / profits.length;
        const stdDev = Math.sqrt(variance);
        return stdDev === 0 ? 0 : mean / stdDev;
    }
    
    calculateProfitFactor(winningTrades, losingTrades) {
        const totalWins = winningTrades.reduce((sum, trade) => {
            const rTarget = parseFloat(trade.rTarget) || 1;
            return sum + (Number.isFinite(rTarget) ? rTarget : 1);
        }, 0);
        const totalLosses = losingTrades.length;
        if (totalLosses === 0) {
            return totalWins > 0 ? Number.MAX_SAFE_INTEGER : 0;
        }
        const profitFactor = totalWins / totalLosses;
        return Number.isFinite(profitFactor) ? profitFactor : 0;
    }

    // Copy to clipboard for easy sharing
    copyToClipboard(reportType = 'comprehensive') {
        const data = JSON.stringify(this.generateGammaPresentation(reportType), null, 2);
        navigator.clipboard.writeText(data);
        return `${reportType.charAt(0).toUpperCase() + reportType.slice(1)} report copied to clipboard - paste into Gamma.app`;
    }

    // Generate webhook URL for real-time updates
    generateWebhook() {
        return `${this.baseUrl}/api/trading-data?format=gamma&timestamp=${Date.now()}`;
    }

    // Get AI insights for trading data
    async getAIInsights(prompt = 'Analyze my trading performance and provide actionable insights') {
        try {
            let trades = [];
            let propFirms = [];
            try {
                trades = JSON.parse(localStorage.getItem('tradingData') || '[]');
                propFirms = JSON.parse(localStorage.getItem('propFirmsV2_2024-01') || '[]');
            } catch (e) {
                console.error('Error parsing localStorage data:', e);
            }
            
            const data = this.exportForGamma();
            
            const response = await fetch('/api/ai-insights', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRF-Token': this.getCSRFToken()
                },
                body: JSON.stringify({
                    prompt: prompt,
                    data: {
                        summary: data.summary,
                        metrics: data.metrics,
                        recentTrades: trades.slice(-10),
                        propFirms: propFirms
                    }
                })
            });
            
            const result = await response.json();
            return result;
        } catch (error) {
            console.error('AI insights error:', error);
            return { error: error.message, status: 'error' };
        }
    }
}

// Initialize API
window.TradingAPI = new TradingDashboardAPI();

// Add export and AI buttons to dashboard
function addExportButton() {
    const exportBtn = document.createElement('button');
    exportBtn.textContent = '📊 Export for Gamma';
    exportBtn.className = 'btn';
    exportBtn.style.background = '#17a2b8';
    exportBtn.onclick = () => {
        const result = window.TradingAPI.copyToClipboard();
        console.log(result);
        showNotification(result);
    };
    
    const aiBtn = document.createElement('button');
    aiBtn.textContent = '🤖 AI Insights';
    aiBtn.className = 'btn';
    aiBtn.style.background = '#28a745';
    aiBtn.style.marginLeft = '10px';
    aiBtn.onclick = async () => {
        aiBtn.textContent = '⏳ Analyzing...';
        const result = await window.TradingAPI.getAIInsights();
        aiBtn.textContent = '🤖 AI Insights';
        
        if (result.status === 'success') {
            const modal = document.createElement('div');
            modal.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);z-index:9999;display:flex;align-items:center;justify-content:center';
            modal.innerHTML = `
                <div style="background:white;padding:20px;border-radius:10px;max-width:80%;max-height:80%;overflow-y:auto">
                    <h3>AI Trading Insights</h3>
                    <p style="white-space:pre-wrap">${result.insight}</p>
                    <button onclick="this.parentElement.parentElement.remove()" style="background:#dc3545;color:white;border:none;padding:10px 20px;border-radius:5px;cursor:pointer">Close</button>
                </div>
            `;
            document.body.appendChild(modal);
        } else {
            console.error('AI insights error:', result.error);
            showNotification('Error: ' + (result.error || 'Failed to get AI insights'), 'error');
        }
    };
    
    const navbar = document.querySelector('.navbar div');
    if (navbar) {
        navbar.appendChild(exportBtn);
        navbar.appendChild(aiBtn);
    }
}

// Auto-initialize when DOM loads
document.addEventListener('DOMContentLoaded', addExportButton);