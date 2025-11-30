import requests
import time

ENDPOINT = "https://web-production-f8c3.up.railway.app/api/automated-signals/webhook"
TRADE_ID = "TEST_LIFECYCLE_001"

def send(event):
    print(f"\n➡ Sending {event['event_type']}...")
    r = requests.post(ENDPOINT, json=event)
    try:
        print("⬅ Response:", r.json())
    except Exception:
        print("⬅ Raw response:", r.text)

# Common base fields, matching f_buildPayload
BASE = {
    "schema_version": "1.0.0",
    "engine_version": "1.0.0",
    "strategy_name": "NQ_FVG_CORE",
    "strategy_id": "NQ_FVG_CORE",
    "strategy_version": "2025.11.20",
    "symbol": "MNQ1!",
    "exchange": "MNQ1!",
    "timeframe": "1",          # 1-minute
    "session": "NY AM",
    "direction": "Bullish",
    "risk_R": 1.0,
    "position_size": 3,
    "mfe_R": 0.0,
    "mae_R": 0.0,
    "final_mfe_R": None,
    "exit_price": None,
    "exit_timestamp": None,
    "exit_reason": None,
    "targets": {
        "tp1_price": 18020.0,
        "tp2_price": 18040.0,
        "tp3_price": 18060.0,
        "target_Rs": [1.0, 2.0, 3.0]
    },
    "setup": {
        "setup_family": "FVG_CORE",
        "setup_variant": "STANDARD",
        "setup_id": "FVG_CORE_STANDARD",
        "signal_strength": 75,
        "confidence_components": {
            "trend_alignment": 0.8,
            "structure_quality": 0.8,
            "volatility_fit": 0.7
        }
    },
    "market_state": {
        "trend_regime": "Bullish",
        "trend_score": 0.8,
        "volatility_regime": "NORMAL",
        "atr": None,
        "atr_percentile_20d": None,
        "daily_range_percentile_20d": None,
        "price_location": {
            "vs_daily_open": None,
            "vs_vwap": None,
            "distance_to_HTF_level_points": None
        },
        "structure": {
            "swing_state": "UNKNOWN",
            "bos_choch_signal": "NONE",
            "liquidity_context": "NEUTRAL"
        }
    }
}

def entry_payload():
    p = BASE.copy()
    p.update({
        "trade_id": TRADE_ID,
        "event_type": "ENTRY",
        "event_timestamp": "2025-11-29T12:00:00Z",
        "entry_price": 18000.25,
        "stop_loss": 17950.50,
        "be_price": None,
        "mfe_R": 0.0,
        "mae_R": 0.0,
        "final_mfe_R": None,
        "exit_price": None,
        "exit_timestamp": None,
        "exit_reason": None
    })
    return p

def mfe_payload():
    p = BASE.copy()
    p.update({
        "trade_id": TRADE_ID,
        "event_type": "MFE_UPDATE",
        "event_timestamp": "2025-11-29T12:01:00Z",
        "entry_price": 18000.25,
        "stop_loss": 17950.50,
        "be_price": None,        # BE not triggered yet
        "mfe_R": 1.2,
        "mae_R": 0.0,
        "final_mfe_R": None,
        "exit_price": None,
        "exit_timestamp": None,
        "exit_reason": None
    })
    return p

def be_payload():
    p = BASE.copy()
    p.update({
        "trade_id": TRADE_ID,
        "event_type": "BE_TRIGGERED",
        "event_timestamp": "2025-11-29T12:02:00Z",
        "entry_price": 18000.25,
        "stop_loss": 17950.50,
        "be_price": 18000.25,    # BE at entry
        "mfe_R": 1.0,            # BE triggered at 1R
        "mae_R": 0.0,
        "final_mfe_R": None,
        "exit_price": None,
        "exit_timestamp": None,
        "exit_reason": "be_triggered"
    })
    return p

def exit_payload():
    p = BASE.copy()
    p.update({
        "trade_id": TRADE_ID,
        "event_type": "EXIT_BREAK_EVEN",  # valid event type from your code
        "event_timestamp": "2025-11-29T12:05:00Z",
        "entry_price": 18000.25,
        "stop_loss": 17950.50,
        "be_price": 18000.25,
        "mfe_R": 1.0,
        "mae_R": 0.0,
        "final_mfe_R": 0.0,
        "exit_price": 18000.25,
        "exit_timestamp": "2025-11-29T12:05:00Z",
        "exit_reason": "be_stop_loss_hit"
    })
    return p

print("🚀 Starting Automated Signals Lifecycle Test (v2)")

send(entry_payload())
time.sleep(1)

send(mfe_payload())
time.sleep(1)

send(be_payload())
time.sleep(1)

send(exit_payload())

print("\n✔ Test Completed! Check the Automated Signals Dashboard.")
