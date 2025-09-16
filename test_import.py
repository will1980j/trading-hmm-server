#!/usr/bin/env python3

print("Starting import test...")

try:
    print("1. Testing basic imports...")
    from flask import Flask
    print("   Flask imported successfully")
    
    from flask_cors import CORS
    print("   CORS imported successfully")
    
    from flask_socketio import SocketIO
    print("   SocketIO imported successfully")
    
    print("2. Testing dotenv...")
    from dotenv import load_dotenv
    load_dotenv()
    print("   dotenv loaded successfully")
    
    print("3. Testing custom modules...")
    from csrf_protection import csrf, csrf_protect
    print("   csrf_protection imported successfully")
    
    from ai_prompts import get_ai_system_prompt
    print("   ai_prompts imported successfully")
    
    from news_api import NewsAPI
    print("   news_api imported successfully")
    
    from auth import login_required
    print("   auth imported successfully")
    
    print("4. All imports successful!")
    
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()