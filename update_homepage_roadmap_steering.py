#!/usr/bin/env python3
"""
Update homepage template with new steering roadmap display
Phases A-J with clear gating and NQ-centric messaging
"""

# Read current template
with open('templates/homepage_video_background.html', 'r', encoding='utf-8') as f:
    content = f.read()

# New roadmap HTML block
new_roadmap_block = '''<!-- LEFT COLUMN: ROADMAP -->
<aside class="roadmap-section">
<div class="roadmap-header">
<h2>Databento-First Trading System Roadmap (2025–2026)</h2>
<p style="font-size:0.85rem;color:rgba(255,255,255,0.7);margin-top:8px;">
<strong>NQ</strong> is the primary research instrument. <strong>MNQ</strong> is execution sizing only.
</p>
</div>

<!-- PHASE A: ACTIVE -->
<div style="background:rgba(34,197,94,0.15);border:1px solid rgba(34,197,94,0.4);border-radius:8px;padding:14px;margin-bottom:12px;">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
<div style="font-weight:700;color:#4ade80;font-size:1rem;">Phase A: Market Truth & Determinism</div>
<span style="background:rgba(34,197,94,0.3);color:#4ade80;padding:4px 10px;border-radius:4px;font-size:0.75rem;font-weight:600;">ACTIVE</span>
</div>
<div style="color:rgba(255,255,255,0.85);font-size:0.875rem;margin-bottom:8px;">
Establish Databento as single source of truth. Ingest 15 years of NQ historical data.
</div>
<div style="font-size:0.8rem;color:rgba(255,255,255,0.6);">
✅ NQ 15yr data ingested (5.27M bars, 2010-2025)<br>
✅ MNQ 6yr data ingested (2.34M bars, 2019-2025)<br>
✅ Database schema established<br>
⏳ Data quality monitoring
</div>
</div>

<!-- PHASES B-J: LOCKED -->
<div style="background:rgba(100,116,139,0.1);border:1px solid rgba(100,116,139,0.3);border-radius:8px;padding:14px;margin-bottom:12px;">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
<div style="font-weight:700;color:rgba(255,255,255,0.5);font-size:1rem;">Phase B: Indicator Parity (Pine → Python)</div>
<span style="background:rgba(100,116,139,0.2);color:rgba(255,255,255,0.5);padding:4px 10px;border-radius:4px;font-size:0.75rem;font-weight:600;">🔒 LOCKED</span>
</div>
<div style="color:rgba(255,255,255,0.5);font-size:0.875rem;">
Replicate TradingView indicators in Python. Run on NQ historical data.
</div>
</div>

<div style="background:rgba(100,116,139,0.1);border:1px solid rgba(100,116,139,0.3);border-radius:8px;padding:14px;margin-bottom:12px;">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
<div style="font-weight:700;color:rgba(255,255,255,0.5);font-size:1rem;">Phase C: Historical Signal Generation</div>
<span style="background:rgba(100,116,139,0.2);color:rgba(255,255,255,0.5);padding:4px 10px;border-radius:4px;font-size:0.75rem;font-weight:600;">🔒 LOCKED</span>
</div>
<div style="color:rgba(255,255,255,0.5);font-size:0.875rem;">
Generate signals from 15 years of NQ data. Calculate MFE/MAE for all signals.
</div>
</div>

<div style="background:rgba(100,116,139,0.1);border:1px solid rgba(100,116,139,0.3);border-radius:8px;padding:14px;margin-bottom:12px;">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
<div style="font-weight:700;color:rgba(255,255,255,0.5);font-size:1rem;">Phase D: Strategy Discovery</div>
<span style="background:rgba(100,116,139,0.2);color:rgba(255,255,255,0.5);padding:4px 10px;border-radius:4px;font-size:0.75rem;font-weight:600;">🔒 LOCKED</span>
</div>
<div style="color:rgba(255,255,255,0.5);font-size:0.875rem;">
Analyze historical signals. Identify optimal sessions, HTF alignments, BE strategies.
</div>
</div>

<div style="background:rgba(100,116,139,0.1);border:1px solid rgba(100,116,139,0.3);border-radius:8px;padding:14px;margin-bottom:12px;">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
<div style="font-weight:700;color:rgba(255,255,255,0.5);font-size:1rem;">Phase E: Backtesting & Validation</div>
<span style="background:rgba(100,116,139,0.2);color:rgba(255,255,255,0.5);padding:4px 10px;border-radius:4px;font-size:0.75rem;font-weight:600;">🔒 LOCKED</span>
</div>
<div style="color:rgba(255,255,255,0.5);font-size:0.875rem;">
Backtest discovered strategies. Monte Carlo simulation. Walk-forward validation.
</div>
</div>

<div style="background:rgba(100,116,139,0.1);border:1px solid rgba(100,116,139,0.3);border-radius:8px;padding:14px;margin-bottom:12px;">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
<div style="font-weight:700;color:rgba(255,255,255,0.5);font-size:1rem;">Phase F: Live Market Data</div>
<span style="background:rgba(100,116,139,0.2);color:rgba(255,255,255,0.5);padding:4px 10px;border-radius:4px;font-size:0.75rem;font-weight:600;">🔒 LOCKED</span>
</div>
<div style="color:rgba(255,255,255,0.5);font-size:0.875rem;">
Databento WebSocket. Real-time NQ tick data. Live bar aggregation.
</div>
</div>

<div style="background:rgba(100,116,139,0.1);border:1px solid rgba(100,116,139,0.3);border-radius:8px;padding:14px;margin-bottom:12px;">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
<div style="font-weight:700;color:rgba(255,255,255,0.5);font-size:1rem;">Phase G: Live Signal Generation</div>
<span style="background:rgba(100,116,139,0.2);color:rgba(255,255,255,0.5);padding:4px 10px;border-radius:4px;font-size:0.75rem;font-weight:600;">🔒 LOCKED</span>
</div>
<div style="color:rgba(255,255,255,0.5);font-size:0.875rem;">
Real-time signal generation. Live MFE tracking. Signal broadcasting.
</div>
</div>

<div style="background:rgba(100,116,139,0.1);border:1px solid rgba(100,116,139,0.3);border-radius:8px;padding:14px;margin-bottom:12px;">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
<div style="font-weight:700;color:rgba(255,255,255,0.5);font-size:1rem;">Phase H: Paper Trading</div>
<span style="background:rgba(100,116,139,0.2);color:rgba(255,255,255,0.5);padding:4px 10px;border-radius:4px;font-size:0.75rem;font-weight:600;">🔒 LOCKED</span>
</div>
<div style="color:rgba(255,255,255,0.5);font-size:0.875rem;">
Simulated trading. Validate strategy in live market. Risk-free testing.
</div>
</div>

<div style="background:rgba(100,116,139,0.1);border:1px solid rgba(100,116,139,0.3);border-radius:8px;padding:14px;margin-bottom:12px;">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
<div style="font-weight:700;color:rgba(255,255,255,0.5);font-size:1rem;">Phase I: Execution & Prop Firms</div>
<span style="background:rgba(100,116,139,0.2);color:rgba(255,255,255,0.5);padding:4px 10px;border-radius:4px;font-size:0.75rem;font-weight:600;">🔒 LOCKED</span>
</div>
<div style="color:rgba(255,255,255,0.5);font-size:0.875rem;">
Execution router. Prop firm integration. Multi-account management.
</div>
</div>

<div style="background:rgba(100,116,139,0.1);border:1px solid rgba(100,116,139,0.3);border-radius:8px;padding:14px;margin-bottom:12px;">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
<div style="font-weight:700;color:rgba(255,255,255,0.5);font-size:1rem;">Phase J: Autonomous Trading</div>
<span style="background:rgba(100,116,139,0.2);color:rgba(255,255,255,0.5);padding:4px 10px;border-radius:4px;font-size:0.75rem;font-weight:600;">🔒 LOCKED</span>
</div>
<div style="color:rgba(255,255,255,0.5);font-size:0.875rem;">
Fully autonomous execution. AI decision-making. 24/7 operation.
</div>
</div>

<div style="margin-top:16px;padding:12px;background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:8px;font-size:0.8rem;color:rgba(255,255,255,0.7);">
<strong style="color:#60a5fa;">Phase Gating:</strong> No work may proceed beyond Phase A until explicitly unlocked by user.
</div>'''

# Find and replace the roadmap section
# Look for the roadmap-section aside tag
start_marker = '<!-- LEFT COLUMN: ROADMAP -->'
end_marker = '</aside>'

start_idx = content.find(start_marker)
if start_idx == -1:
    print("❌ Could not find roadmap section start marker")
    exit(1)

# Find the closing </aside> tag after the start
end_idx = content.find(end_marker, start_idx)
if end_idx == -1:
    print("❌ Could not find roadmap section end marker")
    exit(1)

# Find the next section start (RIGHT COLUMN)
next_section = content.find('<!-- RIGHT COLUMN:', end_idx)
if next_section == -1:
    print("❌ Could not find next section marker")
    exit(1)

# Replace the roadmap section
new_content = content[:start_idx] + new_roadmap_block + '\n\n' + content[next_section:]

# Write back to file
with open('templates/homepage_video_background.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Homepage roadmap updated with steering roadmap (Phases A-J)")
print("\nVerify with: git diff templates/homepage_video_background.html")
print("\nCommit message: 'Update homepage with Databento-first steering roadmap (Phases A-J)'")
