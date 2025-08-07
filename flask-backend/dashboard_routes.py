"""
Dashboard Routes for User Interface
Provides endpoints for user dashboard functionality
"""

from flask import Blueprint, request, jsonify, render_template, session
import logging
import json
import os
from datetime import datetime
from auth_routes import is_authenticated, get_current_user

logger = logging.getLogger(__name__)

# Create Blueprint for dashboard routes
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def user_dashboard():
    """Render user dashboard"""
    return render_template('user_dashboard.html')

@dashboard_bp.route('/api/dashboard/tickets', methods=['GET'])
def get_user_tickets():
    """Get tickets for current user"""
    try:
        if not is_authenticated():
            return jsonify({'error': 'Authentication required'}), 401
        
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Load tickets from JSON file
        tickets_file = 'tickets.json'
        user_tickets = []
        
        if os.path.exists(tickets_file):
            with open(tickets_file, 'r') as f:
                all_tickets = json.load(f)
            
            # Filter tickets for current user
            user_uid = current_user.get('firebase_uid')
            user_email = current_user.get('email')
            
            for ticket_id, ticket_data in all_tickets.items():
                # Match by user UID or email
                if (ticket_data.get('user_uid') == user_uid or 
                    ticket_data.get('user_email') == user_email or
                    ticket_data.get('email') == user_email):
                    
                    user_tickets.append({
                        'id': ticket_data.get('ticket_number', ticket_id),
                        'title': ticket_data.get('title', 'Support Request'),
                        'status': ticket_data.get('status', 'registered'),
                        'priority': ticket_data.get('priority', 'medium'),
                        'category': ticket_data.get('category', 'general'),
                        'created': ticket_data.get('created_at', ''),
                        'updated': ticket_data.get('updated_at', ''),
                        'agent': ticket_data.get('assigned_agent', ''),
                        'eta': ticket_data.get('eta_minutes', ''),
                        'description': ticket_data.get('description', '')
                    })
        
        # Sort by creation date (newest first)
        user_tickets.sort(key=lambda x: x.get('created', ''), reverse=True)
        
        return jsonify({
            'success': True,
            'tickets': user_tickets,
            'total': len(user_tickets)
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to get user tickets: {e}")
        return jsonify({'error': 'Failed to load tickets', 'details': str(e)}), 500

@dashboard_bp.route('/api/tickets/<ticket_id>/status', methods=['GET'])
def get_ticket_status(ticket_id):
    """Get status of a specific ticket"""
    try:
        # Load tickets from JSON file
        tickets_file = 'tickets.json'
        
        if not os.path.exists(tickets_file):
            return jsonify({'error': 'Ticket not found'}), 404
        
        with open(tickets_file, 'r') as f:
            all_tickets = json.load(f)
        
        # Find ticket by ID or ticket number
        ticket_data = None
        for tid, data in all_tickets.items():
            if (tid == ticket_id or 
                data.get('ticket_number') == ticket_id or
                data.get('id') == ticket_id):
                ticket_data = data
                break
        
        if not ticket_data:
            return jsonify({'error': 'Ticket not found'}), 404
        
        # Format ticket information
        ticket_info = {
            'id': ticket_data.get('ticket_number', ticket_id),
            'title': ticket_data.get('title', 'Support Request'),
            'status': ticket_data.get('status', 'registered'),
            'priority': ticket_data.get('priority', 'medium'),
            'category': ticket_data.get('category', 'general'),
            'created': ticket_data.get('created_at', ''),
            'updated': ticket_data.get('updated_at', ''),
            'agent': ticket_data.get('assigned_agent', ''),
            'eta': ticket_data.get('eta_minutes', ''),
            'description': ticket_data.get('description', ''),
            'resolution_notes': ticket_data.get('resolution_notes', '')
        }
        
        return jsonify(ticket_info), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to get ticket status: {e}")
        return jsonify({'error': 'Failed to get ticket status', 'details': str(e)}), 500

@dashboard_bp.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics for current user"""
    try:
        if not is_authenticated():
            return jsonify({'error': 'Authentication required'}), 401
        
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Load tickets and calculate stats
        tickets_file = 'tickets.json'
        stats = {
            'total_tickets': 0,
            'open_tickets': 0,
            'resolved_tickets': 0,
            'urgent_tickets': 0,
            'avg_resolution_time': 0
        }
        
        if os.path.exists(tickets_file):
            with open(tickets_file, 'r') as f:
                all_tickets = json.load(f)
            
            user_uid = current_user.get('firebase_uid')
            user_email = current_user.get('email')
            user_tickets = []
            
            for ticket_id, ticket_data in all_tickets.items():
                if (ticket_data.get('user_uid') == user_uid or 
                    ticket_data.get('user_email') == user_email or
                    ticket_data.get('email') == user_email):
                    user_tickets.append(ticket_data)
            
            # Calculate statistics
            stats['total_tickets'] = len(user_tickets)
            stats['open_tickets'] = len([t for t in user_tickets if t.get('status') not in ['resolved', 'closed']])
            stats['resolved_tickets'] = len([t for t in user_tickets if t.get('status') in ['resolved', 'closed']])
            stats['urgent_tickets'] = len([t for t in user_tickets if t.get('priority') == 'urgent'])
            
            # Calculate average resolution time for resolved tickets
            resolved_tickets = [t for t in user_tickets if t.get('status') in ['resolved', 'closed']]
            if resolved_tickets:
                total_time = sum([t.get('resolution_time', 0) for t in resolved_tickets])
                stats['avg_resolution_time'] = total_time / len(resolved_tickets)
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to get dashboard stats: {e}")
        return jsonify({'error': 'Failed to load stats', 'details': str(e)}), 500

@dashboard_bp.route('/api/dashboard/create-ticket', methods=['POST'])
def create_ticket_from_dashboard():
    """Create a new ticket from dashboard"""
    try:
        if not is_authenticated():
            return jsonify({'error': 'Authentication required'}), 401
        
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description', 'category']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Generate ticket ID
        import uuid
        ticket_id = f"ZER0-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Create ticket data
        ticket_data = {
            'ticket_number': ticket_id,
            'user_uid': current_user.get('firebase_uid'),
            'user_email': current_user.get('email'),
            'title': data['title'],
            'description': data['description'],
            'category': data.get('category', 'general'),
            'priority': data.get('priority', 'medium'),
            'status': 'registered',
            'source': 'dashboard',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Load existing tickets
        tickets_file = 'tickets.json'
        all_tickets = {}
        
        if os.path.exists(tickets_file):
            with open(tickets_file, 'r') as f:
                all_tickets = json.load(f)
        
        # Add new ticket
        all_tickets[ticket_id] = ticket_data
        
        # Save tickets
        with open(tickets_file, 'w') as f:
            json.dump(all_tickets, f, indent=2)
        
        logger.info(f"✅ Created ticket from dashboard: {ticket_id}")
        
        return jsonify({
            'success': True,
            'message': 'Ticket created successfully',
            'ticket': {
                'id': ticket_id,
                'title': ticket_data['title'],
                'status': ticket_data['status'],
                'created': ticket_data['created_at']
            }
        }), 201
        
    except Exception as e:
        logger.error(f"❌ Failed to create ticket: {e}")
        return jsonify({'error': 'Failed to create ticket', 'details': str(e)}), 500

@dashboard_bp.route('/api/dashboard/escalate', methods=['POST'])
def escalate_to_advanced():
    """Handle escalation from JotForm to advanced support"""
    try:
        data = request.get_json()
        
        # Log escalation event
        escalation_data = {
            'timestamp': datetime.now().isoformat(),
            'source': data.get('source', 'jotform'),
            'reason': data.get('reason', 'user_request'),
            'user_session': session.get('user_uid', 'anonymous'),
            'context': data.get('context', {})
        }
        
        # Save escalation log
        escalations_file = 'escalations.json'
        escalations = []
        
        if os.path.exists(escalations_file):
            with open(escalations_file, 'r') as f:
                escalations = json.load(f)
        
        escalations.append(escalation_data)
        
        # Keep only last 1000 escalations
        if len(escalations) > 1000:
            escalations = escalations[-1000:]
        
        with open(escalations_file, 'w') as f:
            json.dump(escalations, f, indent=2)
        
        logger.info(f"✅ Escalation logged: {escalation_data['source']} -> advanced")
        
        return jsonify({
            'success': True,
            'message': 'Escalated to advanced support',
            'redirect_url': '/chatbot?referral=jotform&escalated=true'
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to handle escalation: {e}")
        return jsonify({'error': 'Failed to escalate', 'details': str(e)}), 500

@dashboard_bp.route('/api/dashboard/feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback"""
    try:
        if not is_authenticated():
            return jsonify({'error': 'Authentication required'}), 401
        
        current_user = get_current_user()
        data = request.get_json()
        
        # Create feedback entry
        feedback_data = {
            'timestamp': datetime.now().isoformat(),
            'user_uid': current_user.get('firebase_uid'),
            'user_email': current_user.get('email'),
            'rating': data.get('rating'),
            'comment': data.get('comment', ''),
            'category': data.get('category', 'general'),
            'ticket_id': data.get('ticket_id', ''),
            'source': data.get('source', 'dashboard')
        }
        
        # Save feedback
        feedback_file = 'feedback.json'
        feedback_list = []
        
        if os.path.exists(feedback_file):
            with open(feedback_file, 'r') as f:
                feedback_list = json.load(f)
        
        feedback_list.append(feedback_data)
        
        with open(feedback_file, 'w') as f:
            json.dump(feedback_list, f, indent=2)
        
        logger.info(f"✅ Feedback submitted by {current_user.get('email')}")
        
        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to submit feedback: {e}")
        return jsonify({'error': 'Failed to submit feedback', 'details': str(e)}), 500

@dashboard_bp.route('/api/dashboard/profile', methods=['GET', 'PUT'])
def manage_user_profile():
    """Get or update user profile"""
    try:
        if not is_authenticated():
            return jsonify({'error': 'Authentication required'}), 401
        
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        if request.method == 'GET':
            # Return current user profile
            profile_data = {
                'display_name': current_user.get('display_name', ''),
                'email': current_user.get('email', ''),
                'phone': current_user.get('phone', ''),
                'timezone': current_user.get('timezone', 'UTC'),
                'language': current_user.get('language', 'en'),
                'notification_preferences': current_user.get('notification_preferences', ['email', 'push'])
            }
            
            return jsonify({
                'success': True,
                'profile': profile_data
            }), 200
        
        elif request.method == 'PUT':
            # Update user profile
            data = request.get_json()
            
            # Load users file
            users_file = 'users.json'
            users = {}
            
            if os.path.exists(users_file):
                with open(users_file, 'r') as f:
                    users = json.load(f)
            
            user_uid = current_user.get('firebase_uid')
            if user_uid not in users:
                users[user_uid] = current_user.copy()
            
            # Update profile fields
            if 'fullName' in data:
                users[user_uid]['display_name'] = data['fullName']
            if 'phone' in data:
                users[user_uid]['phone'] = data['phone']
            if 'timezone' in data:
                users[user_uid]['timezone'] = data['timezone']
            if 'language' in data:
                users[user_uid]['language'] = data['language']
            if 'notifications' in data:
                users[user_uid]['notification_preferences'] = data['notifications']
            
            users[user_uid]['updated_at'] = datetime.now().isoformat()
            
            # Save updated users
            with open(users_file, 'w') as f:
                json.dump(users, f, indent=2)
            
            logger.info(f"✅ Profile updated for {current_user.get('email')}")
            
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully'
            }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to manage profile: {e}")
        return jsonify({'error': 'Failed to manage profile', 'details': str(e)}), 500

@dashboard_bp.route('/api/dashboard/notifications', methods=['GET'])
def get_user_notifications():
    """Get user notifications"""
    try:
        if not is_authenticated():
            return jsonify({'error': 'Authentication required'}), 401
        
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Load notifications from file
        notifications_file = 'notifications.json'
        all_notifications = []
        
        if os.path.exists(notifications_file):
            with open(notifications_file, 'r') as f:
                all_notifications = json.load(f)
        
        # Filter notifications for current user
        user_uid = current_user.get('firebase_uid')
        user_email = current_user.get('email')
        
        user_notifications = []
        for notification in all_notifications:
            if (notification.get('user_uid') == user_uid or 
                notification.get('user_email') == user_email):
                user_notifications.append(notification)
        
        # Sort by timestamp (newest first)
        user_notifications.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Limit to last 50 notifications
        user_notifications = user_notifications[:50]
        
        return jsonify({
            'success': True,
            'notifications': user_notifications,
            'unread_count': len([n for n in user_notifications if not n.get('read', False)])
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to get notifications: {e}")
        return jsonify({'error': 'Failed to load notifications', 'details': str(e)}), 500

# Helper function to integrate dashboard routes with Flask app
def integrate_dashboard_routes(app):
    """Integrate dashboard routes with Flask app"""
    try:
        app.register_blueprint(dashboard_bp)
        logger.info("✅ Dashboard routes registered")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to register dashboard routes: {e}")
        return False