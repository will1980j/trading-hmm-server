"""
Create the complete main_dashboard.js file
"""

js_content = '''/**
 * H1.2 MAIN DASHBOARD - CLEAN REBUILD (MASTER PATCH)
 * NO FAKE DATA - All metrics from real APIs or marked as locked
 * Lifecycle-driven signal and trade display
 */

class MainDashboard {
    constructor() {
        this.refreshInterval = 15000;
        this.intervalId = null;
        this.data = {
            signals: [],
            stats: {},
            pnl: {},
            sessions: {},
            risk: {},
            quality: {}
        };
        this.init();
    }
    
    async init() {
        console.log('🚀 H1.2 Main Dashboard - Clean Rebuild Initialized');
        await this.fetchAllData();
        this.startPolling();
    }
    
    async fetchAllData() {
        try {
            await Promise.all([
                this.fetchDashboardData(),
                this.fetchStats()
            ]);
            this.renderAll();
        } catch (error) {
            console.error('❌ Error fetching dashboard data:', error);
            this.showErrorStates();
        }
    }
    
    async fetchDashboardData() {
        try {
            const response = await fetch('/api/automated-signals/dashboard-data');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            if (data && data.success) {
                this.data.signals = [...(data.active_trades || []), ...(data.completed_trades || [])];
                this.calculateStats();
            }
        } catch (error) {
            console.error('❌ Error fetching dashboard data:', error);
            this.data.signals = [];
        }
    }
'''

with open('static/js/main_dashboard.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print("✅ Created main_dashboard.js (part 1)")
