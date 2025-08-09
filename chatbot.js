// Trading AI Chatbot - Universal Component
class TradingChatbot {
    constructor() {
        this.isOpen = false;
        this.messages = [];
        this.init();
    }

    init() {
        this.createChatWidget();
        this.loadContext();
    }

    loadContext() {
        // Load trading data for context
        this.tradingData = JSON.parse(localStorage.getItem('tradingData')) || [];
        this.propFirms = JSON.parse(localStorage.getItem('propFirmsV2_2024-01')) || [];
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

        // Welcome message
        this.addMessage('assistant', 'Hi! I\'m your trading AI assistant. I can analyze your performance, explain ICT concepts, help with prop firm strategies, and answer trading questions. What would you like to know?');
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
                'background: #667eea; color: white; margin-left: auto; text-align: right;' : 
                'background: white; border: 1px solid #eee; margin-right: auto;'
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
        this.addMessage('assistant', '🤔 Thinking...');

        try {
            const response = await fetch('/api/ai-insights', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: `Trading Question: ${message}\n\nContext: You are helping a trader who uses ICT concepts, trades prop firms, and focuses on institutional trading. Answer their question with specific, actionable advice.`,
                    data: {
                        tradingData: this.tradingData.slice(-20),
                        propFirms: this.propFirms,
                        currentPage: window.location.pathname,
                        summary: this.generateQuickSummary()
                    }
                })
            });

            const result = await response.json();
            
            // Remove thinking message
            const messages = document.getElementById('chat-messages');
            messages.removeChild(messages.lastChild);

            if (result.status === 'success') {
                this.addMessage('assistant', result.insight);
            } else {
                this.addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
            }
        } catch (error) {
            const messages = document.getElementById('chat-messages');
            messages.removeChild(messages.lastChild);
            this.addMessage('assistant', 'Connection error. Please check your internet and try again.');
        }
    }

    generateQuickSummary() {
        const totalTrades = this.tradingData.length;
        const wins = this.tradingData.filter(t => t.outcome === 'win').length;
        const winRate = totalTrades ? (wins / totalTrades * 100).toFixed(1) : 0;
        const fundedAccounts = this.propFirms.filter(f => f.status === 'funded').length;

        return {
            totalTrades,
            winRate: winRate + '%',
            fundedAccounts,
            recentTrades: this.tradingData.slice(-5)
        };
    }
}

// Initialize chatbot when DOM loads
document.addEventListener('DOMContentLoaded', () => {
    window.tradingChatbot = new TradingChatbot();
});