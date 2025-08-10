// Trading Empire Knowledge Base - Comprehensive Business Intelligence
// Modularized for better maintainability and performance
class TradingEmpireKB {
    constructor() {
        this.initializeModules();
    }
    
    initializeModules() {
        this.propFirmModule = new PropFirmModule();
        this.taxModule = new AustralianTaxModule();
        this.propertyModule = new PropertyInvestmentModule();
        this.businessModule = new BusinessGrowthModule();
        this.wealthModule = new WealthStrategiesModule();
        this.planningModule = new StrategicPlanningModule();
    }
    
    // Getter methods for accessing modules
    getPropFirmIntelligence() {
        return this.propFirmModule.getData();
    }
    
    getAustralianTaxStrategy() {
        return this.taxModule.getData();
    }
    
    getPropertyInvestment() {
        return this.propertyModule.getData();
    }
    
    getBusinessGrowth() {
        return this.businessModule.getData();
    }
    
    getWealthStrategies() {
        return this.wealthModule.getData();
    }
    
    getStrategicPlanning() {
        return this.planningModule.getData();
    }
}

// Prop Firm Intelligence Module
class PropFirmModule {
    getData() {
        return {
        // Prop Firm Intelligence (PropFirmMatch.com insights)
        topTierFirms: {
            'FTMO': { 
                maxSize: '2M', 
                profitSplit: '90%', 
                challenge: '$540-$1080',
                strengths: 'Established, reliable payouts',
                strategy: 'Conservative approach, focus on consistency'
            },
            'MyForexFunds': { 
                maxSize: '300K', 
                profitSplit: '85%', 
                challenge: '$99-$999',
                strengths: 'Fast payouts, good support',
                strategy: 'Aggressive scaling possible'
            },
            'FundedNext': { 
                maxSize: '4M', 
                profitSplit: '90%', 
                challenge: '$99-$1999',
                strengths: 'Largest accounts available',
                strategy: 'Scale to massive size'
            }
        },
        challengeOptimization: {
            phase1: 'Risk 1-2% max, focus on consistency over profits',
            phase2: 'Maintain discipline, avoid revenge trading',
            funded: 'Scale gradually, compound profits intelligently'
        },
        marketIntelligence: {
            bestTimes: 'London/NY overlap for volatility',
            avoidNews: 'High-impact news events increase risk',
            optimalPairs: 'EURUSD, GBPUSD, AUDUSD for predictability'
        }
        };
    }
}

// Australian Tax Strategy Module
class AustralianTaxModule {
    getData() {
        return {
        tradingTaxStructures: {
            soleTrader: {
                pros: 'Simple, direct control',
                cons: 'High personal tax rates (up to 47%)',
                suitable: 'Small scale operations'
            },
            company: {
                pros: '25-30% tax rate, asset protection',
                cons: 'Compliance costs, complexity',
                suitable: 'Serious trading business'
            },
            trust: {
                pros: 'Income distribution flexibility',
                cons: 'Complex, ongoing costs',
                suitable: 'Family wealth building'
            },
            smsf: {
                pros: '15% tax rate, retirement focus',
                cons: 'Strict rules, minimum balance',
                suitable: 'Long-term wealth building'
            }
        },
        deductibleExpenses: [
            'Trading software subscriptions',
            'Data feeds and market analysis tools',
            'Home office expenses (percentage)',
            'Computer equipment and hardware',
            'Professional development and education',
            'Accounting and legal fees',
            'Internet and phone costs (business portion)'
        ],
        taxOptimizationStrategies: {
            timing: 'Realize losses in high-income years',
            structure: 'Company + discretionary trust combination',
            super: 'Concessional contributions to reduce taxable income',
            cgt: 'Hold investments >12 months for 50% discount'
        },
        reportingRequirements: {
            quarterly: 'BAS lodgment for GST and PAYG',
            annual: 'Tax return with trading profit/loss',
            records: 'Detailed trading records for 5 years',
            aasb: 'Accounting standards compliance for companies'
        }
        };
    }
}

// Property Investment Module
class PropertyInvestmentModule {
    getData() {
        return {
        australianMarkets: {
            sydney: {
                growth: 'Strong long-term, high entry cost',
                yield: '2-4% rental yield',
                strategy: 'Capital growth focus, premium locations'
            },
            melbourne: {
                growth: 'Steady growth, cultural hub',
                yield: '3-5% rental yield',
                strategy: 'Balanced growth and yield'
            },
            brisbane: {
                growth: 'Emerging growth, infrastructure development',
                yield: '4-6% rental yield',
                strategy: 'Value play with growth potential'
            },
            perth: {
                growth: 'Cyclical, mining dependent',
                yield: '4-7% rental yield',
                strategy: 'Timing the cycle, higher yields'
            }
        },
        investmentStrategies: {
            buyAndHold: 'Long-term wealth building, tax benefits',
            renovation: 'Value-add through improvements',
            development: 'Higher returns, higher risk and capital',
            commercial: 'Higher yields, longer leases, business risk'
        },
        financingOptimization: {
            structure: 'Interest-only loans for investment properties',
            offset: 'Offset accounts for tax efficiency',
            crossCollateral: 'Use equity to expand portfolio',
            smsf: 'Property in super for tax advantages'
        },
        globalOpportunities: {
            usa: 'Strong rental yields, established markets',
            uk: 'Stable growth, currency considerations',
            singapore: 'Asian gateway, stable government',
            dubai: 'Tax-free jurisdiction, tourism growth'
        }
        };
    }
}

// Business Growth Module
class BusinessGrowthModule {
    getData() {
        return {
        revenueStreams: {
            trading: {
                propFirms: 'Multiple funded accounts, scale systematically',
                personalCapital: 'Compound trading profits intelligently',
                signalService: 'Monetize successful strategies'
            },
            education: {
                courses: 'ICT concepts, prop firm strategies',
                mentoring: '1-on-1 coaching for premium rates',
                community: 'Subscription-based trading community'
            },
            technology: {
                tradingTools: 'Custom indicators and EAs',
                platforms: 'Trading dashboard and analytics',
                apis: 'Data feeds and automation services'
            },
            consulting: {
                propFirmConsulting: 'Help others pass challenges',
                businessConsulting: 'Trading business setup',
                taxConsulting: 'Structure optimization'
            }
        },
        scalingStrategies: {
            systemization: 'Document all processes and strategies',
            automation: 'Reduce manual work through technology',
            teamBuilding: 'Hire specialists for key functions',
            partnerships: 'Strategic alliances with complementary businesses'
        },
        operationalEfficiency: {
            trading: 'Automated trade management and risk controls',
            accounting: 'Integrated bookkeeping and reporting',
            marketing: 'Automated lead generation and nurturing',
            customer: 'Streamlined onboarding and support'
        }
        };
    }
}

// Wealth Strategies Module
class WealthStrategiesModule {
    getData() {
        return {
        assetAllocation: {
            conservative: '60% property, 30% stocks, 10% alternatives',
            balanced: '40% property, 40% stocks, 20% alternatives',
            aggressive: '30% property, 50% stocks, 20% alternatives'
        },
        diversificationPrinciples: {
            geographic: 'Australia, US, Asia, Europe exposure',
            assetClass: 'Property, equities, bonds, commodities',
            currency: 'AUD, USD, EUR hedging strategies',
            timeframe: 'Short, medium, long-term investments'
        },
        taxEfficientInvesting: {
            frankedDividends: 'Australian shares for tax credits',
            capitalGains: 'Long-term holdings for CGT discount',
            superannuation: 'Maximize concessional contributions',
            trusts: 'Income distribution for tax optimization'
        },
        generationalWealth: {
            familyTrust: 'Protect and distribute wealth efficiently',
            education: 'Financial literacy for next generation',
            succession: 'Business transition planning',
            philanthropy: 'Tax-effective charitable giving'
        }
        };
    }
}

// Strategic Planning Module
class StrategicPlanningModule {
    getData() {
        return {
        shortTerm: {
            trading: 'Pass 3+ prop firm challenges',
            tax: 'Optimize current structure',
            cash: 'Build emergency fund (6 months expenses)'
        },
        mediumTerm: {
            business: 'Diversify revenue streams',
            property: 'Acquire first investment property',
            team: 'Hire key specialists'
        },
        longTerm: {
            wealth: 'Build $10M+ net worth',
            passive: 'Create passive income streams',
            legacy: 'Establish generational wealth'
        },
        riskManagement: {
            trading: 'Never risk more than 1-2% per trade',
            business: 'Diversify income sources',
            personal: 'Adequate insurance coverage',
            market: 'Hedge against major downturns'
        }
        };
    }
}

// Create singleton instance
const tradingEmpireKB = new TradingEmpireKB();

// Export for use in chatbot
if (typeof module !== 'undefined' && module.exports) {
    module.exports = tradingEmpireKB;
} else if (typeof window !== 'undefined') {
    window.TradingEmpireKB = tradingEmpireKB;
}