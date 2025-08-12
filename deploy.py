#!/usr/bin/env python3
"""
Quick Railway deployment script
"""
import subprocess
import sys
import os

def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(f"Running: {cmd}")
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode == 0

def main():
    print("🚀 Deploying to Railway...")
    
    # Check if railway CLI is installed
    if not run_command("railway --version"):
        print("❌ Railway CLI not found. Install it first:")
        print("npm install -g @railway/cli")
        return
    
    # Login to Railway
    print("📝 Login to Railway...")
    run_command("railway login")
    
    # Create new project
    print("🆕 Creating Railway project...")
    run_command("railway new")
    
    # Add PostgreSQL
    print("🗄️ Adding PostgreSQL...")
    run_command("railway add postgresql")
    
    # Deploy
    print("🚀 Deploying...")
    run_command("railway up")
    
    # Get domain
    print("🌐 Getting domain...")
    run_command("railway domain")
    
    print("✅ Deployment complete!")
    print("Update your Chrome extension with the new Railway URL")

if __name__ == "__main__":
    main()