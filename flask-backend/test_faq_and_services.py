#!/usr/bin/env python3
"""
Test FAQ and Services functionality
"""

import requests
import json
import time

BASE_URL = "http://172.28.0.217:5000"

def test_faq_flow():
    """Test the FAQ functionality"""
    print("❓ Testing FAQ Flow")
    print("=" * 50)
    
    session_id = f"test-faq-{int(time.time())}"
    
    # Step 1: Initiate FAQ
    print("1️⃣ Testing FAQ initiation...")
    response = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "I have questions",
        "session_id": session_id
    })
    
    if response.status_code != 200:
        print(f"❌ Failed to initiate FAQ: {response.status_code}")
        return False
    
    data = response.json()
    bot_message = data['response']['message']
    buttons = data['response'].get('buttons', [])
    
    print("✅ FAQ initiated successfully")
    print(f"   Bot asked: {bot_message}")
    print(f"   Available options: {len(buttons)}")
    
    # Step 2: Test specific FAQ responses
    faq_tests = [
        ("faq_resolution", "Response times & resolution"),
        ("faq_tracking", "How to track my request"),
        ("faq_contact", "Contact options"),
        ("faq_escalation", "Escalation process"),
        ("faq_info", "What info should I provide?")
    ]
    
    for faq_action, faq_name in faq_tests:
        print(f"\n2️⃣ Testing {faq_name}...")
        response = requests.post(f"{BASE_URL}/api/chat", json={
            "message": faq_action,
            "session_id": f"{session_id}-{faq_action}"
        })
        
        if response.status_code == 200:
            data = response.json()
            bot_message = data['response']['message']
            
            if len(bot_message) > 100:  # FAQ responses should be detailed
                print(f"✅ {faq_name} working - {len(bot_message)} characters")
                
                # Check for contact info in contact FAQ
                if faq_action == "faq_contact":
                    if "navadeepmarella@gmail.com" in bot_message and "7075072880" in bot_message:
                        print("   ✅ Contact details included correctly")
                    else:
                        print("   ⚠️  Contact details missing")
            else:
                print(f"❌ {faq_name} response too short: {bot_message}")
        else:
            print(f"❌ {faq_name} failed: {response.status_code}")
    
    return True

def test_services_info():
    """Test the services information"""
    print("\n🌟 Testing Services Information")
    print("=" * 50)
    
    session_id = f"test-services-{int(time.time())}"
    
    # Test services info
    print("1️⃣ Testing services info...")
    response = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "services_info",
        "session_id": session_id
    })
    
    if response.status_code != 200:
        print(f"❌ Failed to get services info: {response.status_code}")
        return False
    
    data = response.json()
    bot_message = data['response']['message']
    
    print("✅ Services info retrieved")
    print(f"   Message length: {len(bot_message)} characters")
    
    # Check for specific content
    required_content = [
        "Troubleshooting device issues",
        "Warranty repairs and replacements",
        "Software setup and updates",
        "Billing or account questions",
        "Shipping, returns, or exchange requests",
        "navadeepmarella@gmail.com",
        "7075072880",
        "Zer0 Support Team"
    ]
    
    missing_content = []
    for content in required_content:
        if content not in bot_message:
            missing_content.append(content)
    
    if not missing_content:
        print("✅ All required content present")
    else:
        print(f"⚠️  Missing content: {missing_content}")
    
    return True

def test_button_actions():
    """Test that buttons send correct actions"""
    print("\n🔘 Testing Button Actions")
    print("=" * 50)
    
    # This would require frontend testing, but we can test the backend responses
    test_actions = [
        ("faq_resolution", "Should show response times"),
        ("faq_contact", "Should show contact info"),
        ("services_info", "Should show services"),
        ("new_complaint", "Should start complaint flow"),
        ("status_check", "Should ask for ticket ID")
    ]
    
    for action, expected in test_actions:
        print(f"Testing {action}...")
        response = requests.post(f"{BASE_URL}/api/chat", json={
            "message": action,
            "session_id": f"test-{action}-{int(time.time())}"
        })
        
        if response.status_code == 200:
            data = response.json()
            bot_message = data['response']['message']
            print(f"✅ {action} - Response: {len(bot_message)} chars")
        else:
            print(f"❌ {action} failed")

def main():
    """Run all tests"""
    print("🚀 FAQ and Services Test Suite")
    print("=" * 60)
    
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
    
    # Run tests
    test_faq_flow()
    test_services_info()
    test_button_actions()
    
    print("\n" + "=" * 60)
    print("🎉 Testing completed!")
    print("\n💡 Now test in your browser:")
    print("   1. Go to: http://172.28.0.217:5000")
    print("   2. Click 'FAQ & Information'")
    print("   3. Try different FAQ topics")
    print("   4. Click 'About Our Services'")
    print("   5. Check for contact details!")

if __name__ == "__main__":
    main()