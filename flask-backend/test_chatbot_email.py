#!/usr/bin/env python3
"""
Test chatbot email functionality specifically
"""

import requests
import json
import time

BASE_URL = "http://172.28.0.217:5000"

def test_chatbot_email_flow():
    """Test the complete chatbot flow with email notifications"""
    print("🤖 Testing Chatbot Email Flow")
    print("=" * 50)
    
    session_id = f"test-session-{int(time.time())}"
    
    # Step 1: Start complaint flow
    print("1️⃣ Starting complaint flow...")
    response1 = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "I need help with a complaint",
        "session_id": session_id
    })
    
    if response1.status_code != 200:
        print(f"❌ Failed to start complaint flow: {response1.status_code}")
        return
    
    print("✅ Complaint flow started")
    
    # Step 2: Provide name
    print("2️⃣ Providing name...")
    response2 = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "Test User",
        "session_id": session_id
    })
    
    if response2.status_code != 200:
        print(f"❌ Failed to provide name: {response2.status_code}")
        return
    
    print("✅ Name provided")
    
    # Step 3: Provide email
    print("3️⃣ Providing email...")
    response3 = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "navadeepmarella@gmail.com",
        "session_id": session_id
    })
    
    if response3.status_code != 200:
        print(f"❌ Failed to provide email: {response3.status_code}")
        return
    
    print("✅ Email provided")
    
    # Step 4: Select category
    print("4️⃣ Selecting category...")
    response4 = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "category_technical",
        "session_id": session_id
    })
    
    if response4.status_code != 200:
        print(f"❌ Failed to select category: {response4.status_code}")
        return
    
    print("✅ Category selected")
    
    # Step 5: Provide description (this should trigger ticket creation and emails)
    print("5️⃣ Providing description (should trigger emails)...")
    response5 = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "Testing the chatbot email functionality. This should create a ticket and send both admin notification and customer confirmation emails.",
        "session_id": session_id
    })
    
    if response5.status_code != 200:
        print(f"❌ Failed to provide description: {response5.status_code}")
        return
    
    data = response5.json()
    print("✅ Description provided and ticket created!")
    
    # Check the response for email status
    bot_message = data.get('response', {}).get('message', '')
    print(f"\n📝 Bot Response:")
    print(bot_message)
    
    if "Email notifications sent successfully" in bot_message:
        print("\n🎉 SUCCESS: Emails were sent from chatbot!")
        print("\n📧 Expected emails:")
        print("   1. Admin notification → navadeepmarella@gmail.com")
        print("   2. Customer confirmation → navadeepmarella@gmail.com")
        print("   Both from: dohaloj488@foboxs.com")
    elif "email notifications failed" in bot_message:
        print("\n⚠️  WARNING: Email sending failed")
        print("💡 Check your email configuration:")
        print("   1. App password for dohaloj488@foboxs.com")
        print("   2. Server console for error messages")
    else:
        print("\n❓ UNCLEAR: Could not determine email status")
        print("Check the server console for logs")
    
    return True

def main():
    """Run the chatbot email test"""
    print("🚀 Chatbot Email Functionality Test")
    print("=" * 50)
    
    # Test server health first
    try:
        health_response = requests.get(f"{BASE_URL}/api/health")
        if health_response.status_code != 200:
            print("❌ Server not responding")
            return
        print("✅ Server is healthy")
    except:
        print("❌ Cannot connect to server")
        print("💡 Make sure to run: python app.py")
        return
    
    # Run the test
    test_chatbot_email_flow()
    
    print("\n" + "=" * 50)
    print("📋 What to check:")
    print("   1. Server console logs for email sending attempts")
    print("   2. navadeepmarella@gmail.com inbox for 2 emails")
    print("   3. Spam folder if emails not in inbox")
    print("\n💡 If emails still don't work:")
    print("   1. Run: python check_email_config.py")
    print("   2. Verify app password in app.py")
    print("   3. Check server console for specific errors")

if __name__ == "__main__":
    main()