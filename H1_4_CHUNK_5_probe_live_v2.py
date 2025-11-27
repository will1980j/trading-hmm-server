"""
H1.4 CHUNK 5: Live V2 Data Verification Probe

Probes production Railway instance to verify V2 data availability.
READ-ONLY - No modifications.
"""

import requests
import json
from datetime import datetime

BASE_URL = "https://web-production-f8c3.up.railway.app"

ENDPOINTS = [
    "/api/automated-signals/stats",
    "/api/automated-signals/dashboard-data",
    "/api/automated-signals/active",
    "/api/automated-signals/completed",
    "/api/automated-signals/mfe-distribution",
    "/api/automated-signals/hourly-distribution",
    "/api/automated-signals/daily-calendar",
]


def probe_endpoint(endpoint):
    """Probe a single endpoint and return results"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        response = requests.get(url, timeout=30)
        
        result = {
            'endpoint': endpoint,
            'url': url,
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'response_time_ms': int(response.elapsed.total_seconds() * 1000),
        }
        
        # Try to parse JSON
        try:
            data = response.json()
            result['has_json'] = True
            result['data'] = data
            result['data_keys'] = list(data.keys()) if isinstance(data, dict) else None
        except:
            result['has_json'] = False
            result['raw_text'] = response.text[:500]  # First 500 chars
        
        return result
        
    except requests.exceptions.Timeout:
        return {
            'endpoint': endpoint,
            'url': url,
            'status_code': 'TIMEOUT',
            'success': False,
            'error': 'Request timed out after 30 seconds'
        }
    except Exception as e:
        return {
            'endpoint': endpoint,
            'url': url,
            'status_code': 'ERROR',
            'success': False,
            'error': str(e)
        }


def analyze_field_availability(data):
    """Analyze which fields are present and populated"""
    fields = {
        'trade_id': {'present': False, 'populated': False, 'sample': None},
        'event_type': {'present': False, 'populated': False, 'sample': None},
        'entry_price': {'present': False, 'populated': False, 'sample': None},
        'stop_loss': {'present': False, 'populated': False, 'sample': None},
        'mfe': {'present': False, 'populated': False, 'sample': None},
        'no_be_mfe': {'present': False, 'populated': False, 'sample': None},
        'be_mfe': {'present': False, 'populated': False, 'sample': None},
        'direction': {'present': False, 'populated': False, 'sample': None},
        'timestamp': {'present': False, 'populated': False, 'sample': None},
        'signal_date': {'present': False, 'populated': False, 'sample': None},
        'signal_time': {'present': False, 'populated': False, 'sample': None},
        'session': {'present': False, 'populated': False, 'sample': None},
    }
    
    # Check in various data structures
    if isinstance(data, dict):
        # Check direct keys
        for field in fields.keys():
            if field in data:
                fields[field]['present'] = True
                if data[field] is not None and data[field] != '':
                    fields[field]['populated'] = True
                    fields[field]['sample'] = data[field]
        
        # Check nested structures
        for key in ['active_trades', 'completed_trades', 'trades', 'data']:
            if key in data and isinstance(data[key], list) and len(data[key]) > 0:
                sample_trade = data[key][0]
                for field in fields.keys():
                    if field in sample_trade:
                        fields[field]['present'] = True
                        if sample_trade[field] is not None and sample_trade[field] != '':
                            fields[field]['populated'] = True
                            if fields[field]['sample'] is None:
                                fields[field]['sample'] = sample_trade[field]
    
    return fields


def main():
    """Main probe execution"""
    print("=" * 80)
    print("H1.4 CHUNK 5: LIVE V2 DATA VERIFICATION PROBE")
    print(f"Target: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)
    print()
    
    results = []
    
    # Probe all endpoints
    print("🔍 PROBING ENDPOINTS...")
    print()
    
    for endpoint in ENDPOINTS:
        print(f"Probing: {endpoint}")
        result = probe_endpoint(endpoint)
        results.append(result)
        
        if result['success']:
            print(f"  ✅ Status: {result['status_code']} ({result['response_time_ms']}ms)")
            if result.get('has_json'):
                print(f"  📊 JSON Keys: {result.get('data_keys', [])}")
        else:
            print(f"  ❌ Status: {result['status_code']}")
            if 'error' in result:
                print(f"  Error: {result['error']}")
        print()
    
    # Analyze data from successful responses
    print("=" * 80)
    print("📊 FIELD AVAILABILITY ANALYSIS")
    print("=" * 80)
    print()
    
    all_fields = {}
    for result in results:
        if result['success'] and result.get('has_json'):
            fields = analyze_field_availability(result['data'])
            for field_name, field_info in fields.items():
                if field_name not in all_fields:
                    all_fields[field_name] = field_info
                else:
                    # Merge info
                    if field_info['present']:
                        all_fields[field_name]['present'] = True
                    if field_info['populated']:
                        all_fields[field_name]['populated'] = True
                    if field_info['sample'] and not all_fields[field_name]['sample']:
                        all_fields[field_name]['sample'] = field_info['sample']
    
    for field_name, field_info in sorted(all_fields.items()):
        status = "✅ PRESENT & POPULATED" if field_info['populated'] else \
                 "⚠️ PRESENT BUT EMPTY" if field_info['present'] else \
                 "❌ MISSING"
        print(f"{field_name:20} {status}")
        if field_info['sample']:
            print(f"{'':20} Sample: {field_info['sample']}")
    
    print()
    
    # Data volume analysis
    print("=" * 80)
    print("📈 DATA VOLUME ANALYSIS")
    print("=" * 80)
    print()
    
    for result in results:
        if result['success'] and result.get('has_json'):
            data = result['data']
            
            if 'total_signals' in data:
                print(f"Total Signals: {data['total_signals']}")
            
            if 'active_trades' in data:
                if isinstance(data['active_trades'], list):
                    print(f"Active Trades: {len(data['active_trades'])}")
                elif isinstance(data['active_trades'], int):
                    print(f"Active Trades: {data['active_trades']}")
            
            if 'completed_trades' in data:
                if isinstance(data['completed_trades'], list):
                    print(f"Completed Trades: {len(data['completed_trades'])}")
                elif isinstance(data['completed_trades'], int):
                    print(f"Completed Trades: {data['completed_trades']}")
            
            if 'stats' in data and isinstance(data['stats'], dict):
                stats = data['stats']
                for key, value in stats.items():
                    print(f"{key}: {value}")
    
    print()
    
    # Readiness verdict
    print("=" * 80)
    print("🎯 READINESS VERDICT")
    print("=" * 80)
    print()
    
    successful_endpoints = sum(1 for r in results if r['success'])
    total_endpoints = len(results)
    
    has_trade_id = all_fields.get('trade_id', {}).get('populated', False)
    has_session = all_fields.get('session', {}).get('populated', False)
    has_signal_time = all_fields.get('signal_time', {}).get('populated', False) or \
                      all_fields.get('timestamp', {}).get('populated', False)
    
    print(f"Endpoints Accessible: {successful_endpoints}/{total_endpoints}")
    print(f"Trade ID Available: {'✅ YES' if has_trade_id else '❌ NO'}")
    print(f"Session Data Available: {'✅ YES' if has_session else '❌ NO'}")
    print(f"Time Data Available: {'✅ YES' if has_signal_time else '❌ NO'}")
    print()
    
    if successful_endpoints >= 5 and has_trade_id and has_session and has_signal_time:
        verdict = "✅ READY"
        reason = "V2 data is complete with all required fields for Time Analysis migration"
    elif successful_endpoints >= 3 and (has_trade_id or has_session):
        verdict = "⚠️ PARTIAL"
        reason = "V2 data exists but some fields may be missing or sparse"
    else:
        verdict = "❌ BLOCKED"
        reason = "Insufficient V2 data - missing critical fields or endpoints not accessible"
    
    print(f"VERDICT: {verdict}")
    print(f"REASON: {reason}")
    print()
    
    # Save detailed results
    with open('H1_4_CHUNK_5_LIVE_V2_PROBE_RESULTS.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'base_url': BASE_URL,
            'endpoints_probed': ENDPOINTS,
            'results': results,
            'field_availability': all_fields,
            'verdict': verdict,
            'reason': reason
        }, f, indent=2, default=str)
    
    print("📄 Detailed results saved to: H1_4_CHUNK_5_LIVE_V2_PROBE_RESULTS.json")
    print()
    
    return 0 if verdict == "✅ READY" else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
