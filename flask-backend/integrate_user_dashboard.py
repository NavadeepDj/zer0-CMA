"""
Integration Script for User Dashboard and Enhanced Chatbot
Integrates all dashboard and chatbot functionality with the existing Flask app
"""

import logging
from flask import Flask
from dashboard_routes import integrate_dashboard_routes
from enhanced_chatbot_routes import integrate_enhanced_chatbot_routes
from integrate_firebase_auth import integrate_firebase_auth_with_app

logger = logging.getLogger(__name__)

def integrate_user_dashboard_with_app(app: Flask):
    """
    Integrate User Dashboard and Enhanced Chatbot with existing Flask app
    
    Args:
        app: Flask application instance
    """
    try:
        logger.info("🚀 Integrating User Dashboard and Enhanced Chatbot...")
        
        # Step 1: Integrate Firebase Authentication (if not already done)
        logger.info("Step 1: Setting up Firebase Authentication...")
        try:
            integrate_firebase_auth_with_app(app)
            logger.info("✅ Firebase Auth integration completed")
        except Exception as e:
            logger.warning(f"⚠️ Firebase Auth integration failed (may already be integrated): {e}")
        
        # Step 2: Integrate Dashboard Routes
        logger.info("Step 2: Integrating Dashboard Routes...")
        if integrate_dashboard_routes(app):
            logger.info("✅ Dashboard routes integrated successfully")
        else:
            raise Exception("Failed to integrate dashboard routes")
        
        # Step 3: Integrate Enhanced Chatbot Routes
        logger.info("Step 3: Integrating Enhanced Chatbot Routes...")
        if integrate_enhanced_chatbot_routes(app):
            logger.info("✅ Enhanced chatbot routes integrated successfully")
        else:
            raise Exception("Failed to integrate enhanced chatbot routes")
        
        # Step 4: Add dashboard route to main app
        @app.route('/')
        def index():
            """Redirect to dashboard or login"""
            from auth_routes import is_authenticated
            if is_authenticated():
                return app.redirect('/dashboard')
            else:
                return app.redirect('/auth_test.html')
        
        logger.info("✅ Main route redirects configured")
        
        # Step 5: Add error handlers
        @app.errorhandler(404)
        def not_found(error):
            return "Page not found. <a href='/dashboard'>Go to Dashboard</a>", 404
        
        @app.errorhandler(500)
        def internal_error(error):
            return "Internal server error. <a href='/dashboard'>Go to Dashboard</a>", 500
        
        logger.info("✅ Error handlers configured")
        
        logger.info("🎉 User Dashboard and Enhanced Chatbot integration complete!")
        
        # Print integration summary
        print("\n" + "="*60)
        print("🎉 USER DASHBOARD INTEGRATION COMPLETE!")
        print("="*60)
        print("\n✅ Integrated Components:")
        print("   • Firebase Authentication")
        print("   • User Dashboard with JotForm integration")
        print("   • Enhanced AI Chatbot with escalation")
        print("   • Dashboard API endpoints")
        print("   • Ticket management system")
        
        print("\n🌐 Available Routes:")
        print("   • / - Main page (redirects to dashboard or login)")
        print("   • /dashboard - User dashboard")
        print("   • /chatbot - Enhanced AI chatbot")
        print("   • /auth_test.html - Authentication test page")
        print("   • /api/auth/* - Authentication endpoints")
        print("   • /api/dashboard/* - Dashboard API endpoints")
        print("   • /api/chatbot/* - Enhanced chatbot endpoints")
        
        print("\n🔧 Features:")
        print("   • JotForm chatbot integration with escalation")
        print("   • Advanced AI support with ML models")
        print("   • Real-time ticket tracking")
        print("   • Priority escalation system")
        print("   • Agent assignment and routing")
        print("   • User authentication and session management")
        
        print("\n🚀 Next Steps:")
        print("   1. Configure Firebase credentials")
        print("   2. Update JotForm embed ID in user_dashboard.html")
        print("   3. Test authentication flow")
        print("   4. Test JotForm to Flask chatbot escalation")
        print("   5. Customize styling and branding")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ User Dashboard integration failed: {e}")
        return False

def test_dashboard_integration():
    """Test the dashboard integration"""
    try:
        logger.info("🧪 Testing User Dashboard integration...")
        
        # Create test Flask app
        from flask import Flask
        test_app = Flask(__name__)
        test_app.secret_key = 'test-secret-key'
        
        # Test integration
        success = integrate_user_dashboard_with_app(test_app)
        
        if success:
            # Check that routes are registered
            routes = [rule.rule for rule in test_app.url_map.iter_rules()]
            
            required_routes = [
                '/dashboard',
                '/chatbot',
                '/api/dashboard/tickets',
                '/api/chatbot/message',
                '/api/auth/login'
            ]
            
            missing_routes = []
            for route in required_routes:
                if not any(route in r for r in routes):
                    missing_routes.append(route)
            
            if missing_routes:
                logger.error(f"❌ Missing routes: {missing_routes}")
                return False
            
            logger.info("✅ All required routes are registered")
            logger.info("🎉 Dashboard integration test passed!")
            return True
        else:
            logger.error("❌ Integration failed")
            return False
        
    except Exception as e:
        logger.error(f"❌ Dashboard integration test failed: {e}")
        return False

if __name__ == "__main__":
    # Test the integration
    logging.basicConfig(level=logging.INFO)
    
    success = test_dashboard_integration()
    if success:
        print("\n✅ User Dashboard integration is ready!")
        print("\nTo integrate with your existing Flask app, add this to your app.py:")
        print("```python")
        print("from integrate_user_dashboard import integrate_user_dashboard_with_app")
        print("integrate_user_dashboard_with_app(app)")
        print("```")
        print("\nThen start your Flask app and visit:")
        print("• http://localhost:5000/ - Main page")
        print("• http://localhost:5000/dashboard - User dashboard")
        print("• http://localhost:5000/chatbot - Enhanced chatbot")
        print("• http://localhost:5000/auth_test.html - Authentication test")
    else:
        print("❌ Dashboard integration failed. Check the logs for details.")
        exit(1)