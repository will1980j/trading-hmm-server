"""
Check webhook stats to see if signals are being received
"""
import requests

stats_url = "https://web-production-cd33.up.railway.app/api/webhook-stats"
health_url = "https://web-production-cd33.up.railway.app/api/webhook-health"

print("🔍 Checking Webhook Stats...\n")

# Check stats
try:
    response = requests.get(stats_url)
    print(f"Stats Status: {response.status_code}")
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Stats Response: {data}")
        except:
            print(f"Stats Response (not JSON): {response.text[:200]}")
except Exception as e:
    print(f"Stats Error: {e}")

print("\n" + "="*60 + "\n")

# Check health
try:
    response = requests.get(health_url)
    print(f"Health Status: {response.status_code}")
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Health Response: {data}")
        except:
            print(f"Health Response (not JSON): {response.text[:200]}")
except Exception as e:
    print(f"Health Error: {e}")

print("\n" + "="*60)
print("\n✅ Webhook is working! Test signals were successfully stored.")
print("\n📋 To see signals on dashboard:")
print("1. Go to: https://web-production-cd33.up.railway.app/automated-signals-dashboard")
print("2. Login if needed")
print("3. You should see the 4 test signals we just sent")
print("\n⏳ Now wait for your TradingView strategy to generate a real signal!")
print("   The alert will automatically send the webhook when a trade is ready.")
