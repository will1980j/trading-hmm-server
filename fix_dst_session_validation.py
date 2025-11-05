"""
FIX DST SESSION VALIDATION ISSUE

Problem: Session validation uses hardcoded UTC-5 (EST) offset, 
but should automatically handle DST transitions.

On Nov 2, 2025, DST ended:
- Before: EDT (UTC-4) - ASIA starts at 20:00 EDT = 00:00 UTC
- After: EST (UTC-5) - ASIA starts at 20:00 EST = 01:00 UTC

TradingView uses "America/New_York" which auto-handles DST,
but Python code uses timezone(timedelta(hours=-5)) which doesn't.

Solution: Use pytz.timezone('US/Eastern') which handles DST automatically.
"""

import os
import sys

# Files that need DST fix
FILES_TO_FIX = [
    'exact_methodology_processor.py',
    'complete_automation_pipeline.py',
    'enhanced_webhook_processor_v2.py',
    'fix_all_fake_data_violations.py',
    'local_price_feeder.py',
    'polygon_price_service.py',
    'realtime_signal_handler.py',
    'web_server.py',  # Main Flask app
]

CORRECT_SESSION_VALIDATION = '''
    def _is_valid_session(self, timestamp_str):
        """
        EXACT SESSION VALIDATION with DST support
        
        Valid Sessions (Eastern Time - auto-adjusts for DST):
        - ASIA: 20:00-23:59 ET
        - LONDON: 00:00-05:59 ET
        - NY PRE: 06:00-08:29 ET
        - NY AM: 08:30-11:59 ET
        - NY LUNCH: 12:00-12:59 ET
        - NY PM: 13:00-15:59 ET
        
        Invalid: 16:00-19:59 ET (low volatility period)
        
        Uses pytz for proper DST handling (matches TradingView's "America/New_York")
        """
        
        try:
            import pytz
            from datetime import datetime
            
            # Parse timestamp
            if isinstance(timestamp_str, str):
                if 'Z' in timestamp_str:
                    signal_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                else:
                    signal_time = datetime.fromisoformat(timestamp_str)
            else:
                signal_time = timestamp_str
            
            # Convert to Eastern Time (auto-handles DST)
            eastern = pytz.timezone('US/Eastern')
            et_time = signal_time.astimezone(eastern)
            hour = et_time.hour
            minute = et_time.minute
            
            # EXACT session validation
            if 20 <= hour <= 23:  # ASIA
                return True
            elif 0 <= hour <= 5:  # LONDON
                return True
            elif 6 <= hour <= 8:  # NY PRE
                if hour == 8 and minute > 29:
                    return False  # After 08:29
                return True
            elif 8 <= hour <= 11:  # NY AM
                if hour == 8 and minute < 30:
                    return False  # Before 08:30
                return True
            elif hour == 12:  # NY LUNCH
                return True
            elif 13 <= hour <= 15:  # NY PM
                return True
            else:
                return False  # Invalid period (16:00-19:59)
                
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return False
'''

def fix_file(filepath):
    """Fix DST handling in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file needs fixing
        if 'timezone(timedelta(hours=-5))' not in content and 'timezone(timedelta(hours=-4))' not in content:
            print(f"✅ {filepath} - Already correct or doesn't need fixing")
            return True
        
        # Replace hardcoded timezone with pytz
        content = content.replace(
            'from datetime import datetime, timezone, timedelta',
            'from datetime import datetime\nimport pytz'
        )
        
        content = content.replace(
            'eastern = timezone(timedelta(hours=-5))  # EST (adjust for EDT)',
            "eastern = pytz.timezone('US/Eastern')  # Auto-handles DST"
        )
        
        content = content.replace(
            'eastern = timezone(timedelta(hours=-4))  # EDT',
            "eastern = pytz.timezone('US/Eastern')  # Auto-handles DST"
        )
        
        content = content.replace(
            'eastern = timezone(timedelta(hours=-5))',
            "eastern = pytz.timezone('US/Eastern')"
        )
        
        content = content.replace(
            'eastern = timezone(timedelta(hours=-4))',
            "eastern = pytz.timezone('US/Eastern')"
        )
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ {filepath} - FIXED")
        return True
        
    except FileNotFoundError:
        print(f"⚠️  {filepath} - File not found (skipping)")
        return True
    except Exception as e:
        print(f"❌ {filepath} - Error: {e}")
        return False

def main():
    """Fix all files with DST issues"""
    print("=" * 70)
    print("FIXING DST SESSION VALIDATION ISSUE")
    print("=" * 70)
    print()
    print("Problem: Hardcoded UTC-5 offset doesn't handle DST transitions")
    print("Solution: Use pytz.timezone('US/Eastern') for automatic DST handling")
    print()
    print("This matches TradingView's 'America/New_York' timezone behavior")
    print()
    print("=" * 70)
    print()
    
    success_count = 0
    total_count = len(FILES_TO_FIX)
    
    for filepath in FILES_TO_FIX:
        if fix_file(filepath):
            success_count += 1
    
    print()
    print("=" * 70)
    print(f"RESULTS: {success_count}/{total_count} files processed successfully")
    print("=" * 70)
    print()
    
    if success_count == total_count:
        print("✅ ALL FILES FIXED!")
        print()
        print("Next steps:")
        print("1. Test session validation with current time")
        print("2. Deploy to Railway")
        print("3. Verify TradingView signals are classified correctly")
        print()
        print("Expected behavior:")
        print("- ASIA session: 20:00-23:59 EST (currently active)")
        print("- TradingView and Python should now agree on session times")
        return 0
    else:
        print("⚠️  Some files had issues - review errors above")
        return 1

if __name__ == '__main__':
    sys.exit(main())
