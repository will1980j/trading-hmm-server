"""
Test the automated signals webhook with strategy format
"""
import requests
import json

# Test data matching the strategy's JSON format
test_signal_created = {
    "type": "signal_created",
    "signal_id": "20241110_143025_BULLISH",
    "date": "2024-11-10",
    "time": "14:30:25",
    "bias": "Bullish",
    "session": "NY PM",
    "entry_price": 4156.25,
    "sl_price": 4153.75,
    "risk_distance": 2.50,
    "be_price": 4156.25,
    "target_1r": 4158.75,
    "target_2r": 4161.25,
    "target_3r": 4163.75,
    "be_hit": False,
    "be_mfe": 0.00,
    "no_be_mfe": 0.00,
    "status": "active",
    "timestamp": 1699632625000
}

test_mfe_update = {
    "type": "mfe_update",
    "signal_id": "20241110_143025_BULLISH",
    "current_price": 4157.50,
    "be_mfe": 0.50,
    "no_be_mfe": 0.50,
    "lowest_low": 4155.00,
    "highest_high": 4157.50,
    "status": "active",
    "timestamp": 1699632685000
}

test_be_triggered = {
    "type": "be_triggered",
    "signal_id": "20241110_143025_BULLISH",
    "be_hit": True,
    "be_mfe": 1.00,
    "no_be_mfe": 1.00,
    "timestamp": 1699632745000
}

test_signal_completed = {
    "type": "signal_completed",
    "signal_id": "20241110_143025_BULLISH",
    "completion_reason": "be_stop_loss_hit",
    "final_be_mfe": 2.50,
    "final_no_be_mfe": 3.25,
    "status": "completed",
    "timestamp": 1699633805000
}

webhook_url = "https://web-production-cd33.up.railway.app/api/automated-signals"

print("🧪 Testing Strategy Webhook Format\n")
print("=" * 60)

# Test 1: Signal Created
print("\n1️⃣ Testing SIGNAL CREATED...")
print(f"Payload: {json.dumps(test_signal_created, indent=2)}")
response = requests.post(webhook_url, json=test_signal_created)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

# Test 2: MFE Update
print("\n2️⃣ Testing MFE UPDATE...")
print(f"Payload: {json.dumps(test_mfe_update, indent=2)}")
response = requests.post(webhook_url, json=test_mfe_update)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

# Test 3: BE Triggered
print("\n3️⃣ Testing BE TRIGGERED...")
print(f"Payload: {json.dumps(test_be_triggered, indent=2)}")
response = requests.post(webhook_url, json=test_be_triggered)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

# Test 4: Signal Completed
print("\n4️⃣ Testing SIGNAL COMPLETED...")
print(f"Payload: {json.dumps(test_signal_completed, indent=2)}")
response = requests.post(webhook_url, json=test_signal_completed)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

print("\n" + "=" * 60)
print("✅ All tests completed!")
print("\nNow check the Automated Signals Dashboard:")
print("https://web-production-cd33.up.railway.app/automated-signals-dashboard")
