#!/usr/bin/env python3
"""
Test script for email functionality
"""

import requests
import json

BASE_URL = "http://172.28.0.217:5000"

def test_simple_form_submission():
    """Test form submission with email notifications"""
    print("🧪 Testing Support Form Submission with Email...")
    
    # Test data
    test_ticket = {
        "name": "John Doe",
        "email": "john.doe@example.com",  # Replace with your test email
        "category": "Technical Help & Troubleshooting",
        "description": "My laptop screen keeps flickering and sometimes goes completely black. This started happening after the latest Windows update. I've tried restarting multiple times but the issue persists."
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/complaint", json=test_ticket)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Form submission successful!")
            print(f"   Ticket ID: {data['ticket_id']}")
            print(f"   Assigned Agent: {data['assigned_agent']}")
            print(f"   Message: {data['message']}")
            print("\n📧 Check your email for:")
            print("   1. Admin notification (support team)")
            print("   2. Customer confirmation")
            return data['ticket_id']
        else:
            print(f"❌ Form submission failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing form submission: {e}")
    
    return None

def test_ticket_status(ticket_id):
    """Test ticket status retrieval"""
    if not ticket_id:
        print("\n⏭️  Skipping status test (no ticket ID)")
        return
        
    print(f"\n🔍 Testing Ticket Status for {ticket_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/status/{ticket_id}")
        
        if response.status_code == 200:
            data = response.json()
            ticket = data['ticket']
            print("✅ Status retrieval successful!")
            print(f"   Status: {ticket['status']}")
            print(f"   Priority: {ticket['priority']}")
            print(f"   Created: {ticket['created_at']}")
            print(f"   Customer: {ticket['customer_name']}")
        else:
            print(f"❌ Status retrieval failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing status retrieval: {e}")

def test_health_check():
    """Test server health"""
    print("🔍 Testing Server Health...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is healthy!")
            print(f"   Service: {data['service']}")
            print(f"   Status: {data['status']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing health check: {e}")

def main():
    """Run all tests"""
    print("🚀 Testing Zer0 Customer Support System")
    print("=" * 50)
    
    # Test server health
    test_health_check()
    
    # Test form submission with emails
    ticket_id = test_simple_form_submission()
    
    # Test ticket status
    test_ticket_status(ticket_id)
    
    print("\n" + "=" * 50)
    print("🎉 Testing completed!")
    print("\n💡 To test the web interfaces:")
    print("   📝 Simple Form: http://172.28.0.217:5000/form")
    print("   💬 Chatbot: http://172.28.0.217:5000")
    print("\n📧 Email Setup:")
    print("   1. Update email credentials in app.py")
    print("   2. Replace test email addresses")
    print("   3. Check spam folders for test emails")

if __name__ == "__main__":
    main()