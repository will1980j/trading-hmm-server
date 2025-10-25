#!/usr/bin/env python3

import requests
import json

class AuthenticatedAPIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.authenticated = False
    
    def login(self, username="admin", password="n2351447"):
        """Login to get authenticated session"""
        print(f"🔐 Logging in as {username}...")
        
        # First get the login page to establish session
        login_page = self.session.get(f"{self.base_url}/login")
        print(f"Login page status: {login_page.status_code}")
        
        # Submit login credentials
        login_data = {
            'username': username,
            'password': password
        }
        
        response = self.session.post(
            f"{self.base_url}/login",
            data=login_data,
            allow_redirects=False
        )
        
        print(f"Login response status: {response.status_code}")
        
        if response.status_code == 302:  # Redirect means success
            print("✅ Login successful!")
            self.authenticated = True
            return True
        else:
            print(f"❌ Login failed: {response.text[:200]}")
            return False
    
    def deploy_schema(self, schema_sql):
        """Deploy schema using authenticated session"""
        if not self.authenticated:
            print("❌ Not authenticated!")
            return None
        
        payload = {"schema_sql": schema_sql}
        
        try:
            print(f"📡 Sending request to {self.base_url}/api/deploy-signal-lab-v2...")
            response = self.session.post(
                f"{self.base_url}/api/deploy-signal-lab-v2",
                json=payload,
                timeout=180  # Longer timeout for large schema
            )
            print(f"📨 Response received: {response.status_code}")
            return response
        except requests.exceptions.Timeout:
            print(f"⏰ Request timed out after 180 seconds")
            return None
        except Exception as e:
            print(f"❌ Request exception: {e}")
            return None

def deploy_v2_with_auth():
    """Deploy V2 schema with proper authentication"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    # Read the V2 schema
    try:
        with open('database/signal_lab_v2_schema.sql', 'r') as f:
            schema_sql = f.read()
    except FileNotFoundError:
        print("❌ Schema file not found!")
        return
    
    print("🚀 AUTHENTICATED SIGNAL LAB V2 DEPLOYMENT")
    print("=" * 60)
    print(f"📋 Schema size: {len(schema_sql)} characters")
    
    # Create authenticated client
    client = AuthenticatedAPIClient(base_url)
    
    # Login first
    if not client.login():
        print("❌ Authentication failed!")
        return
    
    # Test with minimal payload first
    print("\n🔍 Testing with minimal payload...")
    try:
        test_response = client.deploy_schema("-- Test comment only")
        
        if test_response:
            print(f"Test Status: {test_response.status_code}")
            
            if test_response.status_code == 200:
                result = test_response.json()
                print(f"✅ Test successful: {result}")
            else:
                print(f"❌ Test failed: {test_response.text}")
                return
        else:
            print("❌ No test response received")
            return
    except Exception as e:
        print(f"❌ Test request failed: {e}")
        return
    
    # Deploy full schema
    print("\n🚀 Deploying full V2 schema...")
    try:
        response = client.deploy_schema(schema_sql)
        
        if response:
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
        else:
            print("❌ No response received")
    except Exception as e:
        print(f"❌ Deployment request failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    deploy_v2_with_auth()