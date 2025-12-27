# Parity V1 Runbook: get_bias FVG/IFVG

## Step 1: Generate Python Bias CSV

```powershell
python scripts/parity_v1_generate_bias_csv.py GLBX.MDP3:NQ 2024-01-02 2024-01-03 python_bias.csv
```

**Output:** `python_bias.csv` with columns: ts_utc, open, high, low, close, bias_str, bias_code

## Step 2: Export TradingView Bias Data

1. Open TradingView chart for NQ 1-minute
2. Add indicator: `pine/parity_v1_get_bias_only.pine`
3. Set date range: 2024-01-02 to 2024-01-03
4. Right-click chart → "Export chart data"
5. Save as `tv_bias.csv`

**Expected columns:** time, open, high, low, close, Bias Code, ATH, ATL

## Step 3: Compare CSVs

```powershell
python scripts/parity_v1_compare_csvs.py python_bias.csv tv_bias.csv
```

**Success:** Exit code 0, prints "✅ PERFECT MATCH - Parity V1 PASS"  
**Failure:** Exit code 1, prints mismatches

## Troubleshooting

**If mismatches occur:**
1. Check timestamp alignment (UTC vs local time)
2. Verify bar order (both ascending by time)
3. Check for off-by-one errors in array indexing
4. Verify FVG detection logic (c2_high < c0_low for bullish)
5. Verify IFVG logic (close crosses through opposite FVG)

**Common issues:**
- ATH/ATL initialization difference
- Array removal order (must iterate backwards)
- Bias change conditions (close > ath[1] vs close > prev_ath)
