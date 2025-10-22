# Navigation Bar Update Guide

## Universal Navigation Component

Add this navigation bar to all 12 dashboard pages for consistency.

### Navigation HTML (Insert after `<body>` tag):

```html
<nav style="background: #141b3d; padding: 12px 20px; margin-bottom: 20px; border-bottom: 1px solid #2d3a5f; display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">
    <a href="/ml-dashboard" data-page="ml" style="padding: 8px 12px; background: #1a2142; color: #f8fafc; text-decoration: none; border-radius: 6px; font-size: 14px; white-space: nowrap;">🤖 ML</a>
    <a href="/live-signals-dashboard" data-page="live" style="padding: 8px 12px; background: #1a2142; color: #f8fafc; text-decoration: none; border-radius: 6px; font-size: 14px; white-space: nowrap;">📶 Live</a>
    <a href="/signal-lab-dashboard" data-page="dashboard" style="padding: 8px 12px; background: #1a2142; color: #f8fafc; text-decoration: none; border-radius: 6px; font-size: 14px; white-space: nowrap;">🏠 Dashboard</a>
    <a href="/signal-analysis-lab" data-page="lab" style="padding: 8px 12px; background: #1a2142; color: #f8fafc; text-decoration: none; border-radius: 6px; font-size: 14px; white-space: nowrap;">🧪 Signal Lab</a>
    <a href="/time-analysis" data-page="time" style="padding: 8px 12px; background: #1a2142; color: #f8fafc; text-decoration: none; border-radius: 6px; font-size: 14px; white-space: nowrap;">⏰ Time</a>
    <a href="/strategy-optimizer" data-page="optimizer" style="padding: 8px 12px; background: #1a2142; color: #f8fafc; text-decoration: none; border-radius: 6px; font-size: 14px; white-space: nowrap;">🎯 Optimizer</a>
    <a href="/strategy-comparison" data-page="compare" style="padding: 8px 12px; background: #1a2142; color: #f8fafc; text-decoration: none; border-radius: 6px; font-size: 14px; white-space: nowrap;">🏆 Compare</a>
    <a href="/ai-business-advisor" data-page="advisor" style="padding: 8px 12px; background: #1a2142; color: #f8fafc; text-decoration: none; border-radius: 6px; font-size: 14px; white-space: nowrap;">🧠 AI Advisor</a>
    <a href="/prop-portfolio" data-page="prop" style="padding: 8px 12px; background: #1a2142; color: #f8fafc; text-decoration: none; border-radius: 6px; font-size: 14px; white-space: nowrap;">💼 Prop</a>
    <a href="/trade-manager" data-page="trades" style="padding: 8px 12px; background: #1a2142; color: #f8fafc; text-decoration: none; border-radius: 6px; font-size: 14px; white-space: nowrap;">📋 Trades</a>
    <a href="/financial-summary" data-page="finance" style="padding: 8px 12px; background: #1a2142; color: #f8fafc; text-decoration: none; border-radius: 6px; font-size: 14px; white-space: nowrap;">💰 Finance</a>
    <a href="/reporting-hub" data-page="reports" style="padding: 8px 12px; background: #1a2142; color: #f8fafc; text-decoration: none; border-radius: 6px; font-size: 14px; white-space: nowrap;">📊 Reports</a>
</nav>

<script>
// Auto-highlight active page
(function() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('nav a[data-page]');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.style.background = '#3b82f6';
            link.style.color = 'white';
        }
    });
})();
</script>
```

## Files to Update:

1. ✅ `ml_feature_dashboard.html` - Already has navigation
2. ⏳ `live_signals_dashboard.html`
3. ⏳ `signal_lab_dashboard.html`
4. ⏳ `signal_analysis_lab.html`
5. ⏳ `time_analysis.html`
6. ⏳ `strategy_optimizer.html`
7. ⏳ `strategy_comparison.html`
8. ⏳ `ai_business_dashboard.html`
9. ⏳ `prop_firms_v2.html` (or `prop_firm_management.html`)
10. ⏳ `trade_manager.html`
11. ⏳ `financial_summary.html`
12. ⏳ `reporting_hub.html`

## Update Instructions:

For each file:
1. Open the HTML file
2. Find the `<body>` tag
3. Insert the navigation HTML immediately after `<body>`
4. Remove any existing navigation if present
5. Save the file

## Benefits:

- ✅ Consistent navigation across all pages
- ✅ Auto-highlights current page
- ✅ Mobile responsive
- ✅ Matches ML dashboard styling
- ✅ Easy to maintain (update one place, copy to all)
