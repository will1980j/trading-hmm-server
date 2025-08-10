// Trading Empire AI Advisor - Comprehensive Business Intelligence
class TradingChatbot {
    constructor() {
        try {
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
        } catch (error) {
            console.error('Error initializing chatbot:', error);
        }
    }

    init() {
        try {
            this.createChatWidget();
            this.loadContext();
            this.analyzeBusinessMetrics();
            this.initializeVoice();
            this.setupSmartNotifications();
        } catch (error) {
            console.error('Error initializing chatbot:', error);
        }
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
        const NOTIFICATION_INTERVAL = 300000; // 5 minutes
        setInterval(() => {
            this.checkForSmartNotifications();
        }, NOTIFICATION_INTERVAL);
    }

    checkForSmartNotifications() {
        const alerts = this.businessIntelligence.alerts || [];
        const highPriorityAlerts = alerts.filter(alert => alert.priority === 'high');
        
        if (highPriorityAlerts.length > 0 && !this.isOpen) {
            this.showSmartNotification(highPriorityAlerts[0]);
        }
    }

    showSmartNotification(alert) {
        try {
            if ('Notification' in window && Notification.permission === 'granted') {
                new Notification('Trading Empire Alert', {
                    body: alert.message,
                    icon: '🚨',
                    tag: 'trading-alert'
                });
            }
        } catch (error) {
            console.error('Error showing notification:', error);
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
        const dataKeys = ['tradingData', 'propFirmsV2_2024-01', 'businessMetrics', 'taxData', 'propertyData'];
        const defaults = [[], [], {}, {}, []];
        
        dataKeys.forEach((key, index) => {
            try {
                const data = JSON.parse(localStorage.getItem(key) || JSON.stringify(defaults[index]));
                switch(index) {
                    case 0: this.tradingData = Array.isArray(data) ? data : []; break;
                    case 1: this.propFirms = Array.isArray(data) ? data : []; break;
                    case 2: this.businessMetrics = data || {}; break;
                    case 3: this.taxData = data || {}; break;
                    case 4: this.propertyPortfolio = Array.isArray(data) ? data : []; break;
                }
            } catch (error) {
                console.error(`Error loading ${key}:`, error);
                if (index < 2 || index === 4) {
                    this[index === 0 ? 'tradingData' : index === 1 ? 'propFirms' : 'propertyPortfolio'] = [];
                } else {
                    this[index === 2 ? 'businessMetrics' : 'taxData'] = {};
                }
            }
        });
    }

    analyzeBusinessMetrics() {
        if (!this.tradingData) this.loadContext();
        
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
        
        if (!trades || !firms) {
            return alerts;
        }
        
        const recentTrades = trades.slice(-20);
        const londonTrades = recentTrades.filter(trade => trade.session === 'LONDON');
        if (londonTrades.length >= 5) {
            const londonWinRate = londonTrades.filter(trade => trade.rScore > 0).length / londonTrades.length;
            const overallWinRate = recentTrades.filter(trade => trade.rScore > 0).length / recentTrades.length;
            if (londonWinRate < overallWinRate - 0.15) {
                alerts.push({
                    type: 'performance',
                    priority: 'high',
                    message: `Your London session win rate dropped ${((overallWinRate - londonWinRate) * 100).toFixed(0)}% - consider reviewing your London strategy`,
                    action: 'Review London session trades and market structure analysis'
                });
            }
        }
        
        const fundedCount = firms.filter(firm => firm.status === 'funded').length;
        if (fundedCount < 3 && trades.length > 50) {
            const winRate = trades.filter(trade => trade.rScore > 0).length / trades.length;
            if (winRate > 0.6) {
                alerts.push({
                    type: 'opportunity',
                    priority: 'medium',
                    message: `FTMO has new scaling opportunities based on your ${(winRate * 100).toFixed(0)}% win rate performance`,
                    action: 'Consider applying for larger account sizes or additional challenges'
                });
            }
        }
        
        const forexFirms = firms.filter(firm => firm.marketType === 'Forex').length;
        const futuresFirms = firms.filter(firm => firm.marketType === 'Futures').length;
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

    generatePredictiveAnalytics() {
        const trades = this.tradingData || [];
        const firms = this.propFirms || [];
        
        if (trades.length < 20) {
            return { message: 'Need more data for predictions' };
        }
        
        const recentTrades = trades.slice(-Math.min(30, trades.length));
        const avgDailyR = recentTrades.length > 0 ? recentTrades.reduce((sum, trade) => sum + (trade.rScore || 0), 0) / recentTrades.length : 0;
        const TRADING_DAYS_PER_MONTH = 20;
        const monthlyRProjection = avgDailyR * TRADING_DAYS_PER_MONTH;
        
        const fundedCapital = firms.filter(firm => firm.status === 'funded')
            .reduce((sum, firm) => sum + (firm.accountSize || 0), 0);
        const RISK_PER_R = 0.01;
        const monthlyProfitProjection = monthlyRProjection * (fundedCapital * RISK_PER_R);
        
        const GROWTH_RATE = 1.5;
        const q3Projection = monthlyProfitProjection * GROWTH_RATE;
        
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
            try {
                if (trade && trade.session) {
                    if (!sessionStats[trade.session]) sessionStats[trade.session] = { total: 0, count: 0 };
                    sessionStats[trade.session].total += trade.rScore || 0;
                    sessionStats[trade.session].count++;
                }
            } catch (e) {
                console.error('Error processing trade session data:', e);
            }
        });
        
        let bestSession = 'NY PRE MARKET';
        let bestAvg = 0;
        let potentialIncrease = 0;
        
        Object.entries(sessionStats).forEach(([session, stats]) => {
            if (stats.count >= 5) {
                const avg = stats.total / stats.count;
                if (avg > bestAvg) {
                    bestAvg = avg;
                    bestSession = session;
                    const SCALING_FACTOR = 0.23;
                    potentialIncrease = (avg - 0.5) * stats.count * SCALING_FACTOR;
                }
            }
        });
        
        return {
            topRecommendation: `Scaling ${bestSession} trades could increase profits ${potentialIncrease.toFixed(0)}%`,
            sessionFocus: bestSession,
            expectedIncrease: potentialIncrease.toFixed(0) + '%'
        };
    }

    createChatWidget() {
        const existingToggle = document.getElementById('chat-toggle');
        const existingWindow = document.getElementById('chat-window');
        if (existingToggle) existingToggle.remove();
        if (existingWindow) existingWindow.remove();
        
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
            pointer-events: auto;
        `;
        chatToggle.addEventListener('click', () => this.toggleChat());

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
                <span id="chat-close-btn" style="float: right; cursor: pointer; font-size: 18px;">×</span>
            </div>
            <div id="chat-messages" style="flex: 1; padding: 15px; overflow-y: auto; background: #f8f9fa;"></div>
            <div style="padding: 15px; border-top: 1px solid #eee; background: white;">
                <div style="display: flex; gap: 10px;">
                    <input id="chat-input" type="text" placeholder="Ask about your trading..." 
                           style="flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 20px; outline: none;">
                    <button id="chat-send-btn" 
                            style="background: #667eea; color: white; border: none; padding: 10px 15px; border-radius: 20px; cursor: pointer;">Send</button>
                </div>
                <div style="margin-top: 10px; display: flex; gap: 5px; flex-wrap: wrap;">
                    <button id="gamma-btn" 
                            style="background: #28a745; color: white; border: none; padding: 5px 10px; border-radius: 15px; cursor: pointer; font-size: 12px;">📊 Generate Report</button>
                    <button id="predictions-btn" 
                            style="background: #17a2b8; color: white; border: none; padding: 5px 10px; border-radius: 15px; cursor: pointer; font-size: 12px;">🔮 Predictions</button>
                    <button id="alerts-btn" 
                            style="background: #ffc107; color: black; border: none; padding: 5px 10px; border-radius: 15px; cursor: pointer; font-size: 12px;">🚨 Alerts</button>
                    <button id="voice-btn" 
                            style="background: #6f42c1; color: white; border: none; padding: 5px 10px; border-radius: 15px; cursor: pointer; font-size: 12px;">🎤 Voice</button>
                </div>
            </div>
        `;

        document.body.appendChild(chatToggle);
        document.body.appendChild(chatWindow);
        
        setTimeout(() => {
            this.setupEventListeners();
            const welcomeMsg = this.generateIntelligentWelcome();
            this.addMessage('assistant', welcomeMsg);
        }, 100);
        
        this.requestNotificationPermission();
    }
    
    setupEventListeners() {
        const sendBtn = document.getElementById('chat-send-btn');
        if (sendBtn) sendBtn.addEventListener('click', () => this.sendMessage());
        
        const closeBtn = document.getElementById('chat-close-btn');
        if (closeBtn) closeBtn.addEventListener('click', () => this.toggleChat());
        
        const chatInput = document.getElementById('chat-input');
        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.sendMessage();
            });
        }
        
        const gammaBtn = document.getElementById('gamma-btn');
        if (gammaBtn) gammaBtn.addEventListener('click', () => this.quickAction('gamma-report'));
        
        const predictionsBtn = document.getElementById('predictions-btn');
        if (predictionsBtn) predictionsBtn.addEventListener('click', () => this.quickAction('predictions'));
        
        const alertsBtn = document.getElementById('alerts-btn');
        if (alertsBtn) alertsBtn.addEventListener('click', () => this.quickAction('alerts'));
        
        const voiceBtn = document.getElementById('voice-btn');
        if (voiceBtn) voiceBtn.addEventListener('click', () => this.toggleVoice());
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
            line-height: 1.4;
            ${role === 'user' ? 
                'background: #667eea; color: white; margin-left: auto; text-align: right;' : 
                'background: #ffffff; border: 1px solid #dee2e6; margin-right: auto; color: #333333; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'
            }
        `;
        const sanitizedContent = content.replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>');
        messageDiv.innerHTML = sanitizedContent;
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
                headers: { 
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRF-Token': this.getCSRFToken()
                },
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
        const relevantAlerts = alerts.filter(alert => alert.type === context.toLowerCase() || alert.priority === 'high');
        
        let prompt = `TRADING EMPIRE ADVISOR - Multi-Disciplinary Expert\n\nUser Query: ${userMessage}\n\nContext Analysis: ${context}\n\nCurrent Business Intelligence:\n• Trading Performance: ${this.businessIntelligence.tradingPerformance?.summary || 'Analyzing...'}\n• Active Alerts: ${alerts.length} insights available`;
        
        if (relevantAlerts.length > 0) {
            prompt += `\n\nRelevant Alerts:\n${relevantAlerts.map(alert => `• ${alert.message}`).join('\n')}`;
        }
        
        prompt += `\n\nYou are an expert advisor specializing in:\n🎯 TRADING: ICT concepts, prop firms, institutional trading, risk management\n💼 BUSINESS: Australian tax optimization, accounting standards, business scaling\n🏠 WEALTH: Property investment (Australia/global), portfolio diversification\n🚀 STRATEGY: PropFirmMatch.com intelligence, revenue optimization, next-step planning\n\nProvide specific, actionable advice using the comprehensive business data provided. Focus on practical solutions that drive real results.`;
        
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
        const highPriorityAlerts = alerts.filter(alert => alert.priority === 'high');
        
        let welcomeMsg = `🚀 **TRADING EMPIRE ADVISOR** - Your Multi-Disciplinary Expert\n\n📊 **CURRENT STATUS:**\n• Trading Performance: ${metrics.tradingPerformance?.summary || 'Analyzing...'}\n• Prop Firm Progress: ${metrics.propFirmStatus?.summary || 'Loading...'}\n• Tax Efficiency: ${metrics.taxEfficiency?.rating || 'Optimizing'}\n• Wealth Growth: ${metrics.wealthGrowth?.trend || 'Growing'}`;
        
        if (highPriorityAlerts.length > 0) {
            welcomeMsg += `\n\n🚨 **URGENT ALERTS:**`;
            highPriorityAlerts.forEach(alert => {
                welcomeMsg += `\n• ${alert.message}`;
            });
        }
        
        if (alerts.length > highPriorityAlerts.length) {
            welcomeMsg += `\n\n💡 **OPPORTUNITIES:** ${alerts.length - highPriorityAlerts.length} insights available`;
        }
        
        welcomeMsg += `\n\n🎯 **EXPERTISE AREAS:**\n• ICT Trading & Prop Firm Mastery\n• Australian Tax Optimization & Accounting\n• Property Investment & Wealth Building\n• Business Scaling & Strategic Growth\n\n💡 **NEXT STEPS:** ${metrics.nextSteps?.priority || 'Scale operations + optimize tax structure'}\n\nWhat empire-building challenge shall we tackle?`;
        
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
        const wins = trades.filter(trade => trade && (trade.outcome === 'win' || trade.rScore > 0)).length;
        const winRate = trades.length ? (wins / trades.length * 100).toFixed(1) : 0;
        const avgProfit = trades.length ? trades.reduce((sum, trade) => {
            const profit = (trade && trade.profit) || (trade && trade.rScore) || 0;
            return sum + (isNaN(profit) ? 0 : profit);
        }, 0) / trades.length : 0;
        
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
        
        let bestSession = 'Unknown';
        let bestAvg = -999;
        Object.entries(sessionPerformance).forEach(([session, scores]) => {
            if (scores.length >= 3) {
                const avg = scores.reduce((a, b) => a + b, 0) / scores.length;
                if (avg > bestAvg) {
                    bestAvg = avg;
                    bestSession = session;
                }
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
        
        const fundedCapital = firms.filter(firm => firm.status === 'funded')
            .reduce((sum, firm) => sum + (firm.accountSize || 0), 0);
        
        const monthlyProfit = firms.filter(firm => firm.status === 'funded')
            .reduce((sum, firm) => sum + (firm.monthlyProfit || 0), 0);
        
        const roi = fundedCapital > 0 ? (monthlyProfit / fundedCapital * 100).toFixed(1) : 0;
        
        const health = roi > 5 ? 'Excellent' : roi > 2 ? 'Good' : 'Needs Improvement';
        const recommendation = roi < 2 ? 'Focus on consistency and risk management' : 'Consider scaling operations';
        
        return {
            fundedCapital: fundedCapital,
            monthlyProfit: monthlyProfit,
            roi: roi + '%',
            health: health,
            recommendation: recommendation
        };
    }

    analyzePropFirmProgress() {
        const firms = this.propFirms || [];
        const funded = firms.filter(firm => firm && firm.status === 'funded').length;
        const challenges = firms.filter(firm => firm && firm.status === 'challenge').length;
        
        return {
            fundedAccounts: funded,
            activeChallenges: challenges,
            totalFirms: firms.length,
            summary: `${funded} funded, ${challenges} challenges`,
            nextTarget: funded < 3 ? 'Focus on getting 3+ funded accounts' : 'Scale to larger account sizes'
        };
    }

    calculateTaxEfficiency() {
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
        const actions = {
            'gamma-report': () => {
                const report = this.generateGammaReport('monthly');
                navigator.clipboard.writeText(JSON.stringify(report, null, 2));
                this.addMessage('assistant', '📊 **Monthly Report Generated!**\n\nProfessional presentation data copied to clipboard.\n\n🎯 **Next Steps:**\n1. Open Gamma.app\n2. Create new presentation\n3. Paste data (Ctrl+V)\n4. Select "Professional" template\n\n💡 **Includes:** Performance analytics, predictive insights, optimization recommendations');
            },
            'predictions': () => {
                const predictions = this.generatePredictiveAnalytics();
                this.addMessage('assistant', `🔮 **Predictive Analytics**\n\n🎯 **Key Insight:** ${predictions.keyInsight}\n\n📊 **Projections:**\n• Monthly Target: ${predictions.monthlyRTarget}\n• Profit Projection: ${predictions.monthlyProfitProjection}\n• Q3 Target: ${predictions.q3Projection}\n\n🚀 **Optimization:** ${predictions.optimizations?.topRecommendation}\n\n📈 **Growth Rate:** ${predictions.growthRate}`);
            },
            'alerts': () => {
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
            }
        };
        
        if (actions[action]) {
            actions[action]();
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
            
            const commandActions = {
                'win rate': () => {
                    const winRate = this.businessIntelligence.tradingPerformance?.winRate || '0%';
                    this.speak(`Your current win rate is ${winRate}`);
                    this.addMessage('assistant', `🎤 Your current win rate is **${winRate}**`);
                },
                'alert': () => {
                    this.quickAction('alerts');
                    this.speak('Checking your alerts now');
                },
                'report': () => {
                    this.quickAction('gamma-report');
                    this.speak('Generating your monthly report');
                },
                'prediction': () => {
                    this.quickAction('predictions');
                    this.speak('Here are your predictive analytics');
                }
            };
            
            const matchedCommand = Object.keys(commandActions).find(cmd => actualCommand.includes(cmd));
            if (matchedCommand) {
                commandActions[matchedCommand]();
            } else {
                this.speak('I can help with win rate, alerts, reports, or predictions');
                this.addMessage('assistant', '🎤 Available commands:\n• "win rate"\n• "alerts"\n• "generate report"\n• "predictions"');
            }
        }
    }

    speak(text) {
        try {
            if (this.synthesis) {
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = 0.9;
                utterance.pitch = 1;
                this.synthesis.speak(utterance);
            }
        } catch (error) {
            console.error('Error with speech synthesis:', error);
        }
    }

    analyzeLosingTrades() {
        const trades = this.tradingData || [];
        const losingTrades = trades.filter(trade => trade.rScore < 0 || trade.outcome === 'loss');
        
        if (!losingTrades || losingTrades.length === 0) {
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

    generateGammaReport(reportType) {
        return {
            title: `${reportType.charAt(0).toUpperCase() + reportType.slice(1)} Trading Report`,
            data: this.generateComprehensiveSummary(),
            insights: this.generatePredictiveAnalytics(),
            timestamp: new Date().toISOString()
        };
    }

    getCSRFToken() {
        try {
            return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
        } catch (error) {
            console.error('Error getting CSRF token:', error);
            return '';
        }
    }

    requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.tradingChatbot = new TradingChatbot();
});