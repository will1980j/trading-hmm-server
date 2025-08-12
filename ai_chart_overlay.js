// AI Chart Overlay - Inject into TradingView
// This script adds AI signals directly to the TradingView chart

class AIChartOverlay {
    constructor() {
        this.aiServerUrl = 'http://127.0.0.1:8080';
        this.signals = [];
        this.sweepLevels = [];
        this.fvgZones = [];
        this.lastUpdate = 0;
        this.updateInterval = 10000; // 10 seconds
        
        this.init();
    }
    
    init() {
        console.log('🤖 AI Chart Overlay initialized');
        this.createOverlayElements();
        this.startUpdates();
    }
    
    createOverlayElements() {
        // Create AI signal markers container
        this.signalContainer = document.createElement('div');
        this.signalContainer.id = 'ai-signal-container';
        this.signalContainer.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1000;
        `;
        
        // Find TradingView chart container
        const chartContainer = document.querySelector('[data-name="legend-source-item"]')?.closest('.chart-container') || 
                              document.querySelector('.chart-widget') ||
                              document.body;
        
        if (chartContainer) {
            chartContainer.appendChild(this.signalContainer);
            console.log('✅ AI overlay attached to chart');
        }
    }
    
    async getAIAnalysis() {
        try {
            const currentPrice = this.getCurrentPrice();
            const session = this.getCurrentSession();
            
            const response = await chrome.runtime.sendMessage({
                action: 'fetchData',
                url: `${this.aiServerUrl}/api/ai-chart-analysis?symbol=NQ1&price=${currentPrice}&session=${session}`
            });
            
            if (!response.success) {
                throw new Error(response.error);
            }
            
            const data = response.data;
            
            console.log('🤖 AI Analysis:', data);
            return data;
        } catch (error) {
            console.error('❌ AI Analysis failed:', error);
            return null;
        }
    }
    
    getCurrentPrice() {
        // Extract current price from TradingView
        const priceElements = document.querySelectorAll('[class*="price"], [class*="last"]');
        for (const element of priceElements) {
            const text = element.textContent || '';
            const match = text.match(/\b(1[5-9]\d{3}|2[0-5]\d{3})(?:\.\d+)?\b/);
            if (match) {
                return parseFloat(match[0]);
            }
        }
        return 15000; // Default
    }
    
    getCurrentSession() {
        const hour = new Date().getUTCHours();
        if (hour >= 0 && hour < 8) return 'ASIA';
        if (hour >= 8 && hour < 13) return 'LONDON';
        if (hour >= 13 && hour < 17) return 'NEW YORK AM';
        return 'NEW YORK PM';
    }
    
    markSignalOnChart(signal) {
        const marker = document.createElement('div');
        marker.className = 'ai-signal-marker';
        
        const isBuy = signal.bias && signal.bias.includes('LONG');
        const isSell = signal.bias && signal.bias.includes('SHORT');
        
        if (isBuy) {
            marker.innerHTML = '🔵 BUY';
            marker.style.cssText = `
                position: absolute;
                background: rgba(0, 255, 0, 0.9);
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                bottom: 20px;
                right: 20px;
                z-index: 1001;
                animation: pulse 2s infinite;
            `;
        } else if (isSell) {
            marker.innerHTML = '🔴 SELL';
            marker.style.cssText = `
                position: absolute;
                background: rgba(255, 0, 0, 0.9);
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                top: 20px;
                right: 20px;
                z-index: 1001;
                animation: pulse 2s infinite;
            `;
        } else {
            marker.innerHTML = '⚪ WAIT';
            marker.style.cssText = `
                position: absolute;
                background: rgba(128, 128, 128, 0.9);
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                top: 50%;
                right: 20px;
                z-index: 1001;
            `;
        }
        
        // Add pulse animation
        if (!document.getElementById('ai-pulse-style')) {
            const style = document.createElement('style');
            style.id = 'ai-pulse-style';
            style.textContent = `
                @keyframes pulse {
                    0% { opacity: 1; transform: scale(1); }
                    50% { opacity: 0.7; transform: scale(1.1); }
                    100% { opacity: 1; transform: scale(1); }
                }
            `;
            document.head.appendChild(style);
        }
        
        // Remove old markers
        const oldMarkers = this.signalContainer.querySelectorAll('.ai-signal-marker');
        oldMarkers.forEach(m => m.remove());
        
        // Add new marker
        this.signalContainer.appendChild(marker);
        
        // Auto-remove after 30 seconds
        setTimeout(() => {
            if (marker.parentNode) {
                marker.remove();
            }
        }, 30000);
    }
    
    markSweepLevels(sessionHigh, sessionLow) {
        // Create horizontal lines for sweep levels
        const highLine = document.createElement('div');
        highLine.className = 'sweep-level-high';
        highLine.style.cssText = `
            position: absolute;
            top: 10%;
            left: 0;
            right: 0;
            height: 2px;
            background: rgba(255, 255, 0, 0.8);
            z-index: 999;
        `;
        
        const lowLine = document.createElement('div');
        lowLine.className = 'sweep-level-low';
        lowLine.style.cssText = `
            position: absolute;
            bottom: 10%;
            left: 0;
            right: 0;
            height: 2px;
            background: rgba(255, 255, 0, 0.8);
            z-index: 999;
        `;
        
        // Remove old levels
        const oldLevels = this.signalContainer.querySelectorAll('.sweep-level-high, .sweep-level-low');
        oldLevels.forEach(l => l.remove());
        
        // Add new levels
        this.signalContainer.appendChild(highLine);
        this.signalContainer.appendChild(lowLine);
    }
    
    async startUpdates() {
        const update = async () => {
            const analysis = await this.getAIAnalysis();
            if (analysis) {
                this.markSignalOnChart(analysis);
                
                // Mark sweep levels if available
                if (analysis.sessionHigh && analysis.sessionLow) {
                    this.markSweepLevels(analysis.sessionHigh, analysis.sessionLow);
                }
            }
        };
        
        // Initial update
        await update();
        
        // Regular updates
        setInterval(update, this.updateInterval);
    }
}

// Initialize when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new AIChartOverlay();
    });
} else {
    new AIChartOverlay();
}

console.log('🚀 AI Chart Overlay script loaded');