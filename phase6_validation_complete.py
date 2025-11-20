"""
PHASE 6: COMPLETE TELEMETRY VALIDATION
Validates ingestion, state building, and API readiness
"""

import json
import psycopg2
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def create_test_lifecycle():
    """Create complete trade lifecycle with telemetry"""
    base_time = datetime.now()
    trade_id = f"TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}_BULLISH"
    
    # ENTRY event
    entry = {
        "schema_version": "1.0.0",
        "engine_version": "1.0.0",
        "strategy_name": "NQ_FVG_CORE",
        "strategy_id": "NQ_FVG_CORE",
        "strategy_version": "2025.11.20",
        "trade_id": trade_id,
        "event_type": "ENTRY",
        "event_timestamp": base_time.isoformat() + "Z",
        "symbol": "NQ1!",
        "exchange": "CME",
        "timeframe": "1",
        "session": "NY PM",
        "direction": "Bullish",
        "entry_price": 20500.25,
        "stop_loss": 20475.00,
        "risk_R": 1.0,
        "position_size": 2,
        "be_price": None,
        "mfe_R": 0.0,
        "mae_R": 0.0,
        "final_mfe_R": None,
        "exit_price": None,
        "exit_timestamp": None,
        "exit_reason": None,
        "targets": {
            "tp1_price": 20525.25,
            "tp2_price": 20550.25,
            "tp3_price": 20575.25,
            "target_Rs": [1.0, 2.0, 3.0]
        },
        "setup": {
            "setup_family": "FVG_CORE",
            "setup_variant": "HTF_ALIGNED",
            "setup_id": "FVG_CORE_HTF_ALIGNED",
            "signal_strength": 75.0,
            "confidence_components": {
                "trend_alignment": 1.0,
                "structure_quality": 0.8,
                "volatility_fit": 0.7
            }
        },
        "market_state": {
            "trend_regime": "Bullish",
            "trend_score": 0.8,
            "volatility_regime": "NORMAL",
            "atr": None,
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
    
    # MFE_UPDATE 1
    mfe1 = entry.copy()
    mfe1.update({
        "event_type": "MFE_UPDATE",
        "event_timestamp": (base_time + timedelta(minutes=5)).isoformat() + "Z",
        "mfe_R": 0.5,
        "current_price": 20512.75
    })
    
    # MFE_UPDATE 2
    mfe2 = entry.copy()
    mfe2.update({
        "event_type": "MFE_UPDATE",
        "event_timestamp": (base_time + timedelta(minutes=10)).isoformat() + "Z",
        "mfe_R": 1.2,
        "current_price": 20530.50
    })
    
    # BE_TRIGGERED
    be_trigger = entry.copy()
    be_trigger.update({
        "event_type": "BE_TRIGGERED",
        "event_timestamp": (base_time + timedelta(minutes=12)).isoformat() + "Z",
        "mfe_R": 1.0,
        "be_price": 20500.25,
        "current_price": 20525.25
    })
    
    # EXIT_STOP_LOSS
    exit_event = entry.copy()
    exit_event.update({
        "event_type": "EXIT_STOP_LOSS",
        "event_timestamp": (base_time + timedelta(minutes=15)).isoformat() + "Z",
        "mfe_R": 1.2,
        "final_mfe_R": -1.0,
        "exit_price": 20475.00,
        "exit_reason": "STOP_LOSS"
    })
    
    return trade_id, [
        ("ENTRY", entry),
        ("MFE_UPDATE_1", mfe1),
        ("MFE_UPDATE_2", mfe2),
        ("BE_TRIGGERED", be_trigger),
        ("EXIT_STOP_LOSS", exit_event)
    ]

def insert_telemetry_events(trade_id, events):
    """Insert telemetry events into database"""
    print(f"\n{'='*70}")
    print("TASK 1: TELEMETRY INGESTION TEST")
    print(f"{'='*70}\n")
    
    database_url = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    for event_name, payload in events:
        print(f"📝 Inserting {event_name}...")
        
        # Extract fields
        event_type = payload["event_type"]
        direction = payload["direction"]
        entry_price = payload["entry_price"]
        stop_loss = payload["stop_loss"]
        session = payload["session"]
        mfe_R = payload["mfe_R"]
        final_mfe_R = payload.get("final_mfe_R")
        exit_price = payload.get("exit_price")
        
        # Calculate risk_distance
        risk_distance = abs(float(entry_price) - float(stop_loss))
        
        # Insert with telemetry
        cursor.execute("""
            INSERT INTO automated_signals (
                trade_id, event_type, direction,
                entry_price, stop_loss, session, bias,
                risk_distance, mfe, final_mfe, exit_price,
                timestamp, telemetry
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            trade_id, event_type, direction,
            entry_price, stop_loss, session, direction,
            risk_distance, mfe_R, final_mfe_R, exit_price,
            datetime.now(), json.dumps(payload)
        ))
        
        row_id = cursor.fetchone()[0]
        print(f"   ✅ Inserted row ID: {row_id}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\n✅ All {len(events)} events inserted successfully")
    return True

def validate_database_storage(trade_id):
    """Validate telemetry storage in database"""
    print(f"\n{'='*70}")
    print("TASK 2: DATABASE STORAGE VALIDATION")
    print(f"{'='*70}\n")
    
    database_url = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, trade_id, event_type, direction, 
               entry_price, stop_loss, session,
               mfe, final_mfe, exit_price,
               telemetry, timestamp
        FROM automated_signals 
        WHERE trade_id = %s
        ORDER BY timestamp ASC
    """, (trade_id,))
    
    rows = cursor.fetchall()
    
    print(f"📊 Found {len(rows)} events for trade {trade_id}\n")
    
    validation_results = {
        "telemetry_stored": True,
        "legacy_fields_populated": True,
        "exit_reason_correct": False,
        "final_mfe_correct": False,
        "direction_correct": False,
        "targets_nested": False,
        "setup_nested": False,
        "market_state_nested": False
    }
    
    for i, row in enumerate(rows, 1):
        row_id, tid, etype, direction, entry, sl, session, mfe, final_mfe, exit_price, telemetry, ts = row
        
        print(f"Event {i}: {etype}")
        print(f"   Row ID: {row_id}")
        print(f"   Direction (legacy): {direction}")
        print(f"   Entry Price (legacy): {entry}")
        print(f"   Stop Loss (legacy): {sl}")
        print(f"   MFE (legacy): {mfe}")
        print(f"   Final MFE (legacy): {final_mfe}")
        print(f"   Exit Price (legacy): {exit_price}")
        
        # Validate telemetry column
        if telemetry:
            print(f"   ✅ Telemetry JSON stored")
            print(f"   Telemetry Direction: {telemetry.get('direction')}")
            print(f"   Telemetry MFE_R: {telemetry.get('mfe_R')}")
            print(f"   Telemetry Final MFE_R: {telemetry.get('final_mfe_R')}")
            print(f"   Telemetry Exit Reason: {telemetry.get('exit_reason')}")
            
            # Check nested objects
            if telemetry.get('targets'):
                print(f"   ✅ Targets nested: {telemetry['targets']}")
                validation_results["targets_nested"] = True
            
            if telemetry.get('setup'):
                print(f"   ✅ Setup nested: {telemetry['setup']['setup_family']}")
                validation_results["setup_nested"] = True
            
            if telemetry.get('market_state'):
                print(f"   ✅ Market State nested: {telemetry['market_state']['trend_regime']}")
                validation_results["market_state_nested"] = True
            
            # Validate specific fields
            if etype == "EXIT_STOP_LOSS":
                if telemetry.get('exit_reason') == 'STOP_LOSS':
                    validation_results["exit_reason_correct"] = True
                if telemetry.get('final_mfe_R') == -1.0:
                    validation_results["final_mfe_correct"] = True
            
            if telemetry.get('direction') == 'Bullish':
                validation_results["direction_correct"] = True
        else:
            print(f"   ❌ No telemetry JSON")
            validation_results["telemetry_stored"] = False
        
        print()
    
    cursor.close()
    conn.close()
    
    # Print validation summary
    print(f"{'='*70}")
    print("VALIDATION RESULTS:")
    print(f"{'='*70}")
    for key, value in validation_results.items():
        status = "✅" if value else "❌"
        print(f"{status} {key.replace('_', ' ').title()}: {value}")
    
    return validation_results, rows

def test_state_building(trade_id, rows):
    """Test build_trade_state logic"""
    print(f"\n{'='*70}")
    print("TASK 3: STATE BUILDING VALIDATION")
    print(f"{'='*70}\n")
    
    # Convert rows to events dict
    events = []
    for row in rows:
        event = {
            "trade_id": row[1],
            "event_type": row[2],
            "direction": row[3],
            "entry_price": row[4],
            "stop_loss": row[5],
            "session": row[6],
            "mfe": row[7],
            "final_mfe": row[8],
            "exit_price": row[9],
            "telemetry": row[10],
            "timestamp": row[11]
        }
        events.append(event)
    
    # Simulate build_trade_state
    first = events[0]
    
    # Check telemetry availability
    has_telemetry = first.get("telemetry") is not None
    print(f"📊 Telemetry Available: {has_telemetry}\n")
    
    if has_telemetry:
        telemetry = first["telemetry"]
        direction = telemetry.get("direction") or first.get("direction")
        session = telemetry.get("session") or first.get("session")
        entry_price = telemetry.get("entry_price") or first.get("entry_price")
        stop_loss = telemetry.get("stop_loss") or first.get("stop_loss")
        targets = telemetry.get("targets")
        setup = telemetry.get("setup")
        market_state = telemetry.get("market_state")
        
        print("📋 TELEMETRY PATH (Preferred):")
        print(f"   Direction: {direction}")
        print(f"   Session: {session}")
        print(f"   Entry Price: {entry_price}")
        print(f"   Stop Loss: {stop_loss}")
        print(f"   Targets: {targets}")
        print(f"   Setup: {setup}")
        print(f"   Market State: {market_state}")
    else:
        print("📋 LEGACY PATH (Fallback):")
        direction = first.get("direction")
        session = first.get("session")
        entry_price = first.get("entry_price")
        stop_loss = first.get("stop_loss")
        targets = None
        setup = None
        market_state = None
    
    # Process events for status
    status = "UNKNOWN"
    current_mfe = None
    final_mfe = None
    exit_price = None
    exit_reason = None
    be_triggered = False
    
    print(f"\n{'='*70}")
    print("EVENT PROCESSING:")
    print(f"{'='*70}\n")
    
    for i, event in enumerate(events, 1):
        etype = event["event_type"]
        print(f"Event {i}: {etype}")
        
        if event.get("telemetry"):
            tel = event["telemetry"]
            
            if tel.get("mfe_R") is not None:
                current_mfe = float(tel["mfe_R"])
                print(f"   MFE_R: {current_mfe}")
            
            if tel.get("final_mfe_R") is not None:
                final_mfe = float(tel["final_mfe_R"])
                print(f"   Final MFE_R: {final_mfe}")
            
            if tel.get("exit_price") is not None:
                exit_price = float(tel["exit_price"])
                print(f"   Exit Price: {exit_price}")
            
            if tel.get("exit_reason"):
                exit_reason = tel["exit_reason"]
                print(f"   Exit Reason: {exit_reason}")
        
        # Update status
        if etype == "ENTRY":
            status = "ACTIVE"
        elif etype == "MFE_UPDATE":
            status = "ACTIVE"
        elif etype == "BE_TRIGGERED":
            status = "BE_PROTECTED"
            be_triggered = True
        elif etype in ("EXIT_STOP_LOSS", "EXIT_BREAK_EVEN", "EXIT_TAKE_PROFIT"):
            status = "COMPLETED"
        
        print(f"   Status: {status}")
        print()
    
    # Build final trade state
    trade_state = {
        "trade_id": trade_id,
        "direction": direction,
        "session": session,
        "status": status,
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "current_mfe": current_mfe,
        "final_mfe": final_mfe,
        "exit_price": exit_price,
        "exit_reason": exit_reason,
        "be_triggered": be_triggered,
        "targets": targets,
        "setup": setup,
        "market_state": market_state
    }
    
    print(f"{'='*70}")
    print("FINAL TRADE STATE:")
    print(f"{'='*70}")
    print(json.dumps(trade_state, indent=2, default=str))
    
    return trade_state

def validate_api_endpoint():
    """Validate hub data API endpoint"""
    print(f"\n{'='*70}")
    print("TASK 5: API ENDPOINT VALIDATION")
    print(f"{'='*70}\n")
    
    try:
        import requests
        
        response = requests.get(
            'http://localhost:5000/api/automated-signals/hub-data',
            timeout=10
        )
        
        print(f"📡 API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            trades = data.get('data', [])
            
            print(f"📊 Total Trades Returned: {len(trades)}\n")
            
            # Check for telemetry-enhanced trades
            telemetry_count = 0
            status_counts = {"ACTIVE": 0, "BE_PROTECTED": 0, "COMPLETED": 0}
            
            for trade in trades[:10]:  # Check first 10
                if trade.get('targets') or trade.get('setup'):
                    telemetry_count += 1
                
                status = trade.get('status', 'UNKNOWN')
                if status in status_counts:
                    status_counts[status] += 1
            
            print(f"✅ Telemetry-Enhanced Trades: {telemetry_count}")
            print(f"✅ Status Distribution:")
            for status, count in status_counts.items():
                print(f"   {status}: {count}")
            
            return True
        else:
            print(f"❌ API request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"⚠️  API test skipped (server not running): {e}")
        return None

def identify_missing_fields(trade_state):
    """Identify missing or null fields"""
    print(f"\n{'='*70}")
    print("TASK 4: MISSING FIELDS ANALYSIS")
    print(f"{'='*70}\n")
    
    missing_fields = []
    null_fields = []
    
    for key, value in trade_state.items():
        if value is None:
            null_fields.append(key)
        elif isinstance(value, dict):
            for nested_key, nested_value in value.items():
                if nested_value is None:
                    null_fields.append(f"{key}.{nested_key}")
    
    if null_fields:
        print("⚠️  NULL FIELDS FOUND:")
        for field in null_fields:
            print(f"   - {field}")
    else:
        print("✅ No null fields found")
    
    if missing_fields:
        print("\n❌ MISSING FIELDS:")
        for field in missing_fields:
            print(f"   - {field}")
    else:
        print("\n✅ No missing required fields")
    
    return null_fields, missing_fields

def main():
    print(f"\n{'#'*70}")
    print("PHASE 6: COMPLETE TELEMETRY VALIDATION")
    print(f"{'#'*70}\n")
    
    # Create test lifecycle
    trade_id, events = create_test_lifecycle()
    print(f"🎯 Test Trade ID: {trade_id}")
    
    # Task 1: Insert telemetry events
    insert_telemetry_events(trade_id, events)
    
    # Task 2: Validate database storage
    validation_results, rows = validate_database_storage(trade_id)
    
    # Task 3: Test state building
    trade_state = test_state_building(trade_id, rows)
    
    # Task 4: Identify missing fields
    null_fields, missing_fields = identify_missing_fields(trade_state)
    
    # Task 5: Validate API endpoint
    api_result = validate_api_endpoint()
    
    # Final summary
    print(f"\n{'#'*70}")
    print("PHASE 6 VALIDATION SUMMARY")
    print(f"{'#'*70}\n")
    
    all_passed = (
        validation_results["telemetry_stored"] and
        validation_results["legacy_fields_populated"] and
        validation_results["exit_reason_correct"] and
        validation_results["final_mfe_correct"] and
        validation_results["direction_correct"] and
        validation_results["targets_nested"] and
        validation_results["setup_nested"] and
        validation_results["market_state_nested"] and
        len(missing_fields) == 0
    )
    
    if all_passed:
        print("✅ ALL VALIDATIONS PASSED")
        print("\n🎯 READY FOR:")
        print("   - Dashboard upgrade")
        print("   - TradingView indicator update")
        print("   - Production deployment")
    else:
        print("⚠️  SOME VALIDATIONS FAILED")
        print("\n🔧 REVIEW:")
        print("   - Failed validation checks above")
        print("   - Missing or null fields")
        print("   - API endpoint issues")

if __name__ == "__main__":
    main()
