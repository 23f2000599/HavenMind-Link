#!/usr/bin/env python3
"""
Setup script for HavenMind with Gemini AI integration
"""

import os
import sys

def setup_gemini_ai():
    """Setup Gemini AI integration"""
    print("🤖 Setting up HavenMind with Gemini AI...")
    
    # Check if .env file exists
    env_path = os.path.join("havenmind-basic", ".env")
    
    if not os.path.exists(env_path):
        print("❌ .env file not found!")
        return False
    
    # Read current .env file
    with open(env_path, 'r') as f:
        env_content = f.read()
    
    # Check if API key is set
    if "your_gemini_api_key_here" in env_content:
        print("\n📝 Gemini API Key Setup Required")
        print("=" * 50)
        print("To enable advanced therapeutic AI responses, you need a Gemini API key.")
        print("\n🔗 Get your free API key at: https://makersuite.google.com/app/apikey")
        print("\n📋 Steps:")
        print("1. Visit the link above")
        print("2. Sign in with your Google account")
        print("3. Create a new API key")
        print("4. Copy the API key")
        print("5. Replace 'your_gemini_api_key_here' in havenmind-basic/.env with your actual key")
        print("\n⚠️  Without the API key, the app will use basic fallback responses.")
        
        choice = input("\n❓ Do you have your API key ready? (y/n): ").lower().strip()
        
        if choice == 'y':
            api_key = input("🔑 Enter your Gemini API key: ").strip()
            if api_key:
                # Update .env file
                updated_content = env_content.replace("your_gemini_api_key_here", api_key)
                with open(env_path, 'w') as f:
                    f.write(updated_content)
                print("✅ API key saved successfully!")
                return True
            else:
                print("❌ No API key provided. Using fallback responses.")
                return False
        else:
            print("ℹ️  You can add your API key later by editing havenmind-basic/.env")
            return False
    else:
        print("✅ Gemini API key already configured!")
        return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    # Install for basic app
    basic_requirements = "havenmind-basic/requirements.txt"
    if os.path.exists(basic_requirements):
        os.system(f"pip install -r {basic_requirements}")
        print("✅ Basic app dependencies installed!")
    
    # Install for backend (if exists)
    backend_requirements = "havenmind-backend/requirements.txt"
    if os.path.exists(backend_requirements):
        os.system(f"pip install -r {backend_requirements}")
        print("✅ Backend dependencies installed!")

def main():
    """Main setup function"""
    print("🏥 HavenMind - AI-Powered Student Mental Health Platform")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required!")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Install dependencies
    install_dependencies()
    
    # Setup Gemini AI
    gemini_configured = setup_gemini_ai()
    
    print("\n🚀 Setup Complete!")
    print("=" * 30)
    
    if gemini_configured:
        print("✅ Gemini AI: Enabled (Advanced therapeutic responses)")
    else:
        print("⚠️  Gemini AI: Disabled (Using fallback responses)")
    
    print("\n📋 Next Steps:")
    print("1. Navigate to havenmind-basic directory: cd havenmind-basic")
    print("2. Run the application: python app.py")
    print("3. Open your browser to: http://localhost:5000")
    
    print("\n🔧 Features Available:")
    print("• AI-powered journal with therapeutic responses")
    print("• Personalized writing prompts")
    print("• Mood tracking and analytics")
    print("• Crisis detection and support resources")
    print("• Student-focused mental health tools")
    
    if not gemini_configured:
        print("\n💡 To enable advanced AI features later:")
        print("   Edit havenmind-basic/.env and add your Gemini API key")

if __name__ == "__main__":
    main()