#!/usr/bin/env python3
"""
Screenshot Analysis Setup Script
Installs dependencies and configures the system for automated screenshot analysis
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_screenshot.txt"])
        print("✅ Python dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_tesseract():
    """Check if Tesseract OCR is installed"""
    print("🔍 Checking Tesseract OCR installation...")
    try:
        result = subprocess.run(["tesseract", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Tesseract OCR is installed")
            print(f"Version: {result.stdout.split()[1]}")
            return True
        else:
            print("❌ Tesseract OCR not found")
            return False
    except FileNotFoundError:
        print("❌ Tesseract OCR not found in PATH")
        return False

def setup_tesseract_path():
    """Setup Tesseract path for Windows"""
    if os.name == 'nt':  # Windows
        common_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe".format(os.getenv('USERNAME'))
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                print(f"✅ Found Tesseract at: {path}")
                
                # Update screenshot_analyzer.py with correct path
                analyzer_file = Path("screenshot_analyzer.py")
                if analyzer_file.exists():
                    content = analyzer_file.read_text()
                    updated_content = content.replace(
                        "# pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'",
                        f"pytesseract.pytesseract.tesseract_cmd = r'{path}'"
                    )
                    analyzer_file.write_text(updated_content)
                    print("✅ Updated screenshot_analyzer.py with Tesseract path")
                
                return True
        
        print("❌ Tesseract not found in common locations")
        return False
    else:
        print("ℹ️  Non-Windows system - Tesseract should be in PATH")
        return True

def test_screenshot_analysis():
    """Test the screenshot analysis system"""
    print("🧪 Testing screenshot analysis system...")
    try:
        from screenshot_analyzer import ScreenshotAnalyzer
        analyzer = ScreenshotAnalyzer()
        print("✅ Screenshot analyzer initialized successfully")
        
        # Test with a simple image (if available)
        print("✅ Screenshot analysis system is ready")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Screenshot Analysis System")
    print("=" * 50)
    
    success = True
    
    # Step 1: Install Python dependencies
    if not install_requirements():
        success = False
    
    # Step 2: Check Tesseract installation
    if not check_tesseract():
        print("\n📋 Tesseract OCR Installation Instructions:")
        print("1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("2. Install with default settings")
        print("3. Add to PATH or run this script again")
        success = False
    else:
        # Step 3: Setup Tesseract path (Windows)
        setup_tesseract_path()
    
    # Step 4: Test the system
    if success and test_screenshot_analysis():
        print("\n🎉 Screenshot Analysis Setup Complete!")
        print("\nFeatures now available:")
        print("• 📊 Automatic price extraction from charts")
        print("• 🎯 FVG quality scoring (0-10)")
        print("• 🔍 Confluence detection")
        print("• 📈 Trend strength analysis")
        print("• 🤖 Auto-population of trade fields")
        print("• 💾 Analysis data storage in database")
        
        print("\nNext steps:")
        print("1. Upload screenshots in Signal Lab")
        print("2. Watch automatic analysis and field population")
        print("3. Review AI-generated setup quality scores")
        
    else:
        print("\n⚠️  Setup incomplete - please resolve issues above")
    
    return success

if __name__ == "__main__":
    main()