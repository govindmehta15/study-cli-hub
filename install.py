#!/usr/bin/env python3
"""
CLI Study Hub Installation Script
Automatically installs all required dependencies
"""

import subprocess
import sys
import os

def install_requirements():
    """Install all requirements from requirements.txt"""
    print("🚀 CLI Study Hub - Complete Dependency Installer")
    print("=" * 50)
    
    # Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        print("Make sure you're running this from the CLI Study Hub directory.")
        return False
    
    print("📦 Installing ALL dependencies to ensure complete file format support...")
    print("This will install/update all packages regardless of current status.")
    print()
    
    # Define all dependencies explicitly
    dependencies = [
        "rich>=13.0.0",
        "PyPDF2>=3.0.0", 
        "python-docx>=0.8.11",
        "getch>=1.0.0",
        "lxml>=4.6.0"
    ]
    
    all_success = True
    
    for package in dependencies:
        print(f"Installing {package}...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], check=True, capture_output=True, text=True)
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            all_success = False
        except Exception as e:
            print(f"❌ Error installing {package}: {e}")
            all_success = False
    
    print()
    
    if all_success:
        print("🎉 ALL dependencies installed successfully!")
        print()
        print("✅ CLI Study Hub is ready to use!")
        print("✅ All file formats are now supported!")
        print("✅ No dependency errors will occur!")
        print()
        print("🚀 Run: python3 study.py")
        print()
        print("📋 Supported file types:")
        print("  • Text files (txt, md, py, json, js, html, css, xml, yaml, etc.)")
        print("  • Documents (pdf, doc, docx, csv)")
        print("  • Images (jpg, png, gif, bmp, tiff, svg, webp)")
        print("  • Archives (zip, rar, 7z, tar, gz, bz2, xz)")
        print("  • Executables (exe, dll, so, dylib, bin)")
        print("  • Media files (mp3, wav, flac, mp4, avi, mkv, mov, wmv)")
        print("  • Any other file format (with hex dump or text preview)")
    else:
        print("⚠️ Some dependencies failed to install.")
        print("The application will still work, but some file types may not be supported.")
        print()
        print("Try running manually:")
        print("pip install rich PyPDF2 python-docx getch lxml")
    
    return all_success

def main():
    """Main installation function"""
    print("CLI Study Hub v4.0 - Installation Script")
    print("=" * 50)
    print()
    
    # Check Python version
    if sys.version_info < (3, 6):
        print("❌ Python 3.6 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python version: {sys.version.split()[0]}")
    print()
    
    # Install dependencies
    success = install_requirements()
    
    if success:
        print()
        print("🎯 Next steps:")
        print("1. Run: python3 study.py")
        print("2. Enter your username or press Enter for global mode")
        print("3. Start studying!")
        print()
        print("📚 For help, check the README.md file")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
