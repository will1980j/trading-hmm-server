# TD Ameritrade API Setup for VIX Data

## Quick Setup (5 minutes):

1. **Get TD Ameritrade Developer Account**:
   - Go to https://developer.tdameritrade.com/
   - Sign up for free developer account
   - Create new app to get Consumer Key

2. **Add Environment Variable**:
   ```bash
   # Add to your .env file:
   TD_CONSUMER_KEY=your_consumer_key_here
   ```

3. **Test VIX Data**:
   ```bash
   curl "https://api.tdameritrade.com/v1/marketdata/$VIX/quotes?apikey=YOUR_KEY"
   ```

## Current Behavior:
- **With TD Key**: Uses TD Ameritrade for real-time VIX data
- **Without TD Key**: Falls back to Yahoo Finance → 20.0 fallback

## Benefits:
- ✅ Real-time VIX data (15-minute delay for free accounts)
- ✅ Professional-grade market data
- ✅ No rate limits for basic quotes
- ✅ Supports all major indices ($VIX, $SPX, etc.)

## API Response Example:
```json
{
  "$VIX": {
    "lastPrice": 21.85,
    "mark": 21.85,
    "bidPrice": 21.80,
    "askPrice": 21.90,
    "volatility": 0.0234
  }
}
```

Your system will automatically use TD Ameritrade if the key is configured, otherwise it falls back gracefully.