// Inject script to bypass CORS
(function() {
    const script = document.createElement('script');
    script.textContent = `
        window.aiAnalysis = async function(chartData) {
            try {
                const response = await fetch('http://127.0.0.1:5000/api/ai-chart-analysis?' + new URLSearchParams({
                    symbol: chartData.symbol,
                    price: chartData.price,
                    session: chartData.session,
                    timestamp: chartData.timestamp
                }));
                const data = await response.json();
                window.postMessage({type: 'AI_RESULT', data: data}, '*');
            } catch (error) {
                window.postMessage({type: 'AI_ERROR', error: error.message}, '*');
            }
        };
    `;
    document.documentElement.appendChild(script);
    script.remove();
})();