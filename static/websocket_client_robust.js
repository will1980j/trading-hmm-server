/**
 * Robust WebSocket Client for Automated Signals Dashboard
 * Production-grade implementation with:
 * - Automatic reconnection with exponential backoff
 * - Connection state management
 * - Error handling and recovery
 * - Graceful degradation to HTTP polling
 * - Health monitoring
 */

class RobustWebSocketClient {
    constructor(options = {}) {
        this.options = {
            reconnectDelay: 1000,
            maxReconnectDelay: 30000,
            reconnectDecay: 1.5,
            maxReconnectAttempts: 10,
            pollingFallbackDelay: 60000,
            ...options
        };
        
        this.socket = null;
        this.reconnectAttempts = 0;
        this.reconnectTimer = null;
        this.pollingTimer = null;
        this.isConnected = false;
        this.usePollingFallback = false;
        this.eventHandlers = {};
        
        this.init();
    }
    
    init() {
        console.log('[WebSocket] Initializing robust WebSocket client');
        this.connect();
    }
    
    connect() {
        try {
            console.log('[WebSocket] Attempting connection...');
            
            // Initialize Socket.IO with robust configuration
            this.socket = io({
                transports: ['websocket', 'polling'],  // Try WebSocket first, fallback to polling
                upgrade: true,
                rememberUpgrade: true,
                reconnection: true,
                reconnectionDelay: this.options.reconnectDelay,
                reconnectionDelayMax: this.options.maxReconnectDelay,
                reconnectionAttempts: this.options.maxReconnectAttempts,
                timeout: 20000,
                autoConnect: true,
                forceNew: false
            });
            
            this.registerSocketHandlers();
            
        } catch (error) {
            console.error('[WebSocket] Connection initialization failed:', error);
            this.handleConnectionError(error);
        }
    }
    
    registerSocketHandlers() {
        // Connection successful
        this.socket.on('connect', () => {
            console.log('[WebSocket] Connected successfully');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.usePollingFallback = false;
            
            // Stop polling fallback if active
            if (this.pollingTimer) {
                clearInterval(this.pollingTimer);
                this.pollingTimer = null;
            }
            
            this.updateConnectionStatus(true);
            this.emit('connected');
            
            // Request initial data
            this.requestSignalHistory();
            this.requestHealthStatus();
        });
        
        // Connection error
        this.socket.on('connect_error', (error) => {
            console.error('[WebSocket] Connection error:', error);
            this.isConnected = false;
            this.handleConnectionError(error);
        });
        
        // Disconnection
        this.socket.on('disconnect', (reason) => {
            console.warn('[WebSocket] Disconnected:', reason);
            this.isConnected = false;
            this.updateConnectionStatus(false);
            this.emit('disconnected', reason);
            
            // Handle different disconnect reasons
            if (reason === 'io server disconnect') {
                // Server initiated disconnect, reconnect manually
                console.log('[WebSocket] Server disconnect, attempting reconnect...');
                this.socket.connect();
            } else if (reason === 'transport close' || reason === 'transport error') {
                // Network issue, start polling fallback
                this.startPollingFallback();
            }
        });
        
        // Reconnection attempt
        this.socket.on('reconnect_attempt', (attemptNumber) => {
            console.log(`[WebSocket] Reconnection attempt ${attemptNumber}`);
            this.reconnectAttempts = attemptNumber;
            this.updateConnectionStatus(false, `Reconnecting (${attemptNumber})...`);
        });
        
        // Reconnection failed
        this.socket.on('reconnect_failed', () => {
            console.error('[WebSocket] Reconnection failed after max attempts');
            this.startPollingFallback();
        });
        
        // Reconnection successful
        this.socket.on('reconnect', (attemptNumber) => {
            console.log(`[WebSocket] Reconnected after ${attemptNumber} attempts`);
            this.reconnectAttempts = 0;
            this.updateConnectionStatus(true);
        });
        
        // Signal updates
        this.socket.on('signal_update', (data) => {
            console.log('[WebSocket] Signal update received:', data);
            this.emit('signal_update', data);
        });
        
        // MFE updates
        this.socket.on('mfe_update', (data) => {
            console.log('[WebSocket] MFE update received:', data);
            this.emit('mfe_update', data);
        });
        
        // Trade completion
        this.socket.on('trade_completed', (data) => {
            console.log('[WebSocket] Trade completed:', data);
            this.emit('trade_completed', data);
        });
        
        // Health updates
        this.socket.on('health_update', (data) => {
            console.log('[WebSocket] Health update:', data);
            this.emit('health_update', data);
        });
        
        // Signal history
        this.socket.on('signal_history', (data) => {
            console.log('[WebSocket] Signal history received:', data);
            this.emit('signal_history', data);
        });
        
        // Pong response
        this.socket.on('pong', (data) => {
            console.log('[WebSocket] Pong received');
            this.emit('pong', data);
        });
        
        // Error handling
        this.socket.on('error', (error) => {
            console.error('[WebSocket] Socket error:', error);
            this.emit('error', error);
        });
    }
    
    handleConnectionError(error) {
        this.reconnectAttempts++;
        
        if (this.reconnectAttempts >= this.options.maxReconnectAttempts) {
            console.error('[WebSocket] Max reconnection attempts reached');
            this.startPollingFallback();
        } else {
            const delay = Math.min(
                this.options.reconnectDelay * Math.pow(this.options.reconnectDecay, this.reconnectAttempts),
                this.options.maxReconnectDelay
            );
            
            console.log(`[WebSocket] Retrying in ${delay}ms (attempt ${this.reconnectAttempts})`);
            this.updateConnectionStatus(false, `Retrying in ${Math.round(delay/1000)}s...`);
        }
    }
    
    startPollingFallback() {
        if (this.usePollingFallback) {
            return; // Already using fallback
        }
        
        console.warn('[WebSocket] Starting HTTP polling fallback');
        this.usePollingFallback = true;
        this.updateConnectionStatus(false, 'Using HTTP polling');
        
        // Poll for updates
        this.pollingTimer = setInterval(() => {
            this.pollForUpdates();
        }, this.options.pollingFallbackDelay);
        
        // Immediate poll
        this.pollForUpdates();
    }
    
    async pollForUpdates() {
        try {
            console.log('[Polling] Fetching dashboard data...');
            const response = await fetch('/api/automated-signals/dashboard-data');
            const data = await response.json();
            
            if (data.success) {
                this.emit('polling_update', data);
            }
        } catch (error) {
            console.error('[Polling] Failed to fetch data:', error);
        }
    }
    
    updateConnectionStatus(connected, message = null) {
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        
        if (statusDot && statusText) {
            if (connected) {
                statusDot.classList.remove('disconnected');
                statusText.textContent = 'Connected';
                statusText.style.color = '#10b981';
            } else {
                statusDot.classList.add('disconnected');
                statusText.textContent = message || 'Disconnected';
                statusText.style.color = '#ef4444';
            }
        }
        
        this.emit('connection_status', { connected, message });
    }
    
    // Event emitter methods
    on(event, handler) {
        if (!this.eventHandlers[event]) {
            this.eventHandlers[event] = [];
        }
        this.eventHandlers[event].push(handler);
    }
    
    emit(event, data) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event].forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`[WebSocket] Event handler error for ${event}:`, error);
                }
            });
        }
    }
    
    // Request methods
    requestSignalHistory(limit = 10) {
        if (this.isConnected && this.socket) {
            this.socket.emit('request_signal_history', { limit });
        }
    }
    
    requestHealthStatus() {
        if (this.isConnected && this.socket) {
            this.socket.emit('request_health_status');
        }
    }
    
    ping() {
        if (this.isConnected && this.socket) {
            this.socket.emit('ping');
        }
    }
    
    // Cleanup
    disconnect() {
        console.log('[WebSocket] Disconnecting...');
        
        if (this.pollingTimer) {
            clearInterval(this.pollingTimer);
        }
        
        if (this.socket) {
            this.socket.disconnect();
        }
        
        this.isConnected = false;
        this.usePollingFallback = false;
    }
    
    // Status getters
    getConnectionStatus() {
        return {
            connected: this.isConnected,
            reconnectAttempts: this.reconnectAttempts,
            usingPolling: this.usePollingFallback,
            transport: this.socket?.io?.engine?.transport?.name || 'unknown'
        };
    }
}

// Export for use in dashboard
window.RobustWebSocketClient = RobustWebSocketClient;
