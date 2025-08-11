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
        typingDiv.innerHTML = '<div class="message-content">🤖 Analyzing your trading data...</div>';
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
                addMessage(data.insight, false);
            } else {
                addMessage('I\'m having trouble accessing my AI capabilities right now. Let me provide some basic analysis based on your data...', false);
                
                // Fallback to local analysis
                const fallbackResponse = generateFallbackResponse(message, filteredTrades, metrics);
                setTimeout(() => addMessage(fallbackResponse, false), 1000);
            }
        } catch (error) {
            console.error('Chat AI error:', error);
            
            // Remove typing indicator
            if (chatMessages.contains(typingDiv)) {
                chatMessages.removeChild(typingDiv);
            }
            
            addMessage('I\'m currently running in offline mode. Let me analyze your data locally...', false);
            
            // Provide local analysis as fallback
            const filteredTrades = getFilteredTrades();
            const metrics = calculateAdvancedMetrics(filteredTrades, parseInt(document.getElementById('rTargetFilter').value));
            const fallbackResponse = generateFallbackResponse(message, filteredTrades, metrics);
            
            setTimeout(() => addMessage(fallbackResponse, false), 1500);
        }
    }
    
    // Generate fallback responses for offline mode
    function generateFallbackResponse(message, trades, metrics) {
        const messageLower = message.toLowerCase();
        
        if (messageLower.includes('win rate') || messageLower.includes('winrate')) {
            return `Your current win rate is ${metrics.winRate}%. ${parseFloat(metrics.winRate) > 60 ? 'Excellent performance!' : parseFloat(metrics.winRate) > 50 ? 'Good performance, room for improvement.' : 'Focus on setup quality to improve win rate.'}`;
        }
        
        if (messageLower.includes('risk') || messageLower.includes('drawdown')) {
            return `Your maximum drawdown is ${metrics.maxDrawdown}. ${parseFloat(metrics.maxDrawdown) < 10 ? 'Excellent risk management!' : parseFloat(metrics.maxDrawdown) < 20 ? 'Good risk control, monitor closely.' : 'Consider reducing position size to manage risk.'}`;
        }
        
        if (messageLower.includes('expectancy') || messageLower.includes('profit')) {
            return `Your expectancy is ${metrics.expectancy}. ${parseFloat(metrics.expectancy) > 0.5 ? 'Strong positive expectancy!' : parseFloat(metrics.expectancy) > 0 ? 'Positive expectancy, good foundation.' : 'Work on improving your edge - expectancy should be positive.'}`;
        }
        
        if (messageLower.includes('target') || messageLower.includes('r-target')) {
            const optimal = analyzeOptimalRTarget(trades);
            const current = parseInt(document.getElementById('rTargetFilter').value);
            return `Based on your MFE data, optimal R-target is ${optimal}R. You're currently using ${current}R. ${optimal === current ? 'Your target is optimized!' : `Consider switching to ${optimal}R for better expectancy.`}`;
        }
        
        if (messageLower.includes('session') || messageLower.includes('time')) {
            const bestSession = analyzeBestSession(trades);
            return `Your best performing session is ${bestSession}. Consider focusing more trades during this time period for optimal results.`;
        }
        
        if (messageLower.includes('improve') || messageLower.includes('better')) {
            const suggestions = [];
            if (parseFloat(metrics.winRate) < 55) suggestions.push('improve setup quality');
            if (parseFloat(metrics.maxDrawdown) > 15) suggestions.push('reduce position size');
            if (parseFloat(metrics.expectancy) < 0.3) suggestions.push('optimize R-targets');
            
            return suggestions.length > 0 ? 
                `To improve performance, focus on: ${suggestions.join(', ')}. Your current stats: ${metrics.winRate}% win rate, ${metrics.expectancy} expectancy.` :
                `Your performance looks solid! Continue with current approach. Stats: ${metrics.winRate}% win rate, ${metrics.expectancy} expectancy.`;
        }
        
        // Default response
        return `Based on your ${trades.length} trades: Win Rate: ${metrics.winRate}%, Expectancy: ${metrics.expectancy}, Max DD: ${metrics.maxDrawdown}. What specific aspect would you like me to analyze?`;
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
        addMessage('Hi! I\'m your AI trading assistant powered by advanced analytics. Ask me about your performance, risk management, optimal R-targets, or strategy optimization!', false);
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