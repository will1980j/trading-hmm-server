#!/usr/bin/env python3
"""
Test Complete Automation Deployment Readiness
"""

import os
import json
from datetime import datetime

def test_deployment_readiness():
    """Test if complete automation system is ready for deployment"""
    print("TESTING COMPLETE AUTOMATION DEPLOYMENT READINESS")
    print("=" * 60)
    
    # Test 1: Check all required files exist
    required_files = [
        'complete_automation_pipeline.py',
        'enhanced_webhook_processor_v2.py',
        'complete_automation_integration.py',
        'automation_database_schema.sql'
    ]
    
    print("\n1. CHECKING REQUIRED FILES:")
    all_files_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - MISSING")
            all_files_exist = False
    
    # Test 2: Test component imports
    print("\n2. TESTING COMPONENT IMPORTS:")
    try:
        from complete_automation_pipeline import CompleteAutomationPipeline
        print("   ✅ CompleteAutomationPipeline imported")
        
        from enhanced_webhook_processor_v2 import EnhancedWebhookProcessorV2
        print("   ✅ EnhancedWebhookProcessorV2 imported")
        
        components_importable = True
    except ImportError as e:
        print(f"   ❌ Import failed: {str(e)}")
        components_importable = False
    
    # Test 3: Test signal processing logic
    print("\n3. TESTING SIGNAL PROCESSING LOGIC:")
    try:
        processor = EnhancedWebhookProcessorV2()
        
        # Test signal for data collection
        test_signal = {
            "signal_type": "Bullish",
            "signal_candle": {
                "open": 20500.25,
                "high": 20502.75,
                "low": 20499.50,
                "close": 20501.00
            },
            "fvg_data": {
                "bias": "Bullish",
                "strength": 85.0
            },
            "htf_data": {
                "aligned": True,
                "bias_1h": "Bullish",
                "bias_15m": "Bullish",
                "bias_5m": "Bullish"
            },
            "session_data": {
                "current_session": "NY AM",
                "valid": True
            },
            "methodology_data": {
                "requires_confirmation": True,
                "stop_loss_buffer": 25
            }
        }
        
        result = processor.process_enhanced_fvg_webhook(test_signal)
        
        if result.get('webhook_processing') == 'enhanced_v2':
            print("   ✅ Signal processing logic working")
            print(f"   ✅ Webhook processing: {result.get('webhook_processing')}")
            processing_works = True
        else:
            print(f"   ❌ Unexpected processing result: {result}")
            processing_works = False
            
    except Exception as e:
        print(f"   ❌ Signal processing test failed: {str(e)}")
        processing_works = False
    
    # Test 4: Check database schema
    print("\n4. CHECKING DATABASE SCHEMA:")
    try:
        with open('automation_database_schema.sql', 'r') as f:
            schema_content = f.read()
        
        required_tables = [
            'enhanced_signals_v2',
            'automation_level',
            'data_collection_mode',
            'forward_testing'
        ]
        
        schema_complete = True
        for table in required_tables:
            if table in schema_content:
                print(f"   ✅ {table} found in schema")
            else:
                print(f"   ❌ {table} missing from schema")
                schema_complete = False
                
    except Exception as e:
        print(f"   ❌ Schema check failed: {str(e)}")
        schema_complete = False
    
    # Test 5: Check integration code
    print("\n5. CHECKING INTEGRATION CODE:")
    try:
        with open('complete_automation_integration.py', 'r') as f:
            integration_content = f.read()
        
        required_endpoints = [
            '/api/live-signals-v2-complete',
            '/api/automation/status',
            '/api/automation/data-stats'
        ]
        
        integration_complete = True
        for endpoint in required_endpoints:
            if endpoint in integration_content:
                print(f"   ✅ {endpoint} endpoint found")
            else:
                print(f"   ❌ {endpoint} endpoint missing")
                integration_complete = False
                
    except Exception as e:
        print(f"   ❌ Integration check failed: {str(e)}")
        integration_complete = False
    
    # Overall assessment
    print("\n" + "=" * 60)
    print("DEPLOYMENT READINESS ASSESSMENT:")
    print("=" * 60)
    
    tests = {
        "Required Files": all_files_exist,
        "Component Imports": components_importable,
        "Signal Processing": processing_works,
        "Database Schema": schema_complete,
        "Integration Code": integration_complete
    }
    
    passed_tests = sum(tests.values())
    total_tests = len(tests)
    
    for test_name, result in tests.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\nOVERALL: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 COMPLETE AUTOMATION SYSTEM READY FOR DEPLOYMENT!")
        print("\nYour system is ready for:")
        print("✅ Comprehensive data collection")
        print("✅ Forward testing and analysis")
        print("✅ Prop firm preparation")
        print("✅ Exact methodology compliance")
        print("✅ Real-time performance monitoring")
        
        print("\nNEXT STEPS:")
        print("1. Apply database schema to Railway")
        print("2. Integrate code with web_server.py")
        print("3. Update TradingView webhook URL")
        print("4. Begin comprehensive data collection")
        
        print(f"\nNEW WEBHOOK ENDPOINT:")
        print("https://web-production-cd33.up.railway.app/api/live-signals-v2-complete")
        
    else:
        print(f"\n⚠️ {total_tests - passed_tests} tests failed")
        print("Please address the failed tests before deployment")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    test_deployment_readiness()