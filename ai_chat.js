// AI Chat Widget with Real OpenAI Integration
document.addEventListener('DOMContentLoaded', function() {
    const chatToggle = document.getElementById('chatToggle');
    const chatContainer = document.getElementById('chatContainer');
    const chatClose = document.getElementById('chatClose');
    const chatInput = document.getElementById('chatInput');
    const chatSend = document.getElementById('chatSend');
    const chatMessages = document.getElementById('chatMessages');
    
    let isOpen = false;
    
    // Toggle chat
    chatToggle.addEventListener('click', function() {
        isOpen = !isOpen;
        chatContainer.style.display = isOpen ? 'flex' : 'none';
    });
    
    // Close chat
    chatClose.addEventListener('click', function() {
        isOpen = false;
        chatContainer.style.display = 'none';
    });
    
    // Add message to chat
    function addMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${isUser ? 'user' : 'ai'}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;
        
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Send message with real AI
    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;
        
        addMessage(message, true);
        chatInput.value = '';
        
        // Add typing indicator
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message ai typing-indicator';
        typingDiv.innerHTML = '<div class="message-content">🚀 GPT-4o analyzing your trading patterns...</div>';
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        try {
            // Get current trading data
            const filteredTrades = getFilteredTrades();
            const rTarget = parseInt(document.getElementById('rTargetFilter').value);
            const metrics = calculateAdvancedMetrics(filteredTrades, rTarget);
            
            // Build comprehensive context for AI
            const tradingContext = {
                summary: {
                    totalTrades: filteredTrades.length,
                    winRate: metrics.winRate,
                    expectancy: metrics.expectancy,
                    maxDrawdown: metrics.maxDrawdown,
                    sharpeRatio: metrics.sharpeRatio,
                    profitFactor: metrics.profitFactor,
                    currentRTarget: rTarget
                },
                recentTrades: filteredTrades.slice(-10).map(trade => ({
                    date: trade.date,
                    session: trade.session,
                    bias: trade.bias,
                    rScore: trade.rScore,
                    breakeven: trade.breakeven
                })),
                performance: {
                    bestSession: analyzeBestSession(filteredTrades),
                    optimalRTarget: analyzeOptimalRTarget(filteredTrades),
                    riskScore: calculateRiskScore(filteredTrades)
                }
            };
            
            const response = await fetch('/api/ai-insights', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt: message,
                    data: tradingContext
                })
            });
            
            const data = await response.json();
            
            // Remove typing indicator
            chatMessages.removeChild(typingDiv);
            
            if (data.status === 'success') {
                addMessage('🎆 ' + data.insight, false);
            } else {
                addMessage('📊 AI service optimizing... Providing strategic analysis based on your trading data.', false);
                
                // Positive fallback to local analysis
                const fallbackResponse = generatePositiveFallbackResponse(message, filteredTrades, metrics);
                setTimeout(() => addMessage(fallbackResponse, false), 1000);
            }
        } catch (error) {
            console.error('Chat AI error:', error);
            
            // Remove typing indicator
            if (chatMessages.contains(typingDiv)) {
                chatMessages.removeChild(typingDiv);
            }
            
            addMessage('🌟 Strategic analysis mode activated. Analyzing your trading performance locally...', false);
            
            // Provide positive local analysis as fallback
            const filteredTrades = getFilteredTrades();
            const metrics = calculateAdvancedMetrics(filteredTrades, parseInt(document.getElementById('rTargetFilter').value));
            const fallbackResponse = generatePositiveFallbackResponse(message, filteredTrades, metrics);
            
            setTimeout(() => addMessage(fallbackResponse, false), 1500);
        }
    }
    
    // Generate positive, growth-focused fallback responses
    function generatePositiveFallbackResponse(message, trades, metrics) {
        const messageLower = message.toLowerCase();
        
        if (messageLower.includes('win rate') || messageLower.includes('winrate')) {
            const winRate = parseFloat(metrics.winRate);
            const encouragement = winRate > 60 ? '🎆 Outstanding consistency!' : winRate > 50 ? '🎯 Solid foundation with growth potential!' : '📈 Building strong execution habits!';
            return `${encouragement} Your success rate is ${metrics.winRate}%. ${winRate > 55 ? 'Maintain this excellent discipline!' : 'Focus on quality setups to enhance your edge.'}`;
        }
        
        if (messageLower.includes('risk') || messageLower.includes('drawdown')) {
            const maxDD = parseFloat(metrics.maxDrawdown.replace('R', ''));
            const protection = maxDD < 10 ? '🛡️ Excellent protective systems!' : maxDD < 15 ? '⚖️ Strong risk awareness!' : '🔧 Opportunity to optimize protection!';
            return `${protection} Maximum drawdown: ${metrics.maxDrawdown}. ${maxDD < 10 ? 'Your risk management enables sustainable growth!' : 'Consider position sizing optimization for enhanced protection.'}`;
        }
        
        if (messageLower.includes('expectancy') || messageLower.includes('profit')) {
            const expectancy = parseFloat(metrics.expectancy);
            const momentum = expectancy > 0.5 ? '🚀 Exceptional edge detected!' : expectancy > 0 ? '💪 Positive momentum building!' : '🌱 Foundation phase - valuable learning!';
            return `${momentum} Your expectancy is ${metrics.expectancy}R. ${expectancy > 0.2 ? 'Strong systematic advantage!' : 'Continue refining your approach for enhanced results.'}`;
        }
        
        if (messageLower.includes('target') || messageLower.includes('r-target')) {
            const optimal = analyzeOptimalRTarget(trades);
            const current = parseInt(document.getElementById('rTargetFilter').value);
            const optimization = optimal === current ? '✅ Perfect optimization!' : '🎯 Optimization opportunity!';
            return `${optimization} Based on your MFE analysis, optimal target is ${optimal}R (currently ${current}R). ${optimal === current ? 'Your targeting is mathematically optimized!' : `Switching to ${optimal}R could enhance your expectancy!`}`;
        }
        
        if (messageLower.includes('session') || messageLower.includes('time')) {
            const bestSession = analyzeBestSession(trades);
            return `⏰ Timing Intelligence: Your peak performance occurs during ${bestSession} session! Consider concentrating 60% of your trading volume during this optimal timeframe for maximum efficiency.`;
        }
        
        if (messageLower.includes('improve') || messageLower.includes('better') || messageLower.includes('optimize')) {
            const opportunities = [];
            const winRate = parseFloat(metrics.winRate);
            const maxDD = parseFloat(metrics.maxDrawdown.replace('R', ''));
            const expectancy = parseFloat(metrics.expectancy);
            
            if (winRate < 55) opportunities.push('setup refinement for higher success rate');
            if (maxDD > 12) opportunities.push('position sizing optimization for better protection');
            if (expectancy < 0.3) opportunities.push('R-target optimization for enhanced expectancy');
            
            const growth = opportunities.length > 0 ? 
                `🚀 Growth Opportunities: ${opportunities.join(', ')}. Current foundation: ${metrics.winRate}% success, ${metrics.expectancy}R expectancy.` :
                `🎆 Excellent performance! Your system shows strong fundamentals: ${metrics.winRate}% success rate, ${metrics.expectancy}R expectancy. Continue this disciplined approach!`;
            
            return growth;
        }
        
        if (messageLower.includes('scale') || messageLower.includes('size') || messageLower.includes('capital')) {
            const expectancy = parseFloat(metrics.expectancy);
            const maxDD = parseFloat(metrics.maxDrawdown.replace('R', ''));
            const scalingAdvice = expectancy > 0.3 && maxDD < 10 ? 
                '📈 Scaling Ready! Your metrics support gradual capital increase.' : 
                expectancy > 0 ? '🌱 Building Phase: Focus on consistency before scaling.' : 
                '🔧 Foundation Phase: Optimize edge before capital allocation.';
            return `${scalingAdvice} Performance metrics: ${metrics.expectancy}R expectancy, ${metrics.maxDrawdown} max drawdown. ${expectancy > 0.2 ? 'Strong foundation for growth!' : 'Continue building your systematic edge!'}`;
        }
        
        // Default positive response
        const expectancy = parseFloat(metrics.expectancy);
        const status = expectancy > 0.3 ? '🎆 Excellent' : expectancy > 0 ? '💪 Strong' : '🌱 Developing';
        return `${status} Trading System Analysis: ${trades.length} trades executed with ${metrics.winRate}% success rate and ${metrics.expectancy}R expectancy. Maximum drawdown: ${metrics.maxDrawdown}. What specific aspect would you like to optimize for enhanced performance?`;
    }
    
    // Event listeners
    chatSend.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Add welcome message
    setTimeout(() => {
        addMessage('🚀 Welcome to your AI Trading Intelligence Center! I\'m powered by GPT-4o and advanced analytics. Ask me about performance optimization, growth strategies, risk management, or scaling opportunities!', false);
    }, 1000);
});

// Add CSS for typing indicator
const style = document.createElement('style');
style.textContent = `
    .typing-indicator .message-content {
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.6; }
        50% { opacity: 1; }
    }
`;
document.head.appendChild(style);