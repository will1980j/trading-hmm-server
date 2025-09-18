// Xero API Integration for Trading Business Automation
class XeroIntegration {
    constructor() {
        this.clientId = null;
        this.clientSecret = null;
        this.accessToken = null;
        this.tenantId = null;
        this.baseURL = 'https://api.xero.com/api.xro/2.0';
        this.authURL = 'https://identity.xero.com/connect/authorize';
        this.tokenURL = 'https://identity.xero.com/connect/token';
        this.redirectURI = window.location.origin + '/xero-callback';
    }

    // Initialize Xero connection
    async initializeXero(clientId, clientSecret) {
        this.clientId = clientId;
        this.clientSecret = clientSecret;
        
        // Check for existing tokens
        const savedTokens = localStorage.getItem('xeroTokens');
        if (savedTokens) {
            const tokens = JSON.parse(savedTokens);
            this.accessToken = tokens.accessToken;
            this.tenantId = tokens.tenantId;
            
            // Verify token is still valid
            if (await this.verifyConnection()) {
                return { success: true, message: 'Connected to Xero' };
            }
        }
        
        // Need to authenticate
        return this.startAuthFlow();
    }

    // Start OAuth flow
    startAuthFlow() {
        const scopes = 'accounting.transactions accounting.reports.read accounting.contacts';
        const state = Math.random().toString(36).substring(7);
        localStorage.setItem('xeroState', state);
        
        const authUrl = `${this.authURL}?response_type=code&client_id=${this.clientId}&redirect_uri=${encodeURIComponent(this.redirectURI)}&scope=${encodeURIComponent(scopes)}&state=${state}`;
        
        window.open(authUrl, 'xeroAuth', 'width=600,height=700');
        return { success: false, message: 'Please complete Xero authentication' };
    }

    // Handle OAuth callback
    async handleCallback(code, state) {
        const savedState = localStorage.getItem('xeroState');
        if (state !== savedState) {
            throw new Error('Invalid state parameter');
        }

        const tokenResponse = await fetch(this.tokenURL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': `Basic ${btoa(this.clientId + ':' + this.clientSecret)}`
            },
            body: new URLSearchParams({
                grant_type: 'authorization_code',
                code: code,
                redirect_uri: this.redirectURI
            })
        });

        const tokens = await tokenResponse.json();
        this.accessToken = tokens.access_token;
        
        // Get tenant ID
        const connectionsResponse = await fetch('https://api.xero.com/connections', {
            headers: { 'Authorization': `Bearer ${this.accessToken}` }
        });
        const connections = await connectionsResponse.json();
        this.tenantId = connections[0].tenantId;

        // Save tokens
        localStorage.setItem('xeroTokens', JSON.stringify({
            accessToken: this.accessToken,
            tenantId: this.tenantId,
            refreshToken: tokens.refresh_token,
            expiresAt: Date.now() + (tokens.expires_in * 1000)
        }));

        return { success: true, message: 'Successfully connected to Xero' };
    }

    // Verify connection
    async verifyConnection() {
        try {
            const response = await this.makeXeroRequest('/Organisation');
            return response.Organisations && response.Organisations.length > 0;
        } catch (error) {
            return false;
        }
    }

    // Make authenticated Xero API request
    async makeXeroRequest(endpoint, method = 'GET', data = null) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            method,
            headers: {
                'Authorization': `Bearer ${this.accessToken}`,
                'Xero-tenant-id': this.tenantId,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: data ? JSON.stringify(data) : null
        });

        if (!response.ok) {
            throw new Error(`Xero API error: ${response.status}`);
        }

        return await response.json();
    }

    // Sync trading data to Xero
    async syncTradingData() {
        const trades = JSON.parse(localStorage.getItem('tradingData') || '[]');
        const results = { created: 0, updated: 0, errors: [] };

        // Group trades by month for batch processing
        const monthlyTrades = this.groupTradesByMonth(trades);

        for (const [month, monthTrades] of Object.entries(monthlyTrades)) {
            try {
                await this.createMonthlyTradingEntry(month, monthTrades);
                results.created++;
            } catch (error) {
                results.errors.push(`${month}: ${error.message}`);
            }
        }

        return results;
    }

    // Group trades by month
    groupTradesByMonth(trades) {
        const grouped = {};
        trades.forEach(trade => {
            const date = new Date(trade.date);
            const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
            
            if (!grouped[monthKey]) {
                grouped[monthKey] = [];
            }
            grouped[monthKey].push(trade);
        });
        return grouped;
    }

    // Create monthly trading entry in Xero
    async createMonthlyTradingEntry(month, trades) {
        const totalProfit = trades.reduce((sum, t) => sum + parseFloat(t.profit || 0), 0);
        const totalTrades = trades.length;
        const winningTrades = trades.filter(t => parseFloat(t.profit || 0) > 0).length;

        // Create journal entry for trading P&L
        const journalEntry = {
            JournalLines: [
                {
                    AccountCode: '200', // Trading Income account
                    Description: `Trading P&L - ${month} (${totalTrades} trades, ${winningTrades} wins)`,
                    NetAmount: totalProfit,
                    TaxType: 'NONE'
                },
                {
                    AccountCode: '090', // Trading Account/Cash
                    Description: `Trading P&L - ${month}`,
                    NetAmount: -totalProfit,
                    TaxType: 'NONE'
                }
            ],
            Narration: `Automated trading results for ${month}`,
            Date: `${month}-01`
        };

        return await this.makeXeroRequest('/ManualJournals', 'POST', { ManualJournals: [journalEntry] });
    }

    // Create expense entries
    async createExpenseEntry(description, amount, category = 'Office Expenses') {
        const expense = {
            Type: 'SPEND',
            Contact: { Name: 'Trading Business Expenses' },
            Date: new Date().toISOString().split('T')[0],
            LineItems: [{
                Description: description,
                Quantity: 1,
                UnitAmount: amount,
                AccountCode: '404', // Office Expenses
                TaxType: 'INPUT'
            }]
        };

        return await this.makeXeroRequest('/BankTransactions', 'POST', { BankTransactions: [expense] });
    }

    // Generate tax report
    async generateTaxReport() {
        const trades = JSON.parse(localStorage.getItem('tradingData') || '[]');
        const currentYear = new Date().getFullYear();
        
        // Filter trades for current tax year
        const yearTrades = trades.filter(t => new Date(t.date).getFullYear() === currentYear);
        
        const taxData = {
            totalIncome: yearTrades.reduce((sum, t) => sum + Math.max(0, parseFloat(t.profit || 0)), 0),
            totalLosses: Math.abs(yearTrades.reduce((sum, t) => sum + Math.min(0, parseFloat(t.profit || 0)), 0)),
            netIncome: yearTrades.reduce((sum, t) => sum + parseFloat(t.profit || 0), 0),
            totalTrades: yearTrades.length,
            tradingDays: new Set(yearTrades.map(t => t.date)).size
        };

        // Get Xero P&L report for verification
        try {
            const plReport = await this.makeXeroRequest(`/Reports/ProfitAndLoss?fromDate=${currentYear}-01-01&toDate=${currentYear}-12-31`);
            taxData.xeroNetProfit = this.extractNetProfitFromReport(plReport);
        } catch (error) {
            taxData.xeroNetProfit = 'Unable to fetch';
        }

        return taxData;
    }

    // Extract net profit from Xero P&L report
    extractNetProfitFromReport(report) {
        try {
            const rows = report.Reports[0].Rows;
            const netProfitRow = rows.find(row => row.RowType === 'SummaryRow' && row.Cells[0].Value === 'Net Profit');
            return netProfitRow ? parseFloat(netProfitRow.Cells[1].Value) : 0;
        } catch (error) {
            return 'Parse error';
        }
    }

    // Auto-categorize transactions
    async autoCategorizeTransactions() {
        const uncategorized = await this.makeXeroRequest('/BankTransactions?where=Type=="SPEND"AND(LineItems.AccountCode="000"OR LineItems.AccountCode="")');
        const results = { categorized: 0, errors: [] };

        for (const transaction of uncategorized.BankTransactions || []) {
            try {
                const category = this.categorizeTransaction(transaction.LineItems[0].Description);
                if (category) {
                    transaction.LineItems[0].AccountCode = category.code;
                    await this.makeXeroRequest(`/BankTransactions/${transaction.BankTransactionID}`, 'POST', { BankTransactions: [transaction] });
                    results.categorized++;
                }
            } catch (error) {
                results.errors.push(`${transaction.BankTransactionID}: ${error.message}`);
            }
        }

        return results;
    }

    // Categorize transaction based on description
    categorizeTransaction(description) {
        const categories = {
            'software': { code: '404', name: 'Software & Subscriptions' },
            'internet': { code: '404', name: 'Internet & Communications' },
            'education': { code: '404', name: 'Training & Education' },
            'data': { code: '404', name: 'Market Data' },
            'commission': { code: '405', name: 'Trading Commissions' },
            'platform': { code: '404', name: 'Trading Platform' }
        };

        const desc = description.toLowerCase();
        for (const [keyword, category] of Object.entries(categories)) {
            if (desc.includes(keyword)) {
                return category;
            }
        }
        return null;
    }

    // Generate comprehensive business report
    async generateBusinessReport() {
        const trades = JSON.parse(localStorage.getItem('tradingData') || '[]');
        const propFirms = JSON.parse(localStorage.getItem('propFirms') || '[]');
        
        // Get Xero financial data
        const currentYear = new Date().getFullYear();
        const plReport = await this.makeXeroRequest(`/Reports/ProfitAndLoss?fromDate=${currentYear}-01-01&toDate=${currentYear}-12-31`);
        const balanceSheet = await this.makeXeroRequest(`/Reports/BalanceSheet?date=${currentYear}-12-31`);

        return {
            trading: {
                totalTrades: trades.length,
                netProfit: trades.reduce((sum, t) => sum + parseFloat(t.profit || 0), 0),
                winRate: trades.length ? (trades.filter(t => parseFloat(t.profit || 0) > 0).length / trades.length * 100).toFixed(1) : 0
            },
            propFirms: {
                count: propFirms.length,
                totalCapital: propFirms.reduce((sum, f) => sum + parseFloat(f.accountSize || 0), 0),
                monthlyTargets: propFirms.reduce((sum, f) => sum + parseFloat(f.monthlyTarget || 0), 0)
            },
            xero: {
                netProfit: this.extractNetProfitFromReport(plReport),
                totalAssets: this.extractTotalFromBalanceSheet(balanceSheet, 'Assets'),
                totalLiabilities: this.extractTotalFromBalanceSheet(balanceSheet, 'Liabilities')
            },
            generated: new Date().toISOString()
        };
    }

    // Extract totals from balance sheet
    extractTotalFromBalanceSheet(report, section) {
        try {
            const rows = report.Reports[0].Rows;
            const sectionRow = rows.find(row => row.Title === section);
            if (sectionRow && sectionRow.Rows) {
                const totalRow = sectionRow.Rows.find(row => row.RowType === 'SummaryRow');
                return totalRow ? parseFloat(totalRow.Cells[1].Value) : 0;
            }
            return 0;
        } catch (error) {
            return 'Parse error';
        }
    }
}

// Global instance
window.xeroIntegration = new XeroIntegration();