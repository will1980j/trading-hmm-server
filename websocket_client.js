/**
 * WebSocket Client for Real-time Trading Platform
 * Handles instant signal updates, ML predictions, and system health
 */

class TradingWebSocketClient {
    constructor() {
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.isConnected = false;
        this.eventHandlers = {};
        
        this.init();
    }
    
    init() {
        try {
            // Initialize Socket.IO connection
            this.socket = io({
                transports: ['websocket', 'polling'],
                upgrade: true,
                rememberUpgrade: true
            });
            
            this.setupEventHandlers();
            this.setupReconnection();
            
        } catch (error) {
            console.error('WebSocket initialization failed:', error);
            this.scheduleReconnect();
        }
    }
    
    setupEventHandlers() {
        // Connection events
        this.socket.on('connect', () => {
            this.isConnected = true;
            this.reconnectAttempts = 0;
            console.log('🚀 WebSocket connected');
            this.updateConnectionStatus('connected');
            
            // Request initial data
            this.requestWebhookStats();
            this.requestLivePrediction();
        });
        
        this.socket.on('disconnect', () => {
            this.isConnected = false;
            console.log('🔌 WebSocket disconnected');
            this.updateConnectionStatus('disconnected');
        });
        
        // Signal events
        this.socket.on('signal_update', (data) => {
            this.handleSignalUpdate(data);
        });
        
        this.socket.on('ml_prediction_update', (data) => {
            this.handleMLPredictionUpdate(data);
        });
        
        this.socket.on('webhook_health_update', (data) => {
            this.handleWebhookHealthUpdate(data);
        });
        
        this.socket.on('webhook_stats_update', (data) => {
            this.handleWebhookStatsUpdate(data);
        });
        
        this.socket.on('live_prediction_update', (data) => {
            this.handleLivePredictionUpdate(data);
        });
        
        this.socket.on('signal_gap_alert', (data) => {
            this.handleSignalGapAlert(data);
        });
        
        this.socket.on('system_health_update', (data) => {
            this.handleSystemHealthUpdate(data);
        });
        
        this.socket.on('ml_model_update', (data) => {
            this.handleMLModelUpdate(data);
        });
    }
    
    setupReconnection() {
        this.socket.on('connect_error', (error) => {
            console.error('WebSocket connection error:', error);
            this.scheduleReconnect();
        });
    }
    
    scheduleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
            
            console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            setTimeout(() => {
                if (!this.isConnected) {
                    this.init();
                }
            }, delay);
        } else {
            console.error('Max reconnection attempts reached');
            this.updateConnectionStatus('failed');
        }
    }
    
    // Event handlers
    handleSignalUpdate(data) {
        try {
            console.log('📊 Signal update received:', data);
            
            // Update signal displays across all dashboards
            this.updateSignalDisplays(data);
            
            // Show notification for high-confidence signals
            if (data.prediction && data.prediction.confidence > 80) {
                this.showHighConfidenceAlert(data);
            }
            
            // Trigger custom event handlers
            this.triggerEvent('signal_update', data);
        } catch (error) {
            console.error('Error handling signal update:', error);
        }
    }
    
    handleMLPredictionUpdate(data) {
        try {
            console.log('🤖 ML prediction update:', data);
            this.updateMLPredictionDisplay(data);
            this.triggerEvent('ml_prediction_update', data);
        } catch (error) {
            console.error('Error handling ML prediction update:', error);
        }
    }
    
    handleWebhookHealthUpdate(data) {
        try {
            this.updateWebhookHealthDisplay(data);
            this.triggerEvent('webhook_health_update', data);
        } catch (error) {
            console.error('Error handling webhook health update:', error);
        }
    }
    
    handleWebhookStatsUpdate(data) {
        try {
            this.updateWebhookStatsDisplay(data);
            this.triggerEvent('webhook_stats_update', data);
        } catch (error) {
            console.error('Error handling webhook stats update:', error);
        }
    }
    
    updateWebhookStatsDisplay(data) {
        // Update webhook statistics display
        if (data.stats) {
            const bullishStats = data.stats.bullish || {};
            const bearishStats = data.stats.bearish || {};
            
            // Update counts
            const bullishElement = document.getElementById('webhookBullishCount');
            const bearishElement = document.getElementById('webhookBearishCount');
            
            if (bullishElement) bullishElement.textContent = bullishStats.count || 0;
            if (bearishElement) bearishElement.textContent = bearishStats.count || 0;
            
            // Update last signal times
            if (bullishStats.last_signal) {
                const lastBullishElement = document.getElementById('webhookLastBullish');
                if (lastBullishElement) lastBullishElement.textContent = this.getTimeAgo(bullishStats.last_signal);
            }
            if (bearishStats.last_signal) {
                const lastBearishElement = document.getElementById('webhookLastBearish');
                if (lastBearishElement) lastBearishElement.textContent = this.getTimeAgo(bearishStats.last_signal);
            }
            
            // Update health status
            const hasRecent = (bullishStats.count > 0 || bearishStats.count > 0);
            const healthElement = document.getElementById('webhookHealth');
            if (healthElement) healthElement.textContent = hasRecent ? '✅' : '⚠️';
            
            // Update last signal display
            const lastSignalElement = document.getElementById('webhookLastSignal');
            if (lastSignalElement && (bullishStats.last_signal || bearishStats.last_signal)) {
                const mostRecent = bullishStats.last_signal > bearishStats.last_signal ? 
                    { bias: 'Bullish', time: bullishStats.last_signal } :
                    { bias: 'Bearish', time: bearishStats.last_signal };
                
                lastSignalElement.textContent = `${mostRecent.bias} (${this.getTimeAgo(mostRecent.time)})`;
            }
        }
    }
    
    updateWebhookHealthDisplay(data) {
        // Update webhook health indicators
        console.log('Webhook health update:', data);
        
        if (data.status) {
            const statusElement = document.getElementById('connectionStatus');
            if (statusElement) {
                if (data.status === 'healthy') {
                    statusElement.textContent = 'Connected - Signals flowing normally';
                } else {
                    statusElement.textContent = `Warning - ${data.status}`;
                }
            }
            
            // Update health status emoji
            const healthElement = document.getElementById('bannerHealthStatus');
            if (healthElement) {
                healthElement.textContent = data.status === 'healthy' ? '✅' : '⚠️';
            }
        }
    }
    
    handleLivePredictionUpdate(data) {
        this.updateLivePredictionDisplay(data);
        this.triggerEvent('live_prediction_update', data);
    }
    
    handleSignalGapAlert(data) {
        console.warn('⚠️ Signal gap detected:', data);
        this.showSignalGapAlert(data);
        this.triggerEvent('signal_gap_alert', data);
    }
    
    handleSystemHealthUpdate(data) {
        this.updateSystemHealthDisplay(data);
        this.triggerEvent('system_health_update', data);
    }
    
    handleMLModelUpdate(data) {
        console.log('🧠 ML model update:', data);
        this.updateMLModelDisplay(data);
        this.triggerEvent('ml_model_update', data);
    }
    
    // UI update methods
    updateConnectionStatus(status) {
        const statusElement = document.getElementById('connectionStatus');
        const pulseElement = document.getElementById('connectionPulse');
        
        if (statusElement) {
            switch (status) {
                case 'connected':
                    statusElement.textContent = 'Connected - Real-time updates active';
                    if (pulseElement) {
                        pulseElement.style.background = '#10b981';
                        pulseElement.style.animation = 'pulse 2s infinite';
                    }
                    break;
                case 'disconnected':
                    statusElement.textContent = 'Disconnected - Attempting to reconnect...';
                    if (pulseElement) {
                        pulseElement.style.background = '#f59e0b';
                        pulseElement.style.animation = 'pulse-warning 2s infinite';
                    }
                    break;
                case 'failed':
                    statusElement.textContent = 'Connection failed - Refresh page to retry';
                    if (pulseElement) {
                        pulseElement.style.background = '#ef4444';
                        pulseElement.style.animation = 'pulse-danger 2s infinite';
                    }
                    break;
            }
        }
    }
    
    updateSignalDisplays(data) {
        // Update banner information
        const lastSignalElement = document.getElementById('bannerLastSignal');
        const healthStatusElement = document.getElementById('bannerHealthStatus');
        
        if (lastSignalElement && data.signal) {
            const timeAgo = this.getTimeAgo(data.timestamp);
            lastSignalElement.textContent = `${data.signal.bias} ${timeAgo}`;
        }
        
        if (healthStatusElement) {
            healthStatusElement.textContent = '✅';
        }
        
        // Update webhook monitoring section
        this.updateWebhookMonitoringDisplay(data);
    }
    
    updateWebhookMonitoringDisplay(data) {
        if (!data.signal) return;
        
        const bias = data.signal.bias.toLowerCase();
        const countElement = document.getElementById(`webhook${bias.charAt(0).toUpperCase() + bias.slice(1)}Count`);
        const lastElement = document.getElementById(`webhookLast${bias.charAt(0).toUpperCase() + bias.slice(1)}`);
        
        if (countElement) {
            const currentCount = parseInt(countElement.textContent) || 0;
            countElement.textContent = currentCount + 1;
        }
        
        if (lastElement) {
            lastElement.textContent = this.getTimeAgo(data.timestamp);
        }
        
        // Update health indicator
        const healthElement = document.getElementById('webhookHealth');
        if (healthElement) {
            healthElement.textContent = '✅';
        }
        
        // Update last signal display
        const lastSignalElement = document.getElementById('webhookLastSignal');
        if (lastSignalElement) {
            lastSignalElement.textContent = `${data.signal.bias} at ${data.signal.price} (${this.getTimeAgo(data.timestamp)})`;
        }
    }
    
    updateMLPredictionDisplay(data) {
        const container = document.getElementById('livePredictionContent');
        if (!container || !data.prediction) return;
        
        const pred = data.prediction;
        const signal = data.signal;
        
        const confidenceColor = pred.confidence >= 80 ? 'var(--accent-success)' : 
                              pred.confidence >= 60 ? 'var(--accent-warning)' : 'var(--accent-danger)';
        
        container.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin-bottom: 20px;">
                <div class="stat-card">
                    <div class="stat-label">Signal</div>
                    <div style="font-size: 16px; margin-top: 8px;">${signal.session} ${signal.bias}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Price</div>
                    <div style="font-size: 16px; margin-top: 8px; color: var(--accent-primary);">${signal.price ? signal.price.toFixed(2) : 'N/A'}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Prediction</div>
                    <div class="stat-value" style="font-size: 20px; color: ${pred.prediction === 'Success' ? 'var(--accent-success)' : 'var(--accent-danger)'};">
                        ${pred.prediction}
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Confidence</div>
                    <div class="stat-value" style="font-size: 20px; color: ${confidenceColor};">${pred.confidence}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Position Size</div>
                    <div style="font-size: 16px; margin-top: 8px; color: var(--text-secondary);">${pred.position_size}</div>
                </div>
            </div>
            <div style="background: var(--bg-secondary); padding: 15px; border-radius: 8px; margin-top: 15px;">
                <div style="font-size: 13px; font-weight: 600; margin-bottom: 8px;">Multi-Target Predictions:</div>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
                    ${Object.entries(pred.multi_target || {}).map(([target, prob]) => `
                        <div style="text-align: center; padding: 8px; background: var(--bg-card); border-radius: 6px;">
                            <div style="font-size: 11px; color: var(--text-secondary);">${target}</div>
                            <div style="font-size: 14px; font-weight: 600; margin-top: 2px;">${(prob * 100).toFixed(1)}%</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    updateLivePredictionDisplay(data) {
        if (data.status === 'no_active_signal') {
            const container = document.getElementById('livePredictionContent');
            if (container) {
                container.innerHTML = '<p style="color: var(--text-secondary); text-align: center;">No active signals</p>';
            }
        } else {
            this.updateMLPredictionDisplay(data);
        }
    }
    
    updateSystemHealthDisplay(data) {
        // Update system health indicators
        console.log('System health update:', data);
        
        // Update any system health displays if they exist
        const healthElements = document.querySelectorAll('[data-health-indicator]');
        healthElements.forEach(element => {
            if (data.data && data.data.status) {
                element.textContent = data.data.status === 'healthy' ? '✅' : '⚠️';
            }
        });
    }
    
    updateMLModelDisplay(data) {
        // Update ML model status displays
        console.log('ML model update:', data);
        
        // Show notification for model updates
        if (data.data) {
            let message = '';
            if (data.data.type === 'hyperparameter_optimization') {
                message = `🤖 ML Model Optimized - New accuracy: ${data.data.accuracy || 'N/A'}%`;
            } else if (data.data.type === 'model_retrain') {
                message = `🧠 ML Model Retrained - ${data.data.samples || 'N/A'} samples`;
            } else {
                message = '🔄 ML Model Updated';
            }
            
            this.showInAppAlert(message, 'info');
        }
    }
    
    showHighConfidenceAlert(data) {
        // Show browser notification if permitted
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('High Confidence Signal', {
                body: `${data.signal.bias} ${data.signal.symbol} - ${data.prediction.confidence}% confidence`,
                tag: 'high-confidence-signal',
                icon: '/favicon.ico'
            });
        }
        
        // Show in-app alert
        this.showInAppAlert(`🚀 High Confidence Signal: ${data.signal.bias} ${data.signal.symbol} (${data.prediction.confidence}%)`, 'success');
    }
    
    showSignalGapAlert(data) {
        const alertElement = document.getElementById('signalGapAlert');
        const detailsElement = document.getElementById('signalGapDetails');
        
        if (alertElement && detailsElement) {
            alertElement.style.display = 'block';
            detailsElement.textContent = `No signals received for ${data.minutes_since_last} minutes. Check TradingView connection.`;
        }
        
        this.showInAppAlert(`⚠️ Signal gap detected: ${data.minutes_since_last} minutes since last signal`, 'warning');
    }
    
    showInAppAlert(message, type = 'info') {
        // Create alert element
        const alert = document.createElement('div');
        alert.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            z-index: 10000;
            max-width: 400px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            animation: slideIn 0.3s ease-out;
        `;
        
        // Set background color based on type
        const colors = {
            success: '#10b981',
            warning: '#f59e0b',
            error: '#ef4444',
            info: '#3b82f6'
        };
        alert.style.background = colors[type] || colors.info;
        alert.textContent = message;
        
        document.body.appendChild(alert);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            alert.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.parentNode.removeChild(alert);
                }
            }, 300);
        }, 5000);
    }
    
    // Utility methods
    getTimeAgo(timestamp) {
        const now = new Date();
        const time = new Date(timestamp);
        const diffMs = now - time;
        const diffMins = Math.floor(diffMs / 60000);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        
        const diffHours = Math.floor(diffMins / 60);
        if (diffHours < 24) return `${diffHours}h ago`;
        
        const diffDays = Math.floor(diffHours / 24);
        return `${diffDays}d ago`;
    }
    
    // Public API methods
    requestWebhookStats() {
        if (this.isConnected) {
            this.socket.emit('request_webhook_stats');
        }
    }
    
    requestLivePrediction() {
        if (this.isConnected) {
            this.socket.emit('request_live_prediction');
        }
    }
    
    // Event system for custom handlers
    on(event, handler) {
        if (!this.eventHandlers[event]) {
            this.eventHandlers[event] = [];
        }
        this.eventHandlers[event].push(handler);
    }
    
    off(event, handler) {
        if (this.eventHandlers[event]) {
            const index = this.eventHandlers[event].indexOf(handler);
            if (index > -1) {
                this.eventHandlers[event].splice(index, 1);
            }
        }
    }
    
    triggerEvent(event, data) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event].forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`Error in event handler for ${event}:`, error);
                }
            });
        }
    }
}

// CSS animations for alerts
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Initialize WebSocket client
let wsClient;
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Initializing WebSocket client...');
    wsClient = new TradingWebSocketClient();
    
    // Request notification permission
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
    
    // Debug: Log WebSocket client status
    setTimeout(() => {
        if (wsClient) {
            console.log('✅ WebSocket client initialized:', {
                connected: wsClient.isConnected,
                socket: !!wsClient.socket,
                eventHandlers: Object.keys(wsClient.eventHandlers)
            });
        }
    }, 1000);
});

// Export for use in other scripts
window.TradingWebSocketClient = TradingWebSocketClient;