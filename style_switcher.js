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
            default:
                // Keep original styles
                break;
        }
        
        this.currentStyle = style;
    }
    
    removeExistingStyles() {
        const existingStyles = document.querySelectorAll('#terminal-style, #dark-style, #bsod-style');
        existingStyles.forEach(style => style.remove());
        
        document.body.classList.remove('style-terminal', 'style-dark', 'style-bsod');
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
}

// Initialize style switcher when DOM loads
document.addEventListener('DOMContentLoaded', () => {
    window.styleSwitcher = new StyleSwitcher();
});