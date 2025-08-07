"""
Enhanced Chatbot Routes with JotForm Integration
Handles escalation from JotForm and provides advanced AI support
"""

from flask import Blueprint, request, jsonify, render_template, session
import logging
import json
import os
from datetime import datetime
from auth_routes import is_authenticated, get_current_user

logger = logging.getLogger(__name__)

# Create Blueprint for enhanced chatbot
chatbot_bp = Blueprint('enhanced_chatbot', __name__)

@chatbot_bp.route('/chatbot')
def enhanced_chatbot():
    """Render enhanced chatbot with escalation support"""
    # Get escalation context from URL parameters
    referral = request.args.get('referral', '')
    escalated = request.args.get('escalated', 'false') == 'true'
    reason = request.args.get('reason', '')
    
    # Pass context to template
    context = {
        'referral': referral,
        'escalated': escalated,
        'reason': reason,
        'is_authenticated': is_authenticated(),
        'current_user': get_current_user() if is_authenticated() else None
    }
    
    return render_template('enhanced_chatbot.html', **context)

@chatbot_bp.route('/api/chatbot/escalation-context', methods=['GET'])
def get_escalation_context():
    """Get escalation context for chatbot initialization"""
    try:
        referral = request.args.get('referral', '')
        escalated = request.args.get('escalated', 'false') == 'true'
        reason = request.args.get('reason', '')
        
        context = {
            'referral': referral,
            'escalated': escalated,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
        
        # Add user context if authenticated
        if is_authenticated():
            current_user = get_current_user()
            context['user'] = {
                'email': current_user.get('email'),
                'name': current_user.get('display_name', ''),
                'role': current_user.get('role', 'customer')
            }
        
        # Add escalation-specific welcome message
        if escalated and referral == 'jotform':
            context['welcome_message'] = {
                'type': 'escalation',
                'message': "👋 Hi! I see you've been escalated from our basic support. I'm Prashna, your advanced AI assistant with access to specialized agents and comprehensive support tools. How can I help you with your issue?",
                'priority': 'high'
            }
        
        return jsonify({
            'success': True,
            'context': context
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to get escalation context: {e}")
        return jsonify({'error': 'Failed to get context', 'details': str(e)}), 500

@chatbot_bp.route('/api/chatbot/message', methods=['POST'])
def process_chatbot_message():
    """Process chatbot message with escalation awareness"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')
        context = data.get('context', {})
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Import existing chatbot logic
        from app import PrashnaBot, chat_sessions, save_chat_sessions
        
        # Initialize chatbot
        bot = PrashnaBot()
        
        # Add escalation context to session if not exists
        if session_id not in chat_sessions:
            chat_sessions[session_id] = []
            
            # Add escalation context as first message if escalated
            if context.get('escalated'):
                escalation_context = {
                    'timestamp': datetime.now().isoformat(),
                    'user_message': f"[ESCALATED FROM {context.get('referral', 'unknown').upper()}]",
                    'bot_response': {
                        'message': "I understand you've been escalated from basic support. I have access to advanced features and can connect you directly with specialized agents. Let me help you resolve your issue.",
                        'type': 'escalation_acknowledgment',
                        'escalated': True,
                        'referral_source': context.get('referral', 'unknown')
                    }
                }
                chat_sessions[session_id].append(escalation_context)
        
        # Process message with bot
        bot_response = bot.process_message(message, session_id)
        
        # Enhance response for escalated users
        if context.get('escalated') and isinstance(bot_response, dict):
            # Add escalation-specific options
            if 'buttons' not in bot_response:
                bot_response['buttons'] = []
            
            # Add priority escalation button for escalated users
            escalation_buttons = [
                {"text": "🚨 Urgent Agent Connection", "action": "urgent_agent"},
                {"text": "📋 Create Priority Ticket", "action": "priority_ticket"},
                {"text": "📞 Request Callback", "action": "request_callback"}
            ]
            
            # Add escalation buttons if not already present
            existing_actions = [btn.get('action') for btn in bot_response['buttons']]
            for btn in escalation_buttons:
                if btn['action'] not in existing_actions:
                    bot_response['buttons'].append(btn)
        
        # Store conversation
        conversation_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_message': message,
            'bot_response': bot_response,
            'escalation_context': context if context.get('escalated') else None,
            'user_info': get_current_user() if is_authenticated() else None
        }
        
        chat_sessions[session_id].append(conversation_entry)
        save_chat_sessions()
        
        # Log escalated conversations
        if context.get('escalated'):
            log_escalated_conversation(session_id, message, bot_response, context)
        
        return jsonify({
            'success': True,
            'response': bot_response,
            'session_id': session_id,
            'escalated': context.get('escalated', False)
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Chatbot message processing failed: {e}")
        return jsonify({'error': 'Failed to process message', 'details': str(e)}), 500

@chatbot_bp.route('/api/chatbot/urgent-agent', methods=['POST'])
def request_urgent_agent():
    """Handle urgent agent connection request"""
    try:
        data = request.get_json()
        session_id = data.get('session_id', 'default')
        issue_description = data.get('issue_description', '')
        
        # Create urgent ticket
        import uuid
        ticket_id = f"URGENT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        ticket_data = {
            'ticket_number': ticket_id,
            'title': 'URGENT: Escalated from Advanced Support',
            'description': issue_description or 'User requested urgent agent connection from escalated chat',
            'priority': 'urgent',
            'status': 'registered',
            'category': 'escalation',
            'source': 'escalated_chat',
            'session_id': session_id,
            'escalation_reason': 'urgent_agent_request',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Add user info if authenticated
        if is_authenticated():
            current_user = get_current_user()
            ticket_data.update({
                'user_uid': current_user.get('firebase_uid'),
                'user_email': current_user.get('email'),
                'user_name': current_user.get('display_name', '')
            })
        
        # Save ticket
        tickets_file = 'tickets.json'
        all_tickets = {}
        
        if os.path.exists(tickets_file):
            with open(tickets_file, 'r') as f:
                all_tickets = json.load(f)
        
        all_tickets[ticket_id] = ticket_data
        
        with open(tickets_file, 'w') as f:
            json.dump(all_tickets, f, indent=2)
        
        # Try to assign to available agent immediately
        from app import find_best_available_agent, assign_ticket_to_agent, agents
        
        agent, agent_id, eta = find_best_available_agent('escalation', 'urgent')
        
        if agent and agent_id:
            assign_ticket_to_agent(ticket_id, agent_id)
            agent_info = f"{agent['name']} ({agent['title']})"
            estimated_response = f"{eta} minutes"
        else:
            agent_info = "Next available agent"
            estimated_response = "15 minutes (urgent priority)"
        
        logger.info(f"✅ Urgent agent request created: {ticket_id}")
        
        return jsonify({
            'success': True,
            'message': 'Urgent agent connection requested',
            'ticket_id': ticket_id,
            'agent': agent_info,
            'estimated_response': estimated_response,
            'instructions': 'An agent will contact you within 15 minutes. Please keep this chat window open or check your email for updates.'
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to request urgent agent: {e}")
        return jsonify({'error': 'Failed to request agent', 'details': str(e)}), 500

@chatbot_bp.route('/api/chatbot/priority-ticket', methods=['POST'])
def create_priority_ticket():
    """Create priority ticket from escalated chat"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description', 'category']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Generate priority ticket ID
        import uuid
        ticket_id = f"PRIORITY-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        ticket_data = {
            'ticket_number': ticket_id,
            'title': data['title'],
            'description': data['description'],
            'category': data['category'],
            'priority': 'high',  # Escalated tickets get high priority
            'status': 'registered',
            'source': 'escalated_chat',
            'session_id': data.get('session_id', 'default'),
            'escalation_reason': 'priority_ticket_request',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Add user info if authenticated
        if is_authenticated():
            current_user = get_current_user()
            ticket_data.update({
                'user_uid': current_user.get('firebase_uid'),
                'user_email': current_user.get('email'),
                'user_name': current_user.get('display_name', '')
            })
        
        # Use ML models for intelligent categorization
        from app import ml_models, predict_ticket_category, predict_ticket_priority
        
        if ml_models:
            predicted_category = predict_ticket_category(data['description'], ml_models)
            predicted_priority = predict_ticket_priority(data['description'], ml_models)
            
            # Override with ML predictions but keep high priority for escalated
            ticket_data['ml_category'] = predicted_category
            ticket_data['ml_priority'] = predicted_priority
            ticket_data['priority'] = 'high'  # Keep high for escalated tickets
        
        # Save ticket
        tickets_file = 'tickets.json'
        all_tickets = {}
        
        if os.path.exists(tickets_file):
            with open(tickets_file, 'r') as f:
                all_tickets = json.load(f)
        
        all_tickets[ticket_id] = ticket_data
        
        with open(tickets_file, 'w') as f:
            json.dump(all_tickets, f, indent=2)
        
        logger.info(f"✅ Priority ticket created from escalation: {ticket_id}")
        
        return jsonify({
            'success': True,
            'message': 'Priority ticket created successfully',
            'ticket': {
                'id': ticket_id,
                'title': ticket_data['title'],
                'priority': ticket_data['priority'],
                'status': ticket_data['status'],
                'created': ticket_data['created_at']
            }
        }), 201
        
    except Exception as e:
        logger.error(f"❌ Failed to create priority ticket: {e}")
        return jsonify({'error': 'Failed to create ticket', 'details': str(e)}), 500

def log_escalated_conversation(session_id, user_message, bot_response, context):
    """Log escalated conversations for analysis"""
    try:
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            'user_message': user_message,
            'bot_response': bot_response,
            'escalation_context': context,
            'user_info': get_current_user() if is_authenticated() else None
        }
        
        # Save to escalated conversations log
        log_file = 'escalated_conversations.json'
        logs = []
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        
        logs.append(log_entry)
        
        # Keep only last 10000 entries
        if len(logs) > 10000:
            logs = logs[-10000:]
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
        
    except Exception as e:
        logger.error(f"❌ Failed to log escalated conversation: {e}")

# Helper function to integrate enhanced chatbot routes
def integrate_enhanced_chatbot_routes(app):
    """Integrate enhanced chatbot routes with Flask app"""
    try:
        app.register_blueprint(chatbot_bp)
        logger.info("✅ Enhanced chatbot routes registered")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to register enhanced chatbot routes: {e}")
        return False