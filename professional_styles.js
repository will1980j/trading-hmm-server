// Professional Style System
class ProfessionalStyles {
    constructor() {
        this.currentStyle = localStorage.getItem('professionalStyle') || 'slate';
        this.init();
    }
    
    init() {
        this.applyStyle(this.currentStyle);
        window.addEventListener('storage', (e) => {
            if (e.key === 'professionalStyle') {
                this.applyStyle(e.newValue);
            }
        });
    }
    
    applyStyle(style) {
        this.removeExistingStyles();
        
        const styleElement = document.createElement('style');
        styleElement.id = 'professional-style';
        styleElement.textContent = this.getStyleCSS(style);
        document.head.appendChild(styleElement);
        
        document.body.className = `style-${style}`;
        this.currentStyle = style;
    }
    
    removeExistingStyles() {
        const existing = document.getElementById('professional-style');
        if (existing) existing.remove();
        document.body.className = document.body.className.replace(/style-\w+/g, '');
    }
    
    getStyleCSS(style) {
        const styles = {
            slate: {
                bg: '#0f172a',
                surface: '#1e293b',
                border: '#334155',
                text: '#f1f5f9',
                accent: '#3b82f6',
                font: 'Inter'
            },
            charcoal: {
                bg: '#111827',
                surface: '#1f2937',
                border: '#374151',
                text: '#f9fafb',
                accent: '#10b981',
                font: 'Inter'
            },
            navy: {
                bg: '#0c1426',
                surface: '#1e2a4a',
                border: '#2d3748',
                text: '#e2e8f0',
                accent: '#4299e1',
                font: 'Inter'
            },
            graphite: {
                bg: '#1a1a1a',
                surface: '#2d2d2d',
                border: '#404040',
                text: '#ffffff',
                accent: '#ff6b35',
                font: 'Inter'
            },
            midnight: {
                bg: '#0d1117',
                surface: '#21262d',
                border: '#30363d',
                text: '#f0f6fc',
                accent: '#58a6ff',
                font: 'Inter'
            },
            steel: {
                bg: '#18181b',
                surface: '#27272a',
                border: '#3f3f46',
                text: '#fafafa',
                accent: '#a855f7',
                font: 'Inter'
            },
            carbon: {
                bg: '#0a0a0a',
                surface: '#1c1c1c',
                border: '#2e2e2e',
                text: '#ededed',
                accent: '#22c55e',
                font: 'Inter'
            },
            obsidian: {
                bg: '#1c1917',
                surface: '#292524',
                border: '#44403c',
                text: '#fafaf9',
                accent: '#f59e0b',
                font: 'Inter'
            },
            onyx: {
                bg: '#0c0a09',
                surface: '#1c1917',
                border: '#292524',
                text: '#fafaf9',
                accent: '#ef4444',
                font: 'Inter'
            },
            platinum: {
                bg: '#f8fafc',
                surface: '#ffffff',
                border: '#e2e8f0',
                text: '#0f172a',
                accent: '#3b82f6',
                font: 'Inter'
            },
            arctic: {
                bg: '#ffffff',
                surface: '#f8fafc',
                border: '#cbd5e1',
                text: '#1e293b',
                accent: '#2563eb',
                font: 'Inter'
            }
        };
        
        const theme = styles[style];
        
        return `
            @import url('https://fonts.googleapis.com/css2?family=${theme.font}:wght@400;500;600;700&display=swap');
            
            body {
                background: ${theme.bg} !important;
                color: ${theme.text} !important;
                font-family: '${theme.font}', sans-serif !important;
                font-size: 14px !important;
            }
            
            .navbar,
            .header,
            .controls,
            .metric-card,
            .chart-container,
            .metric-section,
            .card,
            .panel,
            .widget,
            .data-input,
            .stat-card {
                background: ${theme.surface} !important;
                border: 1px solid ${theme.border} !important;
                color: ${theme.text} !important;
                font-family: '${theme.font}', sans-serif !important;
            }
            
            .btn,
            button,
            input[type="button"],
            input[type="submit"] {
                background: ${theme.accent} !important;
                color: ${(style === 'platinum' || style === 'arctic') ? '#ffffff' : theme.bg} !important;
                border: 1px solid ${theme.accent} !important;
                font-family: '${theme.font}', sans-serif !important;
                font-weight: 500 !important;
            }
            
            .metric-value,
            .price,
            .value,
            .number,
            .stat-value {
                color: ${theme.accent} !important;
                font-weight: 600 !important;
                font-family: '${theme.font}', sans-serif !important;
            }
            
            input,
            select,
            textarea {
                background: ${(style === 'platinum' || style === 'arctic') ? '#f1f5f9' : theme.surface} !important;
                border: 1px solid ${theme.border} !important;
                color: ${theme.text} !important;
                font-family: '${theme.font}', sans-serif !important;
            }
            
            .trades-table th,
            .trades-table td {
                border-color: ${theme.border} !important;
                color: ${theme.text} !important;
            }
            
            .trades-table th {
                background: ${(style === 'platinum' || style === 'arctic') ? '#f8fafc' : theme.surface} !important;
            }
            
            .positive { color: #10b981 !important; }
            .negative { color: #ef4444 !important; }
            .neutral { color: #f59e0b !important; }
        `;
    }
    
    setStyle(style) {
        localStorage.setItem('professionalStyle', style);
        this.applyStyle(style);
        window.dispatchEvent(new StorageEvent('storage', {
            key: 'professionalStyle',
            newValue: style
        }));
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.professionalStyles = new ProfessionalStyles();
});