#!/usr/bin/env python3
"""
Test script for Prashna chatbot functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print("❌ Health check failed")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_chat_greeting():
    """Test chat greeting functionality"""
    print("\n🔍 Testing chat greeting...")
    try:
        payload = {
            "message": "hello",
            "session_id": "test-session-1"
        }
        response = requests.post(f"{BASE_URL}/api/chat", json=payload)
        if response.status_code == 200:
            data = response.json()
            print("✅ Chat greeting test passed")
            print(f"   Bot response: {data['response']['message'][:100]}...")
            print(f"   Buttons available: {len(data['response'].get('buttons', []))}")
        else:
            print("❌ Chat greeting test failed")
    except Exception as e:
        print(f"❌ Chat greeting error: {e}")

def test_complaint_intent():
    """Test complaint intent recognition"""
    print("\n🔍 Testing complaint intent...")
    try:
        payload = {
            "message": "I have a problem with my laptop",
            "session_id": "test-session-2"
        }
        response = requests.post(f"{BASE_URL}/api/chat", json=payload)
        if response.status_code == 200:
            data = response.json()
            print("✅ Complaint intent test passed")
            print(f"   Bot response: {data['response']['message'][:100]}...")
        else:
            print("❌ Complaint intent test failed")
    except Exception as e:
        print(f"❌ Complaint intent error: {e}")

def test_ticket_creation():
    """Test ticket creation"""
    print("\n🔍 Testing ticket creation...")
    try:
        payload = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "category": "technical",
            "description": "My laptop screen is flickering and sometimes goes black completely."
        }
        response = requests.post(f"{BASE_URL}/api/complaint", json=payload)
        if response.status_code == 200:
            data = response.json()
            print("✅ Ticket creation test passed")
            print(f"   Ticket ID: {data['ticket_id']}")
            print(f"   Assigned Agent: {data['assigned_agent']}")
            print(f"   ETA: {data['eta_minutes']} minutes")
            return data['ticket_id']
        else:
            print("❌ Ticket creation test failed")
    except Exception as e:
        print(f"❌ Ticket creation error: {e}")
    return None

def test_status_check(ticket_id):
    """Test ticket status check"""
    if not ticket_id:
        print("\n⏭️  Skipping status check (no ticket ID)")
        return
        
    print(f"\n🔍 Testing status check for ticket {ticket_id}...")
    try:
        response = requests.get(f"{BASE_URL}/api/status/{ticket_id}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Status check test passed")
            print(f"   Status: {data['ticket']['status']}")
            print(f"   Priority: {data['ticket']['priority']}")
            print(f"   Created: {data['ticket']['created_at']}")
        else:
            print("❌ Status check test failed")
    except Exception as e:
        print(f"❌ Status check error: {e}")

def test_faq_intent():
    """Test FAQ intent recognition"""
    print("\n🔍 Testing FAQ intent...")
    try:
        payload = {
            "message": "I have some questions",
            "session_id": "test-session-3"
        }
        response = requests.post(f"{BASE_URL}/api/chat", json=payload)
        if response.status_code == 200:
            data = response.json()
            print("✅ FAQ intent test passed")
            print(f"   Bot response: {data['response']['message']}")
            print(f"   FAQ options: {len(data['response'].get('buttons', []))}")
        else:
            print("❌ FAQ intent test failed")
    except Exception as e:
        print(f"❌ FAQ intent error: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting Prashna Chatbot Tests")
    print("=" * 50)
    
    # Test basic functionality
    test_health_check()
    test_chat_greeting()
    test_complaint_intent()
    test_faq_intent()
    
    # Test ticket workflow
    ticket_id = test_ticket_creation()
    test_status_check(ticket_id)
    
    print("\n" + "=" * 50)
    print("🎉 Test suite completed!")
    print("\n💡 To test the web interface:")
    print("   1. Make sure Flask is running: python app.py")
    print("   2. Open your browser to: http://localhost:5000")
    print("   3. Try chatting with Prashna!")

if __name__ == "__main__":
    main()