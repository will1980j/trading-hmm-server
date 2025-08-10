// Add TradingView sync button to trade manager

function addTradingViewSync() {
    const syncButton = document.createElement('button');
    syncButton.className = 'btn';
    syncButton.textContent = 'Sync TradingView';
    syncButton.style.background = '#2196F3';
    syncButton.onclick = syncTradingViewTrades;
    
    // Add to button row
    const buttonRow = document.querySelector('.data-input div[style*="margin-top: 15px"]');
    buttonRow.appendChild(syncButton);
}

async function syncTradingViewTrades() {
    try {
        const response = await fetch('/api/sync-broker-trades');
        const result = await response.json();
        
        if (result.status === 'success') {
            alert(`Synced ${result.trades_synced} trades from TradingView`);
            loadTrades(); // Reload trades
        } else {
            alert('Sync failed: ' + result.error);
        }
    } catch (error) {
        console.error('Sync error:', error);
        alert('Sync failed. Check console for details.');
    }
}

// Auto-sync every 5 minutes
setInterval(async () => {
    try {
        await fetch('/api/sync-broker-trades');
        console.log('Auto-sync completed');
    } catch (error) {
        console.log('Auto-sync failed:', error);
    }
}, 5 * 60 * 1000);

// Add sync button when page loads
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(addTradingViewSync, 1000);
});