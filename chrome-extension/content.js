// AI Trading Assistant - Content Script
let aiOverlay = null;
let analysisInterval = null;
let lastAnalysis = null;

// Initialize when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeExtension);
} else {
    initializeExtension();
}

function initializeExtension() {
    console.log('AI Trading Assistant initialized');
    createAIOverlay();
    startAnalysis();
}

function createAIOverlay() {
    if (aiOverlay) return;
    
    aiOverlay = document.createElement('div');
    aiOverlay.id = 'ai-trading-overlay';
    aiOverlay.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        width: 200px;
        background: rgba(0, 0, 0, 0.9);
        border: 2px solid #00ff00;
        border-radius: 8px;
        color: white;
        font-family: monospace;
        font-size: 12px;
        z-index: 10000;
        padding: 10px;
    `;
    aiOverlay.innerHTML = `
        <div class="ai-panel">
            <div class="ai-header" style="color: #00ff00; font-weight: bold; margin-bottom: 8px;">AI Assistant</div>
            <div class="ai-status" style="margin-bottom: 8px;">Analyzing...</div>
            <div class="ai-signals"></div>
        </div>
    `;
    document.body.appendChild(aiOverlay);
}

function startAnalysis() {
    console.log('Starting analysis interval...');
    // Analyze every 10 seconds
    analysisInterval = setInterval(() => {
        console.log('Analysis interval triggered');
        const chartData = extractChartData();
        console.log('Chart data extracted:', chartData);
        if (chartData) {
            console.log('Sending chart data for analysis');
            analyzeChart(chartData);
        } else {
            console.log('No chart data available');
        }
    }, 10000);
    
    // Also try immediate analysis
    setTimeout(() => {
        console.log('Immediate analysis attempt');
        const chartData = extractChartData();
        if (chartData) {
            analyzeChart(chartData);
        }
    }, 3000);
}

function extractChartData() {
    try {
        const symbol = getSymbol();
        const currentPrice = getCurrentPrice();
        
        console.log('Symbol found:', symbol);
        console.log('Price found:', currentPrice);
        
        // Always return data even if price extraction fails
        return {
            symbol: symbol || 'NQ1!',
            price: currentPrice || 15000, // Default price if extraction fails
            timestamp: Date.now(),
            session: getCurrentSession()
        };
    } catch (error) {
        console.log('Chart data extraction failed:', error);
        // Return default data to keep analysis working
        return {
            symbol: 'NQ1!',
            price: 15000,
            timestamp: Date.now(),
            session: getCurrentSession()
        };
    }
}

function getCurrentPrice() {
    try {
        // Multiple strategies to find current price
        const selectors = [
            '[data-name="legend-source-item"]',
            '[class*="price"]',
            '[class*="last"]',
            '.js-symbol-last',
            '[data-field="last_price"]'
        ];
        
        for (const selector of selectors) {
            const elements = document.querySelectorAll(selector);
            for (const element of elements) {
                const text = element.textContent || element.innerText || '';
                // Look for numbers that could be NQ price (typically 15000-20000)
                const matches = text.match(/\b(1[5-9]\d{3}|2[0-5]\d{3})(?:\.\d+)?\b/g);
                if (matches) {
                    const price = parseFloat(matches[0]);
                    if (price >= 15000 && price <= 25000) {
                        console.log('Price found:', price, 'from element:', text);
                        return price;
                    }
                }
            }
        }
        
        // Fallback: look for any reasonable price in page text
        const bodyText = document.body.innerText;
        const priceMatches = bodyText.match(/\b(1[5-9]\d{3}|2[0-5]\d{3})(?:\.\d+)?\b/g);
        if (priceMatches) {
            const price = parseFloat(priceMatches[0]);
            console.log('Fallback price found:', price);
            return price;
        }
        
        return null;
    } catch (error) {
        console.log('Price extraction error:', error);
        return null;
    }
}

function getSymbol() {
    try {
        // Extract symbol from URL or page elements
        const urlMatch = window.location.href.match(/symbol=([^&]+)/);
        if (urlMatch) return urlMatch[1];
        
        const titleElement = document.querySelector('title');
        if (titleElement) {
            const titleMatch = titleElement.textContent.match(/^([A-Z0-9]+)/);
            if (titleMatch) return titleMatch[1];
        }
        
        return 'NQ1!'; // Default to NQ
    } catch (error) {
        return 'NQ1!';
    }
}

function getCurrentSession() {
    const now = new Date();
    const hour = now.getUTCHours();
    console.log('Current UTC hour:', hour);
    
    if (hour >= 0 && hour < 8) {
        console.log('Session: ASIA');
        return 'ASIA';
    }
    if (hour >= 8 && hour < 13) {
        console.log('Session: LONDON');
        return 'LONDON';
    }
    if (hour >= 13 && hour < 17) {
        console.log('Session: NEW YORK AM');
        return 'NEW YORK AM';
    }
    if (hour >= 17 && hour < 21) {
        console.log('Session: NEW YORK PM');
        return 'NEW YORK PM';
    }
    console.log('Session: ASIA (default)');
    return 'ASIA';
}

async function analyzeChart(chartData) {
    try {
        const response = await chrome.runtime.sendMessage({
            action: 'fetchData',
            url: `http://127.0.0.1:8080/api/ai-chart-analysis?symbol=${chartData.symbol}&price=${chartData.price}&session=${chartData.session}`
        });
        
        if (response.success) {
            updateOverlay(response.data);
        } else {
            throw new Error(response.error);
        }
    } catch (error) {
        console.log('Analysis failed:', error);
        const analysis = {
            session: chartData.session,
            fvgQuality: 0.3,
            entryConfidence: 0.2,
            marketCondition: 'OFFLINE',
            recommendation: 'WAIT'
        };
        updateOverlay(analysis);
    }
}



function updateOverlay(analysis) {
    if (!aiOverlay) return;
    
    const statusElement = aiOverlay.querySelector('.ai-status');
    const signalsElement = aiOverlay.querySelector('.ai-signals');
    
    // Always show analysis, ignore errors
    console.log('Updating overlay with analysis:', analysis);
    
    const session = analysis.session || 'UNKNOWN';
    statusElement.textContent = `${session} Session`;
    statusElement.className = 'ai-status active';
    
    let signalsHtml = '';
    
    const fvgQuality = analysis.fvgQuality || 0.5;
    const quality = fvgQuality > 0.7 ? 'HIGH' : fvgQuality > 0.4 ? 'MED' : 'LOW';
    const color = fvgQuality > 0.7 ? '#00ff00' : fvgQuality > 0.4 ? '#ffff00' : '#ff0000';
    signalsHtml += `<div style="color: ${color}; margin: 2px 0;">FVG: ${quality}</div>`;
    
    const entryConfidence = analysis.entryConfidence || 0.3;
    const confidence = Math.round(entryConfidence * 100);
    const confColor = confidence > 70 ? '#00ff00' : confidence > 40 ? '#ffff00' : '#ff0000';
    signalsHtml += `<div style="color: ${confColor}; margin: 2px 0;">Entry: ${confidence}%</div>`;
    
    const marketCondition = analysis.marketCondition || 'ANALYZING';
    signalsHtml += `<div style="color: #00aaff; margin: 2px 0;">Market: ${marketCondition}</div>`;
    
    const bias = analysis.bias || 'NEUTRAL';
    const recommendation = analysis.recommendation || 'WAIT';
    
    const biasColor = bias.includes('LONG') ? '#00ff00' : bias.includes('SHORT') ? '#ff0000' : '#ffff00';
    signalsHtml += `<div style="color: ${biasColor}; margin: 2px 0; font-weight: bold;">${bias}</div>`;
    signalsHtml += `<div style="color: #ffff00; margin: 2px 0;">Action: ${recommendation}</div>`;
    
    signalsElement.innerHTML = signalsHtml;
    lastAnalysis = analysis;
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (analysisInterval) {
        clearInterval(analysisInterval);
    }
});