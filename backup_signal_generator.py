"""
Backup Signal Generator - Runs independently of TradingView
Fetches market data and generates signals using the same logic as Pine Script
"""
import requests
import time
from datetime import datetime
from database.railway_db import RailwayDB

class BackupSignalGenerator:
    def __init__(self, db):
        self.db = db
        self.last_bias = {}  # Track last bias per symbol
        
    def fetch_market_data(self, symbol):
        """Fetch latest candle data from TwelveData or other provider"""
        # You already have TwelveData integration in your code
        # This would fetch the last 20 candles to detect FVG/IFVG
        pass
    
    def detect_bias_change(self, symbol, candles):
        """
        Implement your FVG/IFVG logic from Pine Script in Python
        Returns: {'bias': 'Bullish'/'Bearish', 'changed': True/False}
        """
        # This would replicate your Pine Script logic:
        # - Check for FVG (bullish/bearish gaps)
        # - Check for IFVG (inversions)
        # - Track ATH/ATL
        # - Determine current bias
        pass
    
    def check_htf_alignment(self, symbol):
        """Check higher timeframe alignment"""
        # Fetch Daily, 4H, 1H, 15M, 5M biases
        # Return alignment status
        pass
    
    def generate_signal(self, symbol):
        """Main signal generation logic"""
        try:
            # 1. Fetch market data
            candles = self.fetch_market_data(symbol)
            
            # 2. Detect bias
            bias_result = self.detect_bias_change(symbol, candles)
            
            # 3. Check if bias changed
            if not bias_result['changed']:
                return None
            
            # 4. Check HTF alignment
            htf_status = self.check_htf_alignment(symbol)
            
            # 5. Create signal (same format as TradingView webhook)
            signal = {
                'symbol': symbol,
                'timeframe': '1m',
                'signal_type': 'BIAS_CHANGE',
                'bias': bias_result['bias'],
                'price': candles[-1]['close'],
                'strength': 85 if htf_status['aligned'] else 70,
                'htf_aligned': htf_status['aligned'],
                'htf_status': htf_status['status'],
                'source': 'BACKUP_GENERATOR'  # Mark as backup
            }
            
            # 6. Send to your webhook endpoint
            self.send_signal(signal)
            
            return signal
            
        except Exception as e:
            print(f"Error generating signal for {symbol}: {e}")
            return None
    
    def send_signal(self, signal):
        """Send signal to your webhook endpoint"""
        try:
            response = requests.post(
                'http://localhost:8080/api/live-signals',
                json=signal,
                timeout=5
            )
            print(f"✅ Backup signal sent: {signal['symbol']} {signal['bias']}")
        except Exception as e:
            print(f"❌ Failed to send backup signal: {e}")
    
    def run_continuous(self, symbols=['NQ1!'], interval=60):
        """Run continuously, checking for signals every interval seconds"""
        print(f"🔄 Backup Signal Generator started for {symbols}")
        print(f"⏰ Checking every {interval} seconds")
        
        while True:
            try:
                for symbol in symbols:
                    signal = self.generate_signal(symbol)
                    if signal:
                        print(f"📊 Generated: {signal['symbol']} {signal['bias']} at {signal['price']}")
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("\n🛑 Backup generator stopped")
                break
            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                time.sleep(interval)

if __name__ == '__main__':
    # This would run as a separate process
    db = RailwayDB()
    generator = BackupSignalGenerator(db)
    
    # Run for NQ, ES, YM, RTY
    generator.run_continuous(
        symbols=['NQ1!', 'ES1!', 'YM1!', 'RTY1!'],
        interval=60  # Check every minute
    )
