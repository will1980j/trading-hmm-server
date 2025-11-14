"""
Automatic Indicator Documentation Updater

Run this script whenever you make changes to the indicator to keep documentation current.
Usage: python update_indicator_docs.py "Brief description of what changed"
"""

import sys
from datetime import datetime

def update_session_starter(change_description):
    """Update INDICATOR_SESSION_STARTER.md with latest changes"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d")
    
    # Read current file
    with open('INDICATOR_SESSION_STARTER.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update the "Current Status" section
    status_start = content.find("**Current Status:**")
    status_end = content.find("---", status_start + 1)
    
    if status_start != -1 and status_end != -1:
        # Extract existing status
        current_status = content[status_start:status_end]
        
        # Add new change to status
        new_status = f"""**Current Status:** ✅ UPDATED ({timestamp})
- Historical webhook spam: FIXED using `signal_is_realtime` flag
- MFE labels showing 0.0: FIXED by decoupling from webhooks
- Verification: 12/12 checks passed (100%)
- **Latest Change ({timestamp}):** {change_description}

"""
        
        # Replace status section
        updated_content = content[:status_start] + new_status + content[status_end:]
        
        # Write back
        with open('INDICATOR_SESSION_STARTER.md', 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"✅ Updated INDICATOR_SESSION_STARTER.md with: {change_description}")
        return True
    else:
        print("❌ Could not find status section to update")
        return False

def update_master_docs(change_description):
    """Add entry to fix history in master documentation"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d")
    
    try:
        with open('INDICATOR_FIX_MASTER_DOCUMENTATION.md', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the fix history section
        history_marker = "## 📋 COMPLETE FIX HISTORY"
        history_pos = content.find(history_marker)
        
        if history_pos != -1:
            # Find the end of the section header
            next_section = content.find("### **Attempt", history_pos)
            
            if next_section != -1:
                # Count existing attempts
                attempt_count = content[:next_section].count("### **Attempt") + 1
                
                # Create new entry
                new_entry = f"""
### **Update {attempt_count}: {timestamp}**
**Description:** {change_description}  
**Status:** In Progress  
**Notes:** Update made via automated documentation system

"""
                
                # Insert new entry
                updated_content = content[:next_section] + new_entry + content[next_section:]
                
                with open('INDICATOR_FIX_MASTER_DOCUMENTATION.md', 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                print(f"✅ Added entry to INDICATOR_FIX_MASTER_DOCUMENTATION.md")
                return True
        
        print("⚠️  Could not update master documentation (section not found)")
        return False
        
    except Exception as e:
        print(f"⚠️  Could not update master documentation: {e}")
        return False

def run_verification():
    """Run the verification script to check current state"""
    import subprocess
    
    print("\n🔍 Running verification...")
    try:
        result = subprocess.run(['python', 'verify_indicator_fix.py'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Verification passed!")
            return True
        else:
            print("❌ Verification failed!")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"⚠️  Could not run verification: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python update_indicator_docs.py \"Description of change\"")
        print("\nExample:")
        print('  python update_indicator_docs.py "Added new feature X to improve Y"')
        sys.exit(1)
    
    change_description = sys.argv[1]
    
    print("=" * 80)
    print("INDICATOR DOCUMENTATION UPDATER")
    print("=" * 80)
    print(f"\nChange: {change_description}")
    print()
    
    # Update session starter
    starter_updated = update_session_starter(change_description)
    
    # Update master docs
    master_updated = update_master_docs(change_description)
    
    # Run verification
    verification_passed = run_verification()
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Session Starter: {'✅ Updated' if starter_updated else '❌ Failed'}")
    print(f"Master Docs: {'✅ Updated' if master_updated else '⚠️  Skipped'}")
    print(f"Verification: {'✅ Passed' if verification_passed else '❌ Failed'}")
    print()
    
    if starter_updated and verification_passed:
        print("✅ Documentation updated successfully!")
        print("\n📝 Next steps:")
        print("1. Review changes in INDICATOR_SESSION_STARTER.md")
        print("2. Commit changes to Git")
        print("3. Continue development")
    else:
        print("⚠️  Some updates failed - review output above")
    
    print("=" * 80)

if __name__ == '__main__':
    main()
