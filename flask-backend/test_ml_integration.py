#!/usr/bin/env python3
"""
Test ML model integration for intelligent ticket processing
"""

import requests
import json
import time

BASE_URL = "http://172.28.0.217:5000"

def test_ml_ticket_creation():
    """Test ticket creation with ML predictions"""
    print("🤖 Testing ML-Powered Ticket Creation")
    print("=" * 60)
    
    # Test cases with different types of issues
    test_cases = [
        {
            "name": "Technical Issue Test",
            "email": "tech.test@example.com",
            "category": "General Assistance",  # User selects general, but AI should detect technical
            "description": "My laptop won't boot up. The screen stays black and I hear beeping sounds. I've tried restarting multiple times but nothing works. Error code 0x0000007B appears sometimes.",
            "expected_ai_category": "Technical Help & Troubleshooting",
            "expected_priority": "high"  # Should be high due to critical system failure
        },
        {
            "name": "Billing Issue Test", 
            "email": "billing.test@example.com",
            "category": "General Assistance",  # User selects general, but AI should detect billing
            "description": "I was charged twice for my monthly subscription. My credit card shows two payments of $29.99 on the same day. Please refund the duplicate charge.",
            "expected_ai_category": "Billing & Account Questions",
            "expected_priority": "medium"
        },
        {
            "name": "Urgent Issue Test",
            "email": "urgent.test@example.com", 
            "category": "General Assistance",
            "description": "URGENT: Our entire office network is down. All employees cannot access email or internet. This is affecting our business operations. Need immediate help!",
            "expected_ai_category": "Technical Help & Troubleshooting",
            "expected_priority": "urgent"  # Should be urgent due to business impact
        },
        {
            "name": "Low Priority Test",
            "email": "low.test@example.com",
            "category": "General Assistance", 
            "description": "I have a question about how to change my profile picture in the app. It's not urgent, just wondering if there's a way to do it.",
            "expected_ai_category": "Product Setup & Software",
            "expected_priority": "low"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}️⃣ Testing: {test_case['name']}")
        print(f"   Description: {test_case['description'][:100]}...")
        
        try:
            response = requests.post(f"{BASE_URL}/api/complaint", json={
                "name": f"Test User {i}",
                "email": test_case['email'],
                "category": test_case['category'],
                "description": test_case['description']
            })
            
            if response.status_code == 200:
                data = response.json()
                ticket_id = data['ticket_id']
                
                # Get the full ticket details
                ticket_response = requests.get(f"{BASE_URL}/api/status/{ticket_id}")
                if ticket_response.status_code == 200:
                    ticket_data = ticket_response.json()
                    ticket = ticket_data['ticket']
                    
                    print(f"   ✅ Ticket created: {ticket_id}")
                    print(f"   🤖 AI Category: {ticket['category']}")
                    print(f"   🎯 AI Priority: {ticket['priority']}")
                    print(f"   👤 AI Agent: {ticket['assigned_agent']}")
                    print(f"   ⏱️  AI ETA: {ticket['eta_minutes']} minutes")
                    print(f"   🔄 AI Processed: {ticket.get('ai_processed', False)}")
                    
                    # Check if AI predictions are reasonable
                    result = {
                        "test_name": test_case['name'],
                        "ticket_id": ticket_id,
                        "ai_category": ticket['category'],
                        "ai_priority": ticket['priority'],
                        "ai_agent": ticket['assigned_agent'],
                        "ai_eta": ticket['eta_minutes'],
                        "ai_processed": ticket.get('ai_processed', False),
                        "user_category": test_case['category'],
                        "expected_category": test_case.get('expected_ai_category'),
                        "expected_priority": test_case.get('expected_priority')
                    }
                    
                    results.append(result)
                    
                    # Validate predictions
                    if ticket.get('ai_processed'):
                        print("   🎉 AI processing successful!")
                    else:
                        print("   ⚠️  AI processing not detected")
                        
                else:
                    print(f"   ❌ Failed to get ticket details: {ticket_response.status_code}")
            else:
                print(f"   ❌ Failed to create ticket: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return results

def test_chatbot_ml_integration():
    """Test ML integration through chatbot flow"""
    print("\n💬 Testing Chatbot ML Integration")
    print("=" * 60)
    
    session_id = f"test-ml-{int(time.time())}"
    
    # Create a ticket through chatbot with technical description
    print("1️⃣ Starting chatbot complaint flow...")
    
    # Start complaint
    response1 = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "I need help with a complaint",
        "session_id": session_id
    })
    
    # Provide name
    response2 = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "ML Test User",
        "session_id": session_id
    })
    
    # Provide email
    response3 = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "ml.test@example.com",
        "session_id": session_id
    })
    
    # Select category (user picks general, but AI should detect technical)
    response4 = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "category_general",
        "session_id": session_id
    })
    
    # Provide technical description
    response5 = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "My server keeps crashing with kernel panic errors. The system logs show memory allocation failures and the database is corrupting. This is a critical production issue affecting all our customers.",
        "session_id": session_id
    })
    
    if response5.status_code == 200:
        data = response5.json()
        bot_message = data['response']['message']
        
        # Extract ticket ID from response
        if "Ticket ID:" in bot_message:
            # Parse ticket ID from message
            lines = bot_message.split('\n')
            ticket_id = None
            for line in lines:
                if "Ticket ID:" in line:
                    ticket_id = line.split("Ticket ID:")[1].strip().split()[0]
                    break
            
            if ticket_id:
                print(f"✅ Chatbot ticket created: {ticket_id}")
                
                # Get ticket details to check AI processing
                ticket_response = requests.get(f"{BASE_URL}/api/status/{ticket_id}")
                if ticket_response.status_code == 200:
                    ticket_data = ticket_response.json()
                    ticket = ticket_data['ticket']
                    
                    print(f"🤖 AI Category: {ticket['category']}")
                    print(f"🎯 AI Priority: {ticket['priority']}")
                    print(f"👤 AI Agent: {ticket['assigned_agent']}")
                    print(f"⏱️  AI ETA: {ticket['eta_minutes']} minutes")
                    
                    if ticket.get('ai_processed'):
                        print("🎉 Chatbot AI processing successful!")
                    else:
                        print("⚠️  Chatbot AI processing not detected")
            else:
                print("❌ Could not extract ticket ID from chatbot response")
        else:
            print("❌ Ticket ID not found in chatbot response")
    else:
        print(f"❌ Chatbot flow failed: {response5.status_code}")

def analyze_results(results):
    """Analyze the ML prediction results"""
    print("\n📊 ML Prediction Analysis")
    print("=" * 60)
    
    if not results:
        print("❌ No results to analyze")
        return
    
    ai_processed_count = sum(1 for r in results if r['ai_processed'])
    print(f"🤖 AI Processing Rate: {ai_processed_count}/{len(results)} ({ai_processed_count/len(results)*100:.1f}%)")
    
    # Analyze category predictions
    print(f"\n📂 Category Predictions:")
    for result in results:
        print(f"   {result['test_name']}:")
        print(f"      User Selected: {result['user_category']}")
        print(f"      AI Predicted: {result['ai_category']}")
        if result.get('expected_category'):
            match = "✅" if result['ai_category'] == result['expected_category'] else "⚠️"
            print(f"      Expected: {result['expected_category']} {match}")
    
    # Analyze priority predictions
    print(f"\n🎯 Priority Predictions:")
    for result in results:
        print(f"   {result['test_name']}: {result['ai_priority']}")
        if result.get('expected_priority'):
            match = "✅" if result['ai_priority'] == result['expected_priority'] else "⚠️"
            print(f"      Expected: {result['expected_priority']} {match}")
    
    # Analyze ETA assignments
    print(f"\n⏱️  ETA Assignments:")
    for result in results:
        print(f"   {result['test_name']}: {result['ai_eta']} minutes (Priority: {result['ai_priority']})")

def main():
    """Run all ML integration tests"""
    print("🚀 ML Model Integration Test Suite")
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
    results = test_ml_ticket_creation()
    test_chatbot_ml_integration()
    analyze_results(results)
    
    print("\n" + "=" * 60)
    print("🎉 ML Integration Testing Complete!")
    print("\n💡 What to check:")
    print("   1. Server logs for AI prediction messages")
    print("   2. Admin dashboard for AI-processed tickets")
    print("   3. Different categories and priorities assigned")
    print("   4. Appropriate agents and ETAs based on AI predictions")
    print("\n🔧 If models aren't loading:")
    print("   1. Check that model files exist in models/ directory")
    print("   2. Install required packages: pip install scikit-learn numpy")
    print("   3. Check server console for model loading errors")

if __name__ == "__main__":
    main()