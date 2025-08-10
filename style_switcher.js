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
            case 'cyber':
                this.applyCyberStyle();
                break;
            default:
                // Keep original styles
                break;
        }
        
        this.currentStyle = style;
    }
    
    removeExistingStyles() {
        const existingStyles = document.querySelectorAll('#terminal-style, #dark-style, #bsod-style, #nighthawk-style, #emerald-style, #amber-style, #cyber-style');
        existingStyles.forEach(style => style.remove());
        
        document.body.classList.remove('style-terminal', 'style-dark', 'style-bsod', 'style-nighthawk', 'style-emerald', 'style-amber', 'style-cyber');
    }
    
    applyTerminalStyle() {
        document.body.classList.add('style-terminal');
        
        const style = document.createElement('style');
        style.id = 'terminal-style';
        style.textContent = `
            @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');
            
            body.style-terminal {
                background: #001100 !important;
                color: #00FF41 !important;
                font-family: 'VT323', monospace !important;
                font-size: 16px !important;
            }
            
            .style-terminal *,
            .style-terminal .navbar,
            .style-terminal .header,
            .style-terminal .controls,
            .style-terminal .metric-card,
            .style-terminal .chart-container,
            .style-terminal .metric-section,
            .style-terminal .card,
            .style-terminal .panel,
            .style-terminal .widget,
            .style-terminal div,
            .style-terminal span,
            .style-terminal p,
            .style-terminal h1,
            .style-terminal h2,
            .style-terminal h3,
            .style-terminal canvas,
            .style-terminal svg {
                background: rgba(0,255,65,0.1) !important;
                border: 1px solid #00FF41 !important;
                color: #00FF41 !important;
                font-family: 'VT323', monospace !important;
                font-size: 16px !important;
            }
            
            .style-terminal .btn,
            .style-terminal button,
            .style-terminal input[type="button"],
            .style-terminal input[type="submit"] {
                background: #00FF41 !important;
                color: #001100 !important;
                border: 2px solid #00FF41 !important;
                font-family: 'VT323', monospace !important;
            }
            
            .style-terminal .metric-value,
            .style-terminal .price,
            .style-terminal .value,
            .style-terminal .number {
                color: #00FF41 !important;
                text-shadow: 0 0 10px #00FF41 !important;
                font-size: 20px !important;
                font-family: 'VT323', monospace !important;
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
            @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
            
            body.style-dark {
                background: #0a0a0a !important;
                color: #ffffff !important;
                font-family: 'Roboto Mono', monospace !important;
                font-size: 14px !important;
            }
            
            .style-dark *,
            .style-dark .navbar,
            .style-dark .header,
            .style-dark .controls,
            .style-dark .metric-card,
            .style-dark .chart-container,
            .style-dark .metric-section,
            .style-dark .card,
            .style-dark .panel,
            .style-dark .widget,
            .style-dark div,
            .style-dark span,
            .style-dark .p,
            .style-dark h1,
            .style-dark h2,
            .style-dark h3,
            .style-dark canvas,
            .style-dark svg {
                background: #111 !important;
                border: 1px solid #333 !important;
                color: #fff !important;
                font-family: 'Roboto Mono', monospace !important;
                font-size: 14px !important;
            }
            
            .style-dark .chart-container {
                background: linear-gradient(135deg, #111 0%, #0a0a0a 100%) !important;
                box-shadow: inset 0 0 20px rgba(255,255,255,0.1) !important;
            }
            
            .style-dark .btn,
            .style-dark button,
            .style-dark input[type="button"],
            .style-dark input[type="submit"] {
                background: #fff !important;
                color: #000 !important;
                border: 2px solid #666 !important;
                font-family: 'Roboto Mono', monospace !important;
                transition: all 0.3s ease !important;
            }
            
            .style-dark .metric-value,
            .style-dark .price,
            .style-dark .value,
            .style-dark .number {
                color: #fff !important;
                font-weight: 700 !important;
                font-size: 18px !important;
                font-family: 'Roboto Mono', monospace !important;
            }
            
            .style-dark .positive { color: #4CAF50 !important; }
            .style-dark .negative { color: #F44336 !important; }
            .style-dark .neutral { color: #FFC107 !important; }
        `;
        document.head.appendChild(style);
    }
    
    applyBSODStyle() {
        document.body.classList.add('style-bsod');
        
        const style = document.createElement('style');
        style.id = 'bsod-style';
        style.textContent = `
            @import url('https://fonts.googleapis.com/css2?family=Perfect+DOS+VGA+437&display=swap');
            
            body.style-bsod {
                background: #0000AA !important;
                color: #FFFFFF !important;
                font-family: 'Perfect DOS VGA 437', 'Courier New', monospace !important;
                font-size: 16px !important;
                cursor: default !important;
            }
            
            body.style-bsod::before {
                content: 'A problem has been detected and Windows has been shut down to prevent damage to your computer.';
                position: fixed;
                top: 20px;
                left: 20px;
                color: #FFFFFF;
                font-family: 'Perfect DOS VGA 437', 'Courier New', monospace;
                font-size: 14px;
                z-index: 1001;
            }
            
            .style-bsod *,
            .style-bsod .navbar,
            .style-bsod .header,
            .style-bsod .controls,
            .style-bsod .metric-card,
            .style-bsod .chart-container,
            .style-bsod .metric-section,
            .style-bsod .card,
            .style-bsod .panel,
            .style-bsod .widget,
            .style-bsod div,
            .style-bsod span,
            .style-bsod p,
            .style-bsod h1,
            .style-bsod h2,
            .style-bsod h3,
            .style-bsod canvas,
            .style-bsod svg {
                background: rgba(255,255,255,0.1) !important;
                border: 2px solid #FFFFFF !important;
                color: #FFFFFF !important;
                font-family: 'Perfect DOS VGA 437', 'Courier New', monospace !important;
                font-size: 16px !important;
            }
            
            .style-bsod .chart-container {
                background: #0000AA !important;
                position: relative !important;
            }
            
            .style-bsod .chart-container::after {
                content: 'SYSTEM_SERVICE_EXCEPTION';
                position: absolute;
                bottom: 10px;
                right: 10px;
                color: #FFFFFF;
                font-family: 'Perfect DOS VGA 437', 'Courier New', monospace;
                font-size: 12px;
                pointer-events: none;
            }
            
            .style-bsod .btn,
            .style-bsod button,
            .style-bsod input[type="button"],
            .style-bsod input[type="submit"] {
                background: #FFFFFF !important;
                color: #0000AA !important;
                border: 3px outset #CCCCCC !important;
                font-family: 'Perfect DOS VGA 437', 'Courier New', monospace !important;
            }
            
            .style-bsod .metric-value,
            .style-bsod .price,
            .style-bsod .value,
            .style-bsod .number {
                color: #FFFFFF !important;
                font-weight: bold !important;
                font-size: 20px !important;
                font-family: 'Perfect DOS VGA 437', 'Courier New', monospace !important;
                animation: blink 1s infinite !important;
            }
            
            .style-bsod .navbar {
                background: #0000AA !important;
                text-align: center !important;
                font-size: 18px !important;
            }
            
            @keyframes blink {
                0%, 50% { opacity: 1; }
                51%, 100% { opacity: 0.5; }
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
                background: #001122 !important;
                color: #66D9EF !important;
                font-family: 'Share Tech Mono', monospace !important;
                font-size: 14px !important;
            }
            
            body.style-nighthawk::before {
                content: '';
                position: fixed;
                top: 0; left: 0; right: 0; bottom: 0;
                background: linear-gradient(transparent 50%, rgba(102, 217, 239, 0.02) 50%);
                background-size: 100% 3px;
                pointer-events: none;
                z-index: 1000;
            }
            
            .style-nighthawk *,
            .style-nighthawk .navbar,
            .style-nighthawk .header,
            .style-nighthawk .controls,
            .style-nighthawk .metric-card,
            .style-nighthawk .chart-container,
            .style-nighthawk .metric-section,
            .style-nighthawk .card,
            .style-nighthawk .panel,
            .style-nighthawk .widget,
            .style-nighthawk div,
            .style-nighthawk span,
            .style-nighthawk p,
            .style-nighthawk h1,
            .style-nighthawk h2,
            .style-nighthawk h3,
            .style-nighthawk canvas,
            .style-nighthawk svg {
                background: #003344 !important;
                border: 1px solid #66D9EF !important;
                color: #FFFFFF !important;
                text-shadow: none !important;
                font-family: 'Share Tech Mono', monospace !important;
                font-size: 14px !important;
                font-weight: 500 !important;
            }
            
            .style-nighthawk .chart-container,
            .style-nighthawk canvas,
            .style-nighthawk svg {
                background: radial-gradient(ellipse at center, #003344 0%, #001122 100%) !important;
                transform: perspective(800px) rotateX(10deg) !important;
                position: relative !important;
            }
            
            .style-nighthawk .chart-container::after {
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0; bottom: 0;
                background-image: 
                    linear-gradient(rgba(102, 217, 239, 0.1) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(102, 217, 239, 0.1) 1px, transparent 1px);
                background-size: 25px 25px;
                pointer-events: none;
            }
            
            .style-nighthawk .btn,
            .style-nighthawk button,
            .style-nighthawk input[type="button"],
            .style-nighthawk input[type="submit"] {
                background: #66D9EF !important;
                color: #001122 !important;
                border: 2px solid #CCFFFF !important;
                clip-path: polygon(0 0, calc(100% - 8px) 0, 100% 8px, 100% 100%, 8px 100%, 0 calc(100% - 8px)) !important;
                text-shadow: none !important;
                font-family: 'Share Tech Mono', monospace !important;
                font-weight: bold !important;
            }
            
            .style-nighthawk .metric-value,
            .style-nighthawk .price,
            .style-nighthawk .value,
            .style-nighthawk .number {
                color: #FFFFFF !important;
                text-shadow: none !important;
                font-size: 20px !important;
                font-family: 'Share Tech Mono', monospace !important;
                font-weight: bold !important;
                background: rgba(102, 217, 239, 0.1) !important;
                padding: 2px 6px !important;
                border-radius: 4px !important;
            }
            
            .style-nighthawk .navbar {
                background: #003344 !important;
                border-bottom: 2px solid #66D9EF !important;
                padding: 8px 15px !important;
                color: #FFFFFF !important;
            }
            
            .style-nighthawk .pulse {
                animation: pulse 2s infinite !important;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
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
                line-height: 1.2 !important;
            }
            
            body.style-emerald::before {
                content: '';
                position: fixed;
                top: 0; left: 0; right: 0; bottom: 0;
                background: radial-gradient(ellipse at center, rgba(0, 255, 0, 0.1) 0%, transparent 70%);
                pointer-events: none;
                z-index: 1000;
            }
            
            .style-emerald *,
            .style-emerald .navbar,
            .style-emerald .header,
            .style-emerald .controls,
            .style-emerald .metric-card,
            .style-emerald .chart-container,
            .style-emerald .metric-section,
            .style-emerald .card,
            .style-emerald .panel,
            .style-emerald .widget,
            .style-emerald div,
            .style-emerald span,
            .style-emerald p,
            .style-emerald h1,
            .style-emerald h2,
            .style-emerald h3,
            .style-emerald canvas,
            .style-emerald svg {
                background: #005500 !important;
                border: double 4px #00FF00 !important;
                color: #00FF00 !important;
                font-family: 'VT323', monospace !important;
                font-size: 16px !important;
            }
            
            .style-emerald .chart-container {
                background: #002200 !important;
                position: relative !important;
            }
            
            .style-emerald .chart-container::after {
                content: '╔══════════════════════════════════════════════════════════════════════════════╗';
                position: absolute;
                top: 5px;
                left: 5px;
                color: #00FF00;
                font-family: 'VT323', monospace;
                font-size: 12px;
                pointer-events: none;
            }
            
            .style-emerald .btn,
            .style-emerald button,
            .style-emerald input[type="button"],
            .style-emerald input[type="submit"] {
                background: #00FF00 !important;
                color: #002200 !important;
                border: solid 2px #99FF99 !important;
                font-family: 'VT323', monospace !important;
            }
            
            .style-emerald .metric-value,
            .style-emerald .price,
            .style-emerald .value,
            .style-emerald .number {
                color: #99FF99 !important;
                animation: pulse 2s infinite !important;
                font-weight: bold !important;
                font-size: 20px !important;
                font-family: 'VT323', monospace !important;
            }
            
            .style-emerald .navbar {
                background: #00FF00 !important;
                color: #002200 !important;
                text-align: center !important;
                font-size: 20px !important;
                text-shadow: 0 0 10px #00FF00 !important;
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
                font-size: 14px !important;
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
            
            .style-amber *,
            .style-amber .navbar,
            .style-amber .header,
            .style-amber .controls,
            .style-amber .metric-card,
            .style-amber .chart-container,
            .style-amber .metric-section,
            .style-amber .card,
            .style-amber .panel,
            .style-amber .widget,
            .style-amber div,
            .style-amber span,
            .style-amber p,
            .style-amber h1,
            .style-amber h2,
            .style-amber h3,
            .style-amber canvas,
            .style-amber svg {
                background: #804000 !important;
                border: 2px solid #FFB000 !important;
                color: #FFB000 !important;
                font-family: 'Share Tech Mono', monospace !important;
                font-size: 14px !important;
                clip-path: polygon(0 0, calc(100% - 10px) 0, 100% 10px, 100% 100%, 10px 100%, 0 calc(100% - 10px)) !important;
            }
            
            .style-amber .chart-container {
                position: relative !important;
                background: radial-gradient(ellipse at center, #804000 0%, #2A1400 70%) !important;
            }
            
            .style-amber .chart-container::after {
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0; bottom: 0;
                background-image: 
                    linear-gradient(45deg, transparent 49%, rgba(255, 176, 0, 0.3) 50%, transparent 51%),
                    linear-gradient(-45deg, transparent 49%, rgba(255, 176, 0, 0.3) 50%, transparent 51%);
                background-size: 30px 30px;
                pointer-events: none;
            }
            
            .style-amber .btn,
            .style-amber button,
            .style-amber input[type="button"],
            .style-amber input[type="submit"] {
                background: #FFB000 !important;
                color: #2A1400 !important;
                border: 2px solid #FFD700 !important;
                clip-path: polygon(5px 0, 100% 0, calc(100% - 5px) 100%, 0 100%) !important;
                font-family: 'Share Tech Mono', monospace !important;
            }
            
            .style-amber .metric-value,
            .style-amber .price,
            .style-amber .value,
            .style-amber .number {
                color: #FFD700 !important;
                text-shadow: 0 0 15px #FFB000 !important;
                font-weight: bold !important;
                font-size: 18px !important;
                font-family: 'Share Tech Mono', monospace !important;
            }
            
            .style-amber .navbar {
                background: #804000 !important;
                padding: 0 20px !important;
                clip-path: polygon(0 0, calc(100% - 20px) 0, 100% 100%, 20px 100%) !important;
                text-shadow: 0 0 10px #FFB000 !important;
            }
            
            @keyframes scanlines {
                0% { opacity: 1; }
                50% { opacity: 0.8; }
                100% { opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }
    
    applyCyberStyle() {
        document.body.classList.add('style-cyber');
        
        const style = document.createElement('style');
        style.id = 'cyber-style';
        style.textContent = `
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
            
            body.style-cyber {
                background: linear-gradient(135deg, #0F1419 0%, #1A2332 50%, #0F1419 100%) !important;
                color: #E1E8F0 !important;
                font-family: 'Inter', sans-serif !important;
                font-size: 14px !important;
            }
            
            .style-cyber *,
            .style-cyber .navbar,
            .style-cyber .header,
            .style-cyber .controls,
            .style-cyber .metric-card,
            .style-cyber .chart-container,
            .style-cyber .metric-section,
            .style-cyber .card,
            .style-cyber .panel,
            .style-cyber .widget,
            .style-cyber div,
            .style-cyber span,
            .style-cyber p,
            .style-cyber h1,
            .style-cyber h2,
            .style-cyber h3 {
                background: linear-gradient(145deg, #1E2A3A 0%, #2A3B4D 100%) !important;
                border: 1px solid rgba(59, 130, 246, 0.3) !important;
                border-radius: 8px !important;
                color: #E1E8F0 !important;
                font-family: 'Inter', sans-serif !important;
                font-size: 14px !important;
                box-shadow: 0 4px 20px rgba(59, 130, 246, 0.1) !important;
            }
            
            .style-cyber canvas,
            .style-cyber svg {
                background: transparent !important;
                border: none !important;
                border-radius: 8px !important;
            }
            
            .style-cyber .chart-container {
                background: linear-gradient(145deg, #1E2A3A 0%, #2A3B4D 100%) !important;
                border: 1px solid rgba(59, 130, 246, 0.4) !important;
                border-radius: 12px !important;
                box-shadow: 0 8px 32px rgba(59, 130, 246, 0.15) !important;
                position: relative !important;
                overflow: hidden !important;
            }
            
            .style-cyber .chart-container::before {
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0; bottom: 0;
                background: linear-gradient(45deg, transparent 30%, rgba(59, 130, 246, 0.05) 50%, transparent 70%);
                pointer-events: none;
            }
            
            .style-cyber .btn,
            .style-cyber button,
            .style-cyber input[type="button"],
            .style-cyber input[type="submit"] {
                background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%) !important;
                color: #FFFFFF !important;
                border: 1px solid rgba(59, 130, 246, 0.5) !important;
                border-radius: 6px !important;
                font-family: 'Inter', sans-serif !important;
                font-weight: 500 !important;
                box-shadow: 0 4px 16px rgba(59, 130, 246, 0.3) !important;
                transition: all 0.3s ease !important;
            }
            
            .style-cyber .btn:hover,
            .style-cyber button:hover {
                box-shadow: 0 6px 24px rgba(59, 130, 246, 0.4) !important;
                transform: translateY(-2px) !important;
            }
            
            .style-cyber .metric-value,
            .style-cyber .price,
            .style-cyber .value,
            .style-cyber .number {
                color: #60A5FA !important;
                font-weight: 600 !important;
                font-size: 24px !important;
                font-family: 'Inter', sans-serif !important;
                text-shadow: 0 0 20px rgba(96, 165, 250, 0.5) !important;
            }
            
            .style-cyber .navbar {
                background: linear-gradient(135deg, #1E2A3A 0%, #2A3B4D 100%) !important;
                border-bottom: 2px solid rgba(59, 130, 246, 0.3) !important;
                border-radius: 0 !important;
                padding: 12px 20px !important;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
            }
            
            .style-cyber .positive { 
                color: #10B981 !important; 
                text-shadow: 0 0 15px rgba(16, 185, 129, 0.4) !important;
            }
            .style-cyber .negative { 
                color: #EF4444 !important; 
                text-shadow: 0 0 15px rgba(239, 68, 68, 0.4) !important;
            }
            .style-cyber .neutral { 
                color: #F59E0B !important; 
                text-shadow: 0 0 15px rgba(245, 158, 11, 0.4) !important;
            }
            
            .style-cyber .metric-card:hover,
            .style-cyber .chart-container:hover {
                border-color: rgba(59, 130, 246, 0.6) !important;
                box-shadow: 0 12px 40px rgba(59, 130, 246, 0.2) !important;
                transform: translateY(-4px) !important;
                transition: all 0.3s ease !important;
            }
        `;
        document.head.appendChild(style);
    }
}

// Initialize style switcher when DOM loads
document.addEventListener('DOMContentLoaded', () => {
    window.styleSwitcher = new StyleSwitcher();
});