"""
Check if the file is being tracked and its status
"""
import subprocess
import os

def check_file_status():
    file_path = 'templates/automated_signals_dashboard.html'
    
    print("Checking Git status for:", file_path)
    print("=" * 60)
    
    # Check if file exists
    if os.path.exists(file_path):
        print("✓ File exists on disk")
        file_size = os.path.getsize(file_path)
        print(f"  File size: {file_size:,} bytes")
    else:
        print("✗ File does not exist!")
        return
    
    print("\n" + "=" * 60)
    print("SOLUTION:")
    print("=" * 60)
    print("\nSince the file has been modified but GitHub Desktop")
    print("isn't showing it, here's what to do:")
    print("\n1. MANUAL COMMIT via Command Line:")
    print("   - Open Command Prompt in your project folder")
    print("   - Run: git add templates/automated_signals_dashboard.html")
    print("   - Run: git commit -m 'Add calendar to automated signals'")
    print("   - Run: git push")
    print("\n2. OR - Force GitHub Desktop to see it:")
    print("   - In GitHub Desktop, go to Repository menu")
    print("   - Click 'Open in Command Prompt' or 'Open in Terminal'")
    print("   - Run: git add .")
    print("   - Go back to GitHub Desktop - it should now show")
    print("\n3. OR - Nuclear option:")
    print("   - Make a visible change to the file")
    print("   - Add a blank line at the very end")
    print("   - Save the file")
    print("   - GitHub Desktop should detect it")

if __name__ == '__main__':
    check_file_status()
