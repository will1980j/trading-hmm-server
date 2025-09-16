-- Quick Calendar Fix - Resolve discrepancy between Signal Lab and Dashboard
-- The issue: Dashboard only shows trades where active_trade=false AND mfe_data exists
-- Signal Lab shows all trades regardless of active_trade status

-- Step 1: Check current state
SELECT 'Current State Analysis' as step;
SELECT 
    date,
    COUNT(*) as total_trades,
    COUNT(CASE WHEN COALESCE(mfe_none, mfe, 0) != 0 THEN 1 END) as trades_with_mfe,
    COUNT(CASE WHEN COALESCE(active_trade, false) = true THEN 1 END) as active_trades,
    COUNT(CASE WHEN COALESCE(mfe_none, mfe, 0) != 0 AND COALESCE(active_trade, false) = false THEN 1 END) as dashboard_visible
FROM signal_lab_trades 
WHERE date BETWEEN '2024-09-01' AND '2024-09-03'
GROUP BY date 
ORDER BY date;

-- Step 2: Fix the discrepancy by marking all trades with MFE data as completed (non-active)
SELECT 'Applying Fix 1: Mark trades with MFE as completed' as step;
UPDATE signal_lab_trades 
SET active_trade = false 
WHERE COALESCE(mfe_none, mfe, 0) != 0
AND COALESCE(active_trade, false) = true;

-- Step 3: Mark all historical trades (before today) as completed
SELECT 'Applying Fix 2: Mark historical trades as completed' as step;
UPDATE signal_lab_trades 
SET active_trade = false 
WHERE date < CURRENT_DATE
AND COALESCE(active_trade, false) = true;

-- Step 4: Verify the fix
SELECT 'Verification After Fix' as step;
SELECT 
    date,
    COUNT(*) as total_trades,
    COUNT(CASE WHEN COALESCE(mfe_none, mfe, 0) != 0 THEN 1 END) as trades_with_mfe,
    COUNT(CASE WHEN COALESCE(active_trade, false) = true THEN 1 END) as active_trades,
    COUNT(CASE WHEN COALESCE(mfe_none, mfe, 0) != 0 AND COALESCE(active_trade, false) = false THEN 1 END) as dashboard_visible
FROM signal_lab_trades 
WHERE date BETWEEN '2024-09-01' AND '2024-09-03'
GROUP BY date 
ORDER BY date;