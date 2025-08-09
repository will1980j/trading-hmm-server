// Trading Empire AI Advisor - Comprehensive Business Intelligence
class TradingChatbot {
    constructor() {
        this.isOpen = false;
        this.messages = [];
        this.tradingData = [];
        this.propFirms = [];
        this.businessIntelligence = {};
        this.knowledgeBase = this.initializeKnowledgeBase();
        this.init();
    }

    init() {
        this.createChatWidget();
        this.loadContext();
        this.analyzeBusinessMetrics();
    }

    initializeKnowledgeBase() {
        return {
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
            nextSteps: this.generateStrategicRecommendations()
        };
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
        return `TRADING EMPIRE ADVISOR - Multi-Disciplinary Expert

User Query: ${userMessage}

Context Analysis: ${context}

You are an expert advisor specializing in:
🎯 TRADING: ICT concepts, prop firms, institutional trading, risk management
💼 BUSINESS: Australian tax optimization, accounting standards, business scaling
🏠 WEALTH: Property investment (Australia/global), portfolio diversification
🚀 STRATEGY: PropFirmMatch.com intelligence, revenue optimization, next-step planning

Provide specific, actionable advice using the comprehensive business data provided. Focus on practical solutions that drive real results.`;
    }

    determineContext(message) {
        const msg = message.toLowerCase();
        if (msg.includes('tax') || msg.includes('accounting')) return 'Australian Tax & Accounting';
        if (msg.includes('prop') || msg.includes('challenge')) return 'Prop Firm Strategy';
        if (msg.includes('property') || msg.includes('invest')) return 'Wealth & Investment';
        if (msg.includes('business') || msg.includes('scale')) return 'Business Growth';
        if (msg.includes('trade') || msg.includes('ict')) return 'Trading Performance';
        return 'Strategic Planning';
    }

    generateIntelligentWelcome() {
        const metrics = this.businessIntelligence;
        return `🚀 **TRADING EMPIRE ADVISOR** - Your Multi-Disciplinary Expert\n\n📊 **CURRENT STATUS:**\n• Trading Performance: ${metrics.tradingPerformance.summary}\n• Prop Firm Progress: ${metrics.propFirmStatus.summary}\n• Tax Efficiency: ${metrics.taxEfficiency.rating}\n• Wealth Growth: ${metrics.wealthGrowth.trend}\n\n🎯 **EXPERTISE AREAS:**\n• ICT Trading & Prop Firm Mastery\n• Australian Tax Optimization & Accounting\n• Property Investment & Wealth Building\n• Business Scaling & Strategic Growth\n\n💡 **NEXT STEPS:** ${metrics.nextSteps.priority}\n\nWhat empire-building challenge shall we tackle?`;
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
        const wins = trades.filter(t => t && t.outcome === 'win').length;
        const winRate = trades.length ? (wins / trades.length * 100).toFixed(1) : 0;
        const avgProfit = trades.length ? trades.reduce((sum, t) => sum + ((t && t.profit) || 0), 0) / trades.length : 0;
        
        return {
            totalTrades: trades.length,
            winRate: winRate + '%',
            avgProfit: avgProfit.toFixed(2),
            summary: `${winRate}% WR, ${trades.length} trades, $${avgProfit.toFixed(0)} avg`,
            trend: winRate > 60 ? 'Excellent' : winRate > 45 ? 'Good' : 'Needs Improvement'
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
}

// Initialize chatbot when DOM loads
document.addEventListener('DOMContentLoaded', () => {
    window.tradingChatbot = new TradingChatbot();
});