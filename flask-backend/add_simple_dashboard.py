"""
Add Simple Dashboard to Existing Flask App
Simple integration without Firebase - just session-based authentication
"""

from flask import Flask
from simple_user_dashboard import add_simple_auth_routes
import logging

logger = logging.getLogger(__name__)

def integrate_simple_dashboard(app: Flask):
    """
    Add simple dashboard with session-based authentication to existing Flask app
    No Firebase required - uses simple JSON file storage
    """
    try:
        logger.info("🚀 Adding Simple Dashboard to existing Flask app...")
        
        # Add authentication routes
        if add_simple_auth_routes(app):
            logger.info("✅ Simple authentication routes added")
        else:
            raise Exception("Failed to add authentication routes")
        
        # Modify existing index route to handle authenticated users
        @app.route('/dashboard-redirect')
        def dashboard_redirect():
            """Redirect authenticated users to dashboard"""
            from flask import session, redirect
            
            if session.get('logged_in'):
                return redirect('/dashboard')
            else:
                return redirect('/login')
        
        logger.info("✅ Dashboard redirect route added")
        
        logger.info("🎉 Simple Dashboard integration complete!")
        
        print("\n" + "="*60)
        print("🎉 SIMPLE DASHBOARD INTEGRATION COMPLETE!")
        print("="*60)
        print("\n✅ New Routes Added:")
        print("   • /login - User login page")
        print("   • /register - User registration page")
        print("   • /dashboard - User dashboard with JotForm")
        print("   • /logout - User logout")
        print("   • /api/user-info - Get current user info")
        
        print("\n🔐 Default Users (for testing):")
        print("   • admin@zer0.com / admin123")
        print("   • user@zer0.com / user123")
        
        print("\n🌐 How to Use:")
        print("   1. Go to http://localhost:5000/login")
        print("   2. Login with demo credentials")
        print("   3. Access dashboard with JotForm integration")
        print("   4. Use escalation to your existing chatbot")
        
        print("\n🔧 Features:")
        print("   • Session-based authentication (no Firebase needed)")
        print("   • JotForm chatbot integration")
        print("   • Escalation to your existing Flask chatbot")
        print("   • User registration and login")
        print("   • Responsive dashboard design")
        
        print("\n📝 Your existing routes remain unchanged!")
        print("   • / - Your existing chatbot (unchanged)")
        print("   • All other existing functionality preserved")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Simple Dashboard integration failed: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("🚀 Simple Dashboard Integration")
    print("\nThis adds a complete user dashboard with authentication to your existing Flask app.")
    print("\nTo integrate, add this to your app.py:")
    print("```python")
    print("from add_simple_dashboard import integrate_simple_dashboard")
    print("integrate_simple_dashboard(app)")
    print("```")
    
    print("\nFeatures:")
    print("✅ No Firebase configuration needed")
    print("✅ Simple session-based authentication")
    print("✅ JotForm chatbot integration")
    print("✅ Escalation to your existing chatbot")
    print("✅ User registration and login")
    print("✅ Preserves all existing functionality")
    
    print("\nDefault test users:")
    print("• admin@zer0.com / admin123")
    print("• user@zer0.com / user123")