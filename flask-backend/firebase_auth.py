"""
Firebase Authentication Integration
Handles user authentication using Firebase Auth while keeping existing data storage
"""

import firebase_admin
from firebase_admin import credentials, auth
import os
import logging
from datetime import datetime
import json
from functools import wraps
from flask import request, jsonify

logger = logging.getLogger(__name__)

class FirebaseAuth:
    """Firebase Authentication manager"""
    
    def __init__(self):
        self.app = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK for authentication only"""
        try:
            # Check if Firebase is already initialized
            if firebase_admin._apps:
                self.app = firebase_admin.get_app()
                logger.info("✅ Using existing Firebase app for authentication")
            else:
                # Initialize Firebase with service account credentials
                service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH', 'firebase-service-account.json')
                
                if os.path.exists(service_account_path):
                    # Use service account file
                    cred = credentials.Certificate(service_account_path)
                    self.app = firebase_admin.initialize_app(cred)
                    logger.info("✅ Firebase Auth initialized with service account file")
                else:
                    # Try to use environment variables for service account
                    service_account_info = self._get_service_account_from_env()
                    if service_account_info:
                        cred = credentials.Certificate(service_account_info)
                        self.app = firebase_admin.initialize_app(cred)
                        logger.info("✅ Firebase Auth initialized with environment variables")
                    else:
                        # Use default credentials (for development)
                        cred = credentials.ApplicationDefault()
                        self.app = firebase_admin.initialize_app(cred)
                        logger.info("✅ Firebase Auth initialized with default credentials")
            
            # Test authentication service
            self._test_auth_connection()
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Firebase Auth: {e}")
            raise
    
    def _get_service_account_from_env(self):
        """Get service account info from environment variables"""
        try:
            service_account_json = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')
            if service_account_json:
                return json.loads(service_account_json)
            
            # Alternative: individual environment variables
            project_id = os.getenv('FIREBASE_PROJECT_ID')
            private_key = os.getenv('FIREBASE_PRIVATE_KEY')
            client_email = os.getenv('FIREBASE_CLIENT_EMAIL')
            
            if project_id and private_key and client_email:
                return {
                    "type": "service_account",
                    "project_id": project_id,
                    "private_key": private_key.replace('\\n', '\n'),
                    "client_email": client_email,
                    "client_id": os.getenv('FIREBASE_CLIENT_ID', ''),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{client_email}"
                }
            
            return None
        except Exception as e:
            logger.error(f"Error parsing service account from environment: {e}")
            return None
    
    def _test_auth_connection(self):
        """Test Firebase Auth connection"""
        try:
            # Try to list users (this will work even if no users exist)
            users = auth.list_users(max_results=1)
            logger.info("✅ Firebase Auth connection test successful")
        except Exception as e:
            logger.error(f"❌ Firebase Auth connection test failed: {e}")
            raise
    
    def create_user(self, email: str, password: str, display_name: str = None, **kwargs):
        """Create a new user in Firebase Auth"""
        try:
            user_record = auth.create_user(
                email=email,
                password=password,
                display_name=display_name,
                **kwargs
            )
            logger.info(f"✅ Created Firebase user: {user_record.uid}")
            return {
                'uid': user_record.uid,
                'email': user_record.email,
                'display_name': user_record.display_name,
                'created': True
            }
        except Exception as e:
            logger.error(f"❌ Failed to create user {email}: {e}")
            raise
    
    def get_user_by_email(self, email: str):
        """Get user by email from Firebase Auth"""
        try:
            user_record = auth.get_user_by_email(email)
            return {
                'uid': user_record.uid,
                'email': user_record.email,
                'display_name': user_record.display_name,
                'email_verified': user_record.email_verified,
                'disabled': user_record.disabled,
                'created_at': user_record.user_metadata.creation_timestamp,
                'last_sign_in': user_record.user_metadata.last_sign_in_timestamp
            }
        except auth.UserNotFoundError:
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get user by email {email}: {e}")
            raise
    
    def get_user_by_uid(self, uid: str):
        """Get user by UID from Firebase Auth"""
        try:
            user_record = auth.get_user(uid)
            return {
                'uid': user_record.uid,
                'email': user_record.email,
                'display_name': user_record.display_name,
                'email_verified': user_record.email_verified,
                'disabled': user_record.disabled,
                'created_at': user_record.user_metadata.creation_timestamp,
                'last_sign_in': user_record.user_metadata.last_sign_in_timestamp
            }
        except auth.UserNotFoundError:
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get user by UID {uid}: {e}")
            raise
    
    def verify_token(self, id_token: str):
        """Verify Firebase ID token"""
        try:
            decoded_token = auth.verify_id_token(id_token)
            return {
                'uid': decoded_token['uid'],
                'email': decoded_token.get('email'),
                'email_verified': decoded_token.get('email_verified', False),
                'name': decoded_token.get('name'),
                'valid': True
            }
        except Exception as e:
            logger.error(f"❌ Token verification failed: {e}")
            return {'valid': False, 'error': str(e)}
    
    def update_user(self, uid: str, **kwargs):
        """Update user in Firebase Auth"""
        try:
            user_record = auth.update_user(uid, **kwargs)
            logger.info(f"✅ Updated Firebase user: {uid}")
            return {
                'uid': user_record.uid,
                'email': user_record.email,
                'display_name': user_record.display_name,
                'updated': True
            }
        except Exception as e:
            logger.error(f"❌ Failed to update user {uid}: {e}")
            raise
    
    def delete_user(self, uid: str):
        """Delete user from Firebase Auth"""
        try:
            auth.delete_user(uid)
            logger.info(f"✅ Deleted Firebase user: {uid}")
            return {'deleted': True}
        except Exception as e:
            logger.error(f"❌ Failed to delete user {uid}: {e}")
            raise
    
    def set_custom_claims(self, uid: str, custom_claims: dict):
        """Set custom claims for a user (for role-based access)"""
        try:
            auth.set_custom_user_claims(uid, custom_claims)
            logger.info(f"✅ Set custom claims for user {uid}: {custom_claims}")
            return {'claims_set': True}
        except Exception as e:
            logger.error(f"❌ Failed to set custom claims for {uid}: {e}")
            raise
    
    def create_custom_token(self, uid: str, additional_claims: dict = None):
        """Create a custom token for a user"""
        try:
            custom_token = auth.create_custom_token(uid, additional_claims)
            logger.info(f"✅ Created custom token for user: {uid}")
            return custom_token.decode('utf-8')
        except Exception as e:
            logger.error(f"❌ Failed to create custom token for {uid}: {e}")
            raise

# Global Firebase Auth instance
firebase_auth = None

def get_firebase_auth():
    """Get Firebase Auth instance"""
    global firebase_auth
    if not firebase_auth:
        firebase_auth = FirebaseAuth()
    return firebase_auth

def initialize_firebase_auth():
    """Initialize Firebase Auth (called from app startup)"""
    global firebase_auth
    if not firebase_auth:
        firebase_auth = FirebaseAuth()
    return firebase_auth

# Flask decorators for authentication
def require_auth(f):
    """Decorator to require Firebase authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No authorization header'}), 401
        
        try:
            # Extract token from "Bearer <token>"
            token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header
            
            # Verify token
            firebase_auth_instance = get_firebase_auth()
            decoded_token = firebase_auth_instance.verify_token(token)
            
            if not decoded_token['valid']:
                return jsonify({'error': 'Invalid token', 'details': decoded_token.get('error')}), 401
            
            # Add user info to request context
            request.current_user = decoded_token
            
        except Exception as e:
            return jsonify({'error': 'Authentication failed', 'details': str(e)}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_role(required_role):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'error': 'Authentication required'}), 401
            
            user_role = request.current_user.get('role', 'customer')
            
            if user_role != required_role and user_role != 'admin':
                return jsonify({'error': f'Role {required_role} required'}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

# User management functions that integrate with existing JSON storage
def sync_user_to_local_storage(firebase_user, role='customer'):
    """Sync Firebase user to local JSON storage"""
    try:
        # Load existing users from JSON
        users_file = 'users.json'
        users = {}
        
        if os.path.exists(users_file):
            with open(users_file, 'r') as f:
                users = json.load(f)
        
        # Create user entry
        user_data = {
            'firebase_uid': firebase_user['uid'],
            'email': firebase_user['email'],
            'display_name': firebase_user.get('display_name', ''),
            'role': role,
            'created_at': datetime.now().isoformat(),
            'last_login': datetime.now().isoformat(),
            'is_active': True
        }
        
        # Use Firebase UID as key
        users[firebase_user['uid']] = user_data
        
        # Save to JSON
        with open(users_file, 'w') as f:
            json.dump(users, f, indent=2)
        
        logger.info(f"✅ Synced user {firebase_user['email']} to local storage")
        return user_data
        
    except Exception as e:
        logger.error(f"❌ Failed to sync user to local storage: {e}")
        raise

def get_local_user_by_firebase_uid(firebase_uid):
    """Get user from local JSON storage by Firebase UID"""
    try:
        users_file = 'users.json'
        if not os.path.exists(users_file):
            return None
        
        with open(users_file, 'r') as f:
            users = json.load(f)
        
        return users.get(firebase_uid)
        
    except Exception as e:
        logger.error(f"❌ Failed to get local user: {e}")
        return None

def update_local_user_login(firebase_uid):
    """Update last login time for user in local storage"""
    try:
        users_file = 'users.json'
        if not os.path.exists(users_file):
            return False
        
        with open(users_file, 'r') as f:
            users = json.load(f)
        
        if firebase_uid in users:
            users[firebase_uid]['last_login'] = datetime.now().isoformat()
            
            with open(users_file, 'w') as f:
                json.dump(users, f, indent=2)
            
            logger.info(f"✅ Updated last login for user {firebase_uid}")
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"❌ Failed to update user login: {e}")
        return False