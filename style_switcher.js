// Style switching functionality for trading dashboard
class StyleSwitcher {
    constructor() {
        this.currentStyle = localStorage.getItem('dashboardStyle') || 'default';
        this.init();
    }
    
    init() {
        // Apply saved style on page load
        if (this.currentStyle !== 'default') {
            this.applyStyle(this.currentStyle);
        }
        
        // Listen for style changes from other pages
        window.addEventListener('storage', (e) => {
            if (e.key === 'dashboardStyle') {
                this.applyStyle(e.newValue);
            }
        });
    }
    
    applyStyle(style) {
        // Remove existing style sheets
        this.removeExistingStyles();
        
        // Apply new style
        switch(style) {
            case 'terminal':
                this.applyTerminalStyle();
                break;
            case 'dark':
                this.applyDarkStyle();
                break;
            case 'bsod':
                this.applyBSODStyle();
                break;
            case 'nighthawk':
                this.applyNightHawkStyle();
                break;
            case 'emerald':
                this.applyEmeraldStyle();
                break;
            case 'amber':
                this.applyAmberStyle();
                break;
            default:
                // Keep original styles
                break;
        }
        
        this.currentStyle = style;
    }
    
    removeExistingStyles() {
        const existingStyles = document.querySelectorAll('#terminal-style, #dark-style, #bsod-style, #nighthawk-style, #emerald-style, #amber-style');
        existingStyles.forEach(style => style.remove());
        
        document.body.classList.remove('style-terminal', 'style-dark', 'style-bsod', 'style-nighthawk', 'style-emerald', 'style-amber');
    }
    
    applyTerminalStyle() {
        document.body.classList.add('style-terminal');
        
        const style = document.createElement('style');
        style.id = 'terminal-style';
        style.textContent = `
            body.style-terminal {
                background: #001100 !important;
                color: #00FF41 !important;
                font-family: 'Courier New', monospace !important;
            }
            .style-terminal .navbar,
            .style-terminal .header,
            .style-terminal .controls,
            .style-terminal .metric-card,
            .style-terminal .chart-container,
            .style-terminal .metric-section {
                background: rgba(0,255,65,0.1) !important;
                border: 1px solid #00FF41 !important;
                color: #00FF41 !important;
            }
            .style-terminal .btn {
                background: #00FF41 !important;
                color: #001100 !important;
            }
            .style-terminal .metric-value {
                color: #00FF41 !important;
                text-shadow: 0 0 10px #00FF41 !important;
            }
            .style-terminal .positive { color: #00FF41 !important; }
            .style-terminal .negative { color: #FF4444 !important; }
            .style-terminal .neutral { color: #FFFF00 !important; }
        `;
        document.head.appendChild(style);
    }
    
    applyDarkStyle() {
        document.body.classList.add('style-dark');
        
        const style = document.createElement('style');
        style.id = 'dark-style';
        style.textContent = `
            body.style-dark {
                background: #0a0a0a !important;
                color: #ffffff !important;
            }
            .style-dark .navbar,
            .style-dark .header,
            .style-dark .controls,
            .style-dark .metric-card,
            .style-dark .chart-container,
            .style-dark .metric-section {
                background: #111 !important;
                border: 1px solid #333 !important;
                color: #fff !important;
            }
            .style-dark .btn {
                background: #fff !important;
                color: #000 !important;
            }
            .style-dark .metric-value {
                color: #fff !important;
            }
            .style-dark .positive { color: #fff !important; }
            .style-dark .negative { color: #888 !important; }
            .style-dark .neutral { color: #ccc !important; }
        `;
        document.head.appendChild(style);
    }
    
    applyBSODStyle() {
        document.body.classList.add('style-bsod');
        
        const style = document.createElement('style');
        style.id = 'bsod-style';
        style.textContent = `
            body.style-bsod {
                background: #0000AA !important;
                color: #FFFFFF !important;
                font-family: 'Courier New', monospace !important;
            }
            .style-bsod .navbar,
            .style-bsod .header,
            .style-bsod .controls,
            .style-bsod .metric-card,
            .style-bsod .chart-container,
            .style-bsod .metric-section {
                background: rgba(255,255,255,0.1) !important;
                border: 1px solid #FFFFFF !important;
                color: #FFFFFF !important;
            }
            .style-bsod .btn {
                background: #FFFFFF !important;
                color: #0000AA !important;
            }
            .style-bsod .metric-value {
                color: #FFFFFF !important;
            }
            .style-bsod .positive { color: #FFFFFF !important; }
            .style-bsod .negative { color: #FFFFFF !important; }
            .style-bsod .neutral { color: #FFFFFF !important; }
        `;
        document.head.appendChild(style);
    }
    
    applyNightHawkStyle() {
        document.body.classList.add('style-nighthawk');
        
        const style = document.createElement('style');
        style.id = 'nighthawk-style';
        style.textContent = `
            @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono:wght@400&display=swap');
            
            body.style-nighthawk {
                background: #000F14 !important;
                color: #00B4D8 !important;
                font-family: 'Share Tech Mono', monospace !important;
                animation: scanlines 0.1s linear infinite;
            }
            
            body.style-nighthawk::before {
                content: '';
                position: fixed;
                top: 0; left: 0; right: 0; bottom: 0;
                background: linear-gradient(transparent 50%, rgba(0, 180, 216, 0.03) 50%);
                background-size: 100% 2px;
                pointer-events: none;
                z-index: 1000;
            }
            
            .style-nighthawk .navbar,
            .style-nighthawk .header,
            .style-nighthawk .controls,
            .style-nighthawk .metric-card,
            .style-nighthawk .chart-container,
            .style-nighthawk .metric-section {
                background: #002836 !important;
                border: 2px solid #00B4D8 !important;
                color: #00B4D8 !important;
                text-shadow: 0 0 5px #00B4D8;
            }
            
            .style-nighthawk .btn {
                background: #00B4D8 !important;
                color: #000F14 !important;
                clip-path: polygon(0 0, calc(100% - 10px) 0, 100% 10px, 100% 100%, 10px 100%, 0 calc(100% - 10px));
            }
            
            .style-nighthawk .metric-value {
                color: #90E0EF !important;
                text-shadow: 0 0 10px #00B4D8 !important;
            }
        `;
        document.head.appendChild(style);
    }
    
    applyEmeraldStyle() {
        document.body.classList.add('style-emerald');
        
        const style = document.createElement('style');
        style.id = 'emerald-style';
        style.textContent = `
            @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');
            
            body.style-emerald {
                background: #002200 !important;
                color: #00FF00 !important;
                font-family: 'VT323', monospace !important;
                font-size: 16px !important;
            }
            
            body.style-emerald::before {
                content: '';
                position: fixed;
                top: 0; left: 0; right: 0; bottom: 0;
                background: radial-gradient(ellipse at center, rgba(0, 255, 0, 0.1) 0%, transparent 70%);
                pointer-events: none;
                z-index: 1000;
            }
            
            .style-emerald .navbar,
            .style-emerald .header,
            .style-emerald .controls,
            .style-emerald .metric-card,
            .style-emerald .chart-container,
            .style-emerald .metric-section {
                background: #005500 !important;
                border: double 4px #00FF00 !important;
                color: #00FF00 !important;
            }
            
            .style-emerald .btn {
                background: #00FF00 !important;
                color: #002200 !important;
            }
            
            .style-emerald .metric-value {
                color: #99FF99 !important;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.3; }
            }
        `;
        document.head.appendChild(style);
    }
    
    applyAmberStyle() {
        document.body.classList.add('style-amber');
        
        const style = document.createElement('style');
        style.id = 'amber-style';
        style.textContent = `
            @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono:wght@400&display=swap');
            
            body.style-amber {
                background: #2A1400 !important;
                color: #FFB000 !important;
                font-family: 'Share Tech Mono', monospace !important;
            }
            
            body.style-amber::before {
                content: '';
                position: fixed;
                top: 0; left: 0; right: 0; bottom: 0;
                background: 
                    linear-gradient(transparent 98%, rgba(255, 176, 0, 0.1) 100%),
                    linear-gradient(90deg, transparent 98%, rgba(255, 176, 0, 0.05) 100%);
                background-size: 100% 3px, 3px 100%;
                pointer-events: none;
                z-index: 1000;
                animation: scanlines 0.1s linear infinite;
            }
            
            .style-amber .navbar,
            .style-amber .header,
            .style-amber .controls,
            .style-amber .metric-card,
            .style-amber .chart-container,
            .style-amber .metric-section {
                background: #804000 !important;
                border: 2px solid #FFB000 !important;
                color: #FFB000 !important;
                clip-path: polygon(0 0, calc(100% - 10px) 0, 100% 10px, 100% 100%, 10px 100%, 0 calc(100% - 10px));
            }
            
            .style-amber .btn {
                background: #FFB000 !important;
                color: #2A1400 !important;
                clip-path: polygon(5px 0, 100% 0, calc(100% - 5px) 100%, 0 100%);
            }
            
            .style-amber .metric-value {
                color: #FFD700 !important;
                text-shadow: 0 0 8px #FFB000 !important;
            }
            
            @keyframes scanlines {
                0% { opacity: 1; }
                50% { opacity: 0.8; }
                100% { opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }
}

// Initialize style switcher when DOM loads
document.addEventListener('DOMContentLoaded', () => {
    window.styleSwitcher = new StyleSwitcher();
});