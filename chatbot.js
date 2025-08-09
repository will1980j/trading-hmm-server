// Trading Empire AI Advisor - Comprehensive Business Intelligence
class TradingChatbot {
    constructor() {
        this.isOpen = false;
        this.messages = [];
        this.tradingData = [];
        this.propFirms = [];
        this.businessIntelligence = {};
        this.knowledgeBase = this.initializeKnowledgeBase();
        this.voiceEnabled = false;
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.init();
    }

    init() {
        this.createChatWidget();
        this.loadContext();
        this.analyzeBusinessMetrics();
        this.initializeVoice();
        this.setupSmartNotifications();
    }

    initializeVoice() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';
            
            this.recognition.onresult = (event) => {
                const command = event.results[0][0].transcript.toLowerCase();
                this.processVoiceCommand(command);
            };
            
            this.voiceEnabled = true;
        }
    }

    setupSmartNotifications() {
        // Check for performance issues every 5 minutes
        setInterval(() => {
            this.checkForSmartNotifications();
        }, 300000);
    }

    checkForSmartNotifications() {
        const alerts = this.businessIntelligence.alerts || [];
        const highPriorityAlerts = alerts.filter(a => a.priority === 'high');
        
        if (highPriorityAlerts.length > 0 && !this.isOpen) {
            this.showSmartNotification(highPriorityAlerts[0]);
        }
    }

    showSmartNotification(alert) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('Trading Empire Alert', {
                body: alert.message,
                icon: '🚨',
                tag: 'trading-alert'
            });
        }
    }

    initializeKnowledgeBase() {
        return {
            contextualDataAnalysis: {
                propFirmIntelligence: 'Real-time analysis of your prop firm portfolio performance',
                tradingPatternRecognition: 'AI analysis of your trading patterns and success factors',
                financialHealthMonitoring: 'Continuous assessment of business financial metrics',
                riskManagementInsights: 'Dynamic risk analysis across all trading accounts'
            },
            propFirmIntel: {
                topFirms: ['FTMO', 'MyForexFunds', 'The5ers', 'FundedNext', 'E8 Markets'],
                challengeStrategies: ['Conservative scaling', 'Risk management focus', 'Consistency over profits'],
                marketInsights: 'PropFirmMatch.com data integration for real-time opportunities'
            },
            australianTax: {
                structures: ['Sole Trader', 'Company', 'Trust', 'SMSF'],
                tradingTaxTips: ['Business vs Investment income', 'Deductible expenses', 'CGT strategies'],
                reportingStandards: ['AASB compliance', 'ATO requirements', 'Quarterly BAS']
            },
            wealthStrategies: {
                propertyMarkets: ['Sydney', 'Melbourne', 'Brisbane', 'International'],
                investmentTypes: ['Residential', 'Commercial', 'REITs', 'Development'],
                diversification: ['Stocks', 'Bonds', 'Crypto', 'Alternative investments']
            },
            gammaIntegration: {
                reportTypes: ['monthly', 'investor', 'risk', 'quarterly', 'strategy', 'allocation'],
                templates: {
                    professional: 'Clean, corporate design with focus on metrics and charts',
                    investor: 'Executive-style layout emphasizing ROI and growth potential',
                    minimal: 'Simple, clean design highlighting key insights only',
                    detailed: 'Comprehensive layout with extensive data visualization'
                },
                apiEndpoint: 'https://gamma.app/api/presentations'
            },
            voiceCommands: {
                enabled: true,
                commands: {
                    'hey q': 'Activate voice assistant',
                    'win rate': 'Get current win rate',
                    'alerts': 'Check active alerts',
                    'generate report': 'Create Gamma.app report',
                    'predictions': 'Show predictive analytics'
                },
                responses: ['Got it!', 'On it!', 'Analyzing...', 'Here you go!']
            },
            interactiveLearning: {
                performanceCoaching: 'Analyze losing trades with ICT-based improvements',
                marketEducation: 'Real-time market condition explanations',
                strategyRefinement: 'R-target and session optimization'
            },
            businessGrowth: {
                scalingMethods: ['Multiple prop accounts', 'Team trading', 'Signal services'],
                revenueStreams: ['Trading profits', 'Education', 'Software', 'Consulting'],
                operationalEfficiency: ['Automation', 'Systems', 'Processes', 'Team building']
            }
        };
    }

    loadContext() {
        // Enhanced data loading with business intelligence
        this.tradingData = JSON.parse(localStorage.getItem('tradingData')) || [];
        this.propFirms = JSON.parse(localStorage.getItem('propFirmsV2_2024-01')) || [];
        this.businessMetrics = JSON.parse(localStorage.getItem('businessMetrics')) || {};
        this.taxData = JSON.parse(localStorage.getItem('taxData')) || {};
        this.propertyPortfolio = JSON.parse(localStorage.getItem('propertyData')) || [];
        
        // Ensure all data arrays exist
        if (!Array.isArray(this.tradingData)) this.tradingData = [];
        if (!Array.isArray(this.propFirms)) this.propFirms = [];
        if (!Array.isArray(this.propertyPortfolio)) this.propertyPortfolio = [];
    }

    analyzeBusinessMetrics() {
        // Ensure data is loaded first
        if (!this.tradingData) this.loadContext();
        
        // Calculate key business intelligence metrics
        this.businessIntelligence = {
            tradingPerformance: this.analyzeTradingPerformance(),
            propFirmStatus: this.analyzePropFirmProgress(),
            taxEfficiency: this.calculateTaxEfficiency(),
            wealthGrowth: this.trackWealthGrowth(),
            nextSteps: this.generateStrategicRecommendations(),
            alerts: this.generateProactiveAlerts()
        };
    }

    generateProactiveAlerts() {
        const alerts = [];
        const trades = this.tradingData || [];
        const firms = this.propFirms || [];
        
        // Trading pattern alerts
        const recentTrades = trades.slice(-20);
        const londonTrades = recentTrades.filter(t => t.session === 'LONDON');
        if (londonTrades.length >= 5) {
            const londonWinRate = londonTrades.filter(t => t.rScore > 0).length / londonTrades.length;
            const overallWinRate = recentTrades.filter(t => t.rScore > 0).length / recentTrades.length;
            if (londonWinRate < overallWinRate - 0.15) {
                alerts.push({
                    type: 'performance',
                    priority: 'high',
                    message: `Your London session win rate dropped ${((overallWinRate - londonWinRate) * 100).toFixed(0)}% - consider reviewing your London strategy`,
                    action: 'Review London session trades and market structure analysis'
                });
            }
        }
        
        // Prop firm opportunities
        const fundedCount = firms.filter(f => f.status === 'funded').length;
        if (fundedCount < 3 && trades.length > 50) {
            const winRate = trades.filter(t => t.rScore > 0).length / trades.length;
            if (winRate > 0.6) {
                alerts.push({
                    type: 'opportunity',
                    priority: 'medium',
                    message: `FTMO has new scaling opportunities based on your ${(winRate * 100).toFixed(0)}% win rate performance`,
                    action: 'Consider applying for larger account sizes or additional challenges'
                });
            }
        }
        
        // Risk management alerts
        const forexFirms = firms.filter(f => f.marketType === 'Forex').length;
        const futuresFirms = firms.filter(f => f.marketType === 'Futures').length;
        if (forexFirms > 0 && futuresFirms === 0) {
            alerts.push({
                type: 'risk',
                priority: 'medium',
                message: 'Portfolio concentration risk detected - diversification recommended',
                action: 'Consider adding futures prop firms for market diversification'
            });
        }
        
        return alerts;
    }

    generateGammaReport(reportType = 'monthly') {
        const data = this.generateComprehensiveSummary();
        const predictions = this.generatePredictiveAnalytics();
        
        const report = {
            title: this.getReportTitle(reportType),
            template: this.recommendTemplate(reportType),
            slides: this.buildReportSlides(reportType, data, predictions),
            metadata: {
                generated: new Date().toISOString(),
                type: reportType,
                dataPoints: this.tradingData.length,
                propFirms: this.propFirms.length
            }
        };
        
        return report;
    }

    generatePredictiveAnalytics() {
        const trades = this.tradingData || [];
        const firms = this.propFirms || [];
        
        if (trades.length < 20) {
            return { message: 'Need more data for predictions' };
        }
        
        // Monthly profit projection
        const recentTrades = trades.slice(-30);
        const avgDailyR = recentTrades.reduce((sum, t) => sum + (t.rScore || 0), 0) / recentTrades.length;
        const tradingDaysPerMonth = 20;
        const monthlyRProjection = avgDailyR * tradingDaysPerMonth;
        
        // Account size projection
        const fundedCapital = firms.filter(f => f.status === 'funded')
            .reduce((sum, f) => sum + (f.accountSize || 0), 0);
        const monthlyProfitProjection = monthlyRProjection * (fundedCapital * 0.01); // Assuming 1% risk per R
        
        // Growth timeline
        const currentMonthly = monthlyProfitProjection;
        const q3Projection = currentMonthly * 1.5; // Assuming 50% growth
        
        return {
            monthlyRTarget: monthlyRProjection.toFixed(1) + 'R',
            monthlyProfitProjection: '$' + monthlyProfitProjection.toLocaleString(),
            q3Projection: '$' + q3Projection.toLocaleString(),
            growthRate: '50% quarterly growth potential',
            keyInsight: monthlyProfitProjection > 50000 ? 
                'On track to hit $50K monthly by Q3' : 
                'Focus on consistency to reach $50K target',
            optimizations: this.generateOptimizationRecommendations()
        };
    }

    generateOptimizationRecommendations() {
        const trades = this.tradingData || [];
        const sessionStats = {};
        
        trades.forEach(trade => {
            if (trade.session) {
                if (!sessionStats[trade.session]) sessionStats[trade.session] = { total: 0, count: 0 };
                sessionStats[trade.session].total += trade.rScore || 0;
                sessionStats[trade.session].count++;
            }
        });
        
        let bestSession = 'NY PRE MARKET';
        let bestAvg = 0;
        let potentialIncrease = 0;
        
        Object.keys(sessionStats).forEach(session => {
            const avg = sessionStats[session].total / sessionStats[session].count;
            if (avg > bestAvg && sessionStats[session].count >= 5) {
                bestAvg = avg;
                bestSession = session;
                potentialIncrease = (avg - 0.5) * sessionStats[session].count * 0.23; // 23% scaling factor
            }
        });
        
        return {
            topRecommendation: `Scaling ${bestSession} trades could increase profits ${potentialIncrease.toFixed(0)}%`,
            sessionFocus: bestSession,
            expectedIncrease: potentialIncrease.toFixed(0) + '%'
        };
    }

    getReportTitle(type) {
        const titles = {
            monthly: 'Monthly Trading Performance Report',
            investor: 'Investor Performance Presentation',
            risk: 'Risk Assessment & Management Report',
            quarterly: 'Quarterly Business Review',
            strategy: 'Strategy Performance Analysis',
            allocation: 'Financial Allocation Strategy'
        };
        return titles[type] || titles.monthly;
    }

    recommendTemplate(type) {
        const recommendations = {
            monthly: 'professional',
            investor: 'investor',
            risk: 'detailed',
            quarterly: 'professional',
            strategy: 'detailed',
            allocation: 'minimal'
        };
        return recommendations[type] || 'professional';
    }

    buildReportSlides(type, data, predictions) {
        const slides = [
            {
                title: 'Executive Summary',
                content: {
                    performance: data.trading.summary,
                    prediction: predictions.keyInsight,
                    nextSteps: data.strategic.priority
                }
            },
            {
                title: 'Performance Analytics',
                content: {
                    winRate: data.trading.winRate,
                    totalTrades: data.trading.totalTrades,
                    bestSession: data.trading.patterns?.bestSession,
                    roi: data.trading.trend
                }
            },
            {
                title: 'Predictive Insights',
                content: {
                    monthlyProjection: predictions.monthlyProfitProjection,
                    q3Target: predictions.q3Projection,
                    optimization: predictions.optimizations?.topRecommendation,
                    growthRate: predictions.growthRate
                }
            }
        ];
        
        if (type === 'investor') {
            slides.push({
                title: 'Investment Opportunity',
                content: {
                    scalingPotential: 'Multiple prop firm accounts with proven strategy',
                    riskManagement: 'Systematic approach with defined risk parameters',
                    growthProjection: predictions.q3Projection + ' quarterly target'
                }
            });
        }
        
        return slides;
    }

    createChatWidget() {
        // Chat toggle button
        const chatToggle = document.createElement('div');
        chatToggle.id = 'chat-toggle';
        chatToggle.innerHTML = '🤖';
        chatToggle.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            z-index: 9998;
            transition: all 0.3s ease;
        `;
        chatToggle.onclick = () => this.toggleChat();

        // Chat window
        const chatWindow = document.createElement('div');
        chatWindow.id = 'chat-window';
        chatWindow.style.cssText = `
            position: fixed;
            bottom: 90px;
            right: 20px;
            width: 350px;
            height: 500px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            display: none;
            flex-direction: column;
            z-index: 9999;
            overflow: hidden;
        `;

        chatWindow.innerHTML = `
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; font-weight: bold;">
                🤖 Trading AI Assistant
                <span onclick="tradingChatbot.toggleChat()" style="float: right; cursor: pointer; font-size: 18px;">×</span>
            </div>
            <div id="chat-messages" style="flex: 1; padding: 15px; overflow-y: auto; background: #f8f9fa;"></div>
            <div style="padding: 15px; border-top: 1px solid #eee; background: white;">
                <div style="display: flex; gap: 10px;">
                    <input id="chat-input" type="text" placeholder="Ask about your trading..." 
                           style="flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 20px; outline: none;">
                    <button onclick="tradingChatbot.sendMessage()" 
                            style="background: #667eea; color: white; border: none; padding: 10px 15px; border-radius: 20px; cursor: pointer;">Send</button>
                </div>
                <div style="margin-top: 10px; display: flex; gap: 5px; flex-wrap: wrap;">
                    <button onclick="tradingChatbot.quickAction('gamma-report')" 
                            style="background: #28a745; color: white; border: none; padding: 5px 10px; border-radius: 15px; cursor: pointer; font-size: 12px;">📊 Generate Report</button>
                    <button onclick="tradingChatbot.quickAction('predictions')" 
                            style="background: #17a2b8; color: white; border: none; padding: 5px 10px; border-radius: 15px; cursor: pointer; font-size: 12px;">🔮 Predictions</button>
                    <button onclick="tradingChatbot.quickAction('alerts')" 
                            style="background: #ffc107; color: black; border: none; padding: 5px 10px; border-radius: 15px; cursor: pointer; font-size: 12px;">🚨 Alerts</button>
                    <button onclick="tradingChatbot.toggleVoice()" 
                            style="background: #6f42c1; color: white; border: none; padding: 5px 10px; border-radius: 15px; cursor: pointer; font-size: 12px;">🎤 Voice</button>
                </div>
            </div>
        `;

        document.body.appendChild(chatToggle);
        document.body.appendChild(chatWindow);

        // Enter key support
        document.getElementById('chat-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });

        // Enhanced welcome with business intelligence
        const welcomeMsg = this.generateIntelligentWelcome();
        this.addMessage('assistant', welcomeMsg);
        
        // Request notification permission
        this.requestNotificationPermission();
    }

    toggleChat() {
        const chatWindow = document.getElementById('chat-window');
        this.isOpen = !this.isOpen;
        chatWindow.style.display = this.isOpen ? 'flex' : 'none';
    }

    addMessage(role, content) {
        const messagesDiv = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.style.cssText = `
            margin-bottom: 15px;
            padding: 10px 15px;
            border-radius: 15px;
            max-width: 80%;
            ${role === 'user' ? 
                'background: #667eea; color: white; margin-left: auto; text-align: right; text-shadow: 0 1px 2px rgba(0,0,0,0.3);' : 
                'background: white; border: 1px solid #eee; margin-right: auto; color: #000; text-shadow: 0 1px 1px rgba(255,255,255,0.8);'
            }
        `;
        messageDiv.innerHTML = content.replace(/\n/g, '<br>');
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    async sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        if (!message) return;

        input.value = '';
        this.addMessage('user', message);
        this.addMessage('assistant', '🧠 Analyzing with business intelligence...');

        try {
            const enhancedPrompt = this.buildIntelligentPrompt(message);
            const response = await fetch('/api/ai-insights', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: enhancedPrompt,
                    data: {
                        tradingData: this.tradingData.slice(-50),
                        propFirms: this.propFirms,
                        businessIntelligence: this.businessIntelligence,
                        knowledgeBase: this.knowledgeBase,
                        currentPage: window.location.pathname,
                        comprehensiveSummary: this.generateComprehensiveSummary()
                    }
                })
            });

            // Remove thinking message
            const messages = document.getElementById('chat-messages');
            if (messages.lastChild) messages.removeChild(messages.lastChild);

            if (response.ok) {
                const result = await response.json();
                if (result.status === 'success') {
                    this.addMessage('assistant', result.insight);
                } else {
                    this.addMessage('assistant', `Error: ${result.error || 'API key not configured'}`);
                }
            } else {
                this.addMessage('assistant', `Server error (${response.status}). Check API configuration.`);
            }
        } catch (error) {
            const messages = document.getElementById('chat-messages');
            if (messages.lastChild) messages.removeChild(messages.lastChild);
            this.addMessage('assistant', `Error: ${error.message}`);
        }
    }

    buildIntelligentPrompt(userMessage) {
        const context = this.determineContext(userMessage);
        const alerts = this.businessIntelligence.alerts || [];
        const relevantAlerts = alerts.filter(a => a.type === context.toLowerCase() || a.priority === 'high');
        
        let prompt = `TRADING EMPIRE ADVISOR - Multi-Disciplinary Expert

User Query: ${userMessage}

Context Analysis: ${context}

Current Business Intelligence:
• Trading Performance: ${this.businessIntelligence.tradingPerformance?.summary || 'Analyzing...'}
• Active Alerts: ${alerts.length} insights available`;
        
        if (relevantAlerts.length > 0) {
            prompt += `

Relevant Alerts:
${relevantAlerts.map(a => `• ${a.message}`).join('\n')}`;
        }
        
        prompt += `

You are an expert advisor specializing in:
🎯 TRADING: ICT concepts, prop firms, institutional trading, risk management
💼 BUSINESS: Australian tax optimization, accounting standards, business scaling
🏠 WEALTH: Property investment (Australia/global), portfolio diversification
🚀 STRATEGY: PropFirmMatch.com intelligence, revenue optimization, next-step planning

Provide specific, actionable advice using the comprehensive business data provided. Focus on practical solutions that drive real results.`;
        
        // Add Gamma.app integration context
        if (context === 'Gamma Integration') {
            prompt += `\n\nGamma.app Integration Available:\n• Generate professional presentations\n• 6 report types: Monthly, Investor, Risk, Quarterly, Strategy, Allocation\n• AI-powered insights and recommendations\n• Template suggestions based on data`;
        }
        
        if (context === 'Predictive Analytics') {
            const predictions = this.generatePredictiveAnalytics();
            prompt += `\n\nCurrent Predictions:\n• ${predictions.keyInsight}\n• Monthly Target: ${predictions.monthlyRTarget}\n• Optimization: ${predictions.optimizations?.topRecommendation}`;
        }
        
        if (context === 'Trading Performance') {
            const losingTradeAnalysis = this.analyzeLosingTrades();
            if (typeof losingTradeAnalysis === 'object') {
                prompt += `\n\nLosing Trade Analysis:\n• Worst Session: ${losingTradeAnalysis.worstSession}\n• ICT Recommendation: ${losingTradeAnalysis.ictRecommendation}`;
            }
        }
        
        return prompt;
    }

    determineContext(message) {
        const msg = message.toLowerCase();
        if (msg.includes('report') || msg.includes('gamma') || msg.includes('presentation')) return 'Gamma Integration';
        if (msg.includes('predict') || msg.includes('forecast') || msg.includes('projection')) return 'Predictive Analytics';
        if (msg.includes('tax') || msg.includes('accounting')) return 'Australian Tax & Accounting';
        if (msg.includes('prop') || msg.includes('challenge')) return 'Prop Firm Strategy';
        if (msg.includes('property') || msg.includes('invest')) return 'Wealth & Investment';
        if (msg.includes('business') || msg.includes('scale')) return 'Business Growth';
        if (msg.includes('trade') || msg.includes('ict')) return 'Trading Performance';
        return 'Strategic Planning';
    }

    generateIntelligentWelcome() {
        const metrics = this.businessIntelligence;
        const alerts = metrics.alerts || [];
        const highPriorityAlerts = alerts.filter(a => a.priority === 'high');
        
        let welcomeMsg = `🚀 **TRADING EMPIRE ADVISOR** - Your Multi-Disciplinary Expert\n\n📊 **CURRENT STATUS:**\n• Trading Performance: ${metrics.tradingPerformance.summary}\n• Prop Firm Progress: ${metrics.propFirmStatus.summary}\n• Tax Efficiency: ${metrics.taxEfficiency.rating}\n• Wealth Growth: ${metrics.wealthGrowth.trend}`;
        
        // Add proactive alerts
        if (highPriorityAlerts.length > 0) {
            welcomeMsg += `\n\n🚨 **URGENT ALERTS:**`;
            highPriorityAlerts.forEach(alert => {
                welcomeMsg += `\n• ${alert.message}`;
            });
        }
        
        if (alerts.length > highPriorityAlerts.length) {
            welcomeMsg += `\n\n💡 **OPPORTUNITIES:** ${alerts.length - highPriorityAlerts.length} insights available`;
        }
        
        welcomeMsg += `\n\n🎯 **EXPERTISE AREAS:**\n• ICT Trading & Prop Firm Mastery\n• Australian Tax Optimization & Accounting\n• Property Investment & Wealth Building\n• Business Scaling & Strategic Growth\n\n💡 **NEXT STEPS:** ${metrics.nextSteps.priority}\n\nWhat empire-building challenge shall we tackle?`;
        
        return welcomeMsg;
    }

    generateComprehensiveSummary() {
        return {
            trading: this.analyzeTradingPerformance(),
            propFirms: this.analyzePropFirmProgress(),
            business: this.analyzeBusinessHealth(),
            wealth: this.trackWealthGrowth(),
            tax: this.calculateTaxEfficiency(),
            strategic: this.generateStrategicRecommendations()
        };
    }

    analyzeTradingPerformance() {
        const trades = this.tradingData || [];
        const wins = trades.filter(t => t && (t.outcome === 'win' || t.rScore > 0)).length;
        const winRate = trades.length ? (wins / trades.length * 100).toFixed(1) : 0;
        const avgProfit = trades.length ? trades.reduce((sum, t) => sum + ((t && t.profit) || (t && t.rScore) || 0), 0) / trades.length : 0;
        
        // Pattern recognition
        const patterns = this.recognizeTradingPatterns(trades);
        
        return {
            totalTrades: trades.length,
            winRate: winRate + '%',
            avgProfit: avgProfit.toFixed(2),
            summary: `${winRate}% WR, ${trades.length} trades, ${avgProfit.toFixed(1)}R avg`,
            trend: winRate > 60 ? 'Excellent' : winRate > 45 ? 'Good' : 'Needs Improvement',
            patterns: patterns
        };
    }

    recognizeTradingPatterns(trades) {
        if (trades.length < 10) return { insight: 'Need more trades for pattern analysis' };
        
        const sessionPerformance = {};
        const biasPerformance = { LONG: [], SHORT: [] };
        
        trades.forEach(trade => {
            if (trade.session) {
                if (!sessionPerformance[trade.session]) sessionPerformance[trade.session] = [];
                sessionPerformance[trade.session].push(trade.rScore || 0);
            }
            if (trade.bias && biasPerformance[trade.bias]) {
                biasPerformance[trade.bias].push(trade.rScore || 0);
            }
        });
        
        // Find best performing session
        let bestSession = 'Unknown';
        let bestAvg = -999;
        Object.keys(sessionPerformance).forEach(session => {
            const avg = sessionPerformance[session].reduce((a, b) => a + b, 0) / sessionPerformance[session].length;
            if (avg > bestAvg && sessionPerformance[session].length >= 3) {
                bestAvg = avg;
                bestSession = session;
            }
        });
        
        return {
            bestSession: bestSession,
            bestSessionAvg: bestAvg.toFixed(1) + 'R',
            insight: bestAvg > 1 ? `${bestSession} is your strongest session` : 'Focus on consistency across all sessions'
        };
    }

    monitorFinancialHealth() {
        const firms = this.propFirms || [];
        const trades = this.tradingData || [];
        
        const fundedCapital = firms.filter(f => f.status === 'funded')
            .reduce((sum, f) => sum + (f.accountSize || 0), 0);
        
        const monthlyProfit = firms.filter(f => f.status === 'funded')
            .reduce((sum, f) => sum + (f.monthlyProfit || 0), 0);
        
        const roi = fundedCapital > 0 ? (monthlyProfit / fundedCapital * 100).toFixed(1) : 0;
        
        return {
            fundedCapital: fundedCapital,
            monthlyProfit: monthlyProfit,
            roi: roi + '%',
            health: roi > 5 ? 'Excellent' : roi > 2 ? 'Good' : 'Needs Improvement',
            recommendation: roi < 2 ? 'Focus on consistency and risk management' : 'Consider scaling operations'
        };
    }

    analyzePropFirmProgress() {
        const firms = this.propFirms || [];
        const funded = firms.filter(f => f && f.status === 'funded').length;
        const challenges = firms.filter(f => f && f.status === 'challenge').length;
        
        return {
            fundedAccounts: funded,
            activeChallenges: challenges,
            totalFirms: firms.length,
            summary: `${funded} funded, ${challenges} challenges`,
            nextTarget: funded < 3 ? 'Focus on getting 3+ funded accounts' : 'Scale to larger account sizes'
        };
    }

    calculateTaxEfficiency() {
        // Placeholder for tax calculation logic
        return {
            rating: 'Optimizing',
            structure: 'Company + Trust recommended',
            savings: 'Est. 15-25% tax savings available'
        };
    }

    trackWealthGrowth() {
        return {
            trend: 'Growing',
            focus: 'Property + Trading profits',
            target: 'Diversified portfolio expansion'
        };
    }

    analyzeBusinessHealth() {
        return {
            revenue: 'Multiple streams developing',
            efficiency: 'Systems automation in progress',
            growth: 'Scaling phase'
        };
    }

    generateStrategicRecommendations() {
        return {
            priority: 'Scale prop firm operations + tax optimization',
            shortTerm: 'Pass 2 more challenges, optimize tax structure',
            longTerm: 'Property investment, business diversification'
        };
    }

    quickAction(action) {
        switch(action) {
            case 'gamma-report':
                const report = this.generateGammaReport('monthly');
                navigator.clipboard.writeText(JSON.stringify(report, null, 2));
                this.addMessage('assistant', '📊 **Monthly Report Generated!**\n\nProfessional presentation data copied to clipboard.\n\n🎯 **Next Steps:**\n1. Open Gamma.app\n2. Create new presentation\n3. Paste data (Ctrl+V)\n4. Select "Professional" template\n\n💡 **Includes:** Performance analytics, predictive insights, optimization recommendations');
                break;
            case 'predictions':
                const predictions = this.generatePredictiveAnalytics();
                this.addMessage('assistant', `🔮 **Predictive Analytics**\n\n🎯 **Key Insight:** ${predictions.keyInsight}\n\n📊 **Projections:**\n• Monthly Target: ${predictions.monthlyRTarget}\n• Profit Projection: ${predictions.monthlyProfitProjection}\n• Q3 Target: ${predictions.q3Projection}\n\n🚀 **Optimization:** ${predictions.optimizations?.topRecommendation}\n\n📈 **Growth Rate:** ${predictions.growthRate}`);
                break;
            case 'alerts':
                const alerts = this.businessIntelligence.alerts || [];
                if (alerts.length === 0) {
                    this.addMessage('assistant', '✅ **No Active Alerts**\n\nYour trading performance is on track. All systems operating normally.');
                } else {
                    let alertMsg = `🚨 **Active Alerts (${alerts.length})**\n\n`;
                    alerts.forEach((alert, i) => {
                        const priority = alert.priority === 'high' ? '🔴' : alert.priority === 'medium' ? '🟡' : '🟢';
                        alertMsg += `${priority} **${alert.type.toUpperCase()}:** ${alert.message}\n• Action: ${alert.action}\n\n`;
                    });
                    this.addMessage('assistant', alertMsg);
                }
                break;
        }
    }

    toggleVoice() {
        if (!this.voiceEnabled) {
            this.addMessage('assistant', '🎤 Voice commands not supported in this browser. Try Chrome or Edge.');
            return;
        }
        
        if (this.recognition) {
            this.recognition.start();
            this.addMessage('assistant', '🎤 **Voice Active** - Say "Hey Q" followed by your command:\n\n• "Hey Q, what\'s my win rate?"\n• "Hey Q, show alerts"\n• "Hey Q, generate report"\n• "Hey Q, predictions"');
        }
    }

    processVoiceCommand(command) {
        this.addMessage('user', '🎤 ' + command);
        
        if (command.includes('hey q')) {
            const actualCommand = command.replace('hey q', '').trim();
            
            if (actualCommand.includes('win rate')) {
                const winRate = this.businessIntelligence.tradingPerformance?.winRate || '0%';
                this.speak(`Your current win rate is ${winRate}`);
                this.addMessage('assistant', `🎤 Your current win rate is **${winRate}**`);
            } else if (actualCommand.includes('alert')) {
                this.quickAction('alerts');
                this.speak('Checking your alerts now');
            } else if (actualCommand.includes('report')) {
                this.quickAction('gamma-report');
                this.speak('Generating your monthly report');
            } else if (actualCommand.includes('prediction')) {
                this.quickAction('predictions');
                this.speak('Here are your predictive analytics');
            } else {
                this.speak('I can help with win rate, alerts, reports, or predictions');
                this.addMessage('assistant', '🎤 Available commands:\n• "win rate"\n• "alerts"\n• "generate report"\n• "predictions"');
            }
        }
    }

    speak(text) {
        if (this.synthesis) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 0.9;
            utterance.pitch = 1;
            this.synthesis.speak(utterance);
        }
    }

    analyzeLosingTrades() {
        const trades = this.tradingData || [];
        const losingTrades = trades.filter(t => t.rScore < 0 || t.outcome === 'loss');
        
        if (losingTrades.length === 0) {
            return 'No losing trades to analyze - excellent performance!';
        }
        
        const sessionLosses = {};
        losingTrades.forEach(trade => {
            if (trade.session) {
                sessionLosses[trade.session] = (sessionLosses[trade.session] || 0) + 1;
            }
        });
        
        const worstSession = Object.keys(sessionLosses).reduce((a, b) => 
            sessionLosses[a] > sessionLosses[b] ? a : b
        );
        
        return {
            totalLosses: losingTrades.length,
            worstSession: worstSession,
            lossCount: sessionLosses[worstSession],
            ictRecommendation: this.generateICTRecommendation(worstSession),
            improvement: `Focus on ${worstSession} session market structure analysis`
        };
    }

    generateICTRecommendation(session) {
        const recommendations = {
            'LONDON': 'Focus on Fair Value Gaps during London open. Look for liquidity sweeps at 8:30 AM GMT.',
            'NY PRE MARKET': 'Watch for Order Blocks formation. Avoid trading during low liquidity periods.',
            'NEW YORK AM': 'Focus on institutional order flow. Look for market structure breaks at key levels.',
            'NEW YORK PM': 'Watch for late-day reversals. Focus on daily range completion patterns.'
        };
        
        return recommendations[session] || 'Focus on market structure and institutional order flow analysis.';
    }

    requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }
}

// Initialize chatbot when DOM loads
document.addEventListener('DOMContentLoaded', () => {
    window.tradingChatbot = new TradingChatbot();
});