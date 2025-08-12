// Indicator Reader - Inject into TradingView to read FVG Scanner
class IndicatorReader {
    constructor() {
        this.bias = 'Unknown';
        this.lastUpdate = 0;
        this.init();
    }
    
    init() {
        console.log('🔍 Indicator Reader initialized');
        this.startReading();
    }
    
    startReading() {
        // Read indicator every 2 seconds
        setInterval(() => {
            this.readFVGIndicator();
        }, 2000);
        
        // Initial read
        this.readFVGIndicator();
    }
    
    readFVGIndicator() {
        try {
            // Search all text elements for your specific indicator patterns
            const allElements = document.querySelectorAll('*');
            
            for (const element of allElements) {
                const text = (element.textContent || '').trim();
                
                // Log elements that contain "Scanner" for debugging
                if (text.includes('Scanner')) {
                    console.log('🔍 Found Scanner element:', text);
                }
                
                // Look for your exact patterns from the chart
                // "Scanner [1H ]: BULLISH" or "Scanner [1H ]: BEARISH"
                if (text.includes('Scanner') && text.includes('[1H')) {
                    console.log('📊 Found 1H Scanner:', text);
                    
                    if (text.toUpperCase().includes('BULLISH')) {
                        this.updateBias('Bullish', text);
                        return;
                    } else if (text.toUpperCase().includes('BEARISH')) {
                        this.updateBias('Bearish', text);
                        return;
                    }
                }
                
                // Also look for simpler patterns
                if (text.includes('1H') && (text.includes('BULLISH') || text.includes('BEARISH'))) {
                    console.log('📈 Found 1H bias:', text);
                    
                    if (text.toUpperCase().includes('BULLISH')) {
                        this.updateBias('Bullish', text);
                        return;
                    } else if (text.toUpperCase().includes('BEARISH')) {
                        this.updateBias('Bearish', text);
                        return;
                    }
                }
                
                // Look in bottom area of screen
                const rect = element.getBoundingClientRect();
                if (rect.top > window.innerHeight * 0.8) { // Bottom 20%
                    if (text.toUpperCase().includes('BEARISH')) {
                        console.log('📉 Found BEARISH in bottom area:', text);
                        this.updateBias('Bearish', text);
                        return;
                    } else if (text.toUpperCase().includes('BULLISH')) {
                        console.log('📈 Found BULLISH in bottom area:', text);
                        this.updateBias('Bullish', text);
                        return;
                    }
                }
            }
            
            // Debug: Log some elements from bottom of screen
            const bottomElements = Array.from(allElements).filter(el => {
                const rect = el.getBoundingClientRect();
                return rect.top > window.innerHeight * 0.8 && el.textContent.trim().length > 0;
            }).slice(0, 10);
            
            console.log('🔍 Bottom screen elements:', bottomElements.map(el => el.textContent.trim()));
            console.log('⚠️ No FVG bias found in DOM');
            
        } catch (error) {
            console.error('❌ Error reading indicator:', error);
        }
    }
    
    updateBias(newBias, sourceText) {
        if (this.bias !== newBias) {
            console.log(`🔄 Bias changed: ${this.bias} → ${newBias}`);
            console.log(`📊 Source: ${sourceText}`);
            this.bias = newBias;
            this.lastUpdate = Date.now();
            
            // Send to server
            this.sendBiasToServer(newBias, sourceText);
        }
    }
    
    async sendBiasToServer(bias, source) {
        try {
            console.log(`🚀 Attempting to send bias: ${bias}`);
            
            const response = await fetch('http://127.0.0.1:8080/api/update-bias', {
                method: 'POST',
                mode: 'cors',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    bias: bias,
                    source: source,
                    timestamp: Date.now()
                })
            });
            
            console.log(`📡 Response status: ${response.status}`);
            
            if (response.ok) {
                console.log(`✅ Sent bias to server: ${bias}`);
            } else {
                console.error(`❌ Server responded with: ${response.status}`);
            }
        } catch (error) {
            console.error('❌ Failed to send bias to server:', error);
        }
    }
    
    getBias() {
        return {
            bias: this.bias,
            lastUpdate: this.lastUpdate,
            age: Date.now() - this.lastUpdate
        };
    }
}

// Initialize the reader
window.indicatorReader = new IndicatorReader();

// Expose function to get current bias
window.getCurrentBias = () => window.indicatorReader.getBias();

console.log('🚀 FVG Indicator Reader loaded');