// AI Trading Assistant - Popup Script
document.addEventListener('DOMContentLoaded', function() {
    checkServerStatus();
    checkTradingViewStatus();
    loadSettings();
    
    // Save settings when changed
    document.getElementById('enableAnalysis').addEventListener('change', saveSettings);
    document.getElementById('analysisInterval').addEventListener('change', saveSettings);
    document.getElementById('serverUrl').addEventListener('change', saveSettings);
});

async function checkServerStatus() {
    const statusElement = document.getElementById('serverStatus');
    const serverUrl = document.getElementById('serverUrl').value;
    
    try {
        const response = await fetch(`${serverUrl}/api/health`, {
            method: 'GET',
            timeout: 5000
        });
        
        if (response.ok) {
            statusElement.textContent = 'Connected';
            statusElement.className = 'status-value connected';
        } else {
            statusElement.textContent = 'Error';
            statusElement.className = 'status-value disconnected';
        }
    } catch (error) {
        statusElement.textContent = 'Offline';
        statusElement.className = 'status-value disconnected';
    }
}

function checkTradingViewStatus() {
    const statusElement = document.getElementById('tvStatus');
    
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        if (tabs[0] && tabs[0].url.includes('tradingview.com')) {
            statusElement.textContent = 'Active';
            statusElement.className = 'status-value connected';
        } else {
            statusElement.textContent = 'Not Active';
            statusElement.className = 'status-value disconnected';
        }
    });
}

function loadSettings() {
    chrome.storage.sync.get({
        enableAnalysis: true,
        analysisInterval: 10,
        serverUrl: 'http://localhost:5000'
    }, function(items) {
        document.getElementById('enableAnalysis').checked = items.enableAnalysis;
        document.getElementById('analysisInterval').value = items.analysisInterval;
        document.getElementById('serverUrl').value = items.serverUrl;
    });
}

function saveSettings() {
    const settings = {
        enableAnalysis: document.getElementById('enableAnalysis').checked,
        analysisInterval: parseInt(document.getElementById('analysisInterval').value),
        serverUrl: document.getElementById('serverUrl').value
    };
    
    chrome.storage.sync.set(settings, function() {
        console.log('Settings saved');
        
        // Notify content script of settings change
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            if (tabs[0]) {
                chrome.tabs.sendMessage(tabs[0].id, {
                    type: 'SETTINGS_UPDATED',
                    settings: settings
                });
            }
        });
    });
}