import requests

print("Checking what event types are in the database...")

# This would need direct database access, but let's check via a test webhook
test_completion = {
    "type": "signal_completed",
    "signal_id": "TEST_COMPLETION_CHECK",
    "completion_reason": "be_stop_loss_hit",
    "final_be_mfe": 2.5,
    "final_no_be_mfe": 3.0,
    "status": "completed",
    "timestamp": 1699632652000
}

response = requests.post(
    "https://web-production-cd33.up.railway.app/api/automated-signals",
    json=test_completion
)

print(f"Completion webhook test: {response.status_code}")
print(f"Response: {response.text[:500]}")

# Check if it created an EXIT event
print("\nNow checking active trades...")
r = requests.get("https://web-production-cd33.up.railway.app/api/automated-signals/dashboard-data")
data = r.json()
print(f"Active trades: {len(data['active_trades'])}")
print(f"Completed trades: {len(data['completed_trades'])}")
