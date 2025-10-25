#!/usr/bin/env python3
"""
🧠 EXTRACT VALIDATION KNOWLEDGE
Analyze existing Signal Lab data to understand your validation patterns
"""

import requests
import json
from datetime import datetime
import sys

def extract_validation_knowledge():
    print("🧠 EXTRACTING YOUR VALIDATION KNOWLEDGE")
    print("=" * 60)
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    # Step 1: Get Signal Lab trades (your validated signals)
    print("\n📊 Step 1: Analyzing Signal Lab Trades (Your Validated Signals)")
    try:
        response = requests.get(f"{base_url}/api/signal-lab-trades", timeout=15)
        
        if response.status_code == 200:
            try:
                validated_signals = response.json()
                print(f"✅ Found {len(validated_signals)} validated signals")
                
                if len(validated_signals) > 0:
                    analyze_validated_patterns(validated_signals)
                else:
                    print("❌ No validated signals found in Signal Lab")
                    
            except Exception as e:
                print(f"❌ JSON parse error: {e}")
                print("Response might be HTML (login required)")
        else:
            print(f"❌ API failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Step 2: Get live signals (raw TradingView signals)
    print("\n📡 Step 2: Analyzing Live Signals (Raw TradingView)")
    try:
        response = requests.get(f"{base_url}/api/live-signals", timeout=15)
        
        if response.status_code == 200:
            try:
                raw_signals = response.json()
                print(f"✅ Found {len(raw_signals)} raw TradingView signals")
                
                if len(raw_signals) > 0:
                    analyze_raw_signals(raw_signals)
                    
            except Exception as e:
                print(f"❌ JSON parse error: {e}")
        else:
            print(f"❌ API failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Step 3: Provide next steps
    provide_next_steps()

def analyze_validated_patterns(signals):
    """Analyze your validated Signal Lab entries to understand patterns"""
    print("\n🎯 YOUR VALIDATION PATTERNS:")
    print("-" * 50)
    
    total = len(signals)
    
    # Bias distribution
    bullish = sum(1 for s in signals if s.get('bias', '').lower() == 'bullish')
    bearish = sum(1 for s in signals if s.get('bias', '').lower() == 'bearish')
    
    print(f"📈 Signal Distribution:")
    print(f"   🔵 Bullish: {bullish} ({bullish/total*100:.1f}%)")
    print(f"   🔴 Bearish: {bearish} ({bearish/total*100:.1f}%)")
    
    # Session preferences
    sessions = {}
    for signal in signals:
        session = signal.get('session', 'Unknown')
        sessions[session] = sessions.get(session, 0) + 1
    
    print(f"\n⏰ Session Preferences:")
    for session, count in sorted(sessions.items(), key=lambda x: x[1], reverse=True):
        print(f"   {session}: {count} signals ({count/total*100:.1f}%)")
    
    # Performance analysis
    mfe_values = []
    successful_signals = 0
    
    for signal in signals:
        mfe = signal.get('mfe') or signal.get('mfe_none', 0)
        if mfe and mfe != 0:
            mfe_values.append(float(mfe))
            if float(mfe) > 1.0:  # Assuming 1R+ is successful
                successful_signals += 1
    
    if mfe_values:
        avg_mfe = sum(mfe_values) / len(mfe_values)
        success_rate = (successful_signals / len(mfe_values)) * 100
        
        print(f"\n📊 Performance Metrics:")
        print(f"   Signals with MFE: {len(mfe_values)}/{total}")
        print(f"   Average MFE: {avg_mfe:.2f}R")
        print(f"   Success Rate (1R+): {success_rate:.1f}%")
        print(f"   Best Signal: {max(mfe_values):.2f}R")
        print(f"   Worst Signal: {min(mfe_values):.2f}R")
    
    # Recent validated signals
    print(f"\n📋 Recent Validated Signals (Last 10):")
    recent_signals = sorted(signals, key=lambda x: f"{x.get('date', '')}{x.get('time', '')}", reverse=True)[:10]
    
    for i, signal in enumerate(recent_signals):
        date = signal.get('date', 'N/A')
        time = signal.get('time', 'N/A')
        bias = signal.get('bias', 'N/A')
        session = signal.get('session', 'N/A')
        mfe = signal.get('mfe') or signal.get('mfe_none', 0) or 'N/A'
        signal_type = signal.get('signal_type', 'N/A')
        
        print(f"   {i+1}. {date} {time} - {bias} {session} - {signal_type} - MFE: {mfe}R")

def analyze_raw_signals(signals):
    """Analyze raw TradingView signals to understand what you're filtering"""
    print(f"\n📡 RAW TRADINGVIEW SIGNALS:")
    print("-" * 50)
    
    total = len(signals)
    
    # Bias distribution in raw signals
    bullish = sum(1 for s in signals if s.get('bias', '').lower() == 'bullish')
    bearish = sum(1 for s in signals if s.get('bias', '').lower() == 'bearish')
    
    print(f"📈 Raw Signal Distribution:")
    print(f"   🔵 Bullish: {bullish} ({bullish/total*100:.1f}%)")
    print(f"   🔴 Bearish: {bearish} ({bearish/total*100:.1f}%)")
    
    # Recent raw signals
    print(f"\n📋 Recent Raw Signals (Last 10):")
    recent_signals = sorted(signals, key=lambda x: x.get('timestamp', ''), reverse=True)[:10]
    
    for i, signal in enumerate(recent_signals):
        timestamp = signal.get('timestamp', 'N/A')
        bias = signal.get('bias', 'N/A')
        symbol = signal.get('symbol', 'N/A')
        price = signal.get('price', 'N/A')
        
        print(f"   {i+1}. {timestamp} - {symbol} {bias} @ {price}")

def provide_next_steps():
    """Provide clear next steps for building automation"""
    print(f"\n🚀 NEXT STEPS TO BUILD AUTOMATION:")
    print("=" * 60)
    
    print(f"\n📝 WHAT I NEED FROM YOU:")
    print(f"1. **Signal Validation Criteria** - What makes a signal valid?")
    print(f"   • Market conditions you look for")
    print(f"   • Technical indicators you check")
    print(f"   • Time-based rules you follow")
    print(f"   • News/event considerations")
    
    print(f"\n2. **MFE Calculation Rules** - How do you determine MFE?")
    print(f"   • What price levels do you use?")
    print(f"   • How do you handle different market conditions?")
    print(f"   • What timeframes do you consider?")
    
    print(f"\n3. **Rejection Criteria** - Why do you reject signals?")
    print(f"   • What makes a signal invalid?")
    print(f"   • Common patterns you avoid")
    print(f"   • Market conditions that disqualify signals")
    
    print(f"\n🎯 HOW WE'LL BUILD IT:")
    print(f"1. **Knowledge Capture** - Document your validation rules")
    print(f"2. **Pattern Analysis** - Analyze your historical decisions")
    print(f"3. **ML Training** - Train models on your validation patterns")
    print(f"4. **Automation Pipeline** - Build TradingView → Validation → Signal Lab")
    print(f"5. **Continuous Learning** - System improves with each validation")
    
    print(f"\n💡 READY TO START?")
    print(f"Share your validation criteria and we'll begin building!")

if __name__ == "__main__":
    extract_validation_knowledge()