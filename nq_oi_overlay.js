// NQ Options Open Interest Overlay for Signal Lab Dashboard

async function loadNQOptionsData() {
    try {
        const response = await fetch('https://web-production-cd33.up.railway.app/nq/levels/daily');
        if (response.ok) {
            const data = await response.json();
            
            // Update status
            document.getElementById('oiStatus').textContent = `DTE ${data.nearest_dte}`;
            document.getElementById('oiStatus').style.background = 'rgba(0,255,136,0.3)';
            
            // Display put levels (support)
            let putHtml = '';
            data.top_puts.forEach((put, i) => {
                putHtml += `
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 6px 8px; background: rgba(0,255,136,0.1); border-radius: 6px;">
                        <span style="font-weight: 600; color: #00ff88;">${put.strike}</span>
                        <span style="font-size: 11px; color: rgba(255,255,255,0.8);">${put.oi.toLocaleString()} OI</span>
                    </div>
                `;
            });
            document.getElementById('putLevels').innerHTML = putHtml;
            
            // Display call levels (resistance)
            let callHtml = '';
            data.top_calls.forEach((call, i) => {
                callHtml += `
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 6px 8px; background: rgba(255,165,2,0.1); border-radius: 6px;">
                        <span style="font-weight: 600; color: #ffa502;">${call.strike}</span>
                        <span style="font-size: 11px; color: rgba(255,255,255,0.8);">${call.oi.toLocaleString()} OI</span>
                    </div>
                `;
            });
            document.getElementById('callLevels').innerHTML = callHtml;
            
            // Pin candidate
            document.getElementById('pinCandidate').textContent = data.pin_candidate || 'None';
            document.getElementById('pinDte').textContent = `DTE ${data.nearest_dte}`;
            
            // Pine Script input
            const puts = data.top_puts.map(p => p.strike).slice(0, 3);
            const calls = data.top_calls.map(c => c.strike).slice(0, 3);
            const pineInput = `put1=${puts[0]||0}; put2=${puts[1]||0}; put3=${puts[2]||0}; call1=${calls[0]||0}; call2=${calls[1]||0}; call3=${calls[2]||0}; pin=${data.pin_candidate||0}`;
            document.getElementById('pineScriptInput').textContent = pineInput;
            window.currentPineScript = pineInput;
            
        } else {
            throw new Error('NQ OI API unavailable');
        }
    } catch (error) {
        console.error('Error loading NQ OI data:', error);
        document.getElementById('oiStatus').textContent = 'Offline';
        document.getElementById('oiStatus').style.background = 'rgba(255,71,87,0.3)';
        document.getElementById('putLevels').innerHTML = '<div style="text-align: center; color: rgba(255,255,255,0.7);">OI data offline</div>';
        document.getElementById('callLevels').innerHTML = '<div style="text-align: center; color: rgba(255,255,255,0.7);">OI data offline</div>';
        document.getElementById('pinCandidate').textContent = '-';
        document.getElementById('pinDte').textContent = 'Offline';
        document.getElementById('pineScriptInput').textContent = 'OI data unavailable';
    }
}

function copyPineScript() {
    if (window.currentPineScript) {
        navigator.clipboard.writeText(window.currentPineScript).then(() => {
            const btn = event.target;
            const originalText = btn.textContent;
            btn.textContent = 'Copied!';
            btn.style.background = '#00ff88';
            setTimeout(() => {
                btn.textContent = originalText;
                btn.style.background = '#3742fa';
            }, 2000);
        });
    }
}