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
    print("🚀 CLI Study Hub - Dependency Installer")
    print("=" * 50)
    
    # Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        print("Make sure you're running this from the CLI Study Hub directory.")
        return False
    
    print("📦 Installing dependencies from requirements.txt...")
    print()
    
    try:
        # Install requirements
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True, capture_output=True, text=True)
        
        print("✅ All dependencies installed successfully!")
        print()
        print("🎉 CLI Study Hub is ready to use!")
        print("Run: python3 study.py")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        print()
        print("Error output:")
        print(e.stderr)
        print()
        print("Try installing manually:")
        print("pip install rich PyPDF2 python-docx getch lxml")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

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
