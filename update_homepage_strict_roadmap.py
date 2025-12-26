#!/usr/bin/env python3
"""
Update homepage with authoritative steering roadmap - STRICT MODE
No invention, no expansion, exact rendering only
"""

# Read current template
with open('templates/homepage_video_background.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Exact roadmap HTML (verbatim from authoritative source)
roadmap_html = '''<!-- LEFT COLUMN: ROADMAP -->
<aside class="roadmap-section">
<div class="roadmap-header">
<h2>Databento-First Professional Trading System Roadmap (NQ-Centric) — 2025–2026</h2>
<p style="font-size:0.85rem;color:rgba(255,255,255,0.7);margin-top:8px;">
NQ is the primary research instrument. MNQ is execution sizing only.
</p>
</div>

<!-- PHASE A: ACTIVE -->
<div style="background:rgba(34,197,94,0.15);border:1px solid rgba(34,197,94,0.4);border-radius:8px;padding:14px;margin-bottom:12px;">
<div style="font-weight:700;color:#4ade80;font-size:0.95rem;margin-bottom:6px;">PHASE A — Market Truth & Determinism (LOCK FIRST)</div>
<div style="display:inline-block;background:rgba(34,197,94,0.3);color:#4ade80;padding:3px 8px;border-radius:4px;font-size:0.7rem;font-weight:600;margin-bottom:8px;">ACTIVE</div>
<div style="color:rgba(255,255,255,0.75);font-size:0.85rem;">
Purpose: Establish an unquestionable historical market truth layer.
</div>
</div>

<!-- PHASE B: NOT YET ENABLED -->
<div style="background:rgba(100,116,139,0.08);border:1px solid rgba(100,116,139,0.25);border-radius:8px;padding:14px;margin-bottom:12px;">
<div style="font-weight:700;color:rgba(255,255,255,0.4);font-size:0.95rem;margin-bottom:6px;">PHASE B — Indicator Parity (BLOCKER PHASE)</div>
<div style="display:inline-block;background:rgba(100,116,139,0.15);color:rgba(255,255,255,0.4);padding:3px 8px;border-radius:4px;font-size:0.7rem;font-weight:600;margin-bottom:8px;">NOT YET ENABLED</div>
<div style="color:rgba(255,255,255,0.4);font-size:0.85rem;">
Purpose: Exact Pine → Python translation with zero interpretation.
</div>
</div>

<!-- PHASE C: NOT YET ENABLED -->
<div style="background:rgba(100,116,139,0.08);border:1px solid rgba(100,116,139,0.25);border-radius:8px;padding:14px;margin-bottom:12px;">
<div style="font-weight:700;color:rgba(255,255,255,0.4);font-size:0.95rem;margin-bottom:6px;">PHASE C — Historical Signal Generation (RAW)</div>
<div style="display:inline-block;background:rgba(100,116,139,0.15);color:rgba(255,255,255,0.4);padding:3px 8px;border-radius:4px;font-size:0.7rem;font-weight:600;margin-bottom:8px;">NOT YET ENABLED</div>
<div style="color:rgba(255,255,255,0.4);font-size:0.85rem;">
Purpose: Generate non-opinionated historical signals.
</div>
</div>

<!-- PHASE D: NOT YET ENABLED -->
<div style="background:rgba(100,116,139,0.08);border:1px solid rgba(100,116,139,0.25);border-radius:8px;padding:14px;margin-bottom:12px;">
<div style="font-weight:700;color:rgba(255,255,255,0.4);font-size:0.95rem;margin-bottom:6px;">PHASE D — Signal Quality & Expectancy (EDGE DISCOVERY)</div>
<div style="display:inline-block;background:rgba(100,116,139,0.15);color:rgba(255,255,255,0.4);padding:3px 8px;border-radius:4px;font-size:0.7rem;font-weight:600;margin-bottom:8px;">NOT YET ENABLED</div>
<div style="color:rgba(255,255,255,0.4);font-size:0.85rem;">
Purpose: Determine which signals deserve to exist.
</div>
</div>

<!-- PHASE E: NOT YET ENABLED -->
<div style="background:rgba(100,116,139,0.08);border:1px solid rgba(100,116,139,0.25);border-radius:8px;padding:14px;margin-bottom:12px;">
<div style="font-weight:700;color:rgba(255,255,255,0.4);font-size:0.95rem;margin-bottom:6px;">PHASE E — Regime & Temporal Intelligence</div>
<div style="display:inline-block;background:rgba(100,116,139,0.15);color:rgba(255,255,255,0.4);padding:3px 8px;border-radius:4px;font-size:0.7rem;font-weight:600;margin-bottom:8px;">NOT YET ENABLED</div>
<div style="color:rgba(255,255,255,0.4);font-size:0.85rem;">
Purpose: Explain why signals work or fail.
</div>
</div>

<!-- PHASE F: NOT YET ENABLED -->
<div style="background:rgba(100,116,139,0.08);border:1px solid rgba(100,116,139,0.25);border-radius:8px;padding:14px;margin-bottom:12px;">
<div style="font-weight:700;color:rgba(255,255,255,0.4);font-size:0.95rem;margin-bottom:6px;">PHASE F — Strategy Construction (HUMAN-LED)</div>
<div style="display:inline-block;background:rgba(100,116,139,0.15);color:rgba(255,255,255,0.4);padding:3px 8px;border-radius:4px;font-size:0.7rem;font-weight:600;margin-bottom:8px;">NOT YET ENABLED</div>
<div style="color:rgba(255,255,255,0.4);font-size:0.85rem;">
Purpose: Assemble rule-based strategies from validated components.
</div>
</div>

<!-- PHASE G: NOT YET ENABLED -->
<div style="background:rgba(100,116,139,0.08);border:1px solid rgba(100,116,139,0.25);border-radius:8px;padding:14px;margin-bottom:12px;">
<div style="font-weight:700;color:rgba(255,255,255,0.4);font-size:0.95rem;margin-bottom:6px;">PHASE G — Backtesting & Portfolio Risk</div>
<div style="display:inline-block;background:rgba(100,116,139,0.15);color:rgba(255,255,255,0.4);padding:3px 8px;border-radius:4px;font-size:0.7rem;font-weight:600;margin-bottom:8px;">NOT YET ENABLED</div>
<div style="color:rgba(255,255,255,0.4);font-size:0.85rem;">
Purpose: Stress-test strategies, not invent them.
</div>
</div>

<!-- PHASE H: NOT YET ENABLED -->
<div style="background:rgba(100,116,139,0.08);border:1px solid rgba(100,116,139,0.25);border-radius:8px;padding:14px;margin-bottom:12px;">
<div style="font-weight:700;color:rgba(255,255,255,0.4);font-size:0.95rem;margin-bottom:6px;">PHASE H — Live Data & Paper Trading</div>
<div style="display:inline-block;background:rgba(100,116,139,0.15);color:rgba(255,255,255,0.4);padding:3px 8px;border-radius:4px;font-size:0.7rem;font-weight:600;margin-bottom:8px;">NOT YET ENABLED</div>
<div style="color:rgba(255,255,255,0.4);font-size:0.85rem;">
Purpose: Validate assumptions in real-time.
</div>
</div>

<!-- PHASE I: NOT YET ENABLED -->
<div style="background:rgba(100,116,139,0.08);border:1px solid rgba(100,116,139,0.25);border-radius:8px;padding:14px;margin-bottom:12px;">
<div style="font-weight:700;color:rgba(255,255,255,0.4);font-size:0.95rem;margin-bottom:6px;">PHASE I — Prop Firm Scaling</div>
<div style="display:inline-block;background:rgba(100,116,139,0.15);color:rgba(255,255,255,0.4);padding:3px 8px;border-radius:4px;font-size:0.7rem;font-weight:600;margin-bottom:8px;">NOT YET ENABLED</div>
<div style="color:rgba(255,255,255,0.4);font-size:0.85rem;">
Purpose: Operationalise proven strategies.
</div>
</div>

<!-- PHASE J: NOT YET ENABLED -->
<div style="background:rgba(100,116,139,0.08);border:1px solid rgba(100,116,139,0.25);border-radius:8px;padding:14px;margin-bottom:12px;">
<div style="font-weight:700;color:rgba(255,255,255,0.4);font-size:0.95rem;margin-bottom:6px;">PHASE J — ML (OPTIONAL, CONTROLLED, LATE)</div>
<div style="display:inline-block;background:rgba(100,116,139,0.15);color:rgba(255,255,255,0.4);padding:3px 8px;border-radius:4px;font-size:0.7rem;font-weight:600;margin-bottom:8px;">NOT YET ENABLED</div>
<div style="color:rgba(255,255,255,0.4);font-size:0.85rem;">
Purpose: Assist discovery — never replace judgment.
</div>
</div>

<!-- GLOBAL NON-NEGOTIABLE RULES -->
<div style="margin-top:16px;padding:14px;background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:8px;">
<div style="font-weight:700;color:#60a5fa;font-size:0.9rem;margin-bottom:8px;">Global Non-Negotiable Rules</div>
<ul style="margin:0;padding-left:20px;color:rgba(255,255,255,0.7);font-size:0.8rem;line-height:1.6;">
<li>Databento is the single source of truth</li>
<li>NQ is the research instrument</li>
<li>MNQ is execution sizing only</li>
<li>No live systems before historical understanding</li>
<li>No ML before structure</li>
<li>Every phase must be independently disable-able</li>
</ul>
</div>

<div style="margin-top:12px;padding:10px;background:rgba(251,191,36,0.1);border:1px solid rgba(251,191,36,0.3);border-radius:6px;font-size:0.75rem;color:rgba(255,255,255,0.6);">
<strong style="color:#fbbf24;">Current Active Phase:</strong> Phase A<br>
No work may proceed beyond Phase A until Phase A is explicitly locked.
</div>
</aside>'''

# Find and replace the roadmap section
start_marker = '<!-- LEFT COLUMN: ROADMAP -->'
next_section_marker = '<!-- RIGHT COLUMN:'

start_idx = content.find(start_marker)
if start_idx == -1:
    print("❌ Could not find roadmap section")
    exit(1)

next_idx = content.find(next_section_marker, start_idx)
if next_idx == -1:
    print("❌ Could not find next section")
    exit(1)

# Replace roadmap section
new_content = content[:start_idx] + roadmap_html + '\n\n' + content[next_idx:]

# Write to file
with open('templates/homepage_video_background.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Homepage updated with authoritative steering roadmap (strict mode)")
print("   - Title: Databento-First Professional Trading System Roadmap (NQ-Centric) — 2025–2026")
print("   - Phases A-J rendered verbatim")
print("   - Phase A: ACTIVE")
print("   - Phases B-J: NOT YET ENABLED")
print("   - Global Non-Negotiable Rules included")
print("\nVerify: git diff templates/homepage_video_background.html")
