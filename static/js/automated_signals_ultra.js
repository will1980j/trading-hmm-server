// MODULE 23 — AUTOMATED SIGNALS ULTRA (PHASE 2B)
// Wired to Phase 2A Read-Only APIs - Real Data - No Execution

class AutomatedSignalsUltra {
    constructor() {
        this.liveSignals = [];
        this.filteredSignals = [];
        this.selectedSignal = null;
        this.autoScroll = true;
        this.filtersOpen = false;
        this.detailsOpen = false;
        this.pollingInterval = null;
        this.isLoading = false;
        
        this.init();
    }
    
    async init() {
        console.log('🚀 Automated Signals ULTRA - Phase 2B Initialized (Real Data)');
        
        this.setupEventListeners();
        this.startTimestamp();
        this.setupSparkline();
        
        // Initial data fetch
        await this.fetchAllData();
        
        // Start polling for updates
        this.startPolling();
    }
    
    // ========================================
    // PHASE 2A API INTEGRATION
    // ========================================
    
    async fetchAllData() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        try {
            await Promise.all([
                this.fetchLiveSignals(),
                this.fetchTodayStats(),
                this.fetchSystemStatus()
            ]);
        } catch (error) {
            console.error('❌ Error fetching data:', error);
            this.showError('Data temporarily unavailable');
        } finally {
            this.isLoading = false;
        }
    }
    
    async fetchLiveSignals() {
        try {
            const response = await fetch('/api/signals/live');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            if (data.success && data.signals) {
                this.liveSignals = data.signals.map(s => this.mapSignalToViewModel(s));
                this.filteredSignals = [...this.liveSignals];
                this.renderSignalFeed();
                this.updateMetrics();
                console.log(`📊 Fetched ${this.liveSignals.length} live signals`);
            }
        } catch (error) {
            console.error('❌ Error fetching live signals:', error);
        }
    }
    
    async fetchTodayStats() {
        try {
            const response = await fetch('/api/signals/stats/today');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            if (data.success && data.stats) {
                this.updatePerformanceStrip(data.stats);
                console.log('📊 Fetched today stats:', data.stats);
            }
        } catch (error) {
            console.error('❌ Error fetching today stats:', error);
        }
    }
    
    async fetchSystemStatus() {
        try {
            const response = await fetch('/api/system-status');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            if (data.success && data.status) {
                this.updateSystemStatus(data.status);
                console.log('📊 Fetched system status:', data.status);
            }
        } catch (error) {
            console.error('❌ Error fetching system status:', error);
        }
    }
    
    mapSignalToViewModel(apiSignal) {
        // Map Phase 2A API format to ULTRA view model
        const direction = apiSignal.direction === 'LONG' ? 'long' : 'short';
        const session = this.normalizeSession(apiSignal.session);
        const stage = this.mapStatusToStage(apiSignal.status);
        
        return {
            id: apiSignal.trade_id,
            direction: direction,
            session: session,
            entry: apiSignal.entry_price ? apiSignal.entry_price.toFixed(2) : 'N/A',
            stop: apiSignal.stop_loss ? apiSignal.stop_loss.toFixed(2) : 'N/A',
            timestamp: apiSignal.timestamp ? new Date(apiSignal.timestamp).toISOString() : new Date().toISOString(),
            stage: stage,
            progress: this.calculateProgress(apiSignal),
            mfe: apiSignal.mfe ? apiSignal.mfe.toFixed(2) : '0.00',
            ae: apiSignal.ae ? apiSignal.ae.toFixed(2) : '0.00',
            r_multiple: apiSignal.r_multiple ? apiSignal.r_multiple.toFixed(2) : '0.00',
            duration: this.calculateDuration(apiSignal.timestamp),
            confidence: '0.85', // Placeholder
            volume: 0, // Not available in Phase 2A
            spread: '0.0', // Not available in Phase 2A
            slippage: '0.00', // Not available in Phase 2A
            lifecycle: this.buildLifecycle(apiSignal),
            raw: apiSignal // Keep raw data for reference
        };
    }
    
    normalizeSession(session) {
        const sessionMap = {
            'ASIA': 'asia',
            'LONDON': 'london',
            'NY_PRE': 'ny',
            'NY_AM': 'ny',
            'NY_LUNCH': 'ny',
            'NY_PM': 'ny'
        };
        return sessionMap[session] || 'ny';
    }
    
    mapStatusToStage(status) {
        const stageMap = {
            'PENDING': 'pending',
            'CONFIRMED': 'confirmed',
            'ACTIVE': 'mfe',
            'COMPLETED': 'exit',
            'CANCELLED': 'exit'
        };
        return stageMap[status] || 'pending';
    }
    
    calculateProgress(signal) {
        if (signal.status === 'COMPLETED') return 100;
        if (signal.status === 'PENDING') return 10;
        if (signal.be_triggered) return 75;
        if (signal.mfe && signal.mfe > 0) return 50;
        return 25;
    }
    
    calculateDuration(timestamp) {
        if (!timestamp) return 0;
        const now = Date.now();
        const start = typeof timestamp === 'number' ? timestamp : new Date(timestamp).getTime();
        return Math.floor((now - start) / 60000); // minutes
    }
    
    buildLifecycle(signal) {
        const lifecycle = {
            pending: signal.timestamp ? new Date(signal.timestamp).toISOString() : null,
            confirmed: null,
            be: null,
            mfe: null,
            exit: null
        };
        
        // Parse lifecycle array if available
        if (signal.lifecycle && Array.isArray(signal.lifecycle)) {
            signal.lifecycle.forEach(event => {
                const eventType = event.event_type;
                const timestamp = event.timestamp ? new Date(event.timestamp).toISOString() : null;
                
                if (eventType === 'ENTRY' || eventType === 'SIGNAL_CREATED') {
                    lifecycle.confirmed = timestamp;
                }
                if (eventType === 'BE_TRIGGERED') {
                    lifecycle.be = timestamp;
                }
                if (eventType === 'MFE_UPDATE' && !lifecycle.mfe) {
                    lifecycle.mfe = timestamp;
                }
                if (eventType.startsWith('EXIT_')) {
                    lifecycle.exit = timestamp;
                }
            });
        }
        
        return lifecycle;
    }
    
    startPolling() {
        // Poll every 5 seconds
        this.pollingInterval = setInterval(() => {
            this.fetchAllData();
        }, 5000);
        
        console.log('🔄 Polling started (5s interval)');
    }
    
    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
            console.log('⏸️  Polling stopped');
        }
    }
    
    showError(message) {
        // Non-intrusive error display
        console.warn(`⚠️  ${message}`);
        // Could add a small toast notification here if desired
    }
    
    setupEventListeners() {
        // Dataset selector
        document.querySelectorAll('.dataset-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.dataset-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                console.log(`📊 Dataset switched to: ${e.target.dataset.dataset}`);
            });
        });
        
        // Session selector
        document.getElementById('sessionSelect').addEventListener('change', (e) => {
            console.log(`🌍 Session changed to: ${e.target.value}`);
            this.applyFilters();
        });
        
        // Filters panel
        document.getElementById('collapseFilters').addEventListener('click', () => {
            this.toggleFiltersPanel();
        });
        
        // Filter controls
        ['filterSession', 'filterDirection', 'filterStatus', 'filterTime'].forEach(id => {
            document.getElementById(id).addEventListener('change', () => {
                this.applyFilters();
            });
        });
        
        // Range filters
        ['rRangeMin', 'rRangeMax', 'mfeRangeMin', 'mfeRangeMax'].forEach(id => {
            document.getElementById(id).addEventListener('input', () => {
                this.updateRangeDisplays();
                this.applyFilters();
            });
        });
        
        // Feed controls
        document.getElementById('autoScrollBtn').addEventListener('click', () => {
            this.toggleAutoScroll();
        });
        
        document.getElementById('clearFeedBtn').addEventListener('click', () => {
            this.clearFeed();
        });
        
        // Details panel
        document.getElementById('closeDetailsBtn').addEventListener('click', () => {
            this.closeDetailsPanel();
        });
        
        // Load older signals
        document.getElementById('loadOlderBtn').addEventListener('click', () => {
            this.loadOlderSignals();
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeDetailsPanel();
            }
            if (e.key === 'f' && e.ctrlKey) {
                e.preventDefault();
                this.toggleFiltersPanel();
            }
        });
    }
    
    startTimestamp() {
        const updateTimestamp = () => {
            const now = new Date();
            const timeString = now.toLocaleTimeString('en-US', { 
                hour12: false,
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
            document.getElementById('liveTimestamp').textContent = timeString;
        };
        
        updateTimestamp();
        setInterval(updateTimestamp, 1000);
    }
    
    startLifecycleUpdates() {
        // Simulate lifecycle progression every 3-7 seconds
        this.lifecycleUpdateInterval = setInterval(() => {
            this.simulateLifecycleUpdate();
        }, 3000 + Math.random() * 4000);
    }
    
    simulateLifecycleUpdate() {
        // No longer needed - real data updates via polling
        return;
        
        if (advanceableSignals.length === 0) return;
        
        const signal = advanceableSignals[Math.floor(Math.random() * advanceableSignals.length)];
        const stages = ['pending', 'confirmed', 'be', 'mfe', 'exit'];
        const currentIndex = stages.indexOf(signal.stage);
        
        if (currentIndex < stages.length - 1) {
            const nextStage = stages[currentIndex + 1];
            signal.stage = nextStage;
            signal.progress = Math.min(100, signal.progress + 20 + Math.random() * 30);
            signal.lifecycle[nextStage] = new Date().toISOString();
            
            // Update MFE and other metrics
            if (nextStage === 'mfe') {
                signal.mfe = (parseFloat(signal.mfe) + Math.random() * 2).toFixed(2);
            }
            
            console.log(`🔄 Signal ${signal.id} advanced to ${nextStage}`);
            
            // Re-render the signal feed and update metrics
            this.renderSignalFeed();
            this.updateMetrics();
            this.updatePerformanceStrip();
            
            // Update details panel if this signal is selected
            if (this.selectedSignal && this.selectedSignal.id === signal.id) {
                this.showSignalDetails(signal);
            }
        }
    }
    
    renderSignalFeed() {
        const container = document.getElementById('signalCardsContainer');
        
        if (this.filteredSignals.length === 0) {
            container.innerHTML = `
                <div class="no-signals">
                    <p>No signals match the current filters</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.filteredSignals.map(signal => this.createSignalCard(signal)).join('');
        
        // Add click listeners to signal cards
        container.querySelectorAll('.signal-card').forEach(card => {
            card.addEventListener('click', () => {
                const signalId = card.dataset.signalId;
                const signal = this.liveSignals.find(s => s.id === signalId);
                if (signal) {
                    this.selectSignal(signal);
                }
            });
        });
        
        // Auto scroll to bottom if enabled
        if (this.autoScroll) {
            container.scrollTop = container.scrollHeight;
        }
    }
    
    createSignalCard(signal) {
        const stages = ['pending', 'confirmed', 'be', 'mfe', 'exit'];
        const currentStageIndex = stages.indexOf(signal.stage);
        const progressPercent = (currentStageIndex + 1) / stages.length * 100;
        
        return `
            <div class="signal-card ${this.selectedSignal?.id === signal.id ? 'selected' : ''}" 
                 data-signal-id="${signal.id}">
                <div class="signal-card-header">
                    <div class="direction-badge ${signal.direction}">
                        ${signal.direction.toUpperCase()}
                    </div>
                    <div class="session-badge">${signal.session}</div>
                </div>
                
                <div class="signal-prices">
                    <div class="price-item">
                        <span class="price-label">Entry</span>
                        <span class="price-value">${signal.entry}</span>
                    </div>
                    <div class="price-item">
                        <span class="price-label">Stop</span>
                        <span class="price-value">${signal.stop}</span>
                    </div>
                    <div class="price-item">
                        <span class="price-label">R</span>
                        <span class="price-value ${parseFloat(signal.r_multiple) >= 0 ? 'positive' : 'negative'}">
                            ${signal.r_multiple}
                        </span>
                    </div>
                </div>
                
                <div class="signal-timestamp">
                    ${new Date(signal.timestamp).toLocaleString()}
                </div>
                
                <div class="lifecycle-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${progressPercent}%"></div>
                    </div>
                    <div class="lifecycle-timeline">
                        ${stages.map((stage, index) => `
                            <div class="timeline-stage ${
                                index <= currentStageIndex ? 'completed' : ''
                            } ${
                                index === currentStageIndex ? 'active' : ''
                            }">
                                ${stage}
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }
    
    selectSignal(signal) {
        // Update selected signal
        this.selectedSignal = signal;
        
        // Update UI
        document.querySelectorAll('.signal-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        const selectedCard = document.querySelector(`[data-signal-id="${signal.id}"]`);
        if (selectedCard) {
            selectedCard.classList.add('selected');
        }
        
        // Show details panel
        this.showSignalDetails(signal);
        
        console.log(`🎯 Selected signal: ${signal.id}`);
    }
    
    showSignalDetails(signal) {
        const detailsContent = document.getElementById('detailsContent');
        
        detailsContent.innerHTML = `
            <div class="signal-details active">
                <div class="details-section">
                    <h4>Entry Details</h4>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <span class="detail-label">Direction</span>
                            <span class="detail-value">${signal.direction.toUpperCase()}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Session</span>
                            <span class="detail-value">${signal.session.toUpperCase()}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Entry Price</span>
                            <span class="detail-value">${signal.entry}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Stop Loss</span>
                            <span class="detail-value">${signal.stop}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Volume</span>
                            <span class="detail-value">${signal.volume}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Spread</span>
                            <span class="detail-value">${signal.spread}</span>
                        </div>
                    </div>
                </div>
                
                <div class="details-section">
                    <h4>Full Lifecycle Timeline</h4>
                    <div class="lifecycle-details">
                        ${Object.entries(signal.lifecycle).map(([stage, timestamp]) => `
                            <div class="lifecycle-item ${timestamp ? 'completed' : 'pending'}">
                                <span class="lifecycle-stage">${stage.toUpperCase()}</span>
                                <span class="lifecycle-time">
                                    ${timestamp ? new Date(timestamp).toLocaleString() : 'Pending'}
                                </span>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <div class="details-section">
                    <h4>Price Map</h4>
                    <div class="chart-placeholder">
                        Price Chart Placeholder
                    </div>
                </div>
                
                <div class="details-section">
                    <h4>Signal Statistics</h4>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <span class="detail-label">R Multiple</span>
                            <span class="detail-value ${parseFloat(signal.r_multiple) >= 0 ? 'positive' : 'negative'}">
                                ${signal.r_multiple}
                            </span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">MFE</span>
                            <span class="detail-value">${signal.mfe}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">AE</span>
                            <span class="detail-value">${signal.ae}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Duration</span>
                            <span class="detail-value">${signal.duration}m</span>
                        </div>
                    </div>
                </div>
                
                <div class="details-section">
                    <h4>Future Placeholders</h4>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <span class="detail-label">ML Confidence</span>
                            <span class="detail-value">${signal.confidence}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Slippage</span>
                            <span class="detail-value">${signal.slippage}</span>
                        </div>
                    </div>
                    
                    <div class="chart-placeholder" style="margin-top: 16px;">
                        ML Outcome Distribution Placeholder
                    </div>
                    
                    <div class="ai-explanation">
                        <h5>AI Explanation</h5>
                        <p style="color: var(--text-muted); font-size: 0.85rem; line-height: 1.4;">
                            This signal was generated based on FVG pattern recognition with confluence from multiple timeframes. 
                            The algorithm detected a high-probability setup with favorable risk-reward ratio.
                        </p>
                    </div>
                </div>
            </div>
        `;
        
        // Open details panel
        this.openDetailsPanel();
    }
    
    openDetailsPanel() {
        const panel = document.getElementById('detailsPanel');
        panel.classList.add('open');
        panel.classList.remove('closed');
        this.detailsOpen = true;
    }
    
    closeDetailsPanel() {
        const panel = document.getElementById('detailsPanel');
        panel.classList.remove('open');
        panel.classList.add('closed');
        this.detailsOpen = false;
        this.selectedSignal = null;
        
        // Remove selection from cards
        document.querySelectorAll('.signal-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        // Reset details content
        document.getElementById('detailsContent').innerHTML = `
            <div class="no-selection">
                <p>Select a signal to view details</p>
            </div>
        `;
    }
    
    toggleFiltersPanel() {
        const panel = document.getElementById('filtersPanel');
        const isCollapsed = panel.classList.contains('collapsed');
        
        if (isCollapsed) {
            panel.classList.remove('collapsed');
            this.filtersOpen = true;
        } else {
            panel.classList.add('collapsed');
            this.filtersOpen = false;
        }
    }
    
    toggleAutoScroll() {
        this.autoScroll = !this.autoScroll;
        const btn = document.getElementById('autoScrollBtn');
        
        if (this.autoScroll) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    }
    
    clearFeed() {
        if (confirm('Clear all signals from the feed?')) {
            this.liveSignals = [];
            this.filteredSignals = [];
            this.renderSignalFeed();
            this.updateMetrics();
            this.updatePerformanceStrip();
            console.log('🗑️ Feed cleared');
        }
    }
    
    loadOlderSignals() {
        console.log('📥 Loading older signals (mock)');
        alert('Load older signals feature (mock implementation)');
    }
    
    applyFilters() {
        const sessionFilter = document.getElementById('filterSession').value;
        const directionFilter = document.getElementById('filterDirection').value;
        const statusFilter = document.getElementById('filterStatus').value;
        const timeFilter = document.getElementById('filterTime').value;
        
        const rMin = parseFloat(document.getElementById('rRangeMin').value);
        const rMax = parseFloat(document.getElementById('rRangeMax').value);
        const mfeMin = parseFloat(document.getElementById('mfeRangeMin').value);
        const mfeMax = parseFloat(document.getElementById('mfeRangeMax').value);
        
        this.filteredSignals = this.liveSignals.filter(signal => {
            // Session filter
            if (sessionFilter !== 'all' && signal.session !== sessionFilter) {
                return false;
            }
            
            // Direction filter
            if (directionFilter !== 'all' && signal.direction !== directionFilter) {
                return false;
            }
            
            // Status filter
            if (statusFilter !== 'all' && signal.stage !== statusFilter) {
                return false;
            }
            
            // R range filter
            const rValue = parseFloat(signal.r_multiple);
            if (rValue < rMin || rValue > rMax) {
                return false;
            }
            
            // MFE range filter
            const mfeValue = parseFloat(signal.mfe);
            if (mfeValue < mfeMin || mfeValue > mfeMax) {
                return false;
            }
            
            // Time filter (simplified)
            const signalTime = new Date(signal.timestamp);
            const now = new Date();
            const timeDiff = now - signalTime;
            
            switch (timeFilter) {
                case 'today':
                    return timeDiff < 24 * 60 * 60 * 1000;
                case 'week':
                    return timeDiff < 7 * 24 * 60 * 60 * 1000;
                case 'month':
                    return timeDiff < 30 * 24 * 60 * 60 * 1000;
                default:
                    return true;
            }
        });
        
        console.log(`🔍 Applied filters: ${this.filteredSignals.length}/${this.liveSignals.length} signals`);
        this.renderSignalFeed();
        this.updateMetrics();
    }
    
    updateRangeDisplays() {
        const rMin = document.getElementById('rRangeMin').value;
        const rMax = document.getElementById('rRangeMax').value;
        const mfeMin = document.getElementById('mfeRangeMin').value;
        const mfeMax = document.getElementById('mfeRangeMax').value;
        
        document.getElementById('rRangeDisplay').textContent = `${rMin} to ${rMax}`;
        document.getElementById('mfeRangeDisplay').textContent = `${mfeMin} to ${mfeMax}`;
    }
    
    updateMetrics() {
        const signalsToday = this.filteredSignals.length;
        const confirmedSignals = this.filteredSignals.filter(s => s.stage !== 'pending').length;
        const activeTrades = this.filteredSignals.filter(s => !['exit', 'pending'].includes(s.stage)).length;
        
        const rValues = this.filteredSignals.map(s => parseFloat(s.r_multiple));
        const avgR = rValues.length > 0 ? (rValues.reduce((a, b) => a + b, 0) / rValues.length).toFixed(2) : '0.0';
        
        const mfeValues = this.filteredSignals.map(s => parseFloat(s.mfe));
        const mfeHigh = mfeValues.length > 0 ? Math.max(...mfeValues).toFixed(2) : '0.0';
        
        document.getElementById('signalsToday').textContent = signalsToday;
        document.getElementById('confirmedSignals').textContent = confirmedSignals;
        document.getElementById('activeTrades').textContent = activeTrades;
        document.getElementById('avgR').textContent = avgR;
        document.getElementById('mfeHigh').textContent = mfeHigh;
    }
    
    updatePerformanceStrip() {
        const rValues = this.filteredSignals.map(s => parseFloat(s.r_multiple));
        const todayR = rValues.length > 0 ? rValues.reduce((a, b) => a + b, 0).toFixed(2) : '0.0';
        
        // Mock P&L calculation (assuming $100 per R)
        const todayPnl = (parseFloat(todayR) * 100).toFixed(2);
        const sessionPnl = (parseFloat(todayR) * 0.6 * 100).toFixed(2);
        
        const mfeValues = this.filteredSignals.map(s => parseFloat(s.mfe));
        const mfeHigh = mfeValues.length > 0 ? Math.max(...mfeValues).toFixed(2) : '0.0';
        const mfeLow = mfeValues.length > 0 ? Math.min(...mfeValues).toFixed(2) : '0.0';
        
        const beTriggers = this.filteredSignals.filter(s => s.lifecycle.be).length;
        const slEvents = this.filteredSignals.filter(s => s.stage === 'exit' && parseFloat(s.r_multiple) < 0).length;
        
        // Update values
        const todayREl = document.getElementById('todayR');
        todayREl.textContent = `${parseFloat(todayR) >= 0 ? '+' : ''}${todayR}`;
        todayREl.className = `perf-value ${parseFloat(todayR) >= 0 ? 'positive' : 'negative'}`;
        
        const todayPnlEl = document.getElementById('todayPnl');
        todayPnlEl.textContent = `${parseFloat(todayPnl) >= 0 ? '+$' : '-$'}${Math.abs(parseFloat(todayPnl)).toFixed(2)}`;
        todayPnlEl.className = `perf-value ${parseFloat(todayPnl) >= 0 ? 'positive' : 'negative'}`;
        
        const sessionPnlEl = document.getElementById('sessionPnl');
        sessionPnlEl.textContent = `${parseFloat(sessionPnl) >= 0 ? '+' : ''}${sessionPnl}`;
        sessionPnlEl.className = `perf-value ${parseFloat(sessionPnl) >= 0 ? 'positive' : 'negative'}`;
        
        document.getElementById('mfeHighLow').textContent = `${mfeHigh} / ${mfeLow}`;
        document.getElementById('beTriggers').textContent = beTriggers;
        document.getElementById('slEvents').textContent = slEvents;
    }
    
    setupSparkline() {
        const canvas = document.getElementById('sparklineChart');
        const ctx = canvas.getContext('2d');
        
        // Generate mock sparkline data
        const dataPoints = [];
        let value = 0;
        for (let i = 0; i < 20; i++) {
            value += (Math.random() - 0.5) * 2;
            dataPoints.push(value);
        }
        
        // Draw sparkline
        const drawSparkline = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            const width = canvas.width;
            const height = canvas.height;
            const padding = 4;
            
            const minValue = Math.min(...dataPoints);
            const maxValue = Math.max(...dataPoints);
            const range = maxValue - minValue || 1;
            
            ctx.strokeStyle = '#4C66FF';
            ctx.lineWidth = 2;
            ctx.beginPath();
            
            dataPoints.forEach((point, index) => {
                const x = (index / (dataPoints.length - 1)) * (width - 2 * padding) + padding;
                const y = height - padding - ((point - minValue) / range) * (height - 2 * padding);
                
                if (index === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });
            
            ctx.stroke();
        };
        
        drawSparkline();
        
        // Update sparkline periodically
        setInterval(() => {
            dataPoints.shift();
            dataPoints.push(dataPoints[dataPoints.length - 1] + (Math.random() - 0.5) * 2);
            drawSparkline();
        }, 2000);
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    window.ultraDashboard = new AutomatedSignalsUltra();
});

