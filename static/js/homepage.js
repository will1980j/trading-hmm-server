/* ============================================
   MODULE 15 - HOMEPAGE COMMAND CENTER
   Interactive Functionality
   ============================================ */

// Roadmap Data (Placeholder - will be replaced with API call)
const roadmapData = [
    {
        phase: 0,
        name: "Foundations",
        status: "complete",
        progress: 100,
        stages: [
            "Trading methodology definition",
            "Cloud architecture setup",
            "Platform vision established"
        ]
    },
    {
        phase: 1,
        name: "Expansion & UI/UX Modernization",
        status: "active",
        progress: 35,
        stages: [
            "Unified UI design system",
            "Homepage Command Center (Module 15)",
            "Dashboard rebuilds in progress",
            "Legacy Signal Lab archival"
        ]
    },
    {
        phase: 2,
        name: "Automated Signal Processing",
        status: "upcoming",
        progress: 0,
        stages: [
            "Real-time webhook processing",
            "Signal validation engine",
            "MFE tracking automation"
        ]
    },
    {
        phase: 3,
        name: "Execution & Risk Engine",
        status: "upcoming",
        progress: 0,
        stages: [
            "Trade execution router",
            "Risk management engine",
            "Prop firm rule validation"
        ]
    },
    {
        phase: 4,
        name: "Automated Validation",
        status: "upcoming",
        progress: 0,
        stages: [
            "Signal confirmation automation",
            "Pivot detection system",
            "Stop loss calculation"
        ]
    },
    {
        phase: 5,
        name: "Full Automation",
        status: "upcoming",
        progress: 0,
        stages: [
            "End-to-end automation",
            "Multi-account execution",
            "Position sizing automation"
        ]
    },
    {
        phase: 6,
        name: "ML Intelligence",
        status: "upcoming",
        progress: 0,
        stages: [
            "Predictive ML models",
            "Feature engineering",
            "Regime detection"
        ]
    },
    {
        phase: 7,
        name: "Scaling Infrastructure",
        status: "upcoming",
        progress: 0,
        stages: [
            "Performance optimization",
            "Database scaling",
            "Load balancing"
        ]
    },
    {
        phase: 8,
        name: "Institutional Infrastructure",
        status: "upcoming",
        progress: 0,
        stages: [
            "Enterprise features",
            "Advanced reporting",
            "Compliance tools"
        ]
    },
    {
        phase: 9,
        name: "Autonomous AI Engine",
        status: "upcoming",
        progress: 0,
        stages: [
            "AI-driven decision making",
            "Self-optimizing strategies",
            "Adaptive learning"
        ]
    },
    {
        phase: 10,
        name: "Prop Firm Business Layer",
        status: "upcoming",
        progress: 0,
        stages: [
            "Multi-trader management",
            "Capital allocation",
            "Business intelligence"
        ]
    }
];

// System Status Data (Mock - will be replaced with API)
let systemStatus = {
    webhook_health: "healthy",
    queue_depth: 0,
    risk_engine: "operational",
    last_signal: "2 min ago",
    current_session: "NY AM",
    latency_ms: 45
};

// Initialize Homepage
document.addEventListener('DOMContentLoaded', function() {
    renderRoadmap();
    renderSystemStatus();
    setupEventListeners();
    startStatusRefresh();
});

// Render Roadmap
function renderRoadmap() {
    const container = document.getElementById('roadmapPhases');
    if (!container) return;
    
    container.innerHTML = '';
    
    roadmapData.forEach(phase => {
        const phaseCard = createPhaseCard(phase);
        container.appendChild(phaseCard);
    });
}

// Create Phase Card
function createPhaseCard(phase) {
    const card = document.createElement('div');
    card.className = `phase-card ${phase.status}`;
    card.dataset.phase = phase.phase;
    
    const statusText = phase.status.charAt(0).toUpperCase() + phase.status.slice(1);
    
    card.innerHTML = `
        <div class="phase-header">
            <span class="phase-number">Phase ${phase.phase}</span>
            <span class="phase-status ${phase.status}">${statusText}</span>
        </div>
        <div class="phase-name">${phase.name}</div>
        <div class="phase-progress">
            <div class="phase-progress-bar" style="width: ${phase.progress}%"></div>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 0.8rem; color: var(--text-muted);">${phase.progress}% Complete</span>
            <span class="phase-expand-icon">▼</span>
        </div>
        <div class="phase-stages">
            ${phase.stages.map(stage => `<div class="stage-item">• ${stage}</div>`).join('')}
        </div>
    `;
    
    return card;
}

// Render System Status
function renderSystemStatus() {
    const container = document.getElementById('systemStatus');
    if (!container) return;
    
    container.innerHTML = `
        <div class="status-item">
            <span class="status-label">Webhook:</span>
            <span class="status-badge ${systemStatus.webhook_health}">${systemStatus.webhook_health}</span>
        </div>
        <div class="status-item">
            <span class="status-label">Queue:</span>
            <span class="status-value">${systemStatus.queue_depth}</span>
        </div>
        <div class="status-item">
            <span class="status-label">Risk Engine:</span>
            <span class="status-value">${systemStatus.risk_engine}</span>
        </div>
        <div class="status-item">
            <span class="status-label">Last Signal:</span>
            <span class="status-value">${systemStatus.last_signal}</span>
        </div>
        <div class="status-item">
            <span class="status-label">Session:</span>
            <span class="status-value">${systemStatus.current_session}</span>
        </div>
        <div class="status-item">
            <span class="status-label">Latency:</span>
            <span class="status-value">${systemStatus.latency_ms}ms</span>
        </div>
    `;
}

// Setup Event Listeners
function setupEventListeners() {
    // Phase card expand/collapse
    document.addEventListener('click', function(e) {
        const phaseCard = e.target.closest('.phase-card');
        if (phaseCard) {
            phaseCard.classList.toggle('expanded');
        }
    });
    
    // Category card hover effects
    const categoryCards = document.querySelectorAll('.category-card');
    categoryCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-4px) scale(1.01)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// Start Status Refresh
function startStatusRefresh() {
    // Refresh system status every 30 seconds
    setInterval(async () => {
        try {
            await fetchSystemStatus();
            renderSystemStatus();
        } catch (error) {
            console.log('Status refresh error:', error);
        }
    }, 30000);
}

// Fetch System Status (API call)
async function fetchSystemStatus() {
    try {
        // Try to fetch from automated signals stats
        const response = await fetch('/api/automated-signals/stats');
        if (response.ok) {
            const data = await response.json();
            
            // Update status based on API data
            systemStatus.webhook_health = data.total_signals > 0 ? "healthy" : "warning";
            systemStatus.queue_depth = data.active_signals || 0;
            systemStatus.last_signal = data.last_signal_time || "N/A";
        }
    } catch (error) {
        console.log('Failed to fetch system status:', error);
    }
}

// Utility: Format time ago
function timeAgo(timestamp) {
    const now = Date.now();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes} min ago`;
    if (hours < 24) return `${hours} hr ago`;
    return 'Over 24h ago';
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        roadmapData,
        systemStatus,
        renderRoadmap,
        renderSystemStatus
    };
}
