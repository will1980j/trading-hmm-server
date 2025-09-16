#!/usr/bin/env python3
"""
Diagnose Signal Lab vs Dashboard Discrepancy
Identifies why the 1m Signal Lab shows more signals than the main dashboard
"""

import requests
import json
from datetime import datetime

def diagnose_signal_discrepancy():
    """Diagnose the discrepancy between Signal Lab and Dashboard"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("DIAGNOSING SIGNAL LAB vs DASHBOARD DISCREPANCY")
    print("=" * 60)
    
    try:
        # 1. Get Signal Lab data (all trades)
        print("Fetching Signal Lab data (all trades)...")
        lab_response = requests.get(f"{base_url}/api/signal-lab-trades", timeout=30)
        
        if lab_response.status_code == 200:
            lab_trades = lab_response.json()
            print(f"Signal Lab: {len(lab_trades)} total trades")
        else:
            print(f"Signal Lab request failed: {lab_response.status_code}")
            return
        
        # 2. Get Dashboard data (analysis_only=true)
        print("Fetching Dashboard data (processed trades only)...")
        dashboard_response = requests.get(f"{base_url}/api/signal-lab-trades?analysis_only=true", timeout=30)
        
        if dashboard_response.status_code == 200:
            dashboard_trades = dashboard_response.json()
            print(f"Dashboard: {len(dashboard_trades)} processed trades")
        else:
            print(f"Dashboard request failed: {dashboard_response.status_code}")
            return
        
        # 3. Analyze the differences
        print("\nANALYSIS RESULTS:")
        print("-" * 40)
        
        discrepancy = len(lab_trades) - len(dashboard_trades)
        print(f"Total discrepancy: {discrepancy} trades")
        
        if discrepancy > 0:
            print(f"WARNING: Signal Lab shows {discrepancy} more trades than Dashboard")
            
            # Analyze what types of trades are missing from dashboard
            lab_ids = {trade['id'] for trade in lab_trades}
            dashboard_ids = {trade['id'] for trade in dashboard_trades}
            missing_ids = lab_ids - dashboard_ids
            
            print(f"\nMissing from Dashboard: {len(missing_ids)} trades")
            
            # Categorize missing trades
            active_trades = 0
            no_mfe_trades = 0
            other_trades = 0
            
            for trade in lab_trades:
                if trade['id'] in missing_ids:
                    # Check if it's active (this field might not exist in response)
                    mfe_value = trade.get('mfe', 0) or trade.get('mfe_none', 0)
                    
                    if mfe_value == 0:
                        no_mfe_trades += 1
                    else:
                        other_trades += 1
            
            print(f"   Trades with no MFE data: {no_mfe_trades}")
            print(f"   Other missing trades: {other_trades}")
            
            # Show sample of missing trades
            print(f"\nSample of missing trades:")
            missing_sample = [t for t in lab_trades if t['id'] in missing_ids][:5]
            for trade in missing_sample:
                date = trade.get('date', 'N/A')
                time = trade.get('time', 'N/A')
                bias = trade.get('bias', 'N/A')
                mfe = trade.get('mfe', 0) or trade.get('mfe_none', 0)
                print(f"   ID {trade['id']}: {date} {time} {bias} (MFE: {mfe})")
        
        # 4. Check for date range differences
        print(f"\nDATE RANGE ANALYSIS:")
        print("-" * 30)
        
        if lab_trades:
            lab_dates = [t.get('date') for t in lab_trades if t.get('date')]
            lab_dates = [d for d in lab_dates if d and d != 'None']
            if lab_dates:
                print(f"Signal Lab: {min(lab_dates)} to {max(lab_dates)}")
            else:
                print("Signal Lab: No valid dates found")
        
        if dashboard_trades:
            dash_dates = [t.get('date') for t in dashboard_trades if t.get('date')]
            dash_dates = [d for d in dash_dates if d and d != 'None']
            if dash_dates:
                print(f"Dashboard: {min(dash_dates)} to {max(dash_dates)}")
            else:
                print("Dashboard: No valid dates found")
        
        # 5. Recommendations
        print(f"\nRECOMMENDATIONS:")
        print("-" * 25)
        
        if discrepancy > 0:
            print("1. Complete any active trades in Signal Lab to include them in Dashboard")
            print("2. Check if trades have MFE data filled in")
            print("3. Verify that completed trades are properly marked as non-active")
            print("4. Consider if the filtering logic needs adjustment")
        else:
            print("No discrepancy found - both systems are in sync!")
        
        return {
            'lab_count': len(lab_trades),
            'dashboard_count': len(dashboard_trades),
            'discrepancy': discrepancy,
            'status': 'success'
        }
        
    except Exception as e:
        print(f"Error during diagnosis: {str(e)}")
        return {'error': str(e), 'status': 'error'}

if __name__ == "__main__":
    result = diagnose_signal_discrepancy()
    print(f"\nDiagnosis complete: {result}")