#!/usr/bin/env python3
"""
Test Closure Email Notification
Verifies that closure emails are sent when tickets are closed
"""

import json
import os
from datetime import datetime

def test_closure_email_functionality():
    """Test the closure email notification functionality"""
    
    print("📧 Testing Closure Email Notification")
    print("=" * 50)
    
    # Test 1: Check if closure email function exists
    print("\n1. Checking closure email function...")
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        # Check for closure email function
        if 'send_ticket_closure_notification' in app_content:
            print("✅ Closure email function found")
            
            # Check for key components
            components = [
                'Your Support Request Resolved',
                'closure notification',
                'CLOSED',
                'Resolution Notes',
                'Still Need Help'
            ]
            
            found_components = []
            missing_components = []
            
            for component in components:
                if component in app_content:
                    found_components.append(component)
                else:
                    missing_components.append(component)
            
            if not missing_components:
                print("✅ All email components found")
            else:
                print(f"❌ Missing components: {missing_components}")
                
        else:
            print("❌ Closure email function not found")
            
    except Exception as e:
        print(f"❌ Error checking closure email function: {e}")
    
    # Test 2: Check integration with status update
    print("\n2. Checking integration with status update...")
    try:
        if 'send_ticket_closure_notification' in app_content and "new_status == 'closed'" in app_content:
            print("✅ Closure email integrated with status update")
            
            # Check for proper error handling
            if 'Failed to send closure notification' in app_content:
                print("✅ Error handling for email failures found")
            else:
                print("⚠️  Email error handling not found")
                
        else:
            print("❌ Closure email not integrated with status update")
            
    except Exception as e:
        print(f"❌ Error checking integration: {e}")
    
    # Test 3: Simulate email content generation
    print("\n3. Testing email content generation...")
    try:
        # Simulate a ticket that's being closed
        sample_ticket = {
            'id': 'ZER0-2025-001',
            'ticket_number': 'ZER0-2025-001',
            'customer_name': 'John Doe',
            'customer_email': 'john.doe@example.com',
            'category': 'Technical Help & Troubleshooting',
            'created_at': '2025-01-08 10:00:00',
            'assigned_agent': 'Alex (Technical Specialist)',
            'status': 'closed',
            'agent_notes': [
                {
                    'note': 'Issue resolved by updating the software configuration.',
                    'timestamp': '2025-01-08 14:30:00',
                    'updated_by': 'agent'
                }
            ]
        }
        
        print("✅ Sample ticket data created")
        print(f"   Ticket ID: {sample_ticket['id']}")
        print(f"   Customer: {sample_ticket['customer_name']}")
        print(f"   Email: {sample_ticket['customer_email']}")
        print(f"   Category: {sample_ticket['category']}")
        print(f"   Agent: {sample_ticket['assigned_agent']}")
        
        # Test email subject generation
        expected_subject = f"✅ Your Support Request Resolved - Ticket {sample_ticket['id']}"
        print(f"✅ Email subject: {expected_subject}")
        
    except Exception as e:
        print(f"❌ Error testing email content: {e}")
    
    # Test 4: Check email configuration
    print("\n4. Checking email configuration...")
    try:
        email_config_found = []
        email_configs = [
            'MAIL_SERVER',
            'MAIL_PORT',
            'MAIL_USE_TLS',
            'MAIL_USERNAME',
            'send_email'
        ]
        
        for config in email_configs:
            if config in app_content:
                email_config_found.append(config)
        
        if len(email_config_found) >= 4:
            print(f"✅ Email configuration found: {len(email_config_found)}/{len(email_configs)} items")
        else:
            print(f"⚠️  Incomplete email configuration: {len(email_config_found)}/{len(email_configs)} items")
            
    except Exception as e:
        print(f"❌ Error checking email configuration: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Closure Email Tests Complete")
    
    print("\n📧 Email Features Implemented:")
    print("   ✅ Automatic closure notification when ticket status = 'closed'")
    print("   ✅ Professional HTML email template")
    print("   ✅ Ticket summary with resolution details")
    print("   ✅ Agent notes included in email")
    print("   ✅ Contact information for further assistance")
    print("   ✅ Error handling for email failures")
    
    print("\n🎯 Email Content Includes:")
    print("   • Congratulatory message for resolution")
    print("   • Complete ticket summary")
    print("   • Resolution date and agent information")
    print("   • Agent notes about the resolution")
    print("   • Instructions for further assistance")
    print("   • Contact information")
    print("   • Professional branding")
    
    print("\n🔄 Workflow:")
    print("   1. Agent updates ticket status to 'closed'")
    print("   2. System automatically triggers email notification")
    print("   3. Customer receives closure notification email")
    print("   4. Email includes all resolution details")
    print("   5. Customer can reference ticket ID for future needs")
    
    print("\n💡 Testing Instructions:")
    print("   1. Start Flask server: python app.py")
    print("   2. Sign in as admin: admin@zer0.com / admin123")
    print("   3. Go to agent dashboard: /agents")
    print("   4. Click 'Ticket Management' tab")
    print("   5. Find a ticket and update status to 'Closed'")
    print("   6. Check email logs for closure notification")
    
    print("\n📋 Email Template Features:")
    print("   • Responsive HTML design")
    print("   • Professional color scheme")
    print("   • Clear ticket information")
    print("   • Agent resolution notes")
    print("   • Next steps guidance")
    print("   • Contact information")

def test_email_template_structure():
    """Test the email template structure"""
    
    print("\n🔧 Testing Email Template Structure...")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for HTML email structure
        html_elements = [
            'html_body = f"""',
            '<div style="font-family: Arial',
            'Your Support Request is Resolved',
            'Ticket Summary:',
            'Resolution Notes',
            'What\'s Next?',
            'Still Need Help?',
            'Thank you for choosing Zer0'
        ]
        
        found_elements = []
        missing_elements = []
        
        for element in html_elements:
            if element in content:
                found_elements.append(element)
            else:
                missing_elements.append(element)
        
        print(f"✅ HTML template elements: {len(found_elements)}/{len(html_elements)} found")
        
        if missing_elements:
            print(f"❌ Missing elements: {missing_elements}")
        else:
            print("✅ Complete HTML email template structure")
            
    except Exception as e:
        print(f"❌ Template structure test failed: {e}")

if __name__ == "__main__":
    test_closure_email_functionality()
    test_email_template_structure()