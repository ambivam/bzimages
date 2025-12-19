"""
Setup script for PDF Grouper LLM
This script helps install dependencies and set up the environment for PDF grouping
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required Python packages"""
    print("📦 Installing Python dependencies...")
    
    packages = [
        "openai",
        "PyPDF2", 
        "pytesseract",
        "PyMuPDF",
        "pillow"
    ]
    
    for package in packages:
        try:
            print(f"   Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"   ✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install {package}: {e}")
            return False
    
    return True

def check_tesseract():
    """Check if Tesseract OCR is installed"""
    print("\n🔍 Checking Tesseract OCR installation...")
    
    try:
        import pytesseract
        # Try to get Tesseract version
        version = pytesseract.get_tesseract_version()
        print(f"   ✅ Tesseract OCR found: {version}")
        return True
    except Exception as e:
        print(f"   ⚠️  Tesseract OCR not found: {e}")
        print("   💡 Install Tesseract OCR:")
        print("      Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        print("      macOS: brew install tesseract")
        print("      Linux: sudo apt-get install tesseract-ocr")
        return False

def setup_api_key():
    """Guide user through API key setup"""
    print("\n🔑 OpenAI API Key Setup:")
    print("   1. Get your API key from: https://platform.openai.com/api-keys")
    print("   2. Set environment variable:")
    print("      Windows: set OPENAI_API_KEY=your-key-here")
    print("      macOS/Linux: export OPENAI_API_KEY=your-key-here")
    print("   3. Or create a .env file with: OPENAI_API_KEY=your-key-here")
    
    # Check if API key is already set
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"   ✅ API key found (ends with: ...{api_key[-4:]})")
        return True
    else:
        print("   ⚠️  API key not found in environment variables")
        return False

def main():
    """Main setup function"""
    print("🚀 PDF Grouper LLM Setup")
    print("=" * 40)
    
    # Install Python packages
    if not install_requirements():
        print("\n❌ Failed to install some dependencies")
        return False
    
    # Check Tesseract
    tesseract_ok = check_tesseract()
    
    # Setup API key
    api_key_ok = setup_api_key()
    
    print("\n" + "=" * 40)
    print("📋 Setup Summary:")
    print(f"   Python packages: ✅")
    print(f"   Tesseract OCR: {'✅' if tesseract_ok else '⚠️'}")
    print(f"   OpenAI API Key: {'✅' if api_key_ok else '⚠️'}")
    
    if tesseract_ok and api_key_ok:
        print("\n🎉 Setup complete! You can now run:")
        print("   python pdf_grouper_llm.py")
    else:
        print("\n⚠️  Please complete the missing setup steps above")
    
    return True

if __name__ == "__main__":
    main()
