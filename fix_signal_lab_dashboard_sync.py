#!/usr/bin/env python3
"""
Fix Signal Lab Dashboard Sync
Ensures all processed trades appear in both Signal Lab and Dashboard
"""

import requests
import json

def fix_signal_lab_dashboard_sync():
    """Fix the sync between Signal Lab and Dashboard"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("FIXING SIGNAL LAB <-> DASHBOARD SYNC")
    print("=" * 50)
    
    try:
        # Use the new reconciliation endpoint to analyze the issue
        print("1. Analyzing discrepancies...")
        
        # First, get analysis
        response = requests.get(f"{base_url}/api/signal-lab-reconcile")
        
        if response.status_code == 200:
            analysis = response.json()
            
            if analysis['status'] == 'success':
                data = analysis['analysis']
                
                print(f"   Total Signal Lab trades: {data['total_trades']}")
                print(f"   Dashboard visible trades: {data['dashboard_trades']}")
                print(f"   Discrepancy: {data['discrepancy']} trades")
                
                if data['discrepancy'] > 0:
                    print(f"\\n   Missing categories:")
                    print(f"   - No MFE data: {data['missing_categories']['no_mfe_data']}")
                    print(f"   - Active trades: {data['missing_categories']['active_trades']}")
                    print(f"   - Both issues: {data['missing_categories']['both_issues']}")
                    
                    print(f"\\n   Sample missing trades:")
                    for trade in data['sample_missing'][:5]:
                        print(f"   ID {trade['id']}: {trade['date']} {trade['time']} {trade['bias']} (MFE: {trade['mfe']}, Active: {trade['active']})")
                    
                    # Apply the fix
                    print(f"\\n2. Applying fix...")
                    
                    fix_response = requests.post(
                        f"{base_url}/api/signal-lab-reconcile",
                        json={'action': 'sync_all'},
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if fix_response.status_code == 200:
                        fix_result = fix_response.json()
                        if fix_result['status'] == 'success':
                            print(f"   SUCCESS: {fix_result['message']}")
                            print(f"   Synced {fix_result['synced_count']} trades to dashboard")
                        else:
                            print(f"   ERROR: {fix_result.get('error', 'Unknown error')}")
                    else:
                        print(f"   ERROR: Fix request failed with status {fix_response.status_code}")
                        print(f"   Response: {fix_response.text}")
                
                else:
                    print("   No discrepancies found - systems are already in sync!")
                
            else:
                print(f"   ERROR: {analysis.get('error', 'Unknown error')}")
        
        else:
            print(f"   ERROR: Analysis request failed with status {response.status_code}")
            print(f"   This might be an authentication issue or the endpoint doesn't exist yet")
            
            # Fallback: Try the direct approach
            print(f"\\n   Trying direct approach...")
            
            # Try to mark all completed trades as non-active
            # This is the most likely fix based on the filtering logic
            print(f"   The issue is likely that completed trades are still marked as 'active'")
            print(f"   Dashboard only shows: trades with MFE data AND active_trade = false")
            print(f"   Signal Lab shows: all trades regardless of active status")
            print(f"\\n   SOLUTION: Mark all trades with MFE data as completed (active_trade = false)")
            
        print(f"\\n3. Verification...")
        print(f"   After applying the fix, both Signal Lab and Dashboard should show the same")
        print(f"   processed trades (trades that have MFE data filled in).")
        print(f"\\n   The difference should only be active/incomplete trades that appear")
        print(f"   in Signal Lab but not Dashboard (which is the intended behavior).")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    fix_signal_lab_dashboard_sync()