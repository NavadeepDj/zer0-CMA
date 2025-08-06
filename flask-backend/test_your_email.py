#!/usr/bin/env python3
"""
Test script specifically for your email configuration
"""

import requests
import json

BASE_URL = "http://172.28.0.217:5000"

def test_email_system():
    """Test the complete email system with your configuration"""
    print("🧪 Testing Zer0 Support Email System")
    print("=" * 50)
    print("📧 Sender: dohaloj488@foboxs.com")
    print("📧 Admin: navadeepmarella@gmail.com")
    print("=" * 50)
    
    # Test data - use your email to test customer confirmation
    test_ticket = {
        "name": "Navadeep Marella",
        "email": "navadeepmarella@gmail.com",  # You'll get the customer confirmation
        "category": "Technical Help & Troubleshooting",
        "description": "Testing the email system for Zer0 Customer Support. This is a test ticket to verify that both admin notifications and customer confirmations are working properly."
    }
    
    print("🎫 Creating test ticket...")
    print(f"   Customer: {test_ticket['name']}")
    print(f"   Email: {test_ticket['email']}")
    print(f"   Category: {test_ticket['category']}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/complaint", json=test_ticket)
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Ticket created successfully!")
            print(f"   Ticket ID: {data['ticket_id']}")
            print(f"   Assigned Agent: {data['assigned_agent']}")
            
            print("\n📧 Expected Emails:")
            print("   1. Admin Notification → navadeepmarella@gmail.com")
            print("      Subject: 🎫 New Support Ticket - " + data['ticket_id'])
            print("      From: dohaloj488@foboxs.com")
            print()
            print("   2. Customer Confirmation → navadeepmarella@gmail.com")
            print("      Subject: ✅ Your Support Request Received - " + data['ticket_id'])
            print("      From: dohaloj488@foboxs.com")
            
            print(f"\n💬 Server Response: {data['message']}")
            
            if "Email notifications sent" in data['message']:
                print("\n🎉 SUCCESS: Emails were sent successfully!")
                print("\n📱 Next Steps:")
                print("   1. Check navadeepmarella@gmail.com inbox")
                print("   2. Check spam folder if not in inbox")
                print("   3. You should see 2 emails (admin + customer)")
            else:
                print("\n⚠️  WARNING: Email sending may have failed")
                print("   Check the server logs for error details")
                
        else:
            print(f"\n❌ Ticket creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Error testing email system: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure Flask server is running: python app.py")
        print("   2. Check email configuration in app.py")
        print("   3. Verify app password for dohaloj488@foboxs.com")

def test_server_health():
    """Test if server is running"""
    print("\n🔍 Testing server health...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is healthy!")
            print(f"   Service: {data['service']}")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("💡 Make sure to start the server first: python app.py")
        return False

def main():
    """Run the email test"""
    print("🚀 Zer0 Customer Support Email Test")
    print("=" * 50)
    
    # Check server health first
    if not test_server_health():
        return
    
    # Test email system
    test_email_system()
    
    print("\n" + "=" * 50)
    print("📋 Email Configuration Checklist:")
    print("   □ App password generated for dohaloj488@foboxs.com")
    print("   □ Password updated in flask-backend/app.py")
    print("   □ 2FA enabled on dohaloj488@foboxs.com")
    print("   □ Flask server running on 172.28.0.217:5000")
    print("\n💡 If emails aren't working:")
    print("   1. Check EMAIL_CONFIG_GUIDE.md")
    print("   2. Verify app password is correct")
    print("   3. Check spam folders")
    print("   4. Look at server console for error messages")

if __name__ == "__main__":
    main()