from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
# from flask_mail import Mail, Message
import json
import uuid
from datetime import datetime, timedelta
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import joblib

# Import dashboard routes
try:
    from dashboard_routes import integrate_dashboard_routes
    dashboard_integration_available = True
except ImportError:
    dashboard_integration_available = False
    logging.warning("Dashboard routes not available")

# Import auth routes
try:
    from auth_routes import auth_bp
    auth_integration_available = True
except ImportError:
    auth_integration_available = False
    logging.warning("Auth routes not available")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configure session for authentication
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production

# Integrate dashboard routes
if dashboard_integration_available:
    integrate_dashboard_routes(app)
    logger.info("✅ Dashboard routes integrated")

# Integrate auth routes
if auth_integration_available:
    app.register_blueprint(auth_bp)
    logger.info("✅ Auth routes integrated")

# from integrate_user_dashboard import integrate_user_dashboard_with_app
# integrate_user_dashboard_with_app(app)
# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '99220040115@klu.ac.in'  # Your sender email
app.config['MAIL_PASSWORD'] = 'yogs yflr nddc fibj'  # You need to get the app password for dohaloj488@foboxs.com
app.config['MAIL_DEFAULT_SENDER'] = '99220040115@klu.ac.in'

# Support team email (where tickets will be sent)
SUPPORT_EMAIL = 'navadeepmarella@gmail.com'

# mail = Mail(app)

# Persistent storage using JSON files
import json
import os
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

TICKETS_FILE = 'tickets.json'
SESSIONS_FILE = 'chat_sessions.json'

def load_tickets():
    """Load tickets from JSON file"""
    if os.path.exists(TICKETS_FILE):
        try:
            with open(TICKETS_FILE, 'r') as f:
                return json.load(f)
        except:
            logger.error("Failed to load tickets file")
    return {}

def save_tickets():
    """Save tickets to JSON file"""
    try:
        with open(TICKETS_FILE, 'w') as f:
            json.dump(tickets, f, indent=2)
        logger.info(f"Saved {len(tickets)} tickets to {TICKETS_FILE}")
    except Exception as e:
        logger.error(f"Failed to save tickets: {e}")

def load_chat_sessions():
    """Load chat sessions from JSON file"""
    if os.path.exists(SESSIONS_FILE):
        try:
            with open(SESSIONS_FILE, 'r') as f:
                return json.load(f)
        except:
            logger.error("Failed to load chat sessions file")
    return {}

def save_chat_sessions():
    """Save chat sessions to JSON file"""
    try:
        with open(SESSIONS_FILE, 'w') as f:
            json.dump(chat_sessions, f, indent=2)
        logger.info(f"Saved {len(chat_sessions)} chat sessions to {SESSIONS_FILE}")
    except Exception as e:
        logger.error(f"Failed to save chat sessions: {e}")

# Load existing data on startup
tickets = load_tickets()
chat_sessions = load_chat_sessions()

logger.info(f"Loaded {len(tickets)} existing tickets and {len(chat_sessions)} chat sessions")

# Load ML models for intelligent ticket processing
def load_ml_models():
    """Load the ML models for categorization and priority classification"""
    models = {}
    try:
        # Load customer service categorization model
        with open('models/customer_service_model.pkl', 'rb') as f:
            models['categorization'] = joblib.load(f)
        logger.info("✅ Customer service categorization model loaded")
        
        # Load support severity classifier model
        with open('models/support_severity_classifier.pkl', 'rb') as f:
            models['priority'] = joblib.load(f)
        logger.info("✅ Support severity classifier model loaded")
        
    except Exception as e:
        logger.error(f"❌ Failed to load ML models: {e}")
        models = None
    
    return models

def predict_ticket_category(description, models):
    """Predict ticket category using ML model"""
    if not models or 'categorization' not in models:
        return "General Assistance"  # Fallback
    
    try:
        # Use the categorization model to predict category
        model = models['categorization']
        
        # Assuming the model expects text input
        if hasattr(model, 'predict'):
            prediction = model.predict([description])
            category = prediction[0] if len(prediction) > 0 else "General Assistance"
            
            # Map model output to our categories
            category_mapping = {
                'technical': 'Technical Help & Troubleshooting',
                'billing': 'Billing & Account Questions',
                'warranty': 'Warranty & Repairs',
                'setup': 'Product Setup & Software',
                'returns': 'Returns, Cancellations & Swaps',
                'shipping': 'Shipping & Delivery',
                'general': 'General Assistance'
            }
            
            return category_mapping.get(category.lower(), category)
        
    except Exception as e:
        logger.error(f"Category prediction failed: {e}")
    
    return "General Assistance"  # Fallback

def predict_ticket_priority(description, models):
    """Predict ticket priority using ML model"""
    if not models or 'priority' not in models:
        return "medium"  # Fallback
    
    try:
        # Use the priority model to predict severity
        model = models['priority']
        
        if hasattr(model, 'predict'):
            prediction = model.predict([description])
            priority = prediction[0] if len(prediction) > 0 else "medium"
            
            # Map model output to our priority levels
            priority_mapping = {
                'low': 'low',
                'medium': 'medium', 
                'high': 'high',
                'urgent': 'urgent',
                'critical': 'urgent'  # Map critical to urgent
            }
            
            return priority_mapping.get(priority.lower(), priority.lower())
        
    except Exception as e:
        logger.error(f"Priority prediction failed: {e}")
    
    return "medium"  # Fallback

def get_eta_by_priority(priority):
    """Get estimated response time based on priority"""
    eta_mapping = {
        'urgent': 15,    # 15 minutes for urgent
        'high': 30,      # 30 minutes for high
        'medium': 45,    # 45 minutes for medium
        'low': 120       # 2 hours for low
    }
    return eta_mapping.get(priority, 45)

def assign_agent_by_category(category, priority="medium"):
    """Assign agent based on category and real-time availability"""
    
    # Find the best available agent
    agent, agent_id, eta = find_best_available_agent(category, priority)
    
    if agent:
        return agent['name'] + f" ({agent['title']})", agent_id, eta
    else:
        # Fallback to general support
        return 'Anaya (General Support)', 'anaya_general', 45

# Load ML models on startup
ml_models = load_ml_models()

# Real-time Agent Management System
AGENTS_FILE = 'agents.json'

def load_agents():
    """Load agent data from JSON file"""
    if os.path.exists(AGENTS_FILE):
        try:
            with open(AGENTS_FILE, 'r') as f:
                return json.load(f)
        except:
            logger.error("Failed to load agents file")
    
    # Default agent setup if file doesn't exist
    return {
        "alex_tech": {
            "id": "alex_tech",
            "name": "Alex",
            "title": "Technical Specialist",
            "specialties": ["Technical Help & Troubleshooting", "Product Setup & Software"],
            "status": "available",  # available, busy, offline
            "current_ticket": None,
            "estimated_free_time": None,
            "max_concurrent_tickets": 3,
            "current_tickets": [],
            "avg_resolution_time": 25,  # minutes
            "last_activity": datetime.now().isoformat()
        },
        "sarah_warranty": {
            "id": "sarah_warranty",
            "name": "Sarah",
            "title": "Warranty Expert",
            "specialties": ["Warranty & Repairs"],
            "status": "available",
            "current_ticket": None,
            "estimated_free_time": None,
            "max_concurrent_tickets": 2,
            "current_tickets": [],
            "avg_resolution_time": 35,
            "last_activity": datetime.now().isoformat()
        },
        "mike_billing": {
            "id": "mike_billing",
            "name": "Mike",
            "title": "Billing Specialist",
            "specialties": ["Billing & Account Questions"],
            "status": "available",
            "current_ticket": None,
            "estimated_free_time": None,
            "max_concurrent_tickets": 4,
            "current_tickets": [],
            "avg_resolution_time": 20,
            "last_activity": datetime.now().isoformat()
        },
        "lisa_setup": {
            "id": "lisa_setup",
            "name": "Lisa",
            "title": "Setup Specialist",
            "specialties": ["Product Setup & Software"],
            "status": "busy",
            "current_ticket": "ZER0-2025-001",
            "estimated_free_time": (datetime.now() + timedelta(minutes=15)).isoformat(),
            "max_concurrent_tickets": 3,
            "current_tickets": ["ZER0-2025-001"],
            "avg_resolution_time": 30,
            "last_activity": datetime.now().isoformat()
        },
        "david_returns": {
            "id": "david_returns",
            "name": "David",
            "title": "Returns Manager",
            "specialties": ["Returns, Cancellations & Swaps"],
            "status": "available",
            "current_ticket": None,
            "estimated_free_time": None,
            "max_concurrent_tickets": 3,
            "current_tickets": [],
            "avg_resolution_time": 15,
            "last_activity": datetime.now().isoformat()
        },
        "emma_logistics": {
            "id": "emma_logistics",
            "name": "Emma",
            "title": "Logistics Coordinator",
            "specialties": ["Shipping & Delivery"],
            "status": "offline",
            "current_ticket": None,
            "estimated_free_time": (datetime.now() + timedelta(hours=2)).isoformat(),
            "max_concurrent_tickets": 2,
            "current_tickets": [],
            "avg_resolution_time": 25,
            "last_activity": (datetime.now() - timedelta(hours=1)).isoformat()
        },
        "anaya_general": {
            "id": "anaya_general",
            "name": "Anaya",
            "title": "General Support",
            "specialties": ["General Assistance"],
            "status": "available",
            "current_ticket": None,
            "estimated_free_time": None,
            "max_concurrent_tickets": 5,
            "current_tickets": [],
            "avg_resolution_time": 20,
            "last_activity": datetime.now().isoformat()
        }
    }

def save_agents():
    """Save agent data to JSON file"""
    try:
        with open(AGENTS_FILE, 'w') as f:
            json.dump(agents, f, indent=2)
        logger.info(f"Saved agent data to {AGENTS_FILE}")
    except Exception as e:
        logger.error(f"Failed to save agents: {e}")

def find_best_available_agent(category, priority="medium"):
    """Find the best available agent for a ticket based on category and current availability"""
    
    # Get agents who specialize in this category
    specialist_agents = []
    general_agents = []
    
    for agent_id, agent in agents.items():
        if category in agent['specialties']:
            specialist_agents.append((agent_id, agent))
        elif "General Assistance" in agent['specialties']:
            general_agents.append((agent_id, agent))
    
    # Combine specialists first, then general agents
    candidate_agents = specialist_agents + general_agents
    
    if not candidate_agents:
        return None, None, 60  # Fallback if no agents found
    
    best_agent = None
    best_eta = float('inf')
    
    for agent_id, agent in candidate_agents:
        eta = calculate_agent_eta(agent, priority)
        
        if eta < best_eta:
            best_eta = eta
            best_agent = (agent_id, agent)
    
    if best_agent:
        agent_id, agent = best_agent
        return agent, agent_id, int(best_eta)
    
    return None, None, 60

def calculate_agent_eta(agent, priority="medium"):
    """Calculate when an agent will be available to handle a new ticket"""
    
    # Priority multipliers for queue jumping
    priority_multipliers = {
        "urgent": 0.5,   # Urgent tickets get handled faster
        "high": 0.7,
        "medium": 1.0,
        "low": 1.3
    }
    
    multiplier = priority_multipliers.get(priority, 1.0)
    
    if agent['status'] == 'available':
        # Agent is free now
        return 2 * multiplier  # 2 minutes to pick up
    
    elif agent['status'] == 'busy':
        # Agent is busy, calculate when they'll be free
        if agent['estimated_free_time']:
            try:
                free_time = datetime.fromisoformat(agent['estimated_free_time'])
                now = datetime.now()
                
                if free_time > now:
                    minutes_until_free = (free_time - now).total_seconds() / 60
                    return (minutes_until_free + 5) * multiplier  # +5 min buffer
                else:
                    # Estimated time has passed, agent should be free soon
                    return 5 * multiplier
            except:
                # Fallback to average resolution time
                return agent['avg_resolution_time'] * multiplier
        else:
            # No estimated time, use average
            return agent['avg_resolution_time'] * multiplier
    
    elif agent['status'] == 'offline':
        # Agent is offline, check when they'll be back
        if agent['estimated_free_time']:
            try:
                back_time = datetime.fromisoformat(agent['estimated_free_time'])
                now = datetime.now()
                
                if back_time > now:
                    minutes_until_back = (back_time - now).total_seconds() / 60
                    return (minutes_until_back + 10) * multiplier  # +10 min buffer
                else:
                    # Should be back by now
                    return 15 * multiplier
            except:
                return 120 * multiplier  # 2 hours default
        else:
            return 120 * multiplier  # 2 hours default
    
    return 60 * multiplier  # Default fallback

def assign_ticket_to_agent(ticket_id, agent_id):
    """Assign a ticket to an agent and update their status"""
    if agent_id not in agents:
        return False
    
    agent = agents[agent_id]
    
    # Add ticket to agent's current tickets
    if ticket_id not in agent['current_tickets']:
        agent['current_tickets'].append(ticket_id)
    
    # Update agent status
    if len(agent['current_tickets']) >= agent['max_concurrent_tickets']:
        agent['status'] = 'busy'
    
    # Set current ticket if it's their first
    if not agent['current_ticket']:
        agent['current_ticket'] = ticket_id
    
    # Estimate when they'll be free (based on avg resolution time)
    estimated_completion = datetime.now() + timedelta(minutes=agent['avg_resolution_time'])
    agent['estimated_free_time'] = estimated_completion.isoformat()
    
    # Update last activity
    agent['last_activity'] = datetime.now().isoformat()
    
    # Save changes
    save_agents()
    
    logger.info(f"🎯 Assigned ticket {ticket_id} to {agent['name']} ({agent['title']})")
    
    return True

def get_agent_status_summary():
    """Get a summary of all agent statuses"""
    summary = {
        "available": 0,
        "busy": 0,
        "offline": 0,
        "total_tickets": 0,
        "agents": []
    }
    
    for agent_id, agent in agents.items():
        summary[agent['status']] += 1
        summary['total_tickets'] += len(agent['current_tickets'])
        
        summary['agents'].append({
            "id": agent_id,
            "name": agent['name'],
            "title": agent['title'],
            "status": agent['status'],
            "current_tickets": len(agent['current_tickets']),
            "estimated_free_time": agent['estimated_free_time'],
            "specialties": agent['specialties']
        })
    
    return summary

# Load agents on startup
agents = load_agents()
logger.info(f"Loaded {len(agents)} agents")

class PrashnaBot:
    """Prashna AI Assistant for Zer0 Customer Support"""
    
    def __init__(self):
        self.name = "Prashna"
        self.company = "Zer0"
        self.temp_complaints = {}  # Store temporary complaint data during multi-step flows
        
        # Comprehensive knowledge base
        self.knowledge_base = {
            "company_info": {
                "name": "Zer0",
                "agent_name": "Prashna",
                "description": "Zer0 provides full-spectrum customer care services similar to HP customer support, including technical help, repairs, warranty claims, billing inquiries, product setup guidance, and general assistance.",
                "support_hours": "9 AM–9 PM IST, seven days a week",
                "emergency_support": "Emergency escalations outside these hours are handled on request",
                "support_channels": ["web chat", "phone", "email", "WhatsApp"]
            },
            
            "capabilities": [
                "Checking ticket status",
                "Updating complaint details", 
                "Initiating returns, cancellations, or swaps",
                "Answering FAQs about warranty terms, turnaround times, shipping policies",
                "Seamless transfer to live agents with preserved chat history"
            ],
            
            "response_commitments": {
                "instant_replies": "Common inquiries answered immediately",
                "ticket_issues": "Live human agent call within 1 hour, or ETA provided",
                "email_responses": "Within 4 hours",
                "full_resolution": "Within 24 hours",
                "urgent_escalation": "Live agents may call back within 30 minutes when required"
            },
            
            "support_scope": [
                "Troubleshooting device issues",
                "Warranty repairs and replacements", 
                "Software setup and updates",
                "Billing or account questions",
                "Shipping, returns, or exchange requests"
            ],
            
            "persona": {
                "personality": "Friendly and empathetic digital assistant representing Zer0 Customer Care",
                "tone": "Helpful, respectful tone with follow-up steps when needed",
                "language": "English",
                "goal": "Build lasting relationships by resolving issues and anticipating customer needs"
            },
            
            "company_mission": "Zer0's unwavering dedication to excellence in service delivery. Whether assisting with a simple inquiry or managing complex product challenges, Zer0 Customer Solutions strives to exceed expectations at every opportunity, reinforcing our reputation as a trusted partner in customer satisfaction and support.",
            
            "additional_services": {
                "webinars": "Quarterly webinars and live Q&A sessions with product specialists and service managers",
                "insights": "Product updates, maintenance tips, and upcoming releases",
                "referral_program": "Rewards customers who recommend Zer0 products and services",
                "community": "Building community and trust around our brand"
            }
        }
        
        # Dynamic greeting based on knowledge base
        self.greeting = f"Hi! 👋 Welcome to {self.knowledge_base['company_info']['name']} Customer Support! I'm {self.knowledge_base['company_info']['agent_name']}, your friendly and empathetic digital assistant.\n\nI'm here to provide you with excellent customer care, just like our full-spectrum support services. I can help with technical issues, warranty claims, billing questions, product setup, and much more!\n\nHow can I assist you today? 😊"
    
    def process_message(self, message, session_id):
        """Process incoming message and return appropriate response"""
        message_lower = message.lower().strip()
        
        # Check if we're in a multi-step flow
        if session_id in chat_sessions:
            session_data = chat_sessions[session_id]
            if len(session_data) > 0:
                last_response = session_data[-1].get('bot_response', {})
                if last_response.get('next_step'):
                    return self.handle_multi_step_flow(message, session_id, last_response['next_step'])
        
        # Check for FAQ actions
        if message.startswith('faq_'):
            return self.get_faq_response(message)
        
        # Check for services info action
        if message == 'services_info':
            return self.get_services_info()
        
        # Enhanced intent recognition with knowledge base context
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'start', 'greetings']):
            # Check if this is a JotForm referral (stored in session)
            referral_source = None
            if session_id in chat_sessions and len(chat_sessions[session_id]) > 0:
                referral_source = chat_sessions[session_id][0].get('referral_source')
            return self.handle_greeting(referral_source)
        elif any(word in message_lower for word in ['complaint', 'issue', 'problem', 'help', 'support', 'technical', 'warranty', 'billing', 'setup']):
            return self.handle_new_complaint()
        elif any(word in message_lower for word in ['status', 'check', 'ticket', 'track', 'update']):
            return self.handle_status_check()
        elif any(word in message_lower for word in ['faq', 'question', 'info', 'information', 'about']):
            return self.handle_faq()
        elif any(word in message_lower for word in ['services', 'what do you do', 'company', 'zer0', 'about zer0']):
            return self.get_services_info()
        else:
            return self.handle_general_query(message)
    
    def handle_greeting(self, referral_source=None):
        if referral_source == 'jotform':
            return {
                "message": f"Hi! I see you came from our basic support. I'm {self.knowledge_base['company_info']['agent_name']}, your advanced AI assistant! 🚀\n\nAs part of {self.knowledge_base['company_info']['name']}'s commitment to excellence, I can help with complex issues that need detailed attention:\n\n• Create priority support tickets with expert routing\n• Connect you with specialists in your specific area\n• Provide accurate resolution times based on our SLA\n• Handle urgent escalations (live agents within 30 minutes)\n• Assist with warranty, billing, technical, and setup issues\n\nHow can I assist you today?",
                "type": "jotform_welcome",
                "buttons": [
                    {"text": "Create Priority Ticket", "action": "priority_complaint"},
                    {"text": "Urgent Issue", "action": "urgent_complaint"},
                    {"text": "Technical Problem", "action": "technical_complaint"},
                    {"text": "Check Existing Status", "action": "status_check"}
                ]
            }
        else:
            return {
                "message": self.greeting,
                "type": "greeting",
                "buttons": [
                    {"text": "New Support Request", "action": "new_complaint"},
                    {"text": "Check Ticket Status", "action": "status_check"},
                    {"text": "FAQ & Information", "action": "faq"},
                    {"text": "Our Services", "action": "services_info"}
                ]
            }
    
    
    def handle_new_complaint(self):
        kb = self.knowledge_base
        return {
            "message": f"I'll be delighted to help you with your concern! 😊 As your {kb['persona']['personality']}, I'm here to provide you with excellent support.\n\nWhether it's {', '.join(kb['support_scope'][:3])}, or any other issue, I'll make sure you get the expert help you deserve. Let me gather some details so I can route your request to the right specialist.\n\nWhat's your full name?",
            "type": "collect_info",
            "next_step": "collect_name"
        }
    
    def handle_status_check(self):
        return {
            "message": "I'll help you check your ticket status right away! Please enter your ticket ID (e.g., ZER0-2025-001) or the email address you used when submitting your request:",
            "type": "status_check",
            "next_step": "process_status_query"
        }
    
    def handle_faq(self):
        return {
            "message": "What would you like to know more about?",
            "type": "faq",
            "buttons": [
                {"text": "Response times & resolution", "action": "faq_resolution"},
                {"text": "How to track my request", "action": "faq_tracking"},
                {"text": "What info should I provide?", "action": "faq_info"},
                {"text": "Escalation process", "action": "faq_escalation"},
                {"text": "Contact options", "action": "faq_contact"}
            ]
        }
    
    def get_faq_response(self, faq_type):
        """Get FAQ response based on type using knowledge base"""
        kb = self.knowledge_base
        
        faq_responses = {
            "faq_resolution": f"⏱️ **{kb['company_info']['name']} Customer Care Response Times:**\n\n• **{kb['response_commitments']['instant_replies']}** - That's me, {kb['company_info']['agent_name']}! 😊\n• **{kb['response_commitments']['ticket_issues']}**\n• **Email responses:** {kb['response_commitments']['email_responses']}\n• **Full resolution:** {kb['response_commitments']['full_resolution']}\n• **Emergency escalations:** {kb['response_commitments']['urgent_escalation']}\n\nWe're available {kb['company_info']['support_hours']}, with {kb['company_info']['emergency_support'].lower()}.\n\nOur commitment to excellence means we strive to exceed these expectations whenever possible! 🌟",
            
            "faq_tracking": f"📋 **Tracking Your {kb['company_info']['name']} Support Request:**\n\n1. **Ticket ID:** You'll receive a unique ticket ID (e.g., ZER0-2025-001) when you submit\n2. **Email Updates:** Automatic notifications {kb['response_commitments']['email_responses'].lower()}\n3. **{kb['company_info']['agent_name']} Chat:** Ask me anytime to check your status - I have instant access! 💬\n4. **Multi-Channel Support:** Updates via {', '.join(kb['company_info']['support_channels'])}\n5. **Seamless Transfers:** {kb['capabilities'][4]} - no need to repeat yourself!\n\nYour ticket stages: Registered → Expert Assigned → In Progress → Resolved ✅\n\nI can help you check your status right now if you have a ticket ID! 😊",
            
            "faq_info": f"📝 **Information for {kb['company_info']['name']} Support:**\n\n**Required Information:**\n• Your full name\n• Valid email address\n• Issue category from our support scope:\n  - {chr(10).join(['• ' + scope for scope in kb['support_scope']])}\n• Detailed description of your concern\n\n**Helpful for Faster Resolution:**\n• Device model and serial number\n• Error messages or screenshots\n• Troubleshooting steps you've already tried\n• Purchase date and warranty status\n• Account or order number\n\nAs {kb['company_info']['agent_name']}, I can instantly help with {', '.join(kb['capabilities'][:3])}! My goal is to anticipate your needs and provide excellent service. 😊",
            
            "faq_escalation": f"🚀 **{kb['company_info']['name']} Escalation Process:**\n\n**Automatic Escalation by {kb['company_info']['agent_name']}:**\n• I can identify urgent issues and raise high-priority tickets automatically\n• Emergency situations get immediate live agent attention\n• {kb['capabilities'][4]} - no information lost!\n\n**Manual Escalation:**\n• Simply tell me 'This is urgent' and I'll escalate immediately\n• Reply to any email with 'ESCALATE'\n• Request emergency support - {kb['company_info']['emergency_support'].lower()}\n\n**Our Commitment:**\n• High-priority tickets: {kb['response_commitments']['urgent_escalation']}\n• Available {kb['company_info']['support_hours']}\n• {kb['company_info']['emergency_support']}\n\nRemember, {kb['company_mission'].split('.')[0]}! 🌟",
            
            "faq_contact": f"📞 **{kb['company_info']['name']} Customer Care Contact:**\n\n**📧 Direct Contact Information:**\n• **Email:** navadeepmarella@gmail.com\n• **Phone:** 7075072880\n• **Team:** Zer0 Support Team\n\n**Multi-Channel Support:**\n{chr(10).join([f'• **{channel.title()}:** Professional support available' for channel in kb['company_info']['support_channels']])}\n• **{kb['company_info']['agent_name']} Chatbot:** Available 24/7 (you're chatting with me now!) 😊\n\n**Business Hours:**\n• **{kb['company_info']['support_hours']}**\n• {kb['company_info']['emergency_support']}\n\n**What I Can Help With:**\n{chr(10).join([f'• {capability}' for capability in kb['capabilities']])}\n\n**Our Full Support Scope:**\n• Troubleshooting device issues\n• Warranty repairs and replacements\n• Software setup and updates\n• Billing or account questions\n• Shipping, returns, or exchange requests\n\n**Language:** {kb['persona']['language']} support with a {kb['persona']['tone']} 🌟"
        }
        
        response_text = faq_responses.get(faq_type, f"I don't have specific information about that topic yet, but as your {kb['persona']['personality']}, I'm always here to help! Please choose from the available options or let me know what specific information you need. 😊")
        
        return {
            "message": response_text,
            "type": "faq_response",
            "buttons": [
                {"text": "More FAQ", "action": "faq"},
                {"text": "New Support Request", "action": "new_complaint"},
                {"text": "Check Status", "action": "status_check"},
                {"text": "Our Services", "action": "services_info"}
            ]
        }
    
    def get_services_info(self):
        """Provide information about Zer0's services"""
        kb = self.knowledge_base
        
        services_message = f"🌟 **Welcome to {kb['company_info']['name']} Customer Solutions!**\n\n"
        services_message += f"**Our Mission:** {kb['company_mission']}\n\n"
        services_message += f"**What We Offer:**\n{kb['company_info']['description']}\n\n"
        
        # Add specific support scope
        services_message += f"**Our Support Scope:**\n"
        services_message += f"• Troubleshooting device issues\n"
        services_message += f"• Warranty repairs and replacements\n"
        services_message += f"• Software setup and updates\n"
        services_message += f"• Billing or account questions\n"
        services_message += f"• Shipping, returns, or exchange requests\n\n"
        
        services_message += f"**Support Channels:**\n{chr(10).join([f'• {channel.title()}' for channel in kb['company_info']['support_channels']])}\n\n"
        
        # Add contact information
        services_message += f"**📞 Contact Zer0 Support Team:**\n"
        services_message += f"• **Email:** navadeepmarella@gmail.com\n"
        services_message += f"• **Phone:** 7075072880\n"
        services_message += f"• **Hours:** {kb['company_info']['support_hours']}\n"
        services_message += f"• **Emergency:** {kb['company_info']['emergency_support']}\n\n"
        
        services_message += f"**Additional Services:**\n"
        services_message += f"• {kb['additional_services']['webinars']} providing {kb['additional_services']['insights']}\n"
        services_message += f"• {kb['additional_services']['referral_program']}\n"
        services_message += f"• Focus on {kb['additional_services']['community']}\n\n"
        
        services_message += f"Ready to help you 24/7! 😊"
        
        return {
            "message": services_message,
            "type": "services_info",
            "buttons": [
                {"text": "Get Support Now", "action": "new_complaint"},
                {"text": "FAQ", "action": "faq"},
                {"text": "Check Ticket Status", "action": "status_check"}
            ]
        }
    
    def handle_multi_step_flow(self, message, session_id, step):
        """Handle multi-step conversation flows"""
        if step == "process_status_query":
            # Process status check query
            return self.process_status_query(message)
        elif step == "collect_name":
            # Store name and ask for email
            if session_id not in chat_sessions:
                chat_sessions[session_id] = []
            
            # Store the name
            for session in chat_sessions[session_id]:
                if 'complaint_data' not in session:
                    session['complaint_data'] = {}
            
            # Initialize complaint data if not exists
            if not hasattr(self, 'temp_complaints'):
                self.temp_complaints = {}
            if session_id not in self.temp_complaints:
                self.temp_complaints[session_id] = {}
                
            self.temp_complaints[session_id]['name'] = message.strip()
            
            return {
                "message": f"Thank you, {message.strip()}! It's wonderful to meet you. 😊 Now, what's your email address? I'll use this to send you updates and confirmations about your support request.",
                "type": "collect_info",
                "next_step": "collect_email"
            }
            
        elif step == "collect_email":
            # Store email and ask for category
            if not hasattr(self, 'temp_complaints'):
                self.temp_complaints = {}
            if session_id not in self.temp_complaints:
                self.temp_complaints[session_id] = {}
                
            self.temp_complaints[session_id]['email'] = message.strip()
            
            kb = self.knowledge_base
            return {
                "message": f"Perfect! Now, what type of issue are you experiencing? I'll make sure to connect you with the right specialist from our expert team. We cover all these areas as part of our full-spectrum customer care:",
                "type": "collect_category",
                "buttons": [
                    {"text": "Technical Help & Troubleshooting", "action": "category_technical"},
                    {"text": "Warranty & Repairs", "action": "category_warranty"},
                    {"text": "Billing & Account Questions", "action": "category_billing"},
                    {"text": "Product Setup & Software", "action": "category_setup"},
                    {"text": "Returns, Cancellations & Swaps", "action": "category_returns"},
                    {"text": "General Assistance", "action": "category_general"}
                ],
                "next_step": "collect_category"
            }
            
        elif step == "collect_category":
            # Store category and ask for description
            if not hasattr(self, 'temp_complaints'):
                self.temp_complaints = {}
            if session_id not in self.temp_complaints:
                self.temp_complaints[session_id] = {}
                
            # Map button actions to categories
            category_map = {
                "category_technical": "Technical Help & Troubleshooting",
                "category_warranty": "Warranty & Repairs", 
                "category_billing": "Billing & Account Questions",
                "category_setup": "Product Setup & Software",
                "category_returns": "Returns, Cancellations & Swaps",
                "category_general": "General Assistance"
            }
            
            self.temp_complaints[session_id]['category'] = category_map.get(message, message)
            
            return {
                "message": "Excellent choice! Now, please describe your issue in detail. The more information you provide, the better I can help you and ensure our specialist has everything they need to resolve your concern quickly. 😊\n\nFeel free to include any error messages, steps you've tried, or when the issue started!",
                "type": "collect_description",
                "next_step": "collect_description"
            }
            
        elif step == "collect_description":
            # Store description and create ticket
            if not hasattr(self, 'temp_complaints'):
                self.temp_complaints = {}
            if session_id not in self.temp_complaints:
                self.temp_complaints[session_id] = {}
                
            self.temp_complaints[session_id]['description'] = message.strip()
            
            # Create the ticket with AI-powered categorization and priority
            complaint_data = self.temp_complaints[session_id]
            ticket_id = f"ZER0-2025-{len(tickets) + 1:03d}"
            description = complaint_data.get('description', '')
            
            # Use ML models for intelligent processing
            if ml_models:
                # AI-powered category prediction (overrides user selection if needed)
                ai_category = predict_ticket_category(description, ml_models)
                # AI-powered priority classification
                ai_priority = predict_ticket_priority(description, ml_models)
                # Smart agent assignment based on category and real-time availability
                ai_agent, agent_id, ai_eta = assign_agent_by_category(ai_category, ai_priority)
                
                logger.info(f"🤖 AI Predictions for {ticket_id}: Category={ai_category}, Priority={ai_priority}, Agent={ai_agent}, ETA={ai_eta}min")
            else:
                # Fallback to manual selections
                ai_category = complaint_data.get('category', 'General Assistance')
                ai_priority = "medium"
                ai_agent, agent_id, ai_eta = assign_agent_by_category(ai_category, ai_priority)
            
            ticket = {
                "id": ticket_id,
                "customer_name": complaint_data.get('name'),
                "customer_email": complaint_data.get('email'),
                "category": ai_category,  # AI-predicted category
                "user_selected_category": complaint_data.get('category'),  # Keep user's choice for reference
                "description": description,
                "status": "registered",
                "priority": ai_priority,  # AI-predicted priority
                "created_at": datetime.now().isoformat(),
                "assigned_agent": ai_agent,  # AI-assigned agent
                "assigned_agent_id": agent_id,  # Agent ID for tracking
                "eta_minutes": ai_eta,  # Real-time ETA
                "ai_processed": True if ml_models else False
            }
            
            tickets[ticket_id] = ticket
            save_tickets()  # Save to persistent storage
            
            # Assign ticket to the selected agent
            if agent_id:
                assign_ticket_to_agent(ticket_id, agent_id)
            
            # Send email notifications (same as /api/complaint endpoint)
            try:
                logger.info(f"Attempting to send emails for chatbot ticket {ticket_id}")
                send_admin_notification(ticket)
                logger.info(f"Admin notification sent successfully for chatbot ticket {ticket_id}")
                send_customer_confirmation(ticket)
                logger.info(f"Customer confirmation sent successfully for chatbot ticket {ticket_id}")
                email_status = "✅ Email notifications sent successfully"
            except Exception as e:
                logger.error(f"Email notification failed for chatbot ticket {ticket_id}: {str(e)}")
                email_status = f"⚠️ Ticket created but email notifications failed: {str(e)}"
            
            # Clean up temp data
            del self.temp_complaints[session_id]
            
            kb = self.knowledge_base
            return {
                "message": f"🎉 Wonderful! Your request has been successfully logged with {kb['company_info']['name']} Customer Care! I'm excited to help you get this resolved.\n\n**✅ Your Ticket Details:**\n**Ticket ID:** {ticket_id}\n**Assigned Agent:** {ticket['assigned_agent']}\n**Expected Response:** {kb['response_commitments']['ticket_issues']}\n\n**📧 Email Status:** {email_status}\n\n**📧 What happens next:**\n• You'll receive email confirmation {kb['response_commitments']['email_responses'].lower()}\n• For urgent issues: {kb['response_commitments']['urgent_escalation']}\n• Full resolution: {kb['response_commitments']['full_resolution']}\n\n**💬 Remember:** I'm always here if you need to check your status or have other questions!\n\nIs there anything else I can help you with today? 😊",
                "type": "ticket_created",
                "buttons": [
                    {"text": "Check This Ticket Status", "action": "status_check"},
                    {"text": "New Support Request", "action": "new_complaint"},
                    {"text": "FAQ & Information", "action": "faq"},
                    {"text": "About Our Services", "action": "services_info"}
                ]
            }
        
        return self.handle_general_query(message)

    def handle_general_query(self, message):
        kb = self.knowledge_base
        return {
            "message": f"I understand you're asking about: '{message}'. As your {kb['persona']['personality']}, I want to make sure I give you the most helpful response! 😊\n\nCould you please choose one of these options so I can assist you better? Remember, my goal is to {kb['persona']['goal'].lower()}!",
            "type": "clarification",
            "buttons": [
                {"text": "New Support Request", "action": "new_complaint"},
                {"text": "Check Ticket Status", "action": "status_check"},
                {"text": "FAQ & Information", "action": "faq"},
                {"text": "About Our Services", "action": "services_info"}
            ]
        }
    
    def process_status_query(self, query):
        """Process status check query (ticket ID or email)"""
        query = query.strip()
        
        # Check if it looks like a ticket ID (starts with ZER0-)
        if query.upper().startswith('ZER0-'):
            ticket_id = query.upper()
            if ticket_id in tickets:
                ticket = tickets[ticket_id]
                return {
                    "message": f"✅ **Ticket Status Found!**\n\n**Ticket ID:** {ticket['id']}\n**Status:** {ticket['status'].title()}\n**Customer:** {ticket['customer_name']}\n**Category:** {ticket['category']}\n**Priority:** {ticket['priority'].title()}\n**Assigned Agent:** {ticket['assigned_agent']}\n**Created:** {ticket['created_at']}\n\n**Description:**\n{ticket['description']}\n\n**Next Steps:**\n• Our agent will contact you within 1 hour\n• Check your email for updates\n• I'm here if you need anything else! 😊",
                    "type": "status_result",
                    "buttons": [
                        {"text": "New Support Request", "action": "new_complaint"},
                        {"text": "FAQ & Information", "action": "faq"},
                        {"text": "About Our Services", "action": "services_info"}
                    ]
                }
            else:
                return {
                    "message": f"❌ **Ticket Not Found**\n\nI couldn't find a ticket with ID: {ticket_id}\n\n**Please check:**\n• Make sure the ticket ID is correct\n• Ticket IDs start with 'ZER0-' (e.g., ZER0-2025-001)\n• The ticket was created through our system\n\n**Need help?** I can:\n• Help you create a new support request\n• Answer questions about our services\n• Connect you with a live agent\n\nWhat would you like to do? 😊",
                    "type": "status_not_found",
                    "buttons": [
                        {"text": "New Support Request", "action": "new_complaint"},
                        {"text": "Try Another Ticket ID", "action": "status_check"},
                        {"text": "FAQ & Information", "action": "faq"}
                    ]
                }
        
        # Check if it looks like an email
        elif '@' in query:
            # Find tickets by email
            matching_tickets = []
            for ticket_id, ticket in tickets.items():
                if ticket['customer_email'].lower() == query.lower():
                    matching_tickets.append(ticket)
            
            if matching_tickets:
                if len(matching_tickets) == 1:
                    ticket = matching_tickets[0]
                    return {
                        "message": f"✅ **Ticket Found by Email!**\n\n**Ticket ID:** {ticket['id']}\n**Status:** {ticket['status'].title()}\n**Category:** {ticket['category']}\n**Priority:** {ticket['priority'].title()}\n**Assigned Agent:** {ticket['assigned_agent']}\n**Created:** {ticket['created_at']}\n\n**Description:**\n{ticket['description']}\n\n**Next Steps:**\n• Our agent will contact you within 1 hour\n• Check your email for updates\n• I'm here if you need anything else! 😊",
                        "type": "status_result",
                        "buttons": [
                            {"text": "New Support Request", "action": "new_complaint"},
                            {"text": "FAQ & Information", "action": "faq"},
                            {"text": "About Our Services", "action": "services_info"}
                        ]
                    }
                else:
                    # Multiple tickets found
                    ticket_list = "\n".join([f"• {t['id']} - {t['category']} ({t['created_at']})" for t in matching_tickets])
                    return {
                        "message": f"✅ **Multiple Tickets Found!**\n\nI found {len(matching_tickets)} tickets for {query}:\n\n{ticket_list}\n\nPlease enter a specific ticket ID to get detailed status information. 😊",
                        "type": "multiple_tickets",
                        "buttons": [
                            {"text": "Check Specific Ticket", "action": "status_check"},
                            {"text": "New Support Request", "action": "new_complaint"},
                            {"text": "FAQ & Information", "action": "faq"}
                        ]
                    }
            else:
                return {
                    "message": f"❌ **No Tickets Found**\n\nI couldn't find any tickets for email: {query}\n\n**Please check:**\n• Make sure the email address is correct\n• Use the same email you used when creating the ticket\n• The ticket was created through our system\n\n**Need help?** I can help you create a new support request! 😊",
                    "type": "email_not_found",
                    "buttons": [
                        {"text": "New Support Request", "action": "new_complaint"},
                        {"text": "Try Different Email", "action": "status_check"},
                        {"text": "FAQ & Information", "action": "faq"}
                    ]
                }
        
        else:
            return {
                "message": f"🤔 **Invalid Format**\n\nI didn't recognize '{query}' as a ticket ID or email address.\n\n**Please enter:**\n• **Ticket ID:** ZER0-2025-001 (starts with ZER0-)\n• **Email Address:** your@email.com (contains @)\n\n**Example:** ZER0-2025-001 or john@example.com\n\nTry again! 😊",
                "type": "invalid_format",
                "buttons": [
                    {"text": "Try Again", "action": "status_check"},
                    {"text": "New Support Request", "action": "new_complaint"},
                    {"text": "FAQ & Information", "action": "faq"}
                ]
            }

# Initialize Prashna bot
prashna = PrashnaBot()

@app.route('/')
def index():
    """Serve the chatbot interface"""
    # Check if user came from JotForm
    referral_source = request.args.get('ref', '')
    issue_type = request.args.get('issue', '')
    
    return render_template('chatbot.html', 
                         referral_source=referral_source,
                         issue_type=issue_type)

@app.route('/auth')
def auth_page():
    """Serve the authentication page"""
    return render_template('auth_dashboard.html')

@app.route('/chatbot')
def chatbot_page():
    """Serve the chatbot interface (alternative route)"""
    # Get query parameters for referral tracking
    referral = request.args.get('referral', '')
    escalated = request.args.get('escalated', 'false')
    ticket_id = request.args.get('ticket_id', '')
    action = request.args.get('action', '')
    
    return render_template('chatbot.html', 
                         referral_source=referral,
                         escalated=escalated,
                         ticket_id=ticket_id,
                         action=action)

@app.route('/form')
def simple_form():
    """Serve the simple form interface"""
    return render_template('simple_form.html')

@app.route('/admin')
def admin_dashboard():
    """Serve the admin dashboard"""
    return render_template('admin_dashboard.html')

@app.route('/agents')
def agent_dashboard():
    """Serve the agent status dashboard"""
    return render_template('agent_dashboard.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages from the frontend"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        session_id = data.get('session_id', str(uuid.uuid4()))
        referral_source = data.get('referral_source', '')
        
        # Log the incoming message
        logger.info(f"Received message: {message} from session: {session_id}")
        
        # Store chat history
        if session_id not in chat_sessions:
            chat_sessions[session_id] = []
            # Store referral source in first session entry
            if referral_source:
                chat_sessions[session_id].append({
                    "referral_source": referral_source,
                    "timestamp": datetime.now().isoformat()
                })
        
        # Process message with Prashna
        response = prashna.process_message(message, session_id)
        
        chat_sessions[session_id].append({
            "timestamp": datetime.now().isoformat(),
            "user_message": message,
            "bot_response": response
        })
        save_chat_sessions()  # Save to persistent storage
        
        return jsonify({
            "success": True,
            "response": response,
            "session_id": session_id
        })
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Sorry, I encountered an error. Please try again."
        }), 500

def send_admin_notification(ticket):
    """Send email notification to admin/support team"""
    try:
        subject = f"🎫 New Support Ticket - {ticket['id']}"
        
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center;">
                <h2>🎫 New Support Ticket</h2>
                <h3>Ticket ID: {ticket['id']}</h3>
            </div>
            
            <div style="padding: 20px; background: #f8f9fa;">
                <h3>Customer Details:</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background: white;">
                        <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Name:</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{ticket['customer_name']}</td>
                    </tr>
                    <tr style="background: #f8f9fa;">
                        <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Email:</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{ticket['customer_email']}</td>
                    </tr>
                    <tr style="background: white;">
                        <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Category:</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{ticket['category']}</td>
                    </tr>
                    <tr style="background: #f8f9fa;">
                        <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Priority:</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{ticket['priority']}</td>
                    </tr>
                    <tr style="background: white;">
                        <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Submitted:</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{ticket['created_at']}</td>
                    </tr>
                </table>
                
                <h3>Issue Description:</h3>
                <div style="background: white; padding: 15px; border-radius: 5px; border-left: 4px solid #667eea;">
                    {ticket['description']}
                </div>
                
                <div style="margin-top: 20px; padding: 15px; background: #fff3cd; border-radius: 5px;">
                    <strong>⏰ SLA Reminder:</strong> Please respond within 1 hour as per Zer0 Customer Care standards.
                </div>
            </div>
        </div>
        """
        
        # Send email using simple SMTP (more reliable than Flask-Mail)
        send_email(SUPPORT_EMAIL, subject, html_body)
        logger.info(f"Admin notification sent for ticket {ticket['id']}")
        
    except Exception as e:
        logger.error(f"Failed to send admin notification: {str(e)}")

def send_customer_confirmation(ticket):
    """Send confirmation email to customer"""
    try:
        subject = f"✅ Your Support Request Received - Ticket {ticket['id']}"
        
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center;">
                <h2>✅ Support Request Received</h2>
                <p>Thank you for contacting Zer0 Customer Support!</p>
            </div>
            
            <div style="padding: 20px;">
                <p>Dear <strong>{ticket['customer_name']}</strong>,</p>
                
                <p>We have received your support request and our team is already working on it.</p>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h3>Your Request Details:</h3>
                    <ul style="list-style: none; padding: 0;">
                        <li><strong>🎫 Ticket ID:</strong> {ticket['id']}</li>
                        <li><strong>📂 Category:</strong> {ticket['category']}</li>
                        <li><strong>📅 Submitted:</strong> {ticket['created_at']}</li>
                        <li><strong>👤 Assigned Agent:</strong> {ticket['assigned_agent']}</li>
                        <li><strong>⏱️ Expected Response:</strong> Within 1 hour</li>
                    </ul>
                </div>
                
                <div style="background: #d4edda; padding: 15px; border-radius: 5px; border-left: 4px solid #28a745;">
                    <strong>📞 What happens next?</strong><br>
                    • Our support team will contact you within 1 hour<br>
                    • For urgent issues, we may call back within 30 minutes<br>
                    • You'll receive email updates as we progress<br>
                    • Use your Ticket ID for any follow-up inquiries
                </div>
                
                <div style="margin-top: 30px; text-align: center;">
                    <p><strong>Need immediate help?</strong></p>
                    <p>📞 Phone: Available 9 AM–9 PM IST, Seven Days a Week<br>
                    📧 Email: support@zer0company.com<br>
                    💬 WhatsApp: Direct messaging support</p>
                </div>
                
                <div style="margin-top: 30px; padding: 20px; background: #f8f9fa; text-align: center; border-radius: 10px;">
                    <p><strong>Best regards,</strong><br>
                    Prashna - Zer0 Customer Support Team<br>
                    <em>"Your trusted partner in customer satisfaction"</em></p>
                </div>
            </div>
        </div>
        """
        
        send_email(ticket['customer_email'], subject, html_body)
        logger.info(f"Customer confirmation sent for ticket {ticket['id']}")
        
    except Exception as e:
        logger.error(f"Failed to send customer confirmation: {str(e)}")

def send_ticket_closure_notification(ticket):
    """Send closure notification email to customer"""
    try:
        subject = f"✅ Your Support Request Resolved - Ticket {ticket.get('ticket_number', ticket.get('id'))}"
        
        # Get customer email from different possible fields
        customer_email = ticket.get('customer_email') or ticket.get('user_email') or ticket.get('email')
        customer_name = ticket.get('customer_name') or ticket.get('name') or 'Valued Customer'
        ticket_id = ticket.get('ticket_number') or ticket.get('id')
        
        if not customer_email:
            logger.error(f"No customer email found for ticket {ticket_id}")
            return
        
        # Get resolution details
        resolution_date = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        agent_name = ticket.get('assigned_agent', 'Our Support Team')
        category = ticket.get('category', 'General Support')
        created_date = ticket.get('created_at', 'Recently')
        
        # Get agent notes if available
        agent_notes = ""
        if 'agent_notes' in ticket and ticket['agent_notes']:
            latest_note = ticket['agent_notes'][-1]  # Get the latest note
            agent_notes = f"""
                <div style="background: #e8f5e8; padding: 15px; border-radius: 5px; border-left: 4px solid #28a745; margin: 20px 0;">
                    <strong>📝 Resolution Notes from {agent_name}:</strong><br>
                    <em>"{latest_note.get('note', 'Issue has been resolved successfully.')}"</em>
                </div>
            """
        
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 20px; text-align: center;">
                <h2>🎉 Your Support Request is Resolved!</h2>
                <p>We're happy to let you know your issue has been successfully resolved.</p>
            </div>
            
            <div style="padding: 20px;">
                <p>Dear <strong>{customer_name}</strong>,</p>
                
                <p>Great news! Your support request has been successfully resolved by our team. We hope the solution provided meets your expectations.</p>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h3>📋 Ticket Summary:</h3>
                    <ul style="list-style: none; padding: 0;">
                        <li><strong>🎫 Ticket ID:</strong> {ticket_id}</li>
                        <li><strong>📂 Category:</strong> {category}</li>
                        <li><strong>📅 Submitted:</strong> {created_date}</li>
                        <li><strong>✅ Resolved:</strong> {resolution_date}</li>
                        <li><strong>👤 Handled by:</strong> {agent_name}</li>
                        <li><strong>🔒 Status:</strong> <span style="color: #28a745; font-weight: bold;">CLOSED</span></li>
                    </ul>
                </div>
                
                {agent_notes}
                
                <div style="background: #d1ecf1; padding: 15px; border-radius: 5px; border-left: 4px solid #17a2b8; margin: 20px 0;">
                    <strong>💡 What's Next?</strong><br>
                    • Your ticket is now closed and marked as resolved<br>
                    • If you need further assistance, feel free to create a new support request<br>
                    • We'd love to hear your feedback about our service<br>
                    • Keep your ticket ID for future reference if needed
                </div>
                
                <div style="background: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107; margin: 20px 0;">
                    <strong>📞 Still Need Help?</strong><br>
                    If this resolution doesn't fully address your concern, please don't hesitate to contact us again:<br>
                    • Create a new support request through our website<br>
                    • Reference this ticket ID: <strong>{ticket_id}</strong><br>
                    • Our team is available 9 AM–9 PM IST, seven days a week
                </div>
                
                <div style="margin-top: 30px; text-align: center;">
                    <p><strong>📧 Contact Information:</strong></p>
                    <p>📞 Phone: 7075072880<br>
                    📧 Email: navadeepmarella@gmail.com<br>
                    🌐 Website: Zer0 Customer Support Portal</p>
                </div>
                
                <div style="margin-top: 30px; padding: 20px; background: #f8f9fa; text-align: center; border-radius: 10px;">
                    <p><strong>Thank you for choosing Zer0!</strong><br>
                    We appreciate your patience and trust in our support team.<br>
                    <em>"Your satisfaction is our success"</em></p>
                    
                    <p style="margin-top: 15px; font-size: 14px; color: #666;">
                        Best regards,<br>
                        <strong>{agent_name}</strong><br>
                        Zer0 Customer Support Team
                    </p>
                </div>
            </div>
        </div>
        """
        
        send_email(customer_email, subject, html_body)
        logger.info(f"✅ Closure notification sent to {customer_email} for ticket {ticket_id}")
        
    except Exception as e:
        logger.error(f"❌ Failed to send closure notification: {str(e)}")

def send_email(to_email, subject, html_body):
    """Send email using SMTP"""
    try:
        # Email configuration using app config
        smtp_server = app.config['MAIL_SERVER']
        smtp_port = app.config['MAIL_PORT']
        sender_email = app.config['MAIL_USERNAME']  # dohaloj488@foboxs.com
        sender_password = app.config['MAIL_PASSWORD']  # You need to set this!
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = to_email
        
        # Add HTML content
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            
        logger.info(f"Email sent successfully to {to_email}")
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        raise

@app.route('/api/complaint', methods=['POST'])
def create_complaint():
    """Create a new complaint ticket with email notifications"""
    try:
        data = request.get_json()
        
        # Generate ticket ID
        ticket_id = f"ZER0-2025-{len(tickets) + 1:03d}"
        
        # Create ticket with AI-powered processing
        description = data.get('description', '')
        user_category = data.get('category', 'General Assistance')
        
        # Use ML models for intelligent processing
        if ml_models:
            # AI-powered category prediction
            ai_category = predict_ticket_category(description, ml_models)
            # AI-powered priority classification
            ai_priority = predict_ticket_priority(description, ml_models)
            # Smart agent assignment based on category and real-time availability
            ai_agent, agent_id, ai_eta = assign_agent_by_category(ai_category, ai_priority)
            
            logger.info(f"🤖 AI Predictions for {ticket_id}: Category={ai_category}, Priority={ai_priority}, Agent={ai_agent}, ETA={ai_eta}min")
        else:
            # Fallback to manual selections
            ai_category = user_category
            ai_priority = "medium"
            ai_agent, agent_id, ai_eta = assign_agent_by_category(ai_category, ai_priority)
        
        ticket = {
            "id": ticket_id,
            "customer_name": data.get('name'),
            "customer_email": data.get('email'),
            "category": ai_category,  # AI-predicted category
            "user_selected_category": user_category,  # Keep user's choice for reference
            "description": description,
            "status": "registered",
            "priority": ai_priority,  # AI-predicted priority
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "assigned_agent": ai_agent,  # AI-assigned agent
            "assigned_agent_id": agent_id,  # Agent ID for tracking
            "eta_minutes": ai_eta,  # Real-time ETA
            "ai_processed": True if ml_models else False
        }
        
        tickets[ticket_id] = ticket
        save_tickets()  # Save to persistent storage
        
        # Assign ticket to the selected agent
        if agent_id:
            assign_ticket_to_agent(ticket_id, agent_id)
        
        # Send email notifications
        try:
            logger.info(f"Attempting to send emails for ticket {ticket_id}")
            send_admin_notification(ticket)
            logger.info(f"Admin notification sent successfully for {ticket_id}")
            send_customer_confirmation(ticket)
            logger.info(f"Customer confirmation sent successfully for {ticket_id}")
            email_status = "✅ Email notifications sent successfully"
        except Exception as e:
            logger.error(f"Email notification failed for {ticket_id}: {str(e)}")
            email_status = f"⚠️ Ticket created but email notifications failed: {str(e)}"
        
        logger.info(f"Created ticket: {ticket_id}")
        
        return jsonify({
            "success": True,
            "message": f"Your request has been logged with Zer0 Customer Care! ✅\n\n{email_status}",
            "ticket_id": ticket_id,
            "assigned_agent": ticket["assigned_agent"],
            "eta_minutes": ticket["eta_minutes"]
        })
        
    except Exception as e:
        logger.error(f"Error creating complaint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to create complaint. Please try again."
        }), 500

@app.route('/api/status/<ticket_id>', methods=['GET'])
def get_ticket_status(ticket_id):
    """Get ticket status by ID"""
    try:
        if ticket_id in tickets:
            ticket = tickets[ticket_id]
            return jsonify({
                "success": True,
                "ticket": ticket
            })
        else:
            return jsonify({
                "success": False,
                "error": "Ticket not found"
            }), 404
            
    except Exception as e:
        logger.error(f"Error getting ticket status: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to retrieve ticket status"
        }), 500

@app.route('/api/tickets/<ticket_id>/status', methods=['PUT'])
def update_ticket_status(ticket_id):
    """Update ticket status (for agents/admins)"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        notes = data.get('notes', '')
        updated_by = data.get('updated_by', 'system')
        
        if not new_status:
            return jsonify({
                'success': False,
                'error': 'Status is required'
            }), 400
        
        # Valid status values
        valid_statuses = ['registered', 'assigned', 'in-progress', 'resolved', 'closed']
        if new_status not in valid_statuses:
            return jsonify({
                'success': False,
                'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }), 400
        
        # Find ticket by ID or ticket_number
        ticket_found = False
        ticket_key = None
        
        for key, ticket_data in tickets.items():
            if key == ticket_id or ticket_data.get('ticket_number') == ticket_id:
                ticket_found = True
                ticket_key = key
                break
        
        if not ticket_found:
            return jsonify({
                'success': False,
                'error': 'Ticket not found'
            }), 404
        
        # Update ticket status
        tickets[ticket_key]['status'] = new_status
        tickets[ticket_key]['updated_at'] = datetime.now().isoformat()
        tickets[ticket_key]['updated_by'] = updated_by
        
        if notes:
            if 'agent_notes' not in tickets[ticket_key]:
                tickets[ticket_key]['agent_notes'] = []
            tickets[ticket_key]['agent_notes'].append({
                'note': notes,
                'timestamp': datetime.now().isoformat(),
                'updated_by': updated_by
            })
        
        # Add status history
        if 'status_history' not in tickets[ticket_key]:
            tickets[ticket_key]['status_history'] = []
        
        tickets[ticket_key]['status_history'].append({
            'status': new_status,
            'timestamp': datetime.now().isoformat(),
            'updated_by': updated_by,
            'notes': notes
        })
        
        # Save tickets
        save_tickets()
        
        # Send closure notification email if ticket is closed
        if new_status == 'closed':
            try:
                logger.info(f"📧 Sending closure notification for ticket {ticket_id}")
                send_ticket_closure_notification(tickets[ticket_key])
                logger.info(f"✅ Closure notification sent successfully for ticket {ticket_id}")
            except Exception as e:
                logger.error(f"❌ Failed to send closure notification for ticket {ticket_id}: {str(e)}")
        
        logger.info(f"✅ Ticket {ticket_id} status updated to {new_status} by {updated_by}")
        
        return jsonify({
            'success': True,
            'message': f'Ticket status updated to {new_status}',
            'ticket': tickets[ticket_key]
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error updating ticket status: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update ticket status'
        }), 500

@app.route('/api/webhook/complaint', methods=['POST'])
def webhook_complaint():
    """Webhook endpoint for JotForm integration (backward compatibility)"""
    try:
        data = request.get_json()
        logger.info(f"Received webhook data: {data}")
        
        # Process the webhook data and return response
        return jsonify({
            "success": True,
            "message": "Webhook received successfully"
        })
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Webhook processing failed"
        }), 500

@app.route('/api/tickets', methods=['GET'])
def get_all_tickets():
    """Get all tickets for admin view"""
    try:
        # Convert tickets dictionary to array for frontend
        tickets_array = []
        for ticket_id, ticket_data in tickets.items():
            # Ensure ticket has an ID field
            if 'ticket_number' not in ticket_data and 'id' not in ticket_data:
                ticket_data['id'] = ticket_id
            tickets_array.append(ticket_data)
        
        # Sort by creation date (newest first)
        tickets_array.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return jsonify({
            "success": True,
            "total_tickets": len(tickets_array),
            "tickets": tickets_array
        })
    except Exception as e:
        logger.error(f"Error retrieving tickets: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to retrieve tickets"
        }), 500

@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Get all agent statuses"""
    try:
        summary = get_agent_status_summary()
        return jsonify({
            "success": True,
            "summary": summary
        })
    except Exception as e:
        logger.error(f"Error getting agents: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to retrieve agent information"
        }), 500

@app.route('/api/agents/<agent_id>/status', methods=['PUT'])
def update_agent_status(agent_id):
    """Update agent status (for simulation/testing)"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if agent_id not in agents:
            return jsonify({
                "success": False,
                "error": "Agent not found"
            }), 404
        
        if new_status not in ['available', 'busy', 'offline']:
            return jsonify({
                "success": False,
                "error": "Invalid status"
            }), 400
        
        agents[agent_id]['status'] = new_status
        agents[agent_id]['last_activity'] = datetime.now().isoformat()
        
        # Update estimated free time based on status
        if new_status == 'available':
            agents[agent_id]['estimated_free_time'] = None
            agents[agent_id]['current_ticket'] = None
        elif new_status == 'offline':
            # Set to come back in 2 hours
            agents[agent_id]['estimated_free_time'] = (datetime.now() + timedelta(hours=2)).isoformat()
        
        save_agents()
        
        return jsonify({
            "success": True,
            "message": f"Agent {agents[agent_id]['name']} status updated to {new_status}"
        })
        
    except Exception as e:
        logger.error(f"Error updating agent status: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to update agent status"
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    agent_summary = get_agent_status_summary()
    return jsonify({
        "status": "healthy",
        "service": "Prashna Zer0 Customer Support",
        "total_tickets": len(tickets),
        "agents_available": agent_summary['available'],
        "agents_busy": agent_summary['busy'],
        "agents_offline": agent_summary['offline'],
        "timestamp": datetime.now().isoformat()
    })
@app.route('/escalate')
def escalate_from_jotform():
    """Handle escalation from JotForm chatbot"""
    # Get escalation context
    issue_type = request.args.get('issue', 'general')
    priority = request.args.get('priority', 'medium')
    user_message = request.args.get('message', '')
    
    # Store escalation context in session
    session['escalation_context'] = {
        'source': 'jotform',
        'issue_type': issue_type,
        'priority': priority,
        'user_message': user_message,
        'escalated': True,
        'timestamp': datetime.now().isoformat()
    }
    
    # Log escalation
    logger.info(f"📈 JotForm escalation: {issue_type} - {priority}")
    
    # Redirect to your existing chatbot with escalation parameters
    return redirect(f'/?ref=jotform&escalated=true&issue={issue_type}&priority={priority}')

@app.route('/api/escalation-status')
def escalation_status():
    """Check if current session is escalated"""
    escalation_context = session.get('escalation_context', {})
    
    return jsonify({
        'escalated': escalation_context.get('escalated', False),
        'source': escalation_context.get('source', ''),
        'issue_type': escalation_context.get('issue_type', ''),
        'priority': escalation_context.get('priority', 'medium'),
        'timestamp': escalation_context.get('timestamp', '')
    })

@app.route('/api/escalated-chat', methods=['POST'])
def escalated_chat():
    """Process chat messages for escalated users with enhanced features"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        # Check if user is escalated
        escalation_context = session.get('escalation_context', {})
        is_escalated = escalation_context.get('escalated', False)
        
        # Process message with escalation context
        if is_escalated:
            # Add escalation context to the message processing
            issue_type = escalation_context.get('issue_type', 'general')
            priority = escalation_context.get('priority', 'medium')
            
            # Enhance the message with escalation context
            enhanced_message = f"[ESCALATED FROM JOTFORM - {issue_type.upper()} - {priority.upper()}] {message}"
            
            # Use your existing chatbot logic
            bot_response = prashna.process_message(enhanced_message, session_id)
            
            # Enhance response for escalated users
            if isinstance(bot_response, dict):
                # Add escalation-specific options
                if 'buttons' not in bot_response:
                    bot_response['buttons'] = []
                
                # Add priority options for escalated users
                escalation_buttons = [
                    {"text": "🚨 Urgent Agent Connection", "action": "urgent_agent"},
                    {"text": "📋 Create Priority Ticket", "action": "priority_ticket"},
                    {"text": "📞 Request Callback", "action": "request_callback"}
                ]
                
                # Add buttons if not already present
                existing_actions = [btn.get('action', '') for btn in bot_response.get('buttons', [])]
                for btn in escalation_buttons:
                    if btn['action'] not in existing_actions:
                        bot_response['buttons'].append(btn)
                
                # Add escalation indicator
                bot_response['escalated'] = True
                bot_response['escalation_source'] = 'jotform'
                bot_response['priority'] = priority
        else:
            # Regular message processing using existing logic
            bot_response = prashna.process_message(message, session_id)
        
        return jsonify({
            'success': True,
            'response': bot_response,
            'escalated': is_escalated,
            'escalation_context': escalation_context if is_escalated else None
        })
        
    except Exception as e:
        logger.error(f"❌ Escalated chat processing failed: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to process message',
            'escalated': False
        }), 500

@app.route('/api/create-priority-ticket', methods=['POST'])
def create_priority_ticket():
    """Create a priority ticket for escalated users"""
    try:
        if not session.get('escalation_context', {}).get('escalated', False):
            return jsonify({'error': 'Not an escalated session'}), 403
        
        data = request.get_json()
        title = data.get('title', 'Escalated Support Request')
        description = data.get('description', 'User escalated from JotForm chatbot')
        
        escalation_context = session.get('escalation_context', {})
        
        # Generate ticket ID
        import uuid
        ticket_id = f"PRIORITY-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Create ticket data
        ticket_data = {
            'ticket_number': ticket_id,
            'title': title,
            'description': description,
            'priority': 'high',  # Escalated tickets get high priority
            'status': 'registered',
            'category': escalation_context.get('issue_type', 'general'),
            'source': 'escalated_jotform',
            'escalation_context': escalation_context,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Save to existing tickets system
        tickets[ticket_id] = ticket_data
        save_tickets()
        
        # Try to assign to agent using existing logic
        try:
            agent, agent_id, eta = find_best_available_agent(ticket_data['category'], 'high')
            if agent and agent_id:
                assign_ticket_to_agent(ticket_id, agent_id)
                ticket_data['assigned_agent'] = agent['name']
                ticket_data['eta_minutes'] = eta
        except:
            pass  # Continue even if agent assignment fails
        
        logger.info(f"✅ Priority ticket created from escalation: {ticket_id}")
        
        return jsonify({
            'success': True,
            'message': 'Priority ticket created successfully',
            'ticket': {
                'id': ticket_id,
                'title': title,
                'priority': 'high',
                'status': 'registered',
                'created': ticket_data['created_at'],
                'agent': ticket_data.get('assigned_agent', 'Being assigned...'),
                'eta': ticket_data.get('eta_minutes', 30)
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to create priority ticket: {e}")
        return jsonify({'error': 'Failed to create ticket', 'details': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='172.28.0.217', port=5000)