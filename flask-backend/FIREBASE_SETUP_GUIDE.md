# Firebase Integration Setup Guide

This guide will help you set up Firebase integration for the Complaint Management System.

## Prerequisites

1. Python environment with Flask
2. Firebase project (create one at https://console.firebase.google.com)
3. Firebase Admin SDK credentials

## Step 1: Install Dependencies

```bash
pip install firebase-admin
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

## Step 2: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Click "Create a project" or select existing project
3. Enable Firestore Database:
   - Go to "Firestore Database" in the left sidebar
   - Click "Create database"
   - Choose "Start in test mode" for development
   - Select a location for your database

## Step 3: Generate Service Account Credentials

1. In Firebase Console, go to Project Settings (gear icon)
2. Click on "Service accounts" tab
3. Click "Generate new private key"
4. Save the JSON file as `firebase-service-account.json` in the `flask-backend` directory

## Step 4: Configure Environment

### Option A: Using Service Account File
1. Place your `firebase-service-account.json` file in the `flask-backend` directory
2. Create a `.env` file (copy from `.env.example`)
3. Set: `FIREBASE_SERVICE_ACCOUNT_PATH=firebase-service-account.json`

### Option B: Using Environment Variables
Set these environment variables:
```bash
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project-id.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=123456789012345678901
```

### Option C: Using JSON String
Set the entire service account as a JSON string:
```bash
FIREBASE_SERVICE_ACCOUNT_JSON='{"type":"service_account","project_id":"your-project-id",...}'
```

## Step 5: Initialize Firebase

Run the initialization script:
```bash
python init_firebase.py
```

This will:
- Test Firebase connection
- Create necessary collections
- Set up default admin user and agents
- Verify the setup

## Step 6: Test the Integration

Run the comprehensive tests:
```bash
python test_firebase_integration.py
```

Or run the offline tests first:
```bash
python test_firebase_connection.py
```

## Step 7: Update Flask Application

The Firebase integration is now ready. The Flask app will automatically use Firebase for:
- User management
- Ticket storage and retrieval
- Agent assignment and tracking
- Real-time updates

## Firestore Collections Structure

The system creates these collections:

### users
```json
{
  "email": "user@example.com",
  "full_name": "User Name",
  "role": "customer|agent|admin",
  "is_active": true,
  "notification_preferences": {
    "email": true,
    "sms": false,
    "push": true
  },
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### tickets
```json
{
  "ticket_number": "ZER0-20250107-ABC123",
  "user_id": "user_document_id",
  "title": "Issue title",
  "description": "Detailed description",
  "category": "technical|billing|warranty|setup|returns|shipping|general",
  "priority": "urgent|high|medium|low",
  "status": "registered|assigned|in_progress|resolved|closed",
  "assigned_agent_id": "agent_document_id",
  "eta_minutes": 30,
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "resolved_at": "timestamp"
}
```

### agents
```json
{
  "name": "Agent Name",
  "email": "agent@example.com",
  "title": "Support Specialist",
  "skills": ["technical", "billing"],
  "status": "available|busy|offline",
  "max_concurrent_tickets": 3,
  "current_tickets": ["ticket_id1", "ticket_id2"],
  "avg_resolution_time": 30,
  "total_tickets_resolved": 150,
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

## Security Rules (Optional)

For production, set up Firestore security rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can read/write their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Users can read/write their own tickets
    match /tickets/{ticketId} {
      allow read, write: if request.auth != null && 
        (resource.data.user_id == request.auth.uid || 
         get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role in ['agent', 'admin']);
    }
    
    // Only agents and admins can access agent data
    match /agents/{agentId} {
      allow read, write: if request.auth != null && 
        get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role in ['agent', 'admin'];
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **"No module named 'firebase_admin'"**
   - Install: `pip install firebase-admin`

2. **"Failed to initialize Firebase"**
   - Check service account credentials
   - Verify project ID is correct
   - Ensure Firestore is enabled

3. **"Permission denied"**
   - Check Firestore security rules
   - Verify service account has proper permissions

4. **"Connection timeout"**
   - Check internet connection
   - Verify Firebase project is active

### Testing Without Firebase

If you need to test the models without Firebase connection, you can use the mock version:
```bash
python test_firebase_connection.py
```

This runs offline tests that don't require Firebase connection.

## Next Steps

After successful setup:
1. Integrate with existing Flask routes
2. Update the chatbot to use Firebase models
3. Implement real-time agent dashboard
4. Set up monitoring and logging
5. Configure backup and recovery

## Support

If you encounter issues:
1. Check the logs for detailed error messages
2. Verify all configuration steps
3. Test with a simple Firebase operation first
4. Consult Firebase documentation for specific errors