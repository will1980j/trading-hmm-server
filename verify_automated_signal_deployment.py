#!/usr/bin/env python3
"""
Verify Automated Signal Lab Deployment
Quick verification that all components are ready for deployment
"""

import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} MISSING: {filepath}")
        return False

def check_file_contains(filepath, search_string, description):
    """Check if a file contains a specific string"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if search_string in content:
                print(f"✅ {description}")
                return True
            else:
                print(f"❌ {description} - String not found")
                return False
    except Exception as e:
        print(f"❌ {description} - Error reading file: {e}")
        return False

def main():
    """Run all verification checks"""
    print("🔍 Verifying Automated Signal Lab Deployment")
    print("=" * 60)
    
    all_checks_passed = True
    
    # Check 1: Database migration file
    print("\n📁 Checking Files...")
    all_checks_passed &= check_file_exists(
        'database/add_automated_signal_support.sql',
        'Database migration'
    )
    
    # Check 2: Pine Script file
    all_checks_passed &= check_file_exists(
        'complete_automated_trading_system.pine',
        'Pine Script indicator'
    )
    
    # Check 3: Web server file
    all_checks_passed &= check_file_exists(
        'web_server.py',
        'Web server'
    )
    
    # Check 4: Documentation
    all_checks_passed &= check_file_exists(
        'AUTOMATED_SIGNAL_LAB_DEPLOYMENT_COMPLETE.md',
        'Deployment documentation'
    )
    
    all_checks_passed &= check_file_exists(
        'DEPLOY_AUTOMATED_SIGNALS_NOW.md',
        'Quick start guide'
    )
    
    # Check 5: Pine Script has webhook code
    print("\n🔧 Checking Code Integration...")
    all_checks_passed &= check_file_contains(
        'complete_automated_trading_system.pine',
        'AUTOMATED SIGNAL LAB WEBHOOK ALERTS',
        'Pine Script webhook alerts'
    )
    
    all_checks_passed &= check_file_contains(
        'complete_automated_trading_system.pine',
        'create_signal_id',
        'Pine Script signal ID function'
    )
    
    all_checks_passed &= check_file_contains(
        'complete_automated_trading_system.pine',
        'signal_created_payload',
        'Pine Script signal created webhook'
    )
    
    # Check 6: Web server has webhook endpoint
    all_checks_passed &= check_file_contains(
        'web_server.py',
        '/api/signal-lab-automated',
        'Web server webhook endpoint'
    )
    
    all_checks_passed &= check_file_contains(
        'web_server.py',
        'handle_signal_created',
        'Web server signal created handler'
    )
    
    all_checks_passed &= check_file_contains(
        'web_server.py',
        'handle_mfe_update',
        'Web server MFE update handler'
    )
    
    all_checks_passed &= check_file_contains(
        'web_server.py',
        'handle_be_triggered',
        'Web server BE triggered handler'
    )
    
    all_checks_passed &= check_file_contains(
        'web_server.py',
        'handle_signal_completed',
        'Web server signal completed handler'
    )
    
    # Check 7: Database migration has required columns
    print("\n🗄️ Checking Database Schema...")
    all_checks_passed &= check_file_contains(
        'database/add_automated_signal_support.sql',
        'signal_id VARCHAR(50) UNIQUE',
        'Database signal_id column'
    )
    
    all_checks_passed &= check_file_contains(
        'database/add_automated_signal_support.sql',
        "source VARCHAR(20) DEFAULT 'manual'",
        'Database source column'
    )
    
    all_checks_passed &= check_file_contains(
        'database/add_automated_signal_support.sql',
        'entry_price DECIMAL(10,2)',
        'Database entry_price column'
    )
    
    all_checks_passed &= check_file_contains(
        'database/add_automated_signal_support.sql',
        'status VARCHAR(20)',
        'Database status column'
    )
    
    # Summary
    print("\n" + "=" * 60)
    if all_checks_passed:
        print("✅ ALL CHECKS PASSED - READY FOR DEPLOYMENT!")
        print("\n📋 Next Steps:")
        print("   1. Review changes in GitHub Desktop")
        print("   2. Commit with message: 'Add automated signal lab webhook system'")
        print("   3. Push to main branch")
        print("   4. Wait for Railway deployment (2-3 minutes)")
        print("   5. Set up TradingView alerts")
        print("\n📖 See DEPLOY_AUTOMATED_SIGNALS_NOW.md for detailed instructions")
        return 0
    else:
        print("❌ SOME CHECKS FAILED - REVIEW ERRORS ABOVE")
        print("\n⚠️  Fix the issues before deploying")
        return 1

if __name__ == "__main__":
    sys.exit(main())
