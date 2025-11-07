"""
Local NASDAQ Price Feeder
Runs on your local machine and sends price updates to Railway dashboard
Uses free Yahoo Finance API - no API key needed
"""
import requests
import time
from datetime import datetime
import pytz

WEBHOOK_URL = "https://web-production-cd33.up.railway.app/api/realtime-price"
UPDATE_INTERVAL = 30  # seconds

def get_current_session():
    """Determine current trading session"""
    eastern = pytz.timezone('US/Eastern')
    now = datetime.now(eastern)
    hour = now.hour
    minute = now.minute
    
    if (hour == 8 and minute >= 30) or (9 <= hour <= 11):
        return "NY AM", True
    elif 13 <= hour <= 15:
        return "NY PM", True
    elif hour == 12:
        return "NY LUNCH", False
    elif 0 <= hour <= 5:
        return "LONDON", False
    elif hour >= 6 and (hour < 8 or (hour == 8 and minute <= 29)):
        return "NY PRE", False
    elif 20 <= hour <= 23:
        return "ASIA", False
    else:
        return "INVALID", False

def get_nasdaq_price():
    """Get NASDAQ-100 price from Yahoo Finance (free, no API key)"""
    try:
        # Use QQQ (NASDAQ-100 ETF) as proxy for NQ futures
        # Yahoo Finance API endpoint
        url = "https://query1.finance.yahoo.com/v8/finance/chart/QQQ"
        params = {
            "interval": "1m",
            "range": "1d"
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract latest price
            result = data['chart']['result'][0]
            meta = result['meta']
            quote = result['indicators']['quote'][0]
            
            # Get latest close price
            closes = quote['close']
            volumes = quote['volume']
            timestamps = result['timestamp']
            
            # Get most recent non-null price
            latest_price = None
            latest_volume = 0
            for i in range(len(closes) - 1, -1, -1):
                if closes[i] is not None:
                    latest_price = closes[i]
                    latest_volume = volumes[i] if volumes[i] else 0
                    break
            
            if latest_price is None:
                latest_price = meta['regularMarketPrice']
                latest_volume = meta.get('regularMarketVolume', 0)
            
            # Convert QQQ price to approximate NQ price (NQ ≈ QQQ * 100)
            nq_price = latest_price * 100
            
            return {
                'price': nq_price,
                'volume': latest_volume,
                'timestamp': int(time.time() * 1000)
            }
        else:
            print(f"❌ Yahoo Finance API error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching price: {str(e)}")
        return None

def send_price_update(price_data, session, change=0):
    """Send price update to Railway webhook"""
    try:
        payload = {
            "type": "realtime_price",
            "symbol": "NQ",
            "price": price_data['price'],
            "timestamp": price_data['timestamp'],
            "session": session,
            "volume": price_data['volume'],
            "change": change,
            "bid": price_data['price'] - 0.25,
            "ask": price_data['price'] + 0.25,
            "priority": "local_feeder"
        }
        
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            return True
        else:
            print(f"❌ Webhook error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending webhook: {str(e)}")
        return False

def main():
    """Main loop"""
    print("🚀 NASDAQ LOCAL PRICE FEEDER")
    print("=" * 60)
    print(f"📡 Webhook: {WEBHOOK_URL}")
    print(f"⏱️  Update Interval: {UPDATE_INTERVAL} seconds")
    print(f"📊 Source: Yahoo Finance (QQQ ETF)")
    print("=" * 60)
    print()
    print("✅ Starting price feed...")
    print("   Press Ctrl+C to stop")
    print()
    
    last_price = None
    update_count = 0
    
    try:
        while True:
            # Check session
            session, is_active = get_current_session()
            
            if session == "INVALID":
                print(f"🌙 Market closed (INVALID session) - waiting...")
                time.sleep(UPDATE_INTERVAL)
                continue
            
            # Get price
            price_data = get_nasdaq_price()
            
            if price_data:
                # Calculate change
                change = 0
                if last_price:
                    change = price_data['price'] - last_price
                
                # Send update
                success = send_price_update(price_data, session, change)
                
                if success:
                    update_count += 1
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    print(f"✅ [{timestamp}] ${price_data['price']:.2f} | {session} | {change:+.2f} | Update #{update_count}")
                    last_price = price_data['price']
                else:
                    print(f"⚠️  Failed to send update")
            else:
                print(f"⚠️  Failed to fetch price")
            
            # Wait for next update
            time.sleep(UPDATE_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n")
        print("=" * 60)
        print(f"🛑 Stopped after {update_count} updates")
        print("=" * 60)

if __name__ == "__main__":
    main()
