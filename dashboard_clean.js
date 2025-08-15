// Clean consolidated JavaScript for dashboard
(() => {
    // Chat functionality
    const $ = (id) => document.getElementById(id);
    
    function openChat() {
        const container = $('chatContainer');
        if (container) {
            container.style.display = 'flex';
            setTimeout(() => {
                const input = $('chatInput');
                if (input) {
                    input.disabled = false;
                    input.removeAttribute('readonly');
                    input.focus();
                }
            }, 30);
        }
    }
    
    function closeChat() {
        const container = $('chatContainer');
        if (container) container.style.display = 'none';
    }
    
    // Wire up chat events
    const toggle = $('chatToggle');
    const closeBtn = $('chatClose');
    if (toggle) toggle.addEventListener('click', openChat);
    if (closeBtn) closeBtn.addEventListener('click', closeChat);
    
    // Keyboard shortcut
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.shiftKey && (e.key === 'A' || e.key === 'a')) {
            e.preventDefault();
            openChat();
        }
    });
    
    // Time and market status updates
    function updateCurrentTime() {
        const now = new Date();
        const timeString = now.toLocaleString('en-US', {
            weekday: 'short',
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            timeZoneName: 'short'
        });
        
        const currentTimeEl = $('currentDateTime');
        if (currentTimeEl) {
            currentTimeEl.textContent = timeString;
        }
    }
    
    function updateMarketStatus() {
        const now = new Date();
        const hour = now.getHours();
        const day = now.getDay();
        
        const marketStatusEl = $('marketStatus');
        if (!marketStatusEl) return;
        
        let statusHtml = '';
        const sessions = [
            { name: 'ASIA', start: 18, end: 3, status: 'closed' },
            { name: 'LONDON', start: 3, end: 12, status: 'closed' },
            { name: 'NY', start: 9, end: 16, status: 'closed' }
        ];
        
        if (day === 0 || day === 6) {
            statusHtml = '<div class="market-widget"><div class="market-name">MARKETS</div><div class="market-status market-closed">WEEKEND</div></div>';
        } else {
            sessions.forEach(session => {
                let isOpen = false;
                if (session.start < session.end) {
                    isOpen = hour >= session.start && hour < session.end;
                } else {
                    isOpen = hour >= session.start || hour < session.end;
                }
                
                const statusClass = isOpen ? 'market-open' : 'market-closed';
                const statusText = isOpen ? 'OPEN' : 'CLOSED';
                
                statusHtml += `<div class="market-widget ${isOpen ? 'open' : ''}">
                    <div class="market-name">${session.name}</div>
                    <div class="market-status ${statusClass}">${statusText}</div>
                </div>`;
            });
        }
        
        marketStatusEl.innerHTML = statusHtml;
    }
    
    // Initialize on page load
    document.addEventListener('DOMContentLoaded', () => {
        console.log('DOM loaded, initializing dashboard...');
        if (typeof loadFilterStates === 'function') loadFilterStates();
        if (typeof loadStyle === 'function') loadStyle();
        if (typeof loadDatabaseData === 'function') loadDatabaseData();
        
        updateCurrentTime();
        updateMarketStatus();
        setInterval(updateCurrentTime, 1000);
        setInterval(updateMarketStatus, 60000);
    });
})();