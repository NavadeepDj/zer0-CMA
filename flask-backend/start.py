#!/usr/bin/env python3
"""
Startup script for Prashna Zer0 Customer Support Chatbot
"""

import os
import sys
import subprocess
import time
import webbrowser
from threading import Timer

def check_dependencies():
    """Check if required packages are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import flask
        import flask_cors
        print("✅ All dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Please run: pip install -r requirements.txt")
        return False

def start_server():
    """Start the Flask server"""
    print("🚀 Starting Prashna Chatbot Server...")
    print("=" * 50)
    
    # Import and run the app
    from app import app
    
    def open_browser():
        """Open browser after a short delay"""
        time.sleep(2)
        print("🌐 Opening browser...")
        webbrowser.open('http://localhost:5000')
    
    # Start browser opener in background
    Timer(1.0, open_browser).start()
    
    print("✅ Server starting at http://localhost:5000")
    print("💬 Chat with Prashna in your browser!")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start Flask app
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)

def main():
    """Main startup function"""
    print("🤖 Prashna - Zer0 Customer Support Chatbot")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found!")
        print("💡 Please run this script from the flask-backend directory")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        print("👋 Thanks for using Prashna!")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()