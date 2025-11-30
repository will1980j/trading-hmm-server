import requests
import json

# Check the test trade exists and verify data integrity
url = 'https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data'
response = requests.get(url, timeout=30)
data = response.json()

# Find our test trade
test_id = 'TEST_20251130_162836886843_BULLISH'
for trade in data.get('active_trades', []):
    if trade.get('trade_id') == test_id:
        print('=== TEST TRADE VERIFICATION ===')
        print('Trade ID:', trade.get('trade_id'))
        print('Direction:', trade.get('direction'))
        print('Entry Price:', trade.get('entry_price'))
        print('Stop Loss:', trade.get('stop_loss'))
        print('Session:', trade.get('session'))
        print('MFE:', trade.get('mfe'))
        print('BE MFE:', trade.get('be_mfe'))
        print('No BE MFE:', trade.get('no_be_mfe'))
        print('Status:', trade.get('trade_status'))
        break
else:
    print('Test trade not found in active trades')

# Show total counts
print('\nTotal Active Trades:', len(data.get('active_trades', [])))
print('Total Completed Trades:', len(data.get('completed_trades', [])))

# List any test trades
print('\nTest trades in system:')
for trade in data.get('active_trades', []):
    if 'TEST_' in trade.get('trade_id', ''):
        print('  -', trade.get('trade_id'))
