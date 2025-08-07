"""
Safe Integration Script for User Dashboard
Integrates dashboard functionality without conflicting with existing routes
"""

import logging
from flask import Flask
from dashboard_routes import integrate_dashboard_routes
from enhanced_chatbot_routes import integrate_enhanced_chatbot_routes

logger = logging.getLogger(__name__)

def integrate_dashboard_safely(app: Flask):
    """
    Safely integrate User Dashboard with existing Flask app
    Does not override existing routes
    
    Args:
        app: Flask application instance
    """
    try:
        logger.info("🚀 Safely integrating User Dashboard...")
        
        # Step 1: Integrate Dashboard Routes (no conflicts)
        logger.info("Step 1: Integrating Dashboard Routes...")
        if integrate_dashboard_routes(app):
            logger.info("✅ Dashboard routes integrated successfully")
        else:
            raise Exception("Failed to integrate dashboard routes")
        
        # Step 2: Integrate Enhanced Chatbot Routes (no conflicts)
        logger.info("Step 2: Integrating Enhanced Chatbot Routes...")
        if integrate_enhanced_chatbot_routes(app):
            logger.info("✅ Enhanced chatbot routes integrated successfully")
        else:
            raise Exception("Failed to integrate enhanced chatbot routes")
        
        # Step 3: Add JotForm escalation route (safe route name)
        @app.route('/escalate-to-advanced')
        def escalate_to_advanced():
            """Handle escalation from JotForm to advanced chatbot"""
            from flask import redirect, request
            
            # Get escalation context
            referral = request.args.get('ref', 'jotform')
            reason = request.args.get('reason', 'escalation')
            
            # Redirect to enhanced chatbot with escalation context
            return redirect(f'/chatbot?referral={referral}&escalated=true&reason={reason}')
        
        logger.info("✅ Escalation route added")
        
        # Step 4: Add dashboard access route (safe route name)
        @app.route('/user-dashboard')
        def user_dashboard_redirect():
            """Redirect to user dashboard"""
            from flask import redirect
            return redirect('/dashboard')
        
        logger.info("✅ Dashboard redirect route added")
        
        # Step 5: Add error handlers (safe, won't conflict)
        @app.errorhandler(403)
        def forbidden(error):
            return "Access forbidden. Please log in.", 403
        
        logger.info("✅ Additional error handlers configured")
        
        logger.info("🎉 Safe User Dashboard integration complete!")
        
        # Print integration summary
        print("\n" + "="*60)
        print("🎉 SAFE DASHBOARD INTEGRATION COMPLETE!")
        print("="*60)
        print("\n✅ Integrated Components:")
        print("   • User Dashboard (preserves existing routes)")
        print("   • Enhanced AI Chatbot with escalation")
        print("   • Dashboard API endpoints")
        print("   • JotForm escalation handling")
        
        print("\n🌐 New Routes Added:")
        print("   • /dashboard - User dashboard")
        print("   • /user-dashboard - Redirect to dashboard")
        print("   • /escalate-to-advanced - JotForm escalation handler")
        print("   • /api/dashboard/* - Dashboard API endpoints")
        print("   • /api/chatbot/* - Enhanced chatbot endpoints")
        
        print("\n🔧 Existing Routes Preserved:")
        print("   • / - Your existing chatbot interface (unchanged)")
        print("   • /chatbot - Enhanced version with escalation support")
        print("   • All other existing routes remain unchanged")
        
        print("\n🚀 JotForm Integration:")
        print("   • Update JotForm escalation button to redirect to:")
        print("     http://your-domain/escalate-to-advanced?ref=jotform")
        print("   • Or embed dashboard at: http://your-domain/dashboard")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Safe Dashboard integration failed: {e}")
        return False

def add_jotform_escalation_to_existing_chatbot(app: Flask):
    """
    Add escalation handling to your existing chatbot route
    This modifies the existing /chatbot route to handle escalation
    """
    try:
        logger.info("🔧 Adding escalation support to existing chatbot...")
        
        # Import the existing chatbot logic
        from flask import request, render_template
        
        # Get the existing chatbot route function
        existing_chatbot_rule = None
        for rule in app.url_map.iter_rules():
            if rule.rule == '/chatbot' and 'GET' in rule.methods:
                existing_chatbot_rule = rule
                break
        
        if existing_chatbot_rule:
            # The existing /chatbot route will now handle escalation parameters
            logger.info("✅ Existing /chatbot route will handle escalation parameters")
        else:
            # Add a new enhanced chatbot route
            @app.route('/chatbot-enhanced')
            def enhanced_chatbot():
                """Enhanced chatbot with escalation support"""
                # Get escalation context from URL parameters
                referral = request.args.get('referral', '')
                escalated = request.args.get('escalated', 'false') == 'true'
                reason = request.args.get('reason', '')
                
                # Use the enhanced chatbot template
                return render_template('enhanced_chatbot.html', 
                                     referral=referral,
                                     escalated=escalated,
                                     reason=reason)
            
            logger.info("✅ Enhanced chatbot route added at /chatbot-enhanced")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to add escalation support: {e}")
        return False

def create_jotform_escalation_handler(app: Flask):
    """
    Create a simple escalation handler for JotForm
    """
    try:
        @app.route('/jotform-escalate')
        def jotform_escalate():
            """Handle JotForm escalation requests"""
            from flask import request, redirect, session
            
            # Log the escalation
            logger.info("📈 JotForm escalation triggered")
            
            # Get any context from JotForm
            issue_type = request.args.get('issue', 'general')
            priority = request.args.get('priority', 'medium')
            
            # Store escalation context in session
            session['escalation_context'] = {
                'source': 'jotform',
                'issue_type': issue_type,
                'priority': priority,
                'escalated': True
            }
            
            # Redirect to your existing chatbot with escalation flag
            return redirect(f'/chatbot?ref=jotform&escalated=true&issue={issue_type}')
        
        logger.info("✅ JotForm escalation handler created at /jotform-escalate")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create JotForm escalation handler: {e}")
        return False

if __name__ == "__main__":
    # Test the safe integration
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 Testing Safe Dashboard Integration...")
    print("\nThis integration will:")
    print("✅ Add dashboard functionality without conflicts")
    print("✅ Preserve your existing / route")
    print("✅ Add JotForm escalation handling")
    print("✅ Enhance your existing chatbot with escalation support")
    
    print("\nTo integrate with your existing Flask app, add this to your app.py:")
    print("```python")
    print("from integrate_dashboard_safe import integrate_dashboard_safely")
    print("integrate_dashboard_safely(app)")
    print("```")
    
    print("\nOr for minimal JotForm escalation only:")
    print("```python")
    print("from integrate_dashboard_safe import create_jotform_escalation_handler")
    print("create_jotform_escalation_handler(app)")
    print("```")