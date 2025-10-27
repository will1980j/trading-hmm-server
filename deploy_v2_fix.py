#!/usr/bin/env python3

import subprocess
import sys
import time

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} successful")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} failed")
            print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def deploy_v2_fix():
    """Deploy the V2 dashboard fix"""
    print("🚀 Deploying V2 Dashboard Fix")
    print("=" * 50)
    
    # Check git status
    if not run_command("git status", "Checking git status"):
        return False
    
    # Add the changed file
    if not run_command("git add web_server.py", "Adding web_server.py"):
        return False
    
    # Commit the changes
    commit_message = "Fix V2 dashboard: Update active-trades endpoint to use signal_lab_v2_trades table"
    if not run_command(f'git commit -m "{commit_message}"', "Committing changes"):
        return False
    
    # Push to main branch
    if not run_command("git push origin main", "Pushing to Railway"):
        return False
    
    print("\n🎯 Deployment initiated!")
    print("⏱️  Railway will automatically deploy in 2-3 minutes")
    print("🔗 Monitor deployment: https://railway.app/dashboard")
    
    # Wait a moment and test
    print("\n⏳ Waiting 30 seconds before testing...")
    time.sleep(30)
    
    # Test the fix
    print("\n🧪 Testing V2 endpoints after deployment...")
    import requests
    
    try:
        response = requests.get('https://web-production-cd33.up.railway.app/api/v2/active-trades', timeout=10)
        if response.status_code == 200:
            data = response.json()
            trades = data.get('trades', [])
            print(f"✅ V2 Active Trades: {len(trades)} trades found")
            if trades:
                print(f"   First trade ID: {trades[0].get('id', 'N/A')}")
                print(f"   First trade bias: {trades[0].get('bias', 'N/A')}")
        else:
            print(f"❌ V2 Active Trades test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ V2 Active Trades test error: {e}")
    
    print("\n🎉 V2 Dashboard fix deployment complete!")
    print("🌐 Check your dashboard: https://web-production-cd33.up.railway.app/signal-lab-v2")

if __name__ == '__main__':
    deploy_v2_fix()