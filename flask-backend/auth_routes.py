"""
Authentication Routes for Firebase Integration
Provides login, register, and user management endpoints
"""

from flask import Blueprint, request, jsonify, session
import logging
from firebase_auth import (
    get_firebase_auth, 
    sync_user_to_local_storage, 
    get_local_user_by_firebase_uid,
    update_local_user_login
)

logger = logging.getLogger(__name__)

# Create Blueprint for auth routes
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user with Firebase Auth"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'full_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        email = data['email']
        password = data['password']
        full_name = data['full_name']
        role = data.get('role', 'customer')  # Default to customer
        
        # Validate role
        valid_roles = ['customer', 'agent', 'admin']
        if role not in valid_roles:
            return jsonify({'error': f'Role must be one of: {", ".join(valid_roles)}'}), 400
        
        # Create user in Firebase Auth
        firebase_auth = get_firebase_auth()
        firebase_user = firebase_auth.create_user(
            email=email,
            password=password,
            display_name=full_name
        )
        
        # Set custom claims for role-based access
        firebase_auth.set_custom_claims(firebase_user['uid'], {'role': role})
        
        # Sync to local storage
        local_user = sync_user_to_local_storage(firebase_user, role)
        
        logger.info(f"✅ User registered successfully: {email}")
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': {
                'uid': firebase_user['uid'],
                'email': firebase_user['email'],
                'display_name': firebase_user['display_name'],
                'role': role
            }
        }), 201
        
    except Exception as e:
        logger.error(f"❌ Registration failed: {e}")
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user (verify token and sync with local storage)"""
    try:
        data = request.get_json()
        
        # Get ID token from request
        id_token = data.get('id_token')
        if not id_token:
            return jsonify({'error': 'ID token is required'}), 400
        
        # Verify token with Firebase
        firebase_auth = get_firebase_auth()
        token_result = firebase_auth.verify_token(id_token)
        
        if not token_result['valid']:
            return jsonify({'error': 'Invalid token', 'details': token_result.get('error')}), 401
        
        # Get user details from Firebase
        firebase_uid = token_result['uid']
        firebase_user = firebase_auth.get_user_by_uid(firebase_uid)
        
        if not firebase_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get or create local user record
        local_user = get_local_user_by_firebase_uid(firebase_uid)
        if not local_user:
            # First time login - sync user to local storage
            local_user = sync_user_to_local_storage(firebase_user, 'customer')
        else:
            # Update last login
            update_local_user_login(firebase_uid)
        
        # Store user info in session
        session['user_uid'] = firebase_uid
        session['user_email'] = firebase_user['email']
        session['user_role'] = local_user.get('role', 'customer')
        
        logger.info(f"✅ User logged in successfully: {firebase_user['email']}")
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'uid': firebase_uid,
                'email': firebase_user['email'],
                'display_name': firebase_user.get('display_name', ''),
                'role': local_user.get('role', 'customer'),
                'email_verified': firebase_user.get('email_verified', False)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Login failed: {e}")
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user (clear session)"""
    try:
        # Clear session
        session.clear()
        
        logger.info("✅ User logged out successfully")
        
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Logout failed: {e}")
        return jsonify({'error': 'Logout failed', 'details': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get current user profile"""
    try:
        # Check if user is logged in
        user_uid = session.get('user_uid')
        if not user_uid:
            return jsonify({'error': 'Not authenticated'}), 401
        
        # Get user from Firebase
        firebase_auth = get_firebase_auth()
        firebase_user = firebase_auth.get_user_by_uid(user_uid)
        
        if not firebase_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get local user data
        local_user = get_local_user_by_firebase_uid(user_uid)
        
        return jsonify({
            'success': True,
            'user': {
                'uid': firebase_user['uid'],
                'email': firebase_user['email'],
                'display_name': firebase_user.get('display_name', ''),
                'email_verified': firebase_user.get('email_verified', False),
                'role': local_user.get('role', 'customer') if local_user else 'customer',
                'created_at': firebase_user.get('created_at'),
                'last_sign_in': firebase_user.get('last_sign_in')
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Get profile failed: {e}")
        return jsonify({'error': 'Failed to get profile', 'details': str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
def update_profile():
    """Update user profile"""
    try:
        # Check if user is logged in
        user_uid = session.get('user_uid')
        if not user_uid:
            return jsonify({'error': 'Not authenticated'}), 401
        
        data = request.get_json()
        
        # Prepare update data for Firebase
        firebase_updates = {}
        if 'display_name' in data:
            firebase_updates['display_name'] = data['display_name']
        if 'email' in data:
            firebase_updates['email'] = data['email']
        
        # Update in Firebase if there are changes
        if firebase_updates:
            firebase_auth = get_firebase_auth()
            firebase_auth.update_user(user_uid, **firebase_updates)
        
        # Update local storage
        local_user = get_local_user_by_firebase_uid(user_uid)
        if local_user:
            import json
            import os
            
            users_file = 'users.json'
            with open(users_file, 'r') as f:
                users = json.load(f)
            
            if 'display_name' in data:
                users[user_uid]['display_name'] = data['display_name']
            if 'email' in data:
                users[user_uid]['email'] = data['email']
            
            with open(users_file, 'w') as f:
                json.dump(users, f, indent=2)
        
        logger.info(f"✅ Profile updated for user: {user_uid}")
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Profile update failed: {e}")
        return jsonify({'error': 'Profile update failed', 'details': str(e)}), 500

@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """Verify Firebase ID token"""
    try:
        data = request.get_json()
        id_token = data.get('id_token')
        
        if not id_token:
            return jsonify({'error': 'ID token is required'}), 400
        
        firebase_auth = get_firebase_auth()
        token_result = firebase_auth.verify_token(id_token)
        
        if token_result['valid']:
            # Get local user data for role information
            local_user = get_local_user_by_firebase_uid(token_result['uid'])
            
            return jsonify({
                'valid': True,
                'user': {
                    'uid': token_result['uid'],
                    'email': token_result.get('email'),
                    'email_verified': token_result.get('email_verified', False),
                    'name': token_result.get('name'),
                    'role': local_user.get('role', 'customer') if local_user else 'customer'
                }
            }), 200
        else:
            return jsonify({
                'valid': False,
                'error': token_result.get('error')
            }), 401
            
    except Exception as e:
        logger.error(f"❌ Token verification failed: {e}")
        return jsonify({'error': 'Token verification failed', 'details': str(e)}), 500

@auth_bp.route('/users', methods=['GET'])
def list_users():
    """List all users (admin only)"""
    try:
        # Check if user is admin
        user_role = session.get('user_role')
        if user_role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Load users from local storage
        import json
        import os
        
        users_file = 'users.json'
        if not os.path.exists(users_file):
            return jsonify({'users': []}), 200
        
        with open(users_file, 'r') as f:
            users = json.load(f)
        
        # Format user list
        user_list = []
        for uid, user_data in users.items():
            user_list.append({
                'uid': uid,
                'email': user_data.get('email'),
                'display_name': user_data.get('display_name'),
                'role': user_data.get('role'),
                'created_at': user_data.get('created_at'),
                'last_login': user_data.get('last_login'),
                'is_active': user_data.get('is_active', True)
            })
        
        return jsonify({
            'success': True,
            'users': user_list
        }), 200
        
    except Exception as e:
        logger.error(f"❌ List users failed: {e}")
        return jsonify({'error': 'Failed to list users', 'details': str(e)}), 500

@auth_bp.route('/users/<user_uid>/role', methods=['PUT'])
def update_user_role(user_uid):
    """Update user role (admin only)"""
    try:
        # Check if user is admin
        user_role = session.get('user_role')
        if user_role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        new_role = data.get('role')
        
        if not new_role:
            return jsonify({'error': 'Role is required'}), 400
        
        valid_roles = ['customer', 'agent', 'admin']
        if new_role not in valid_roles:
            return jsonify({'error': f'Role must be one of: {", ".join(valid_roles)}'}), 400
        
        # Update Firebase custom claims
        firebase_auth = get_firebase_auth()
        firebase_auth.set_custom_claims(user_uid, {'role': new_role})
        
        # Update local storage
        import json
        import os
        
        users_file = 'users.json'
        if os.path.exists(users_file):
            with open(users_file, 'r') as f:
                users = json.load(f)
            
            if user_uid in users:
                users[user_uid]['role'] = new_role
                
                with open(users_file, 'w') as f:
                    json.dump(users, f, indent=2)
        
        logger.info(f"✅ Updated role for user {user_uid} to {new_role}")
        
        return jsonify({
            'success': True,
            'message': f'User role updated to {new_role}'
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Update user role failed: {e}")
        return jsonify({'error': 'Failed to update user role', 'details': str(e)}), 500

# Helper function to check if user is authenticated
def is_authenticated():
    """Check if current user is authenticated"""
    return 'user_uid' in session

# Helper function to get current user
def get_current_user():
    """Get current authenticated user"""
    if not is_authenticated():
        return None
    
    user_uid = session.get('user_uid')
    return get_local_user_by_firebase_uid(user_uid)