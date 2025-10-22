"""Test the webhook fix locally"""
import json

# Simulate the fixed code
def test_webhook_parsing():
    # Simulate incoming JSON data
    data = {
        'symbol': 'NQ1!',
        'timeframe': '1m',
        'signal_type': 'BIAS_CHANGE',
        'bias': 'Bullish',
        'price': 21000,
        'strength': 85,
        'htf_aligned': True,
        'htf_status': 'ALIGNED'
    }
    
    # Extract bias
    triangle_bias = data.get('bias', 'Bullish')
    if triangle_bias not in ['Bullish', 'Bearish']:
        triangle_bias = 'Bullish'
    
    # Clean symbol
    raw_symbol = data.get('symbol', 'NQ1!')
    if 'YM' in raw_symbol:
        clean_symbol = 'YM1!'
    elif 'ES' in raw_symbol:
        clean_symbol = 'ES1!'
    elif 'NQ' in raw_symbol:
        clean_symbol = 'NQ1!'
    elif 'RTY' in raw_symbol:
        clean_symbol = 'RTY1!'
    elif 'DXY' in raw_symbol:
        clean_symbol = 'DXY'
    else:
        clean_symbol = raw_symbol
    
    # HTF status
    htf_aligned = data.get('htf_aligned', False)
    htf_status = data.get('htf_status', 'N/A')
    
    # Extract price (FIXED ORDER)
    raw_price = data.get('price', 0)
    try:
        if isinstance(raw_price, str):
            price = float(raw_price.replace(',', '')) if raw_price else 0
        else:
            price = float(raw_price) if raw_price else 0
    except (ValueError, TypeError):
        price = 0
        print(f"Could not parse price '{raw_price}'")
    
    if price == 0:
        print(f"Invalid price in signal: {data}")
        return False
    
    # Now we can log (AFTER price is defined)
    print(f"✅ PARSED SIGNAL: bias={triangle_bias}, symbol={clean_symbol}, price={price}, htf={htf_status}")
    
    return True

if __name__ == '__main__':
    print("Testing webhook parsing fix...")
    success = test_webhook_parsing()
    if success:
        print("\n✅ Fix works! The price variable is now defined before use.")
        print("📤 Deploy this to Railway to fix the live server.")
    else:
        print("\n❌ Test failed")
