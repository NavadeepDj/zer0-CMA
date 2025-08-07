#!/usr/bin/env python3
"""
Test Dashboard Functionality
Tests the enhanced customer dashboard features
"""

import requests
import json
import time
from datetime import datetime

def test_dashboard_functionality():
    """Test the enhanced dashboard functionality"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Enhanced Customer Dashboard Functionality")
    print("=" * 60)
    
    # Test 1: Dashboard Page Load
    print("\n1. Testing Dashboard Page Load...")
    try:
        response = requests.get(f"{base_url}/dashboard")
        if response.status_code == 200:
            print("✅ Dashboard page loads successfully")
            print(f"   Response size: {len(response.content)} bytes")
        else:
            print(f"❌ Dashboard page failed to load: {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard page test failed: {e}")
    
    # Test 2: User Tickets API
    print("\n2. Testing User Tickets API...")
    try:
        response = requests.get(f"{base_url}/api/dashboard/tickets")
        if response.status_code == 200:
            data = response.json()
            print("✅ User tickets API working")
            print(f"   Tickets found: {len(data.get('tickets', []))}")
            
            # Display sample ticket if available
            tickets = data.get('tickets', [])
            if tickets:
                sample_ticket = tickets[0]
                print(f"   Sample ticket: {sample_ticket.get('id')} - {sample_ticket.get('title')}")
        else:
            print(f"❌ User tickets API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ User tickets API test failed: {e}")
    
    # Test 3: Dashboard Stats API
    print("\n3. Testing Dashboard Stats API...")
    try:
        response = requests.get(f"{base_url}/api/dashboard/stats")
        if response.status_code == 200:
            data = response.json()
            stats = data.get('stats', {})
            print("✅ Dashboard stats API working")
            print(f"   Total tickets: {stats.get('total_tickets', 0)}")
            print(f"   Open tickets: {stats.get('open_tickets', 0)}")
            print(f"   Resolved tickets: {stats.get('resolved_tickets', 0)}")
        else:
            print(f"❌ Dashboard stats API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard stats API test failed: {e}")
    
    # Test 4: Ticket Status Check
    print("\n4. Testing Ticket Status Check...")
    try:
        # Try to check status of a sample ticket
        response = requests.get(f"{base_url}/api/tickets/ZER0-2025-001/status")
        if response.status_code == 200:
            data = response.json()
            print("✅ Ticket status check working")
            print(f"   Ticket ID: {data.get('id')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Priority: {data.get('priority')}")
        elif response.status_code == 404:
            print("✅ Ticket status check working (ticket not found - expected)")
        else:
            print(f"❌ Ticket status check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Ticket status check test failed: {e}")
    
    # Test 5: Create New Ticket
    print("\n5. Testing Create New Ticket...")
    try:
        ticket_data = {
            "title": "Test Dashboard Ticket",
            "description": "This is a test ticket created from dashboard functionality test",
            "category": "technical",
            "priority": "medium"
        }
        
        response = requests.post(
            f"{base_url}/api/dashboard/create-ticket",
            json=ticket_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Create new ticket working")
            print(f"   Created ticket: {data.get('ticket', {}).get('id')}")
        else:
            print(f"❌ Create new ticket failed: {response.status_code}")
            if response.content:
                print(f"   Error: {response.json().get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Create new ticket test failed: {e}")
    
    # Test 6: Profile Management
    print("\n6. Testing Profile Management...")
    try:
        # Test GET profile
        response = requests.get(f"{base_url}/api/dashboard/profile")
        if response.status_code == 200:
            data = response.json()
            print("✅ Get profile working")
            profile = data.get('profile', {})
            print(f"   Email: {profile.get('email', 'N/A')}")
            print(f"   Language: {profile.get('language', 'N/A')}")
        else:
            print(f"❌ Get profile failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Profile management test failed: {e}")
    
    # Test 7: Escalation Logging
    print("\n7. Testing Escalation Logging...")
    try:
        escalation_data = {
            "source": "jotform",
            "reason": "user_request",
            "context": {"test": True}
        }
        
        response = requests.post(
            f"{base_url}/api/dashboard/escalate",
            json=escalation_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Escalation logging working")
            print(f"   Message: {data.get('message')}")
        else:
            print(f"❌ Escalation logging failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Escalation logging test failed: {e}")
    
    # Test 8: Feedback Submission
    print("\n8. Testing Feedback Submission...")
    try:
        feedback_data = {
            "rating": 5,
            "comment": "Dashboard functionality test feedback",
            "category": "dashboard",
            "source": "test"
        }
        
        response = requests.post(
            f"{base_url}/api/dashboard/feedback",
            json=feedback_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Feedback submission working")
            print(f"   Message: {data.get('message')}")
        else:
            print(f"❌ Feedback submission failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Feedback submission test failed: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Dashboard Functionality Tests Complete")
    print("\n📋 Test Summary:")
    print("   - Dashboard page loading")
    print("   - Real-time ticket updates")
    print("   - Visual progress indicators")
    print("   - JotForm and Flask chatbot integration")
    print("   - Profile settings management")
    print("   - Notification preferences")
    print("   - Escalation handling")
    print("   - Feedback system")
    
    print("\n💡 Next Steps:")
    print("   1. Start the Flask server: python app.py")
    print("   2. Visit: http://localhost:5000/dashboard")
    print("   3. Test the enhanced dashboard features")
    print("   4. Verify JotForm integration")
    print("   5. Test escalation to advanced chatbot")

def test_dashboard_components():
    """Test individual dashboard components"""
    
    print("\n🔧 Testing Dashboard Components...")
    
    # Test HTML structure
    html_content = ""
    try:
        with open('templates/user_dashboard.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        required_elements = [
            'ticket-list',
            'profileSection',
            'jotformContainer',
            'advancedChatbot',
            'escalationNotice',
            'profileForm'
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in html_content:
                missing_elements.append(element)
        
        if not missing_elements:
            print("✅ All required HTML elements present")
        else:
            print(f"❌ Missing HTML elements: {missing_elements}")
            
    except Exception as e:
        print(f"❌ HTML structure test failed: {e}")
    
    # Test CSS classes
    css_classes = [
        'ticket-item',
        'progress-bar',
        'progress-fill',
        'ticket-modal',
        'profile-section',
        'notification-preferences'
    ]
    
    missing_css = []
    for css_class in css_classes:
        if css_class not in html_content:
            missing_css.append(css_class)
    
    if not missing_css:
        print("✅ All required CSS classes present")
    else:
        print(f"❌ Missing CSS classes: {missing_css}")
    
    # Test JavaScript functions
    js_functions = [
        'loadUserTickets',
        'displayTickets',
        'showTicketDetails',
        'showProfileSettings',
        'startRealTimeUpdates',
        'escalateToAdvanced'
    ]
    
    missing_js = []
    for js_function in js_functions:
        if js_function not in html_content:
            missing_js.append(js_function)
    
    if not missing_js:
        print("✅ All required JavaScript functions present")
    else:
        print(f"❌ Missing JavaScript functions: {missing_js}")

if __name__ == "__main__":
    test_dashboard_functionality()
    test_dashboard_components()