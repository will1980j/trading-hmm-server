"""
Update all dashboard pages with centered navigation and home link
"""
import re

# List of all dashboard HTML files
dashboard_files = [
    'signal_lab_dashboard.html',
    'signal_analysis_lab.html',
    'signal_lab_v2_dashboard.html',
    'ml_feature_dashboard.html',
    'time_analysis.html',
    'strategy_comparison.html',
    'ai_business_advisor.html',
    'prop_portfolio.html',
    'trade_manager.html',
    'financial_summary.html',
    'reporting_hub.html',
    'strategy_optimizer.html'
]

def update_navigation(file_path):
    """Update navigation in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file has navigation
        if '<nav' not in content.lower():
            print(f"⚠️  {file_path}: No navigation found")
            return False
        
        # Add justify-content: center to nav styling
        content = re.sub(
            r'(nav[^{]*\{[^}]*display:\s*flex;[^}]*)',
            r'\1\n    justify-content: center;',
            content,
            flags=re.IGNORECASE
        )
        
        # Add home link if not present
        if '/homepage' not in content:
            # Find the nav opening and add home link
            content = re.sub(
                r'(<nav[^>]*>\s*)(<a\s+href="/ml-dashboard")',
                r'\1<a href="/homepage">🏠 Home</a>\n        \2',
                content,
                flags=re.IGNORECASE
            )
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ {file_path}: Updated")
        return True
        
    except FileNotFoundError:
        print(f"❌ {file_path}: File not found")
        return False
    except Exception as e:
        print(f"❌ {file_path}: Error - {e}")
        return False

def main():
    print("Updating navigation across all dashboard pages...")
    print("=" * 60)
    
    updated = 0
    for file in dashboard_files:
        if update_navigation(file):
            updated += 1
    
    print("=" * 60)
    print(f"✅ Updated {updated}/{len(dashboard_files)} files")
    print("\nCommit these files to deploy the changes.")

if __name__ == '__main__':
    main()
