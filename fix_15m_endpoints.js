// Script to fix remaining 15M API endpoints
const fs = require('fs');

const filePath = 'c:/Users/Will/CascadeProjects/tradingview-indicator/CascadeProjects/windsurf-project/signal_analysis_15m.html';
let content = fs.readFileSync(filePath, 'utf8');

// Replace all remaining signal-lab-15m-trades endpoints
content = content.replace(/signal-lab-15m-trades/g, 'signal-lab-trades');

fs.writeFileSync(filePath, content);
console.log('Fixed all 15M API endpoints');