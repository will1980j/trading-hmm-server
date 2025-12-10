// ============================================================================
// MODULE 22 - REPORTING CENTER (PHASE 2C)
// Wired to Phase 2A Read-Only APIs - Real Data
// ============================================================================

class ReportingCenter {
    constructor() {
        this.isLoading = false;
        this.todayStats = {};
        this.recentSignals = [];
        this.sessionData = {};
        
        this.init();
    }
    
    async init() {
        console.log('🚀 Reporting Center - Phase 2C Initialized (Real Data)');
        
        await this.fetchAllData();
        this.setupCategorySelector();
    }
    
    async fetchAllData() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        try {
            await Promise.all([
                this.fetchTodayStats(),
                this.fetchRecentSignals(),
                this.fetchSessionSummary()
            ]);
            
            this.renderAllReports();
        } catch (error) {
            console.error('❌ Reporting Center - Error fetching data:', error);
            this.renderEmptyReports();
        } finally {
            this.isLoading = false;
        }
    }
    
    async fetchTodayStats() {
        try {
            const response = await fetch('/api/signals/stats/today');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            if (data.success && data.stats) {
                this.todayStats = data.stats;
            }
        } catch (error) {
            console.error('❌ Error fetching today stats:', error);
            this.todayStats = {};
        }
    }
    
    async fetchRecentSignals() {
        try {
            const response = await fetch('/api/signals/recent?limit=100');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            if (data.success && data.signals) {
                this.recentSignals = data.signals;
            }
        } catch (error) {
            console.error('❌ Error fetching recent signals:', error);
            this.recentSignals = [];
        }
    }
    
    async fetchSessionSummary() {
        try {
            const response = await fetch('/api/session-summary');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            if (data.success && data.sessions) {
                this.sessionData = data.sessions;
            }
        } catch (error) {
            console.error('❌ Error fetching session summary:', error);
            this.sessionData = {};
        }
    }
    
    renderAllReports() {
        this.renderDailyReport();
        this.renderWeeklyReport();
        this.renderMonthlyReport();
    }
    
    renderEmptyReports() {
        this.renderDailyReport({});
        this.renderWeeklyReport([]);
        this.renderMonthlyReport({});
    }
    
    renderDailyReport() {
        const container = document.getElementById('tradingReports');
        if (!container) return;
        
        const signals = this.todayStats.total || 0;
        const avgR = this.todayStats.avg_r ? parseFloat(this.todayStats.avg_r).toFixed(1) : '0.0';
        const winrate = this.todayStats.winrate ? parseFloat(this.todayStats.winrate).toFixed(1) : '0.0';
        const estimatedPnl = parseFloat(avgR) * signals * 100;
        
        const avgRClass = parseFloat(avgR) >= 0 ? 'positive' : 'negative';
        const pnlClass = estimatedPnl >= 0 ? 'positive' : 'negative';
        
        const card = document.createElement('div');
        card.className = 'report-card';
        
        card.innerHTML = `
            <h3 class="report-title">Daily Report</h3>
            <div class="report-metrics">
                <div class="metric-item">
                    <div class="metric-label">Signals</div>
                    <div class="metric-value">${signals}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Est. P&L</div>
                    <div class="metric-value ${pnlClass}">${estimatedPnl >= 0 ? '+' : ''}$${Math.abs(estimatedPnl).toFixed(0)}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Win Rate</div>
                    <div class="metric-value">${winrate}%</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Avg R</div>
                    <div class="metric-value ${avgRClass}">${parseFloat(avgR) >= 0 ? '+' : ''}${avgR}R</div>
                </div>
            </div>
            <div class="chart-placeholder">
                <div class="placeholder-text">Equity curve placeholder</div>
            </div>
        `;
        
        container.innerHTML = '';
        container.appendChild(card);
    }
    
    renderWeeklyReport() {
        const weekSignals = this.recentSignals.slice(0, 50);
        
        if (weekSignals.length === 0) {
            console.log('No signals for weekly report');
            return;
        }
        
        const totalR = weekSignals.reduce((sum, s) => sum + (parseFloat(s.r_multiple) || 0), 0);
        const avgR = totalR / weekSignals.length;
        const wins = weekSignals.filter(s => (parseFloat(s.r_multiple) || 0) > 0).length;
        const winrate = (wins / weekSignals.length) * 100;
        const estimatedPnl = totalR * 100;
        
        console.log('Weekly Report:', {
            signals: weekSignals.length,
            avgR: avgR.toFixed(2),
            winrate: winrate.toFixed(1),
            estimatedPnl: estimatedPnl.toFixed(0)
        });
    }
    
    renderMonthlyReport() {
        const sessions = Object.keys(this.sessionData);
        
        if (sessions.length === 0) {
            console.log('No session data for monthly report');
            return;
        }
        
        const totalTrades = sessions.reduce((sum, s) => sum + (this.sessionData[s].total || 0), 0);
        const avgExpectancy = sessions.reduce((sum, s) => sum + (this.sessionData[s].expectancy || 0), 0) / sessions.length;
        
        console.log('Monthly Report:', {
            sessions: sessions.length,
            totalTrades,
            avgExpectancy: avgExpectancy.toFixed(2)
        });
    }
    
    setupCategorySelector() {
        const categoryCards = document.querySelectorAll('.category-card');
        
        categoryCards.forEach(card => {
            card.addEventListener('click', function() {
                const category = this.getAttribute('data-category');
                
                categoryCards.forEach(c => c.classList.remove('active'));
                this.classList.add('active');
                
                document.querySelectorAll('.report-section').forEach(section => {
                    section.style.display = 'none';
                });
                
                const sectionId = `${category}-section`;
                const section = document.getElementById(sectionId);
                if (section) {
                    section.style.display = 'block';
                }
                
                console.log(`Switched to ${category} category`);
            });
        });
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    window.reportingCenter = new ReportingCenter();
});

console.log('Reporting Center JS loaded successfully (Phase 2C)');


// ============================================================================
// WEEKLY DEVELOPMENT REPORTS
// ============================================================================

async function handleReportUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const statusDiv = document.getElementById('uploadStatus');
    statusDiv.textContent = 'Uploading...';
    statusDiv.style.color = '#60a5fa';
    
    const week = prompt('Enter week (e.g., 2025-W50):');
    if (!week) {
        statusDiv.textContent = 'Upload cancelled';
        statusDiv.style.color = '#94a3b8';
        return;
    }
    
    const formData = new FormData();
    formData.append('report', file);
    formData.append('week', week);
    
    try {
        const response = await fetch('/api/reports/upload-weekly', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            statusDiv.textContent = '✅ Report uploaded successfully!';
            statusDiv.style.color = '#10b981';
            loadWeeklyReports();
        } else {
            statusDiv.textContent = '❌ Upload failed: ' + result.error;
            statusDiv.style.color = '#ef4444';
        }
    } catch (error) {
        statusDiv.textContent = '❌ Upload error: ' + error.message;
        statusDiv.style.color = '#ef4444';
    }
}

async function loadWeeklyReports() {
    try {
        const response = await fetch('/api/reports/weekly-list');
        const data = await response.json();
        
        const listDiv = document.getElementById('weeklyReportsList');
        
        if (data.reports && data.reports.length > 0) {
            listDiv.innerHTML = data.reports.map(report => `
                <div class="report-card">
                    <div class="category-title">${report.week}</div>
                    <div class="category-subtitle">${report.filename}</div>
                    <div style="font-size: 12px; color: #94a3b8; margin: 10px 0;">
                        Uploaded: ${new Date(report.uploaded_at).toLocaleDateString()}
                    </div>
                    <div style="display: flex; gap: 10px; margin-top: 15px;">
                        <button class="btn btn-primary" onclick="viewReport('${report.id}')">
                            👁️ View
                        </button>
                        <button class="btn btn-secondary" onclick="downloadReport('${report.id}')">
                            ⬇️ Download
                        </button>
                    </div>
                </div>
            `).join('');
        } else {
            listDiv.innerHTML = `
                <div class="report-card" style="text-align: center; color: #94a3b8;">
                    No reports uploaded yet. Upload your first weekly report above.
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading reports:', error);
    }
}

function viewReport(reportId) {
    window.open(`/api/reports/view/${reportId}`, '_blank');
}

function downloadReport(reportId) {
    window.location.href = `/api/reports/download/${reportId}`;
}

// Load reports when development section is shown
document.addEventListener('DOMContentLoaded', () => {
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            const devSection = document.getElementById('development-section');
            if (devSection && devSection.style.display !== 'none') {
                loadWeeklyReports();
            }
        });
    });
    
    const devSection = document.getElementById('development-section');
    if (devSection) {
        observer.observe(devSection, { attributes: true, attributeFilter: ['style'] });
    }
});
