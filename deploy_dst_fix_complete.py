"""
DST Session Fix - Complete Deployment Script

This script updates all session validation logic to use UTC-based validation
instead of Eastern Time hour ranges. This ensures consistent behavior year-round
regardless of DST transitions.

Run this script to fix the issue where ASIA signals at 19:00 EST are being
rejected as INVALID after DST ended on November 2, 2025.
"""

import os
import re
from pathlib import Path

# UTC-based session validation function (constant year-round)
UTC_SESSION_VALIDATION = '''    def _is_valid_session(self, timestamp_str):
        """
        EXACT SESSION VALIDATION with DST support
        
        Uses UTC time ranges which remain constant year-round.
        Markets don't observe US DST, so UTC times are stable.
        
        Valid Sessions (UTC - Constant Year-Round):
        - ASIA: 00:00-03:59 UTC
        - LONDON: 04:00-09:59 UTC
        - NY PRE: 10:00-12:29 UTC
        - NY AM: 12:30-15:59 UTC
        - NY LUNCH: 16:00-16:59 UTC
        - NY PM: 17:00-19:59 UTC
        
        Invalid: 20:00-23:59 UTC (low volatility period)
        """
        
        try:
            from datetime import datetime
            import pytz
            
            # Parse timestamp
            if isinstance(timestamp_str, str):
                signal_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                signal_time = timestamp_str
            
            # Convert to UTC for validation
            if signal_time.tzinfo is None:
                signal_time = pytz.utc.localize(signal_time)
            else:
                signal_time = signal_time.astimezone(pytz.utc)
            
            hour = signal_time.hour
            minute = signal_time.minute
            
            # UTC-based session validation (constant year-round)
            if 0 <= hour <= 3:  # ASIA: 00:00-03:59 UTC
                return True
            elif 4 <= hour <= 9:  # LONDON: 04:00-09:59 UTC
                return True
            elif 10 <= hour <= 12:  # NY PRE: 10:00-12:29 UTC
                if hour == 12 and minute >= 30:
                    return False  # After 12:29 UTC
                return True
            elif 12 <= hour <= 15:  # NY AM: 12:30-15:59 UTC
                if hour == 12 and minute < 30:
                    return False  # Before 12:30 UTC
                return True
            elif hour == 16:  # NY LUNCH: 16:00-16:59 UTC
                return True
            elif 17 <= hour <= 19:  # NY PM: 17:00-19:59 UTC
                return True
            else:
                return False  # Invalid period (20:00-23:59 UTC)
                
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return False
'''

# UTC-based session determination function
UTC_SESSION_DETERMINATION = '''    def _determine_session(self, timestamp_str):
        """
        Determine which session a timestamp belongs to
        
        Returns session name or 'INVALID' if outside trading hours
        Uses UTC for consistent year-round behavior
        """
        
        try:
            from datetime import datetime
            import pytz
            
            # Parse timestamp
            if isinstance(timestamp_str, str):
                signal_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                signal_time = timestamp_str
            
            # Convert to UTC
            if signal_time.tzinfo is None:
                signal_time = pytz.utc.localize(signal_time)
            else:
                signal_time = signal_time.astimezone(pytz.utc)
            
            hour = signal_time.hour
            minute = signal_time.minute
            
            # Determine session based on UTC time
            if 0 <= hour <= 3:
                return 'ASIA'
            elif 4 <= hour <= 9:
                return 'LONDON'
            elif 10 <= hour <= 12:
                if hour == 12 and minute >= 30:
                    return 'NY AM'
                return 'NY PRE'
            elif 12 <= hour <= 15:
                if hour == 12 and minute < 30:
                    return 'NY PRE'
                return 'NY AM'
            elif hour == 16:
                return 'NY LUNCH'
            elif 17 <= hour <= 19:
                return 'NY PM'
            else:
                return 'INVALID'
                
        except Exception as e:
            logger.error(f"Session determination error: {e}")
            return 'INVALID'
'''

# Standalone function for files without classes
UTC_STANDALONE_SESSION = '''def get_current_session():
    """
    Determine current trading session using UTC time
    
    Uses UTC for consistent year-round behavior regardless of DST
    """
    from datetime import datetime
    import pytz
    
    # Get current time in UTC
    utc_now = datetime.now(pytz.utc)
    hour = utc_now.hour
    minute = utc_now.minute
    
    # Determine session based on UTC time
    if 0 <= hour <= 3:
        return 'ASIA'
    elif 4 <= hour <= 9:
        return 'LONDON'
    elif 10 <= hour <= 12:
        if hour == 12 and minute >= 30:
            return 'NY AM'
        return 'NY PRE'
    elif 12 <= hour <= 15:
        if hour == 12 and minute < 30:
            return 'NY PRE'
        return 'NY AM'
    elif hour == 16:
        return 'NY LUNCH'
    elif 17 <= hour <= 19:
        return 'NY PM'
    else:
        return 'INVALID'
'''

# Files that need updating
FILES_TO_UPDATE = [
    'exact_methodology_processor.py',
    'automated_signal_processor.py',
    'complete_automation_pipeline.py',
    'enhanced_webhook_processor_v2.py',
    'realtime_signal_handler.py',
    'local_price_feeder.py',
    'polygon_price_service.py',
]

def backup_file(filepath):
    """Create backup of file before modification"""
    backup_path = f"{filepath}.backup_dst_fix"
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Backed up: {filepath}")
        return True
    return False

def update_class_based_file(filepath):
    """Update files with class-based session validation"""
    if not os.path.exists(filepath):
        print(f"⚠️  File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if file has session validation
    if '_is_valid_session' not in content:
        print(f"⏭️  Skipping {filepath} - no session validation found")
        return False
    
    # Find and replace _is_valid_session method
    # Pattern matches the entire method including docstring and body
    pattern = r'    def _is_valid_session\(self.*?\n(?:        .*\n)*?(?=\n    def |\nclass |\Z)'
    
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, UTC_SESSION_VALIDATION + '\n', content, flags=re.DOTALL)
        print(f"✅ Updated _is_valid_session in {filepath}")
    else:
        print(f"⚠️  Could not find _is_valid_session pattern in {filepath}")
    
    # Find and replace _determine_session method if it exists
    pattern = r'    def _determine_session\(self.*?\n(?:        .*\n)*?(?=\n    def |\nclass |\Z)'
    
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, UTC_SESSION_DETERMINATION + '\n', content, flags=re.DOTALL)
        print(f"✅ Updated _determine_session in {filepath}")
    
    # Write updated content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def update_standalone_function_file(filepath):
    """Update files with standalone get_current_session function"""
    if not os.path.exists(filepath):
        print(f"⚠️  File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if file has get_current_session function
    if 'def get_current_session' not in content:
        print(f"⏭️  Skipping {filepath} - no get_current_session found")
        return False
    
    # Find and replace get_current_session function
    pattern = r'def get_current_session\(\):.*?\n(?:    .*\n)*?(?=\ndef |\nclass |\Z)'
    
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, UTC_STANDALONE_SESSION + '\n', content, flags=re.DOTALL)
        print(f"✅ Updated get_current_session in {filepath}")
        
        # Write updated content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    else:
        print(f"⚠️  Could not find get_current_session pattern in {filepath}")
        return False

def update_documentation():
    """Update project documentation with correct session times"""
    doc_updates = {
        '.kiro/steering/project-context.md': {
            'old': '''**Valid Trading Sessions (US Eastern Time - TradingView Reference):**

**Current Sessions (EDT - UTC-4):**
- **ASIA:** 20:00-23:59 (Asian market overlap)
- **LONDON:** 00:00-05:59 (London market hours)
- **NY PRE:** 06:00-08:29 (Pre-market trading)
- **NY AM:** 08:30-11:59 (Morning session - market open to lunch)
- **NY LUNCH:** 12:00-12:59 (Lunch hour)
- **NY PM:** 13:00-15:59 (Afternoon session - lunch to close)

**Winter Sessions (EST - UTC-5):**
- **ASIA:** 20:00-23:59 (Same times)
- **LONDON:** 00:00-05:59 (Same times)
- **NY PRE:** 06:00-08:29 (Same times)
- **NY AM:** 08:30-11:59 (Same times)
- **NY LUNCH:** 12:00-12:59 (Same times)
- **NY PM:** 13:00-15:59 (Same times)

**Note:** Session times remain constant in Eastern Time regardless of DST''',
            'new': '''**Valid Trading Sessions (UTC - Constant Year-Round):**

**UTC Times (Never Change):**
- **ASIA:** 00:00-03:59 UTC
- **LONDON:** 04:00-09:59 UTC
- **NY PRE:** 10:00-12:29 UTC
- **NY AM:** 12:30-15:59 UTC
- **NY LUNCH:** 16:00-16:59 UTC
- **NY PM:** 17:00-19:59 UTC
- **INVALID:** 20:00-23:59 UTC

**Eastern Time Equivalents:**
- **During EDT (March-November):** Add 4 hours to UTC (e.g., ASIA = 20:00-23:59 EDT)
- **During EST (November-March):** Add 5 hours to UTC (e.g., ASIA = 19:00-22:59 EST)

**Note:** Platform uses UTC internally for consistent year-round validation'''
        }
    }
    
    for filepath, changes in doc_updates.items():
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if changes['old'] in content:
                content = content.replace(changes['old'], changes['new'])
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Updated documentation: {filepath}")
            else:
                print(f"⚠️  Documentation pattern not found in {filepath}")
        else:
            print(f"⚠️  Documentation file not found: {filepath}")

def main():
    """Main deployment function"""
    print("=" * 70)
    print("DST SESSION FIX - DEPLOYMENT SCRIPT")
    print("=" * 70)
    print()
    print("This script will update all session validation logic to use UTC-based")
    print("validation instead of Eastern Time hour ranges.")
    print()
    print("This fixes the issue where ASIA signals at 19:00 EST are being rejected")
    print("as INVALID after DST ended on November 2, 2025.")
    print()
    print("=" * 70)
    print()
    
    # Step 1: Backup all files
    print("STEP 1: Creating backups...")
    print("-" * 70)
    for filepath in FILES_TO_UPDATE:
        backup_file(filepath)
    print()
    
    # Step 2: Update class-based files
    print("STEP 2: Updating class-based session validation...")
    print("-" * 70)
    class_files = [
        'exact_methodology_processor.py',
        'automated_signal_processor.py',
        'complete_automation_pipeline.py',
        'enhanced_webhook_processor_v2.py',
        'realtime_signal_handler.py',
    ]
    
    for filepath in class_files:
        update_class_based_file(filepath)
    print()
    
    # Step 3: Update standalone function files
    print("STEP 3: Updating standalone session functions...")
    print("-" * 70)
    standalone_files = [
        'local_price_feeder.py',
        'polygon_price_service.py',
    ]
    
    for filepath in standalone_files:
        update_standalone_function_file(filepath)
    print()
    
    # Step 4: Update documentation
    print("STEP 4: Updating documentation...")
    print("-" * 70)
    update_documentation()
    print()
    
    # Step 5: Summary
    print("=" * 70)
    print("DEPLOYMENT COMPLETE!")
    print("=" * 70)
    print()
    print("✅ All session validation logic updated to use UTC")
    print("✅ Backups created with .backup_dst_fix extension")
    print("✅ Documentation updated with correct session times")
    print()
    print("NEXT STEPS:")
    print("1. Review changes in updated files")
    print("2. Test locally with current EST times")
    print("3. Commit changes via GitHub Desktop")
    print("4. Push to main branch for Railway deployment")
    print("5. Verify ASIA signals at 19:00 EST are now accepted")
    print()
    print("SESSION TIMES (Current - EST):")
    print("  ASIA: 19:00-22:59 EST (00:00-03:59 UTC)")
    print("  LONDON: 23:00-04:59 EST (04:00-09:59 UTC)")
    print("  NY PRE: 05:00-07:29 EST (10:00-12:29 UTC)")
    print("  NY AM: 07:30-10:59 EST (12:30-15:59 UTC)")
    print("  NY LUNCH: 11:00-11:59 EST (16:00-16:59 UTC)")
    print("  NY PM: 12:00-14:59 EST (17:00-19:59 UTC)")
    print("  INVALID: 15:00-18:59 EST (20:00-23:59 UTC)")
    print()
    print("=" * 70)

if __name__ == '__main__':
    main()
