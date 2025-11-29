#!/usr/bin/env python3
"""
Install ML dependencies for the system
"""

import subprocess
import sys

def install_dependencies():
    """Install required ML dependencies"""
    
    dependencies = [
        "torch",
        "transformers",
        "sentence-transformers",
        "numpy",
        "scikit-learn"
    ]
    
    print("Installing ML dependencies...")
    print("=" * 50)
    
    for dep in dependencies:
        try:
            print(f"Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✅ {dep} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}: {e}")
    
    print("\\n" + "=" * 50)
    print("ML dependencies installation completed!")
    print("\\nNote: First run will download pre-trained models (~500MB)")
    print("This is normal and only happens once.")

if __name__ == "__main__":
    install_dependencies()