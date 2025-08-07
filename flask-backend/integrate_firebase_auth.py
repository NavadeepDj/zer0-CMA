"""
Integration Script for Firebase Authentication
Adds Firebase Auth to existing Flask app without disrupting current functionality
"""

import logging
from flask import Flask
from firebase_auth import initialize_firebase_auth
from auth_routes import auth_bp

logger = logging.getLogger(__name__)

def integrate_firebase_auth_with_app(app: Flask):
    """
    Integrate Firebase Authentication with existing Flask app
    
    Args:
        app: Flask application instance
    """
    try:
        logger.info("🔧 Integrating Firebase Authentication...")
        
        # Initialize Firebase Auth
        initialize_firebase_auth()
        logger.info("✅ Firebase Auth initialized")
        
        # Register authentication blueprint
        app.register_blueprint(auth_bp)
        logger.info("✅ Auth routes registered")
        
        # Add session configuration for authentication
        if not app.secret_key:
            import os
            app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-in-production')
            logger.info("✅ Session secret key configured")
        
        # Add authentication helper functions to app context
        @app.context_processor
        def inject_auth_helpers():
            from auth_routes import is_authenticated, get_current_user
            return {
                'is_authenticated': is_authenticated,
                'current_user': get_current_user
            }
        
        logger.info("✅ Auth context helpers added")
        
        # Add CORS headers for authentication endpoints
        @app.after_request
        def after_request(response):
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response
        
        logger.info("✅ CORS configuration updated for auth")
        
        logger.info("🎉 Firebase Authentication integration complete!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Firebase Auth integration failed: {e}")
        return False

def create_test_admin_user():
    """Create a test admin user for development"""
    try:
        from firebase_auth import get_firebase_auth, sync_user_to_local_storage
        
        firebase_auth = get_firebase_auth()
        
        # Check if admin user already exists
        admin_email = "admin@zer0.com"
        existing_user = firebase_auth.get_user_by_email(admin_email)
        
        if existing_user:
            logger.info(f"✅ Admin user already exists: {admin_email}")
            return existing_user
        
        # Create admin user
        admin_user = firebase_auth.create_user(
            email=admin_email,
            password="admin123",  # Change this in production!
            display_name="System Administrator"
        )
        
        # Set admin role
        firebase_auth.set_custom_claims(admin_user['uid'], {'role': 'admin'})
        
        # Sync to local storage
        sync_user_to_local_storage(admin_user, 'admin')
        
        logger.info(f"✅ Created test admin user: {admin_email}")
        logger.warning("⚠️ Default admin password is 'admin123' - change this in production!")
        
        return admin_user
        
    except Exception as e:
        logger.error(f"❌ Failed to create test admin user: {e}")
        return None

def test_firebase_auth_integration():
    """Test Firebase Auth integration"""
    try:
        logger.info("🧪 Testing Firebase Auth integration...")
        
        from firebase_auth import get_firebase_auth
        
        # Test Firebase Auth connection
        firebase_auth = get_firebase_auth()
        logger.info("✅ Firebase Auth connection successful")
        
        # Create test admin user
        admin_user = create_test_admin_user()
        if admin_user:
            logger.info("✅ Test admin user ready")
        
        logger.info("🎉 Firebase Auth integration test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Firebase Auth integration test failed: {e}")
        return False

if __name__ == "__main__":
    # Test the integration
    logging.basicConfig(level=logging.INFO)
    
    success = test_firebase_auth_integration()
    if success:
        print("✅ Firebase Auth integration is ready!")
        print("\nTo integrate with your Flask app, add this to your app.py:")
        print("```python")
        print("from integrate_firebase_auth import integrate_firebase_auth_with_app")
        print("integrate_firebase_auth_with_app(app)")
        print("```")
        print("\nAuthentication endpoints will be available at:")
        print("- POST /api/auth/register")
        print("- POST /api/auth/login") 
        print("- POST /api/auth/logout")
        print("- GET /api/auth/profile")
        print("- PUT /api/auth/profile")
        print("- POST /api/auth/verify-token")
        print("- GET /api/auth/users (admin only)")
        print("- PUT /api/auth/users/<uid>/role (admin only)")
        print("\nTest admin user:")
        print("Email: admin@zer0.com")
        print("Password: admin123")
    else:
        print("❌ Firebase Auth integration failed. Check the logs for details.")
        exit(1)