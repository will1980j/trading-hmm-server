#!/usr/bin/env python3
"""
Setup script for new machine deployment
Run this on your personal laptop after cloning the repo
"""

import os
import subprocess
import sys
from pathlib import Path

def check_python():
    """Check Python version"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_dependencies():
    """Install Python dependencies"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def create_env_template():
    """Create .env file from template"""
    env_path = Path(".env")
    if env_path.exists():
        print("✅ .env file already exists")
        return True
    
    # Copy from example and prompt for values
    with open(".env.example", "r") as f:
        template = f.read()
    
    print("\n📝 Creating .env file...")
    print("You'll need to add your actual API keys and credentials")
    
    with open(".env", "w") as f:
        f.write(template)
    
    print("✅ .env template created - EDIT WITH YOUR ACTUAL KEYS!")
    return True

def check_chrome_extension():
    """Check Chrome extension setup"""
    ext_path = Path("chrome-extension")
    if ext_path.exists() and (ext_path / "manifest.json").exists():
        print("✅ Chrome extension ready")
        print("   → Load in Chrome: Extensions → Developer mode → Load unpacked")
        return True
    print("❌ Chrome extension not found")
    return False

def main():
    print("🚀 Setting up Trading HMM Server on new machine...\n")
    
    # Check requirements
    if not check_python():
        return
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Setup environment
    if not create_env_template():
        return
    
    # Check extension
    check_chrome_extension()
    
    print("\n✅ Setup complete!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your actual API keys")
    print("2. Load Chrome extension from chrome-extension/ folder")
    print("3. Run: python web_server.py")
    print("4. Install Amazon Q Developer extension in your IDE")

if __name__ == "__main__":
    main()