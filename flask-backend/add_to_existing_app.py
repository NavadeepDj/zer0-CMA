"""
Simple Addition to Existing Flask App
Add these routes to your existing app.py to enable JotForm escalation
"""

from flask import request, redirect, session, jsonify
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Add these routes to your existing app.py
# Just copy and paste the functions below into your app.py file

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
    
    # Redirect to existing chatbot with escalation parameters
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
                
            elif isinstance(bot_response, str):
                # Convert string response to dict with escalation info
                bot_response = {
                    'message': bot_response,
                    'escalated': True,
                    'escalation_source': 'jotform',
                    'priority': priority,
                    'buttons': escalation_buttons
                }
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

# JavaScript to add to your existing chatbot.html template
ESCALATION_JAVASCRIPT = """
<script>
// Add this JavaScript to your existing chatbot.html

let isEscalated = false;
let escalationContext = {};

// Check escalation status when page loads
async function checkEscalationStatus() {
    try {
        const response = await fetch('/api/escalation-status');
        const status = await response.json();
        
        if (status.escalated) {
            isEscalated = true;
            escalationContext = status;
            showEscalationNotice(status);
        }
    } catch (error) {
        console.log('Escalation check failed:', error);
    }
}

function showEscalationNotice(status) {
    // Create escalation notice
    const notice = document.createElement('div');
    notice.style.cssText = `
        background: linear-gradient(135deg, #ff6b6b, #ee5a52);
        color: white;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        animation: slideIn 0.5s ease-out;
    `;
    notice.innerHTML = `
        🚀 <strong>Escalated from JotForm!</strong><br>
        Issue: ${status.issue_type} | Priority: ${status.priority}<br>
        <small>You now have access to priority support features</small>
    `;
    
    // Insert at top of chat messages
    const chatMessages = document.getElementById('chat-messages') || document.querySelector('.chat-messages');
    if (chatMessages) {
        chatMessages.insertBefore(notice, chatMessages.firstChild);
    }
}

// Modify your existing sendMessage function to use escalated endpoint
async function sendMessageEscalated(message, sessionId) {
    const endpoint = isEscalated ? '/api/escalated-chat' : '/api/chat';
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            const botResponse = result.response;
            
            // Display bot response
            displayBotMessage(botResponse);
            
            // Handle escalated features
            if (result.escalated && botResponse.buttons) {
                handleEscalatedButtons(botResponse.buttons);
            }
        }
        
    } catch (error) {
        console.error('Failed to send message:', error);
    }
}

function handleEscalatedButtons(buttons) {
    buttons.forEach(button => {
        if (button.action === 'priority_ticket') {
            // Handle priority ticket creation
            button.onclick = () => createPriorityTicket();
        } else if (button.action === 'urgent_agent') {
            // Handle urgent agent request
            button.onclick = () => requestUrgentAgent();
        }
    });
}

async function createPriorityTicket() {
    const title = prompt('Brief title for your issue:') || 'Escalated Support Request';
    const description = prompt('Detailed description:') || 'User escalated from JotForm chatbot';
    
    try {
        const response = await fetch('/api/create-priority-ticket', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title: title,
                description: description
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            const ticket = result.ticket;
            displayBotMessage({
                message: `🎫 Priority ticket created!\\n\\nTicket ID: ${ticket.id}\\nPriority: ${ticket.priority}\\nAgent: ${ticket.agent}\\nETA: ${ticket.eta} minutes`,
                type: 'success'
            });
        } else {
            displayBotMessage({
                message: 'Failed to create priority ticket. Please try again.',
                type: 'error'
            });
        }
    } catch (error) {
        console.error('Failed to create priority ticket:', error);
    }
}

// Call on page load
document.addEventListener('DOMContentLoaded', checkEscalationStatus);
</script>
"""

if __name__ == "__main__":
    print("📋 SIMPLE JOTFORM ESCALATION INTEGRATION")
    print("="*50)
    print("\n🚀 To add JotForm escalation to your existing Flask app:")
    print("\n1. Copy these routes to your app.py:")
    print("   • /escalate")
    print("   • /api/escalation-status") 
    print("   • /api/escalated-chat")
    print("   • /api/create-priority-ticket")
    
    print("\n2. Add the JavaScript to your chatbot.html template")
    
    print("\n3. In JotForm, add an escalation button that redirects to:")
    print("   http://your-domain/escalate?issue=technical&priority=high")
    
    print("\n✅ This will enable:")
    print("   • JotForm to Flask chatbot escalation")
    print("   • Priority support features for escalated users")
    print("   • Enhanced chat responses with escalation context")
    print("   • Priority ticket creation")
    
    print("\n📝 No conflicts with existing routes!")
    print("   Your existing / route and chatbot functionality remain unchanged.")