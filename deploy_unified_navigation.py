"""
Deploy unified navigation to Railway
"""

import subprocess
import sys

def run_command(command, description):
    """Run a command and print results"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        if result.stderr:
            print(f"⚠️  Warnings: {result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Deploy navigation changes"""
    print("🎯 UNIFIED NAVIGATION DEPLOYMENT")
    print("="*60)
    
    # List of updated files
    updated_files = [
        'ml_feature_dashboard.html',
        'signal_lab_dashboard.html',
        'signal_analysis_lab.html',
        'automated_signals_dashboard.html',
        'time_analysis.html',
        'strategy_optimizer.html',
        'strategy_comparison.html',
        'ai_business_dashboard.html',
        'prop_firm_management.html',
        'trade_manager.html',
        'financial_summary.html',
        'reporting_hub.html',
        'homepage.html',  # Reference file
    ]
    
    print("\n📋 Files to deploy:")
    for file in updated_files:
        print(f"   ✓ {file}")
    
    print("\n" + "="*60)
    input("Press Enter to continue with deployment...")
    
    # Check git status
    if not run_command("git status", "Checking git status"):
        return False
    
    # Add files
    for file in updated_files:
        if not run_command(f"git add {file}", f"Adding {file}"):
            print(f"⚠️  Warning: Could not add {file}")
    
    # Commit
    commit_message = "Standardize navigation bar across all dashboards - 100% consistency"
    if not run_command(f'git commit -m "{commit_message}"', "Committing changes"):
        print("⚠️  No changes to commit or commit failed")
    
    # Push
    print("\n" + "="*60)
    print("🚀 Ready to push to Railway")
    print("="*60)
    input("Press Enter to push to main branch (triggers Railway deployment)...")
    
    if run_command("git push origin main", "Pushing to Railway"):
        print("\n" + "="*60)
        print("✅ DEPLOYMENT INITIATED")
        print("="*60)
        print("\n📊 Next steps:")
        print("1. Monitor Railway deployment: https://railway.app")
        print("2. Wait 2-3 minutes for build to complete")
        print("3. Test navigation on: https://web-production-cd33.up.railway.app/")
        print("4. Verify all 12 dashboards have consistent navigation")
        print("\n🎯 Navigation should now be identical across:")
        print("   • Homepage")
        print("   • ML Dashboard")
        print("   • Signal Lab Dashboard")
        print("   • Signal Analysis Lab")
        print("   • Automated Signals")
        print("   • Time Analysis")
        print("   • Strategy Optimizer")
        print("   • Strategy Comparison")
        print("   • AI Business Advisor")
        print("   • Prop Portfolio")
        print("   • Trade Manager")
        print("   • Financial Summary")
        print("   • Reports Hub")
        return True
    else:
        print("\n❌ Push failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
