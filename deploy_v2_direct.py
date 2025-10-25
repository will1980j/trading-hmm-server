#!/usr/bin/env python3

import requests
import json

def deploy_v2_schema_direct():
    """Deploy V2 schema directly with better error handling"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    # Read the V2 schema
    try:
        with open('database/signal_lab_v2_schema.sql', 'r') as f:
            schema_sql = f.read()
    except FileNotFoundError:
        print("❌ Schema file not found!")
        return
    
    print("🚀 DEPLOYING SIGNAL LAB V2 SCHEMA")
    print("=" * 50)
    print(f"📋 Schema size: {len(schema_sql)} characters")
    
    # Create a minimal test payload first
    test_payload = {
        "schema_sql": "-- Test comment only"
    }
    
    print("\n🔍 Testing endpoint with minimal payload...")
    try:
        response = requests.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=test_payload,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Test successful: {result}")
        else:
            print(f"❌ Test failed: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Test request failed: {e}")
        return
    
    # Now try with the full schema
    print("\n🚀 Deploying full V2 schema...")
    
    deployment_payload = {
        "schema_sql": schema_sql
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=deployment_payload,
            timeout=120  # Longer timeout for full deployment
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ DEPLOYMENT SUCCESSFUL!")
            print(f"📊 V1 Trade Count: {result.get('v1_trade_count', 'Unknown')}")
            print(f"📋 Tables Created: {result.get('tables_created', [])}")
            print(f"💬 Message: {result.get('message', 'No message')}")
        else:
            print(f"❌ DEPLOYMENT FAILED!")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Raw response: {response.text}")
                
    except Exception as e:
        print(f"❌ Deployment request failed: {e}")

if __name__ == "__main__":
    deploy_v2_schema_direct()