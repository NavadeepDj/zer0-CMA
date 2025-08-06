# Prashna - Zer0 Customer Support Chatbot

A Flask-based intelligent customer support chatbot with HTML frontend interface.

## Features

- **Intelligent Conversation Flow**: Prashna understands user intents and provides contextual responses
- **Real-time Chat Interface**: Clean, modern web-based chat interface
- **Ticket Management**: Automatic ticket creation and status tracking
- **Multi-step Workflows**: Guided complaint submission process
- **FAQ System**: Instant answers to common questions
- **Responsive Design**: Works on desktop and mobile devices

## Quick Start

### 1. Install Dependencies

```bash
cd flask-backend
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

### 3. Access the Chatbot

Open your browser and go to: `http://localhost:5000`

## API Endpoints

### Chat API
- **POST** `/api/chat` - Send message to Prashna
- **POST** `/api/complaint` - Create new complaint ticket
- **GET** `/api/status/<ticket_id>` - Get ticket status
- **GET** `/api/health` - Health check

### Example Chat Request
```json
{
  "message": "I need help with my laptop",
  "session_id": "optional-session-id"
}
```

### Example Chat Response
```json
{
  "success": true,
  "response": {
    "message": "I'll help you with your laptop issue...",
    "type": "greeting",
    "buttons": [
      {"text": "New Complaint", "action": "new_complaint"},
      {"text": "Check Status", "action": "status_check"}
    ]
  },
  "session_id": "generated-session-id"
}
```

## Prashna's Capabilities

### Current Features
- ✅ **Intent Recognition**: Understands greetings, complaints, status checks, FAQ requests
- ✅ **Conversational Flow**: Guided multi-step interactions
- ✅ **Ticket Creation**: Automatic ticket generation with unique IDs
- ✅ **Status Tracking**: Real-time ticket status updates
- ✅ **FAQ System**: Instant answers to common questions
- ✅ **Session Management**: Maintains conversation context

### Planned Enhancements (Next Tasks)
- 🔄 **NLP Integration**: Advanced intent recognition with spaCy
- 🔄 **Firebase Integration**: Persistent data storage
- 🔄 **AI Categorization**: Smart ticket categorization
- 🔄 **Agent Assignment**: Intelligent agent matching
- 🔄 **ETA Prediction**: ML-based response time estimation
- 🔄 **Real-time Updates**: WebSocket support for live updates

## Architecture

```
Frontend (HTML/CSS/JS)
         ↓
Flask Backend API
         ↓
In-Memory Storage (Development)
         ↓
[Future: Firebase + AI/ML]
```

## Development

### Project Structure
```
flask-backend/
├── app.py                 # Main Flask application
├── templates/
│   └── chatbot.html      # Chat interface
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

### Adding New Features

1. **New Intent Recognition**: Add patterns to `PrashnaBot.process_message()`
2. **New API Endpoints**: Add routes to `app.py`
3. **Frontend Updates**: Modify `templates/chatbot.html`

### Testing

Test the chatbot by:
1. Starting the Flask app: `python app.py`
2. Opening `http://localhost:5000`
3. Trying different conversation flows:
   - "Hello" → Greeting with options
   - "I have a complaint" → Complaint flow
   - "Check my status" → Status check
   - "FAQ" → Frequently asked questions

## Next Steps

1. **Implement Task 3**: Firebase integration for persistent storage
2. **Implement Task 4**: NLP intent recognition with spaCy
3. **Implement Task 5**: AI-powered ticket categorization
4. **Implement Task 6**: Intelligent agent assignment
5. **Implement Task 7**: ETA prediction model

## Configuration

Currently uses in-memory storage for development. Future versions will include:
- Firebase configuration
- Environment variables for API keys
- ML model configurations
- Agent management settings

## Support

This is the foundation for the Zer0 Customer Support system. The chatbot will become increasingly intelligent as we add AI/ML components in subsequent tasks.