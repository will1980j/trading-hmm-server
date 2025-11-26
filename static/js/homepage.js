/* ============================================
   MODULE 15 - HOMEPAGE COMMAND CENTER
   Interactive Functionality
   ============================================ */

// Roadmap Data - REMOVED (now fetched from backend API via /api/roadmap)
// This static array is obsolete and has been replaced with dynamic backend data

// System Status Data (Updated from API)
let systemStatus = {
    webhook_health: "--",
    queue_depth: 0,
    signals_today: 0,
    last_signal: "--",
    current_session: "--",
    latency_ms: 0
};

// Initialize Homepage
document.addEventListener('DOMContentLoaded', function() {
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
    // Update DOM elements with current status
    const sessionLabel = document.getElementById('statusSession');
    const signalsToday = document.getElementById('statusSignals');
    const lastSignalTime = document.getElementById('statusLastSignal');
    const webhookHealth = document.getElementById('statusWebhook');
    const queueDepth = document.getElementById('queueDepth');
    const latencyMs = document.getElementById('latencyMs');
    
    if (sessionLabel) sessionLabel.textContent = systemStatus.current_session || '--';
    if (signalsToday) signalsToday.textContent = systemStatus.signals_today || '0';
    if (lastSignalTime) lastSignalTime.textContent = systemStatus.last_signal || '--';
    if (webhookHealth) {
        webhookHealth.textContent = systemStatus.webhook_health || '--';
        webhookHealth.className = `status-value ${systemStatus.webhook_health === 'healthy' ? 'status-healthy' : 'status-warning'}`;
    }
    if (queueDepth) queueDepth.textContent = systemStatus.queue_depth || '0';
    if (latencyMs) latencyMs.textContent = systemStatus.latency_ms ? `${systemStatus.latency_ms}ms` : '--';
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
    // Initial fetch
    fetchSystemStatus().then(() => renderSystemStatus());
    
    // Refresh system status every 15 seconds
    setInterval(async () => {
        try {
            await fetchSystemStatus();
            renderSystemStatus();
        } catch (error) {
            console.log('Status refresh error:', error);
        }
    }, 15000);
}

// Fetch System Status (API call) - UNIFIED ENDPOINT
async function fetchSystemStatus() {
    try {
        // Fetch unified homepage stats from single endpoint
        const response = await fetch('/api/homepage-stats');
        if (response.ok) {
            const data = await response.json();
            
            // Map response to systemStatus object
            systemStatus.current_session = data.current_session || '--';
            systemStatus.signals_today = data.signals_today || 0;
            systemStatus.last_signal = data.last_signal_time || '--';
            systemStatus.webhook_health = data.webhook_health || 'unknown';
            
            // Format last signal time if present
            if (data.last_signal_time && data.last_signal_time !== '--') {
                try {
                    const signalDate = new Date(data.last_signal_time);
                    systemStatus.last_signal = signalDate.toLocaleTimeString('en-US', {
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: true
                    });
                } catch (e) {
                    systemStatus.last_signal = data.last_signal_time;
                }
            }
        } else {
            console.log('Homepage stats API returned error:', response.status);
        }
    } catch (error) {
        console.log('Failed to fetch homepage stats:', error);
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

/* ============================================
   BACKGROUND VIDEO ROTATION (NEW BLOCK)
   ============================================ */

const VIDEO_SOURCES = [
    "/static/login/1039099-uhd_3840_2160_30fps.mp4",
    "/static/login/11273072-uhd_3840_2160_60fps.mp4",
    "/static/login/11750841-uhd_3840_2160.mp4",
    "/static/login/11901242_3840_2160_60fps.mp4",
    "/static/login/11901266_3840_2160_60fps.mp4",
    "/static/login/11901278_3840_2160_60fps.mp4",
    "/static/login/11956328_3840_2160_60fps.mp4",
    "/static/login/11987722_3840_2160_60fps.mp4",
    "/static/login/12175382_3840_2160_60fps.mp4",
    "/static/login/12245087_3840_2160_60fps.mp4",
    "/static/login/12417159_3840_2160_60fps.mp4",
    "/static/login/13206301_3840_2160_60fps.mp4",
    "/static/login/13206313_3840_2160_60fps.mp4",
    "/static/login/13520816_3840_2160_60fps.mp4",
    "/static/login/13572067_3840_2160_60fps.mp4",
    "/static/login/1448735-uhd_4096_2160_24fps.mp4",
    "/static/login/14516377_3840_2160_60fps.mp4",
    "/static/login/14533156_3840_2160_60fps.mp4",
    "/static/login/14549988_3840_2160_60fps.mp4",
    "/static/login/14572815_3840_2160_60fps.mp4",
    "/static/login/14583020_3840_2160_60fps.mp4",
    "/static/login/15441769-uhd_3840_2160_60fps.mp4",
    "/static/login/1722697-uhd_3840_2160_25fps.mp4",
    "/static/login/17422526-uhd_3840_2160_60fps.mp4",
    "/static/login/1757853-uhd_3840_2160_25fps.mp4",
    "/static/login/1851190-uhd_3840_2160_25fps.mp4",
    "/static/login/18674366-uhd_3840_2160_60fps.mp4",
    "/static/login/18919092-uhd_3840_2160_60fps.mp4",
    "/static/login/18924205-uhd_3840_2160_60fps.mp4",
    "/static/login/18991342-uhd_3840_2160_60fps.mp4",
    "/static/login/20174325-uhd_3840_2160_60fps.mp4",
    "/static/login/20412841-uhd_3840_2160_60fps.mp4",
    "/static/login/20528868-uhd_3840_2160_60fps.mp4",
    "/static/login/2439510-hd_1920_1080_30fps.mp4",
    "/static/login/2715412-uhd_3840_2160_30fps.mp4",
    "/static/login/3129595-uhd_3840_2160_30fps.mp4",
    "/static/login/3214448-uhd_3840_2160_25fps.mp4",
    "/static/login/3571264-uhd_3840_2160_30fps.mp4",
    "/static/login/3971351-uhd_3840_2160_25fps.mp4",
    "/static/login/4130872-uhd_3840_2160_25fps.mp4",
    "/static/login/4205697-uhd_3840_2160_30fps.mp4",
    "/static/login/4208317-uhd_3840_2160_24fps.mp4",
    "/static/login/4280450-uhd_3840_2160_30fps.mp4",
    "/static/login/4456305-uhd_3840_2160_30fps.mp4",
    "/static/login/4471213-uhd_3840_2160_30fps.mp4",
    "/static/login/4763824-uhd_3840_2160_24fps.mp4",
    "/static/login/5061405-uhd_3840_2160_30fps.mp4",
    "/static/login/5091624-hd_1920_1080_24fps.mp4",
    "/static/login/5174040-uhd_3840_2160_30fps.mp4",
    "/static/login/5179893-uhd_3840_2160_30fps.mp4",
    "/static/login/5453622-uhd_3840_2160_24fps.mp4",
    "/static/login/5562986-uhd_3840_2160_24fps.mp4",
    "/static/login/5606319-uhd_3840_2160_30fps.mp4",
    "/static/login/5735604-uhd_3840_2160_30fps.mp4",
    "/static/login/6582341-uhd_3840_2160_30fps.mp4",
    "/static/login/856885-hd_1920_1080_30fps.mp4",
    "/static/login/857195-hd_1280_720_25fps.mp4",
    "/static/login/8820216-uhd_3840_2160_25fps.mp4",
    "/static/login/uhd_60fps.mp4"
];

function loadRandomBackgroundVideo() {
    const video = document.getElementById("backgroundVideo");
    if (!video) return;
    
    const index = Math.floor(Math.random() * VIDEO_SOURCES.length);
    video.src = VIDEO_SOURCES[index];
}

// Initialize background video after DOM load
document.addEventListener("DOMContentLoaded", loadRandomBackgroundVideo);


/* ============================================
   MARKET CLOCK — TIME (NEW YORK) IN STATUS RIBBON
   ============================================ */

function initMarketClock() {
    try {
        const ribbon = document.querySelector('.status-ribbon');
        if (!ribbon) return;

        // Avoid duplicating clock if called twice
        if (document.getElementById('statusMarketClock')) return;

        const clockItem = document.createElement('div');
        clockItem.className = 'status-item status-item-clock';
        clockItem.innerHTML = `
            <span class="status-label">Time (NY):</span>
            <span class="status-value status-neutral" id="statusMarketClock">--:--:--</span>
        `;
        ribbon.appendChild(clockItem);

        function updateMarketClock() {
            try {
                const clockEl = document.getElementById('statusMarketClock');
                if (!clockEl) return;

                const now = new Date();
                const options = {
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                    hour12: true,
                    timeZone: 'America/New_York'
                };
                const nyTime = now.toLocaleTimeString('en-US', options);
                clockEl.textContent = nyTime;
            } catch (e) {
                console.log('Market clock update error:', e);
            }
        }

        // Initial draw + 1-second updates
        updateMarketClock();
        setInterval(updateMarketClock, 1000);

    } catch (err) {
        console.log('Market clock init error:', err);
    }
}

// Attach as a separate DOMContentLoaded listener
if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', initMarketClock);
}

/* ============================================
   DISABLE BACKGROUND VIDEO LOADING (NO-OP)
   ============================================ */
function loadRandomBackgroundVideo() {
    try {
        // Background video rotation disabled.
        // Cinematic gradient + neural mesh now control the backdrop.
        const video = document.getElementById('backgroundVideo');
        if (video) {
            video.removeAttribute('src');
        }
    } catch (e) {
        console.log('loadRandomBackgroundVideo disabled error:', e);
    }
}


/* ================================================================
   ROADMAP PHASE EXPANSION CONTROLS — ADD ONLY
   ================================================================ */

function initRoadmapExpansion() {
    try {
        const phases = document.querySelectorAll('.roadmap-phase .phase-toggle');
        if (!phases.length) return;

        phases.forEach(btn => {
            btn.addEventListener('click', function () {
                try {
                    const parent = this.closest('.roadmap-phase');
                    if (!parent) return;
                    parent.classList.toggle('expanded');
                } catch (err) {
                    console.log("Roadmap expansion error:", err);
                }
            });
        });
    } catch (e) {
        console.log("initRoadmapExpansion error:", e);
    }
}

document.addEventListener('DOMContentLoaded', initRoadmapExpansion);


/* ================================================================
   PATCH 8 — ROADMAP JS POLISH (ADD ONLY)
   Smooth expansion, auto-scroll, and animated progress bars
   ================================================================ */

function enhanceRoadmapUX() {
    try {
        const phases = document.querySelectorAll('.roadmap-phase');
        if (!phases.length) return;

        phases.forEach(phase => {
            const toggle = phase.querySelector('.phase-toggle');
            const details = phase.querySelector('.phase-details');
            const progressFill = phase.querySelector('.phase-progress-line-fill');

            if (!toggle || !details) return;

            toggle.addEventListener('click', () => {
                // Toggle expansion state
                const expanded = phase.classList.toggle('expanded');

                // Smooth scroll into view if opening
                if (expanded) {
                    setTimeout(() => {
                        phase.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }, 120);
                }

                // Animate progress bar fill on open
                if (progressFill) {
                    if (expanded) {
                        const width = progressFill.getAttribute('data-progress') || progressFill.style.width;
                        progressFill.style.width = width;
                    } else {
                        // collapse animation (optional)
                        progressFill.style.width = "0%";
                    }
                }
            });
        });
    } catch (error) {
        console.log("enhanceRoadmapUX error:", error);
    }
}

document.addEventListener('DOMContentLoaded', enhanceRoadmapUX);

/* ================================================================
   PATCH 16B — Fix JS selector so expansion WORKS
   ================================================================ */

function fixRoadmapExpansion() {
    try {
        const phases = document.querySelectorAll('.roadmap-phase');
        phases.forEach(phase => {
            const toggle = phase.querySelector('.phase-toggle');
            if (!toggle) return;
            
            toggle.addEventListener('click', () => {
                phase.classList.toggle('expanded');
            });
        });
    } catch (e) {
        console.log("fixRoadmapExpansion error:", e);
    }
}

document.addEventListener('DOMContentLoaded', fixRoadmapExpansion);

/* ============================================================
   PATCH 17B — Remove conflicting JS width logic
   ============================================================ */

function disableProgressWidthReset() {
    try {
        const bars = document.querySelectorAll('.phase-progress-line-fill');
        bars.forEach(bar => {
            bar.style.width = '';  // remove any JS-set width
        });
    } catch (e) {
        console.log("disableProgressWidthReset error:", e);
    }
}

document.addEventListener('DOMContentLoaded', disableProgressWidthReset);
