#!/usr/bin/env python3
"""
Signal Lab Population Diagnostic Tool
Checks why signals aren't populating the 1m Signal Lab
"""

import requests
import json
from datetime import datetime, timedelta

# Your Railway deployment URL
RAILWAY_URL = "https://web-production-cd33.up.railway.app"

def check_server_health():
    """Check if the server is running"""
    try:
        response = requests.get(f"{RAILWAY_URL}/health", timeout=10)
        print(f"Server Health: {response.status_code} - OK")
        if response.status_code == 200:
            data = response.json()
            print(f"   Database: {data.get('database', 'unknown')}")
            print(f"   Status: {data.get('status', 'unknown')}")
        return True
    except Exception as e:
        print(f"Server Health Check Failed: {e}")
        return False

def check_recent_signals():
    """Check recent live signals"""
    try:
        response = requests.get(f"{RAILWAY_URL}/api/live-signals?limit=20", timeout=10)
        if response.status_code == 200:
            data = response.json()
            signals = data.get('signals', [])
            print(f"\nRecent Live Signals: {len(signals)}")
            
            nq_signals = [s for s in signals if 'NQ' in s.get('symbol', '')]
            htf_aligned = [s for s in signals if s.get('htf_aligned', False)]
            
            print(f"   NQ Signals: {len(nq_signals)}")
            print(f"   HTF Aligned: {len(htf_aligned)}")
            
            if signals:
                latest = signals[0]
                print(f"   Latest: {latest.get('symbol')} {latest.get('bias')} at {latest.get('timestamp')}")
                print(f"   HTF Status: {latest.get('htf_aligned', False)}")
            
            return signals
        else:
            print(f"Failed to get signals: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error checking signals: {e}")
        return []

def check_signal_lab_trades():
    """Check recent Signal Lab trades"""
    try:
        response = requests.get(f"{RAILWAY_URL}/api/signal-lab-trades", timeout=10)
        if response.status_code == 200:
            trades = response.json()
            print(f"\nSignal Lab Trades: {len(trades)}")
            
            # Check for recent trades (last 24 hours)
            now = datetime.now()
            recent_trades = []
            
            for trade in trades:
                if trade.get('date'):
                    try:
                        trade_date = datetime.strptime(trade['date'], '%Y-%m-%d')
                        if (now - trade_date).days <= 1:
                            recent_trades.append(trade)
                    except:
                        pass
            
            print(f"   Recent (24h): {len(recent_trades)}")
            
            if recent_trades:
                latest = recent_trades[0]
                print(f"   Latest: {latest.get('date')} {latest.get('time')} - {latest.get('bias')} {latest.get('session')}")
            
            return trades
        else:
            print(f"Failed to get Signal Lab trades: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error checking Signal Lab: {e}")
        return []

def check_contract_status():
    """Check active contract status"""
    try:
        response = requests.get(f"{RAILWAY_URL}/api/contracts/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            contracts = data.get('active_contracts', {})
            print(f"\nActive Contracts:")
            for symbol, contract in contracts.items():
                print(f"   {symbol}: {contract}")
            
            recent_symbols = data.get('recent_symbols', [])
            print(f"\nRecent Signal Symbols:")
            for symbol_data in recent_symbols[:5]:
                print(f"   {symbol_data.get('symbol')}: {symbol_data.get('count')} signals")
            
            return contracts
        else:
            print(f"Failed to get contract status: {response.status_code}")
            return {}
    except Exception as e:
        print(f"Error checking contracts: {e}")
        return {}

def test_webhook():
    """Test webhook endpoint"""
    try:
        test_signal = {
            "bias": "Bullish",
            "price": 20150.25,
            "strength": 75,
            "symbol": "NQ1!",
            "htf_aligned": True,
            "timeframe": "1m"
        }
        
        response = requests.post(
            f"{RAILWAY_URL}/api/live-signals", 
            json=test_signal,
            timeout=10
        )
        
        print(f"\nWebhook Test: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Message: {data.get('message', 'no message')}")
        else:
            print(f"   Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"Webhook test failed: {e}")

def main():
    print("Signal Lab Population Diagnostic")
    print("=" * 50)
    
    # Check server health
    if not check_server_health():
        return
    
    # Check recent signals
    signals = check_recent_signals()
    
    # Check Signal Lab trades
    trades = check_signal_lab_trades()
    
    # Check contract status
    contracts = check_contract_status()
    
    # Test webhook
    test_webhook()
    
    # Analysis
    print("\nANALYSIS:")
    print("=" * 30)
    
    if not signals:
        print("NO RECENT SIGNALS - Check TradingView webhook URL")
        print("   Webhook URL should be: https://web-production-cd33.up.railway.app/api/live-signals")
    
    elif not any('NQ' in s.get('symbol', '') for s in signals):
        print("NO NQ SIGNALS - Check TradingView alert symbol")
    
    elif not any(s.get('htf_aligned', False) for s in signals):
        print("NO HTF ALIGNED SIGNALS - Check Pine Script HTF filter")
        print("   All signals must be HTF aligned to populate Signal Lab")
    
    elif not trades or len([t for t in trades if t.get('date') == datetime.now().strftime('%Y-%m-%d')]) == 0:
        print("SIGNALS NOT POPULATING - Check auto-population logic")
        active_nq = contracts.get('NQ', 'Unknown')
        print(f"   Active NQ contract: {active_nq}")
        print("   Verify signal symbol matches active contract")
    
    else:
        print("System appears to be working")
        print("   Check TradingView for recent alerts")

if __name__ == "__main__":
    main()