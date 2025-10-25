#!/usr/bin/env python3
"""
🔍 ANALYZE CURRENT VALIDATION PATTERNS
Extract insights from existing Signal Lab data to understand validation criteria
"""

import requests
import json
from datetime import datetime

def analyze_signal_patterns():
    print("🔍 ANALYZING YOUR VALIDATION PATTERNS")
    print("=" * 60)
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    # Get Signal Lab data to analyze patterns
    print("\n📊 Step 1: Fetching Signal Lab Data")
    try:
        # Try to get signal lab data
        response = requests.get(f"{base_url}/api/signal-lab-data", timeout=15)
        
        if response.status_code == 200:
            try:
                data = response.json()
                signals = data.get('signals', [])
                print(f"✅ Found {len(signals)} validated signals in Signal Lab")
                
                if len(signals) > 0:
                    analyze_signal_characteristics(signals)
                else:
                    print("❌ No signals found - need Signal Lab data to analyze patterns")
                    
            except Exception as e:
                print(f"❌ JSON parse error: {e}")
        else:
            print(f"❌ API failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Get raw TradingView signals to compare
    print("\n📡 Step 2: Checking Raw TradingView Signals")
    try:
        response = requests.get(f"{base_url}/api/recent-signals", timeout=15)
        
        if response.status_code == 200:
            try:
                data = response.json()
                raw_signals = data.get('signals', [])
                print(f"✅ Found {len(raw_signals)} raw TradingView signals")
                
                if len(raw_signals) > 0:
                    analyze_raw_vs_validated(raw_signals)
                    
            except Exception as e:
                print(f"❌ JSON parse error: {e}")
        else:
            print(f"❌ API failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def analyze_signal_characteristics(signals):
    """Analyze characteristics of validated signals"""
    print("\n🎯 VALIDATED SIGNAL ANALYSIS:")
    print("-" * 40)
    
    # Basic stats
    total_signals = len(signals)
    bullish_count = sum(1 for s in signals if s.get('bias', '').lower() == 'bullish')
    bearish_count = sum(1 for s in signals if s.get('bias', '').lower() == 'bearish')
    
    print(f"📈 Total Validated Signals: {total_signals}")
    print(f"🔵 Bullish Signals: {bullish_count} ({bullish_count/total_signals*100:.1f}%)")
    print(f"🔴 Bearish Signals: {bearish_count} ({bearish_count/total_signals*100:.1f}%)")
    
    # Session analysis
    sessions = {}
    for signal in signals:
        session = signal.get('session', 'Unknown')
        sessions[session] = sessions.get(session, 0) + 1
    
    print(f"\n⏰ SESSION DISTRIBUTION:")
    for session, count in sorted(sessions.items()):
        print(f"   {session}: {count} signals ({count/total_signals*100:.1f}%)")
    
    # MFE analysis
    mfe_values = []
    for signal in signals:
        mfe = signal.get('mfe', 0) or signal.get('mfe_none', 0)
        if mfe and mfe != 0:
            mfe_values.append(float(mfe))
    
    if mfe_values:
        avg_mfe = sum(mfe_values) / len(mfe_values)
        print(f"\n📊 MFE ANALYSIS:")
        print(f"   Signals with MFE: {len(mfe_values)}/{total_signals}")
        print(f"   Average MFE: {avg_mfe:.2f}R")
        print(f"   Best MFE: {max(mfe_values):.2f}R")
        print(f"   Worst MFE: {min(mfe_values):.2f}R")
    
    # Recent signals for pattern analysis
    print(f"\n📋 RECENT VALIDATED SIGNALS (Last 10):")
    for i, signal in enumerate(signals[:10]):
        date = signal.get('date', 'Unknown')
        time = signal.get('time', 'Unknown')
        bias = signal.get('bias', 'Unknown')
        session = signal.get('session', 'Unknown')
        mfe = signal.get('mfe', 0) or signal.get('mfe_none', 0) or 0
        print(f"   {i+1}. {date} {time} - {bias} {session} - MFE: {mfe}R")

def analyze_raw_vs_validated(raw_signals):
    """Compare raw TradingView signals vs validated Signal Lab entries"""
    print(f"\n🔄 RAW vs VALIDATED COMPARISON:")
    print("-" * 40)
    
    print(f"📡 Raw TradingView Signals: {len(raw_signals)}")
    print("📋 Recent Raw Signals:")
    
    for i, signal in enumerate(raw_signals[:10]):
        timestamp = signal.get('timestamp', 'Unknown')
        bias = signal.get('bias', 'Unknown')
        symbol = signal.get('symbol', 'Unknown')
        print(f"   {i+1}. {timestamp} - {symbol} {bias}")

if __name__ == "__main__":
    analyze_signal_patterns()