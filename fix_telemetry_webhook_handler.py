"""
Fix webhook handler to accept telemetry format from NQ_FVG_CORE_TELEMETRY.pine

The telemetry indicator sends:
{
  "message": "",
  "attributes": {
    "event_type": "ENTRY",
    "trade_id": "...",
    ...
  }
}

But webhook expects:
{
  "type": "ENTRY",
  "signal_id": "...",
  ...
}

This script updates the webhook handler to support BOTH formats.
"""

import re

def fix_webhook_handler():
    with open('web_server.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the webhook handler function
    old_code = '''        # DUAL FORMAT SUPPORT: Strategy uses "type", Indicator uses "automation_stage"
        message_type = data.get('type')  # Strategy format
        automation_stage = data.get('automation_stage')  # Indicator format
        
        # Determine event type from either format
        if message_type:'''
    
    new_code = '''        # TRIPLE FORMAT SUPPORT: Strategy uses "type", Indicator uses "automation_stage", Telemetry uses "attributes"
        message_type = data.get('type')  # Strategy format
        automation_stage = data.get('automation_stage')  # Indicator format
        attributes = data.get('attributes')  # Telemetry format (NQ_FVG_CORE_TELEMETRY.pine)
        
        # Determine event type from any of the three formats
        if attributes:
            # TELEMETRY FORMAT (NQ_FVG_CORE_TELEMETRY.pine)
            # Flatten attributes into main data dict for consistent processing
            data.update(attributes)
            event_type = attributes.get('event_type')
            trade_id = attributes.get('trade_id')
            logger.info(f"📥 Telemetry signal: event_type={event_type}, id={trade_id}")
        elif message_type:'''
    
    if old_code not in content:
        print("❌ Could not find webhook handler code to replace")
        return False
    
    content = content.replace(old_code, new_code)
    
    with open('web_server.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Updated webhook handler to support telemetry format")
    return True

if __name__ == '__main__':
    if fix_webhook_handler():
        print("\n🎯 WEBHOOK HANDLER UPDATED")
        print("\nThe webhook now supports THREE formats:")
        print("1. Strategy format: {type: 'ENTRY', signal_id: '...'}")
        print("2. Indicator format: {automation_stage: 'ENTRY', trade_id: '...'}")
        print("3. Telemetry format: {attributes: {event_type: 'ENTRY', trade_id: '...'}}")
        print("\n📤 Commit and push to Railway to deploy the fix")
    else:
        print("\n❌ Fix failed - check the code manually")
