"""
Deploy System Health Monitor to Automated Signals Dashboard
Adds compact status bar at top with expandable details
"""

import sys
import os

# Read the current dashboard
with open('templates/automated_signals_dashboard.html', 'r', encoding='utf-8') as f:
    dashboard_html = f.read()

# System Health Monitor HTML (compact status bar + expandable details)
health_monitor_html = '''
<!-- SYSTEM HEALTH MONITOR -->
<style>
.health-monitor {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border-bottom: 2px solid #0f3460;
    padding: 12px 20px;
    margin: -20px -20px 20px -20px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}

.health-status-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
}

.health-overall {
    display: flex;
    align-items: center;
    gap: 12px;
}

.health-pulse {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    animation: pulse 2s ease-in-out infinite;
}

.health-pulse.healthy {
    background: #00ff88;
    box-shadow: 0 0 10px #00ff88;
}

.health-pulse.warning {
    background: #ffaa00;
    box-shadow: 0 0 10px #ffaa00;
}

.health-pulse.critical {
    background: #ff3366;
    box-shadow: 0 0 10px #ff3366;
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.6; transform: scale(1.2); }
}

.health-title {
    font-size: 14px;
    font-weight: 600;
    color: #fff;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.health-components {
    display: flex;
    gap: 15px;
    flex: 1;
    justify-content: center;
}

.health-component {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    background: rgba(255,255,255,0.05);
    border-radius: 6px;
    border: 1px solid rgba(255,255,255,0.1);
    transition: all 0.3s ease;
    cursor: pointer;
}

.health-component:hover {
    background: rgba(255,255,255,0.1);
    transform: translateY(-2px);
}

.health-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
}

.health-dot.healthy { background: #00ff88; }
.health-dot.warning { background: #ffaa00; }
.health-dot.critical { background: #ff3366; }

.health-label {
    font-size: 11px;
    color: #aaa;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.health-value {
    font-size: 12px;
    color: #fff;
    font-weight: 600;
}

.health-actions {
    display: flex;
    gap: 10px;
}

.health-btn {
    padding: 6px 12px;
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 6px;
    color: #fff;
    font-size: 11px;
    cursor: pointer;
    transition: all 0.3s ease;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.health-btn:hover {
    background: rgba(255,255,255,0.2);
    transform: translateY(-2px);
}

.health-details {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease;
    margin-top: 0;
}

.health-details.expanded {
    max-height: 500px;
    margin-top: 15px;
}

.health-details-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 15px;
}

.health-detail-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    padding: 15px;
}

.health-detail-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
}

.health-detail-title {
    font-size: 12px;
    color: #fff;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.health-detail-status {
    font-size: 10px;
    padding: 3px 8px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.health-detail-status.healthy {
    background: rgba(0,255,136,0.2);
    color: #00ff88;
}

.health-detail-status.warning {
    background: rgba(255,170,0,0.2);
    color: #ffaa00;
}

.health-detail-status.critical {
    background: rgba(255,51,102,0.2);
    color: #ff3366;
}

.health-detail-metrics {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.health-metric {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 11px;
}

.health-metric-label {
    color: #aaa;
}

.health-metric-value {
    color: #fff;
    font-weight: 600;
}

.health-issues {
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid rgba(255,255,255,0.1);
}

.health-issue {
    font-size: 10px;
    color: #ffaa00;
    padding: 4px 0;
    display: flex;
    align-items: center;
    gap: 6px;
}

.health-issue::before {
    content: "⚠";
    font-size: 12px;
}

.health-timestamp {
    font-size: 10px;
    color: #666;
    text-align: right;
}
</style>

<div class="health-monitor">
    <div class="health-status-bar">
        <div class="health-overall">
            <div class="health-pulse healthy" id="healthPulse"></div>
            <div class="health-title">System Status</div>
        </div>
        
        <div class="health-components" id="healthComponents">
            <!-- Populated by JavaScript -->
        </div>
        
        <div class="health-actions">
            <button class="health-btn" onclick="toggleHealthDetails()">Details</button>
            <button class="health-btn" onclick="refreshHealth()">Refresh</button>
        </div>
    </div>
    
    <div class="health-details" id="healthDetails">
        <div class="health-details-grid" id="healthDetailsGrid">
            <!-- Populated by JavaScript -->
        </div>
    </div>
    
    <div class="health-timestamp" id="healthTimestamp"></div>
</div>

<script>
let healthData = null;
let healthDetailsExpanded = false;

// Load health status on page load
document.addEventListener('DOMContentLoaded', function() {
    refreshHealth();
    // Auto-refresh every 60 seconds
    setInterval(refreshHealth, 60000);
});

async function refreshHealth() {
    try {
        const response = await fetch('/api/system-health');
        healthData = await response.json();
        updateHealthDisplay();
    } catch (error) {
        console.error('Health check failed:', error);
        showHealthError();
    }
}

function updateHealthDisplay() {
    if (!healthData) return;
    
    // Update overall status pulse
    const pulse = document.getElementById('healthPulse');
    pulse.className = `health-pulse ${healthData.overall_status}`;
    
    // Update components
    const componentsDiv = document.getElementById('healthComponents');
    componentsDiv.innerHTML = '';
    
    const components = healthData.components;
    
    // Database
    if (components.database) {
        componentsDiv.appendChild(createComponentBadge(
            'Database',
            components.database.status,
            `${components.database.query_time_ms}ms`
        ));
    }
    
    // Webhook
    if (components.webhook) {
        const lastWebhook = components.webhook.last_webhook_seconds_ago;
        componentsDiv.appendChild(createComponentBadge(
            'Webhooks',
            components.webhook.status,
            lastWebhook ? `${lastWebhook}s ago` : 'No data'
        ));
    }
    
    // Events
    if (components.events) {
        componentsDiv.appendChild(createComponentBadge(
            'Events',
            components.events.status,
            `${components.events.mfe_coverage_percent}% MFE`
        ));
    }
    
    // Freshness
    if (components.freshness) {
        const mfeAge = components.freshness.last_mfe_seconds_ago;
        componentsDiv.appendChild(createComponentBadge(
            'Data',
            components.freshness.status,
            mfeAge ? `${Math.floor(mfeAge/60)}m old` : 'No data'
        ));
    }
    
    // API
    if (components.api) {
        componentsDiv.appendChild(createComponentBadge(
            'API',
            components.api.status,
            `${components.api.response_time_ms}ms`
        ));
    }
    
    // Update timestamp
    const timestamp = new Date(healthData.timestamp).toLocaleTimeString();
    document.getElementById('healthTimestamp').textContent = `Last check: ${timestamp}`;
    
    // Update details if expanded
    if (healthDetailsExpanded) {
        updateHealthDetails();
    }
}

function createComponentBadge(label, status, value) {
    const div = document.createElement('div');
    div.className = 'health-component';
    div.onclick = () => {
        if (!healthDetailsExpanded) {
            toggleHealthDetails();
        }
    };
    
    div.innerHTML = `
        <div class="health-dot ${status}"></div>
        <div>
            <div class="health-label">${label}</div>
            <div class="health-value">${value}</div>
        </div>
    `;
    
    return div;
}

function toggleHealthDetails() {
    healthDetailsExpanded = !healthDetailsExpanded;
    const detailsDiv = document.getElementById('healthDetails');
    
    if (healthDetailsExpanded) {
        detailsDiv.classList.add('expanded');
        updateHealthDetails();
    } else {
        detailsDiv.classList.remove('expanded');
    }
}

function updateHealthDetails() {
    if (!healthData || !healthData.components) return;
    
    const grid = document.getElementById('healthDetailsGrid');
    grid.innerHTML = '';
    
    const components = healthData.components;
    
    // Database details
    if (components.database) {
        grid.appendChild(createDetailCard('Database', components.database, [
            { label: 'Connected', value: components.database.connected ? 'Yes' : 'No' },
            { label: 'Table Exists', value: components.database.table_exists ? 'Yes' : 'No' },
            { label: 'Row Count', value: components.database.row_count },
            { label: 'Query Time', value: `${components.database.query_time_ms}ms` },
            { label: 'Columns OK', value: components.database.columns_ok ? 'Yes' : 'No' }
        ]));
    }
    
    // Webhook details
    if (components.webhook) {
        const eventTypes = components.webhook.event_types || {};
        grid.appendChild(createDetailCard('Webhooks', components.webhook, [
            { label: 'Last Webhook', value: `${components.webhook.last_webhook_seconds_ago}s ago` },
            { label: 'Last Hour', value: components.webhook.webhooks_last_hour },
            { label: 'ENTRY Events', value: eventTypes.ENTRY || 0 },
            { label: 'MFE Updates', value: eventTypes.MFE_UPDATE || 0 },
            { label: 'BE Triggered', value: eventTypes.BE_TRIGGERED || 0 },
            { label: 'EXIT Events', value: (eventTypes.EXIT_STOP_LOSS || 0) + (eventTypes.EXIT_BREAK_EVEN || 0) }
        ]));
    }
    
    // Event flow details
    if (components.events) {
        grid.appendChild(createDetailCard('Event Flow', components.events, [
            { label: 'Active Trades', value: components.events.active_trades },
            { label: 'With MFE', value: components.events.trades_with_mfe },
            { label: 'MFE Coverage', value: `${components.events.mfe_coverage_percent}%` },
            { label: 'Completed Today', value: components.events.completed_today }
        ]));
    }
    
    // Data freshness details
    if (components.freshness) {
        grid.appendChild(createDetailCard('Data Freshness', components.freshness, [
            { label: 'Last MFE Update', value: `${components.freshness.last_mfe_seconds_ago}s ago` },
            { label: 'Last Entry', value: `${components.freshness.last_entry_seconds_ago}s ago` }
        ]));
    }
    
    // API details
    if (components.api) {
        grid.appendChild(createDetailCard('API Performance', components.api, [
            { label: 'Response Time', value: `${components.api.response_time_ms}ms` },
            { label: 'Status Code', value: components.api.status_code }
        ]));
    }
}

function createDetailCard(title, data, metrics) {
    const card = document.createElement('div');
    card.className = 'health-detail-card';
    
    let metricsHTML = metrics.map(m => `
        <div class="health-metric">
            <span class="health-metric-label">${m.label}:</span>
            <span class="health-metric-value">${m.value}</span>
        </div>
    `).join('');
    
    let issuesHTML = '';
    if (data.issues && data.issues.length > 0) {
        issuesHTML = `
            <div class="health-issues">
                ${data.issues.map(issue => `<div class="health-issue">${issue}</div>`).join('')}
            </div>
        `;
    }
    
    card.innerHTML = `
        <div class="health-detail-header">
            <div class="health-detail-title">${title}</div>
            <div class="health-detail-status ${data.status}">${data.status}</div>
        </div>
        <div class="health-detail-metrics">
            ${metricsHTML}
        </div>
        ${issuesHTML}
    `;
    
    return card;
}

function showHealthError() {
    const pulse = document.getElementById('healthPulse');
    pulse.className = 'health-pulse critical';
    
    const componentsDiv = document.getElementById('healthComponents');
    componentsDiv.innerHTML = '<div style="color: #ff3366; font-size: 12px;">Health check failed</div>';
}
</script>
'''

# Insert health monitor right after the opening body tag and before the dashboard title
insert_position = dashboard_html.find('<div class="dashboard-container">')
if insert_position == -1:
    insert_position = dashboard_html.find('<body>') + len('<body>')

updated_html = (
    dashboard_html[:insert_position] +
    health_monitor_html +
    dashboard_html[insert_position:]
)

# Write updated dashboard
with open('templates/automated_signals_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(updated_html)

print("✅ System Health Monitor added to dashboard")
print("📍 Location: Top of page, compact status bar")
print("🎯 Features: 5 component checks, expandable details, auto-refresh")
