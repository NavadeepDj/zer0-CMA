"""
Firebase Configuration and Initialization
Handles Firebase Admin SDK setup and database connections
"""

import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class FirebaseConfig:
    """Firebase configuration and initialization"""
    
    def __init__(self):
        self.db = None
        self.app = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase is already initialized
            if firebase_admin._apps:
                self.app = firebase_admin.get_app()
                logger.info("✅ Using existing Firebase app")
            else:
                # Initialize Firebase with service account credentials
                service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH', 'firebase-service-account.json')
                
                if os.path.exists(service_account_path):
                    # Use service account file
                    cred = credentials.Certificate(service_account_path)
                    self.app = firebase_admin.initialize_app(cred)
                    logger.info("✅ Firebase initialized with service account file")
                else:
                    # Try to use environment variables for service account
                    service_account_info = self._get_service_account_from_env()
                    if service_account_info:
                        cred = credentials.Certificate(service_account_info)
                        self.app = firebase_admin.initialize_app(cred)
                        logger.info("✅ Firebase initialized with environment variables")
                    else:
                        # Use default credentials (for development)
                        cred = credentials.ApplicationDefault()
                        self.app = firebase_admin.initialize_app(cred)
                        logger.info("✅ Firebase initialized with default credentials")
            
            # Initialize Firestore client
            self.db = firestore.client()
            logger.info("✅ Firestore client initialized")
            
            # Test connection
            self._test_connection()
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Firebase: {e}")
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
    
    def _test_connection(self):
        """Test Firebase connection"""
        try:
            # Try to access a collection (this will create it if it doesn't exist)
            test_ref = self.db.collection('_test').document('connection_test')
            test_ref.set({
                'timestamp': datetime.now(),
                'status': 'connected'
            })
            
            # Read it back
            doc = test_ref.get()
            if doc.exists:
                logger.info("✅ Firebase connection test successful")
                # Clean up test document
                test_ref.delete()
            else:
                raise Exception("Test document not found")
                
        except Exception as e:
            logger.error(f"❌ Firebase connection test failed: {e}")
            raise
    
    def get_db(self):
        """Get Firestore database client"""
        if not self.db:
            raise Exception("Firebase not initialized")
        return self.db

# Global Firebase instance
firebase_config = None

def get_firebase_db():
    """Get Firebase database instance"""
    global firebase_config
    if not firebase_config:
        firebase_config = FirebaseConfig()
    return firebase_config.get_db()

def initialize_firebase():
    """Initialize Firebase (called from app startup)"""
    global firebase_config
    if not firebase_config:
        firebase_config = FirebaseConfig()
    return firebase_config