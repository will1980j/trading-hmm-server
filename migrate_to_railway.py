#!/usr/bin/env python3
"""
Migrate environment variables to Railway
This eliminates the need for local .env files
"""

import os
from pathlib import Path

def read_env_file():
    """Read current .env file"""
    env_vars = {}
    env_path = Path(".env")
    
    if not env_path.exists():
        print("❌ .env file not found")
        return None
    
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()
    
    return env_vars

def generate_railway_commands():
    """Generate Railway CLI commands to set environment variables"""
    env_vars = read_env_file()
    if not env_vars:
        return
    
    print("🚀 Railway Environment Variable Setup Commands:")
    print("Run these commands in your terminal (requires Railway CLI):\n")
    
    # Filter out local development variables
    skip_vars = {"HOST", "PORT", "DEBUG"}
    
    for key, value in env_vars.items():
        if key not in skip_vars:
            # Mask sensitive values in output
            display_value = value
            if "key" in key.lower() or "secret" in key.lower() or "token" in key.lower():
                display_value = f"{value[:8]}..." if len(value) > 8 else "***"
            
            print(f"railway variables set {key}={display_value}")
    
    print(f"\n✅ Found {len([k for k in env_vars.keys() if k not in skip_vars])} variables to migrate")
    print("\n📋 After running these commands:")
    print("1. Your app will use Railway's environment variables")
    print("2. No need for .env files on any machine")
    print("3. Secrets are securely stored in Railway")

def generate_env_check():
    """Generate a script to verify environment variables"""
    check_script = '''#!/usr/bin/env python3
"""
Verify all required environment variables are set
"""

import os

required_vars = [
    "OPENAI_API_KEY",
    "OPENAI_MODEL", 
    "SECRET_KEY"
]

optional_vars = [
    "DATABASE_URL",
    "DISCORD_WEBHOOK_URL",
    "SLACK_WEBHOOK_URL",
    "TELEGRAM_BOT_TOKEN"
]

def check_env():
    print("🔍 Checking environment variables...")
    
    missing_required = []
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
        else:
            print(f"✅ {var}")
    
    if missing_required:
        print(f"\\n❌ Missing required variables: {missing_required}")
        return False
    
    print(f"\\n📋 Optional variables:")
    for var in optional_vars:
        status = "✅" if os.getenv(var) else "⚪"
        print(f"{status} {var}")
    
    print("\\n✅ Environment check complete!")
    return True

if __name__ == "__main__":
    check_env()
'''
    
    with open("check_env.py", "w") as f:
        f.write(check_script)
    
    print("✅ Created check_env.py - run this to verify your environment")

def main():
    print("🔧 Railway Migration Helper\n")
    generate_railway_commands()
    print("\n" + "="*50)
    generate_env_check()

if __name__ == "__main__":
    main()