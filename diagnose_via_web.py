import requests
import json

BASE_URL = "https://web-production-cd33.up.railway.app"

def diagnose_dashboard_data():
    """Diagnose dashboard data via web API"""
    
    print("=" * 80)
    print("DASHBOARD DATA DIAGNOSTIC")
    print("=" * 80)
    
    # Get dashboard data
    print("\n1. FETCHING DASHBOARD DATA:")
    print("-" * 80)
    
    response = requests.get(f"{BASE_URL}/api/automated-signals/dashboard-data")
    data = response.json()
    
    if not data.get('success'):
        print("ERROR: Dashboard API returned failure")
        print(json.dumps(data, indent=2))
        return
    
    signals = data.get('signals', [])
    print(f"\nTotal signals returned: {len(signals)}")
    
    # Analyze first 10 signals
    print("\n2. ANALYZING FIRST 10 SIGNALS:")
    print("-" * 80)
    
    for i, signal in enumerate(signals[:10], 1):
        print(f"\n  Signal #{i}:")
        print(f"    Trade ID: {signal.get('trade_id')}")
        print(f"    Status: {signal.get('status')}")
        print(f"    Trade Status: {signal.get('trade_status')}")
        print(f"    Direction: {signal.get('direction')}")
        print(f"    BE MFE: {signal.get('be_mfe')}")
        print(f"    No BE MFE: {signal.get('no_be_mfe')}")
        print(f"    Entry Price: {signal.get('entry_price')}")
        print(f"    Stop Loss: {signal.get('stop_loss')}")
        print(f"    Session: {signal.get('session')}")
        print(f"    Signal Time: {signal.get('signal_time')}")
    
    # Count statuses
    print("\n\n3. STATUS DISTRIBUTION:")
    print("-" * 80)
    
    status_counts = {}
    trade_status_counts = {}
    
    for signal in signals:
        status = signal.get('status', 'unknown')
        trade_status = signal.get('trade_status', 'unknown')
        
        status_counts[status] = status_counts.get(status, 0) + 1
        trade_status_counts[trade_status] = trade_status_counts.get(trade_status, 0) + 1
    
    print("\nStatus field:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")
    
    print("\nTrade Status field:")
    for status, count in sorted(trade_status_counts.items()):
        print(f"  {status}: {count}")
    
    # Count missing MFE
    print("\n\n4. MFE ANALYSIS:")
    print("-" * 80)
    
    missing_be_mfe = sum(1 for s in signals if not s.get('be_mfe') or s.get('be_mfe') == 0)
    missing_no_be_mfe = sum(1 for s in signals if not s.get('no_be_mfe') or s.get('no_be_mfe') == 0)
    
    print(f"\nSignals missing BE MFE: {missing_be_mfe} / {len(signals)}")
    print(f"Signals missing No BE MFE: {missing_no_be_mfe} / {len(signals)}")
    
    # Show signals with missing MFE
    print("\nSignals with missing MFE:")
    for signal in signals[:10]:
        if not signal.get('be_mfe') or not signal.get('no_be_mfe'):
            print(f"  {signal.get('trade_id')}: BE={signal.get('be_mfe')}, No BE={signal.get('no_be_mfe')}")
    
    print("\n" + "=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    diagnose_dashboard_data()
