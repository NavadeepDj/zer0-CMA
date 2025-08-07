# Firebase Authentication Setup Guide

## Overview

This guide shows how to integrate Firebase Authentication with the existing Zer0 Support System while keeping all current data storage (JSON files) and ML models intact.

## What Firebase Auth Provides

- **Secure user authentication** with email/password
- **Token-based session management** 
- **Role-based access control** with custom claims
- **Password reset and email verification**
- **Integration with existing JSON data storage**

## Setup Steps

### 1. Firebase Project Setup

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Create a new project or select existing project
3. Enable Authentication:
   - Go to "Authentication" in the left sidebar
   - Click "Get started"
   - Go to "Sign-in method" tab
   - Enable "Email/Password" provider
   - Save changes

### 2. Get Firebase Configuration

1. In Firebase Console, go to Project Settings (gear icon)
2. In "General" tab, scroll down to "Your apps"
3. Click "Add app" → Web app (</>) 
4. Register your app with a name (e.g., "Zer0 Support")
5. Copy the Firebase configuration object

### 3. Service Account Setup

1. In Firebase Console, go to Project Settings → "Service accounts" tab
2. Click "Generate new private key"
3. Save the JSON file as `firebase-service-account.json` in `flask-backend/`

### 4. Environment Configuration

Create or update `.env` file in `flask-backend/`:

```bash
# Firebase Configuration
FIREBASE_SERVICE_ACCOUNT_PATH=firebase-service-account.json

# Flask Configuration  
FLASK_SECRET_KEY=your-secret-key-for-sessions

# Existing configurations...
MAIL_SERVER=smtp.gmail.com
# ... other existing settings
```

### 5. Update Firebase Config in HTML

Update `templates/auth_test.html` with your Firebase config:

```javascript
const firebaseConfig = {
    apiKey: "your-api-key",
    authDomain: "your-project.firebaseapp.com", 
    projectId: "your-project-id",
    storageBucket: "your-project.appspot.com",
    messagingSenderId: "123456789",
    appId: "your-app-id"
};
```

### 6. Install Dependencies

```bash
pip install firebase-admin
```

### 7. Integrate with Existing Flask App

Add these lines to your `app.py`:

```python
# Add at the top with other imports
from integrate_firebase_auth import integrate_firebase_auth_with_app

# Add after creating the Flask app
integrate_firebase_auth_with_app(app)
```

## How It Works

### Data Storage Strategy

- **Firebase Auth**: Handles user authentication, passwords, tokens
- **Local JSON Files**: Stores all application data (tickets, agents, chat sessions)
- **User Sync**: Firebase users are synced to `users.json` for role management

### Authentication Flow

1. **Registration**: User registers → Firebase Auth + local `users.json` entry
2. **Login**: User logs in → Firebase validates → session created → role loaded from local storage
3. **API Calls**: Session-based authentication for existing endpoints
4. **Role Management**: Roles stored locally, custom claims in Firebase

### File Structure

```
flask-backend/
├── firebase_auth.py              # Firebase Auth wrapper
├── auth_routes.py                # Authentication endpoints
├── integrate_firebase_auth.py    # Integration helper
├── templates/auth_test.html      # Test interface
├── users.json                    # User data with roles (created automatically)
├── tickets.json                  # Existing ticket data (unchanged)
├── agents.json                   # Existing agent data (unchanged)
├── chat_sessions.json           # Existing chat data (unchanged)
└── firebase-service-account.json # Firebase credentials
```

## API Endpoints

Once integrated, these endpoints are available:

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user  
- `POST /api/auth/logout` - Logout user
- `POST /api/auth/verify-token` - Verify Firebase token

### User Management
- `GET /api/auth/profile` - Get current user profile
- `PUT /api/auth/profile` - Update user profile
- `GET /api/auth/users` - List all users (admin only)
- `PUT /api/auth/users/<uid>/role` - Update user role (admin only)

### Session Helpers
- `is_authenticated()` - Check if user is logged in
- `get_current_user()` - Get current user data

## Testing

### 1. Test Firebase Auth Integration

```bash
python integrate_firebase_auth.py
```

### 2. Test with Web Interface

1. Start Flask app: `python app.py`
2. Go to `http://localhost:5000/auth_test.html`
3. Test registration and login

### 3. Default Admin User

- **Email**: admin@zer0.com
- **Password**: admin123
- **Role**: admin

## Integration with Existing Features

### Chatbot Integration

The chatbot can now check user authentication:

```python
from auth_routes import is_authenticated, get_current_user

@app.route('/api/chat', methods=['POST'])
def chat():
    if is_authenticated():
        user = get_current_user()
        # Use user data for personalized responses
    # ... existing chatbot logic
```

### Ticket Creation

Tickets can now be associated with authenticated users:

```python
@app.route('/api/tickets', methods=['POST'])
def create_ticket():
    if is_authenticated():
        user = get_current_user()
        # Associate ticket with user
        ticket_data['user_uid'] = user['firebase_uid']
    # ... existing ticket creation logic
```

### Agent Dashboard

Agents can now have secure access:

```python
@app.route('/agent_dashboard')
def agent_dashboard():
    if not is_authenticated():
        return redirect('/auth_test.html')
    
    user = get_current_user()
    if user['role'] not in ['agent', 'admin']:
        return "Access denied", 403
    
    # ... existing dashboard logic
```

## Security Features

- **Secure password handling** by Firebase
- **JWT token validation** for API calls
- **Role-based access control** with custom claims
- **Session management** with Flask sessions
- **CORS configuration** for web clients

## Benefits

✅ **Secure Authentication**: Industry-standard Firebase Auth
✅ **Preserves Existing Data**: All JSON files and ML models unchanged  
✅ **Role-Based Access**: Customer, Agent, Admin roles
✅ **Easy Integration**: Minimal changes to existing code
✅ **Scalable**: Can handle growing user base
✅ **Password Security**: Firebase handles password hashing/validation

## Troubleshooting

### Common Issues

1. **"No auth provider found"**
   - Enable Email/Password in Firebase Console
   - Check Firebase project configuration

2. **"Invalid service account"**
   - Verify `firebase-service-account.json` is correct
   - Check file permissions

3. **"CORS errors"**
   - Add your domain to Firebase Auth authorized domains
   - Check CORS configuration in Flask

4. **"Session not working"**
   - Set `FLASK_SECRET_KEY` in environment
   - Check session configuration

### Testing Without Firebase

If Firebase isn't configured yet, the existing app continues to work normally. Authentication features will be disabled but all other functionality remains intact.

## Next Steps

1. Set up Firebase project and get credentials
2. Update configuration files
3. Test authentication with the provided interface
4. Gradually integrate auth checks into existing endpoints
5. Add user management features to admin dashboard

The authentication system is designed to enhance the existing application without breaking any current functionality.