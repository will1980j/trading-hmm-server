#!/usr/bin/env python3
"""Check actual database schema columns"""
import os
import requests

BASE_URL = "https://web-production-f8c3.up.railway.app"

# Use a diagnostic endpoint to check schema
response = requests.get(f"{BASE_URL}/api/automated-signals/stats-live")
print(f"Stats endpoint: {response.status_code}")
print(response.text[:500] if response.text else "No response")

# Try the trade detail endpoint directly
response2 = requests.get(f"{BASE_URL}/api/automated-signals/trade-detail/TEST_LIFECYCLE_1764490530")
print(f"\nTrade detail endpoint: {response2.status_code}")
print(response2.text[:1000] if response2.text else "No response")
