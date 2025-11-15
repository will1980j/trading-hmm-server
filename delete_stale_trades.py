import requests

BASE_URL = "https://web-production-cd33.up.railway.app"

print("=" * 80)
print("DELETING STALE TRADES (0.0 MFE)")
print("=" * 80)

# Get active trades
response = requests.get(f"{BASE_URL}/api/automated-signals/dashboard-data")
data = response.json()

trades_to_delete = []

for trade in data['active_trades']:
    trade_id = trade['trade_id']
    be_mfe = trade.get('be_mfe', 0)
    no_be_mfe = trade.get('no_be_mfe', 0)
    
    # Only delete if BOTH MFE values are 0
    if be_mfe == 0 and no_be_mfe == 0:
        trades_to_delete.append(trade_id)

print(f"\nFound {len(trades_to_delete)} stale trades to delete:")
for trade_id in trades_to_delete:
    print(f"  - {trade_id}")

if not trades_to_delete:
    print("\nNo stale trades found!")
    exit(0)

print(f"\n⚠️  WARNING: This will delete {len(trades_to_delete)} trades!")
confirm = input("Type 'DELETE' to confirm: ")

if confirm != "DELETE":
    print("\n❌ Deletion cancelled")
    exit(0)

print("\n" + "=" * 80)
print("DELETING TRADES...")
print("=" * 80)

deleted_count = 0
failed_count = 0

for trade_id in trades_to_delete:
    try:
        response = requests.delete(f"{BASE_URL}/api/automated-signals/delete/{trade_id}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Deleted {trade_id}: {result.get('rows_deleted', 0)} rows")
            deleted_count += 1
        else:
            print(f"❌ Failed to delete {trade_id}: {response.status_code}")
            failed_count += 1
    except Exception as e:
        print(f"❌ Error deleting {trade_id}: {e}")
        failed_count += 1

print("\n" + "=" * 80)
print("DELETION COMPLETE")
print("=" * 80)
print(f"Successfully deleted: {deleted_count}")
print(f"Failed: {failed_count}")
print(f"\nRefresh the dashboard to see updated data.")
