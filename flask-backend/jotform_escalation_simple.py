"""
Simple JotForm Escalation Integration
Adds minimal escalation functionality to existing Flask app
"""

import logging
from flask import Flask, request, redirect, session, render_template

logger = logging.getLogger(__name__)

def add_jotform_escalation(app: Flask):
    """
    Add simple JotForm escalation to existing Flask app
    This is the minimal integration that won't conflict with existing routes
    """
    try:
        logger.info("🚀 Adding JotForm escalation support...")
        
        # Route 1: Handle escalation from JotForm
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
                'timestamp': str(datetime.now())
            }
            
            # Log escalation
            logger.info(f"📈 JotForm escalation: {issue_type} - {priority}")
            
            # Redirect to existing chatbot with escalation parameters
            return redirect(f'/?ref=jotform&escalated=true&issue={issue_type}&priority={priority}')
        
        # Route 2: API endpoint to check if user is escalated
        @app.route('/api/escalation-status')
        def escalation_status():
            """Check if current session is escalated"""
            escalation_context = session.get('escalation_context', {})
            
            return {
                'escalated': escalation_context.get('escalated', False),
                'source': escalation_context.get('source', ''),
                'issue_type': escalation_context.get('issue_type', ''),
                'priority': escalation_context.get('priority', 'medium')
            }
        
        # Route 3: Enhanced chatbot message processing for escalated users
        @app.route('/api/escalated-chat', methods=['POST'])
        def escalated_chat():
            """Process chat messages for escalated users"""
            data = request.get_json()
            message = data.get('message', '')
            session_id = data.get('session_id', 'default')
            
            # Check if user is escalated
            escalation_context = session.get('escalation_context', {})
            is_escalated = escalation_context.get('escalated', False)
            
            # Import existing chatbot logic
            from app import prashna, chat_sessions, save_chat_sessions
            
            # Process message with escalation context
            if is_escalated:
                # Add escalation context to the message processing
                enhanced_message = f"[ESCALATED FROM JOTFORM - {escalation_context.get('issue_type', 'general').upper()}] {message}"
                bot_response = prashna.process_message(enhanced_message, session_id)
                
                # Enhance response for escalated users
                if isinstance(bot_response, dict):
                    # Add escalation-specific options
                    if 'buttons' not in bot_response:
                        bot_response['buttons'] = []
                    
                    # Add priority options for escalated users
                    escalation_buttons = [
                        {"text": "🚨 Connect to Agent Now", "action": "urgent_agent"},
                        {"text": "📋 Create Priority Ticket", "action": "priority_ticket"}
                    ]
                    
                    for btn in escalation_buttons:
                        if not any(b.get('action') == btn['action'] for b in bot_response['buttons']):
                            bot_response['buttons'].append(btn)
                
                # Add escalation indicator to response
                bot_response['escalated'] = True
                bot_response['escalation_source'] = escalation_context.get('source')
                
            else:
                # Regular message processing
                bot_response = prashna.process_message(message, session_id)
            
            return {
                'success': True,
                'response': bot_response,
                'escalated': is_escalated
            }
        
        logger.info("✅ JotForm escalation routes added successfully")
        
        print("\n" + "="*50)
        print("🎉 JOTFORM ESCALATION ADDED!")
        print("="*50)
        print("\n✅ New Routes:")
        print("   • /escalate - Handle JotForm escalation")
        print("   • /api/escalation-status - Check escalation status")
        print("   • /api/escalated-chat - Enhanced chat for escalated users")
        
        print("\n🔧 JotForm Integration:")
        print("   • Add escalation button in JotForm that redirects to:")
        print("     http://your-domain/escalate?issue=technical&priority=high")
        print("   • Or use JavaScript to redirect:")
        print("     window.location.href = '/escalate?issue=billing&priority=medium';")
        
        print("\n📝 Usage in your existing chatbot.html:")
        print("   • Check escalation status with: fetch('/api/escalation-status')")
        print("   • Use /api/escalated-chat for enhanced message processing")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to add JotForm escalation: {e}")
        return False

def modify_existing_chatbot_for_escalation(app: Flask):
    """
    Modify the existing chatbot template to handle escalation
    This adds escalation awareness to your existing chatbot
    """
    try:
        # Add JavaScript to existing chatbot for escalation handling
        escalation_js = """
        // Add this JavaScript to your existing chatbot.html
        
        // Check if user is escalated when page loads
        async function checkEscalationStatus() {
            try {
                const response = await fetch('/api/escalation-status');
                const status = await response.json();
                
                if (status.escalated) {
                    // Show escalation notice
                    showEscalationNotice(status);
                    
                    // Use enhanced chat endpoint
                    window.chatEndpoint = '/api/escalated-chat';
                } else {
                    // Use regular chat endpoint
                    window.chatEndpoint = '/api/chat';
                }
            } catch (error) {
                console.log('Escalation check failed, using regular chat');
                window.chatEndpoint = '/api/chat';
            }
        }
        
        function showEscalationNotice(status) {
            const notice = document.createElement('div');
            notice.style.cssText = `
                background: linear-gradient(135deg, #ff6b6b, #ee5a52);
                color: white;
                padding: 1rem;
                margin: 1rem 0;
                border-radius: 10px;
                text-align: center;
                font-weight: bold;
            `;
            notice.innerHTML = `
                🚀 You've been escalated from JotForm!<br>
                Issue Type: ${status.issue_type} | Priority: ${status.priority}<br>
                You now have access to priority support features.
            `;
            
            // Insert at top of chat
            const chatContainer = document.querySelector('.chat-container') || document.body;
            chatContainer.insertBefore(notice, chatContainer.firstChild);
        }
        
        // Call on page load
        document.addEventListener('DOMContentLoaded', checkEscalationStatus);
        """
        
        # Save the JavaScript to a file for easy inclusion
        with open('templates/escalation_enhancement.js', 'w') as f:
            f.write(escalation_js)
        
        logger.info("✅ Escalation JavaScript created at templates/escalation_enhancement.js")
        
        print("\n📝 To enhance your existing chatbot.html:")
        print("   1. Add this script tag to your chatbot.html:")
        print("      <script src='/static/escalation_enhancement.js'></script>")
        print("   2. Or copy the JavaScript from templates/escalation_enhancement.js")
        print("   3. Modify your chat message sending to use window.chatEndpoint")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create escalation enhancement: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("🚀 Simple JotForm Escalation Integration")
    print("\nThis adds minimal escalation support to your existing Flask app.")
    print("\nTo integrate, add this to your app.py:")
    print("```python")
    print("from jotform_escalation_simple import add_jotform_escalation")
    print("add_jotform_escalation(app)")
    print("```")
    
    print("\nThis will:")
    print("✅ Add /escalate route for JotForm redirection")
    print("✅ Add escalation status checking")
    print("✅ Enhance chat processing for escalated users")
    print("✅ Preserve all your existing routes and functionality")
    
    print("\nJotForm Button Setup:")
    print("• Add a button in JotForm that redirects to: /escalate?issue=TYPE&priority=LEVEL")
    print("• Example: /escalate?issue=technical&priority=high")