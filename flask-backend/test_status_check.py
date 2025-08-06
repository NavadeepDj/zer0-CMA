#!/usr/bin/env python3
"""
Test status check functionality in chatbot
"""

import requests
import json
import time

BASE_URL = "http://172.28.0.217:5000"

def test_status_check_flow():
    """Test the complete status check flow"""
    print("🔍 Testing Status Check Flow")
    print("=" * 50)
    
    session_id = f"test-status-{int(time.time())}"
    
    # Step 1: First create a ticket to check
    print("1️⃣ Creating a test ticket first...")
    ticket_data = {
        "name": "Status Test User",
        "email": "status.test@example.com",
        "category": "Technical Help & Troubleshooting",
        "description": "This is a test ticket for status check functionality."
    }
    
    response = requests.post(f"{BASE_URL}/api/complaint", json=ticket_data)
    if response.status_code != 200:
        print(f"❌ Failed to create test ticket: {response.status_code}")
        return False
    
    ticket_response = response.json()
    test_ticket_id = ticket_response['ticket_id']
    print(f"✅ Test ticket created: {test_ticket_id}")
    
    # Step 2: Test status check initiation
    print("\n2️⃣ Testing status check initiation...")
    response = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "I want to check my ticket status",
        "session_id": session_id
    })
    
    if response.status_code != 200:
        print(f"❌ Failed to initiate status check: {response.status_code}")
        return False
    
    data = response.json()
    bot_message = data['response']['message']
    print("✅ Status check initiated")
    print(f"   Bot asked: {bot_message[:100]}...")
    
    # Step 3: Test valid ticket ID lookup
    print("\n3️⃣ Testing valid ticket ID lookup...")
    response = requests.post(f"{BASE_URL}/api/chat", json={
        "message": test_ticket_id,
        "session_id": session_id
    })
    
    if response.status_code != 200:
        print(f"❌ Failed to lookup ticket: {response.status_code}")
        return False
    
    data = response.json()
    bot_message = data['response']['message']
    
    if "Ticket Status Found" in bot_message:
        print("✅ Valid ticket ID lookup successful")
        print(f"   Found ticket: {test_ticket_id}")
        print(f"   Status info provided: {len(bot_message)} characters")
    else:
        print("❌ Valid ticket ID lookup failed")
        print(f"   Bot response: {bot_message}")
        return False
    
    # Step 4: Test invalid ticket ID
    print("\n4️⃣ Testing invalid ticket ID...")
    response = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "I want to check my ticket status",
        "session_id": f"{session_id}-invalid"
    })
    
    # Initiate status check
    response = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "ZER0-9999-999",
        "session_id": f"{session_id}-invalid"
    })
    
    if response.status_code == 200:
        data = response.json()
        bot_message = data['response']['message']
        
        if "Ticket Not Found" in bot_message:
            print("✅ Invalid ticket ID handled correctly")
        else:
            print("❌ Invalid ticket ID not handled properly")
            print(f"   Bot response: {bot_message}")
    
    # Step 5: Test email lookup
    print("\n5️⃣ Testing email lookup...")
    response = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "I want to check my ticket status",
        "session_id": f"{session_id}-email"
    })
    
    # Provide email
    response = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "status.test@example.com",
        "session_id": f"{session_id}-email"
    })
    
    if response.status_code == 200:
        data = response.json()
        bot_message = data['response']['message']
        
        if "Ticket Found by Email" in bot_message:
            print("✅ Email lookup successful")
        else:
            print("❌ Email lookup failed")
            print(f"   Bot response: {bot_message}")
    
    # Step 6: Test invalid format
    print("\n6️⃣ Testing invalid format...")
    response = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "I want to check my ticket status",
        "session_id": f"{session_id}-invalid-format"
    })
    
    # Provide invalid format
    response = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "invalid-format-123",
        "session_id": f"{session_id}-invalid-format"
    })
    
    if response.status_code == 200:
        data = response.json()
        bot_message = data['response']['message']
        
        if "Invalid Format" in bot_message:
            print("✅ Invalid format handled correctly")
        else:
            print("❌ Invalid format not handled properly")
    
    print("\n🎉 Status check flow testing completed!")
    return True

def main():
    """Run status check tests"""
    print("🚀 Prashna Status Check Test")
    print("=" * 50)
    
    # Check server health
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code != 200:
            print("❌ Server not responding")
            return
        print("✅ Server is healthy")
    except:
        print("❌ Cannot connect to server")
        print("💡 Make sure to run: python app.py")
        return
    
    # Run the test
    if test_status_check_flow():
        print("\n" + "=" * 50)
        print("🎉 SUCCESS: Status check functionality is working!")
        print("\n💡 Now you can:")
        print("   1. Go to chatbot: http://172.28.0.217:5000")
        print("   2. Click 'Check Ticket Status'")
        print("   3. Enter a ticket ID (e.g., ZER0-2025-001)")
        print("   4. Get detailed status information!")
        
    else:
        print("\n❌ Some tests failed. Check the server logs.")

if __name__ == "__main__":
    main()