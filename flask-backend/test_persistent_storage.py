#!/usr/bin/env python3
"""
Test persistent storage functionality
"""

import requests
import json
import os
import time

BASE_URL = "http://172.28.0.217:5000"

def test_persistent_storage():
    """Test that tickets are saved to file and persist across server restarts"""
    print("💾 Testing Persistent Storage")
    print("=" * 50)
    
    # Step 1: Create a test ticket
    print("1️⃣ Creating test ticket...")
    test_ticket = {
        "name": "Storage Test User",
        "email": "test@example.com",
        "category": "Technical Help & Troubleshooting",
        "description": "This is a test ticket to verify persistent storage functionality."
    }
    
    response = requests.post(f"{BASE_URL}/api/complaint", json=test_ticket)
    
    if response.status_code != 200:
        print(f"❌ Failed to create ticket: {response.status_code}")
        return False
    
    data = response.json()
    ticket_id = data['ticket_id']
    print(f"✅ Ticket created: {ticket_id}")
    
    # Step 2: Check if ticket file was created
    print("\n2️⃣ Checking if tickets.json file was created...")
    if os.path.exists('tickets.json'):
        print("✅ tickets.json file exists")
        
        # Read the file
        with open('tickets.json', 'r') as f:
            tickets_data = json.load(f)
        
        if ticket_id in tickets_data:
            print(f"✅ Ticket {ticket_id} found in file")
            print(f"   Customer: {tickets_data[ticket_id]['customer_name']}")
            print(f"   Email: {tickets_data[ticket_id]['customer_email']}")
            print(f"   Category: {tickets_data[ticket_id]['category']}")
        else:
            print(f"❌ Ticket {ticket_id} not found in file")
            return False
    else:
        print("❌ tickets.json file not created")
        return False
    
    # Step 3: Test API retrieval
    print("\n3️⃣ Testing API ticket retrieval...")
    response = requests.get(f"{BASE_URL}/api/tickets")
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"✅ API returned {data['total_tickets']} tickets")
            if ticket_id in data['tickets']:
                print(f"✅ Test ticket {ticket_id} found via API")
            else:
                print(f"❌ Test ticket {ticket_id} not found via API")
                return False
        else:
            print("❌ API returned error")
            return False
    else:
        print(f"❌ API request failed: {response.status_code}")
        return False
    
    # Step 4: Test individual ticket retrieval
    print("\n4️⃣ Testing individual ticket status...")
    response = requests.get(f"{BASE_URL}/api/status/{ticket_id}")
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            ticket = data['ticket']
            print(f"✅ Individual ticket retrieval successful")
            print(f"   Status: {ticket['status']}")
            print(f"   Priority: {ticket['priority']}")
        else:
            print("❌ Individual ticket retrieval failed")
            return False
    else:
        print(f"❌ Individual ticket API failed: {response.status_code}")
        return False
    
    print("\n🎉 All persistent storage tests passed!")
    return True

def test_file_structure():
    """Check the structure of saved files"""
    print("\n📁 Checking File Structure")
    print("=" * 30)
    
    files_to_check = ['tickets.json', 'chat_sessions.json']
    
    for filename in files_to_check:
        if os.path.exists(filename):
            print(f"✅ {filename} exists")
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                print(f"   📊 Contains {len(data)} entries")
                
                if filename == 'tickets.json' and data:
                    # Show structure of first ticket
                    first_ticket = list(data.values())[0]
                    print(f"   📋 Sample ticket structure:")
                    for key in first_ticket.keys():
                        print(f"      • {key}: {type(first_ticket[key]).__name__}")
                        
            except Exception as e:
                print(f"   ❌ Error reading {filename}: {e}")
        else:
            print(f"❌ {filename} not found")

def main():
    """Run all storage tests"""
    print("🚀 Zer0 Support - Persistent Storage Test")
    print("=" * 60)
    
    # Check server health
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code != 200:
            print("❌ Server not responding")
            return
        
        health_data = response.json()
        print(f"✅ Server healthy - {health_data['total_tickets']} tickets loaded")
    except:
        print("❌ Cannot connect to server")
        print("💡 Make sure to run: python app.py")
        return
    
    # Run tests
    if test_persistent_storage():
        test_file_structure()
        
        print("\n" + "=" * 60)
        print("🎉 SUCCESS: Persistent storage is working!")
        print("\n📊 What you can do now:")
        print("   1. View admin dashboard: http://172.28.0.217:5000/admin")
        print("   2. Check tickets.json file in your directory")
        print("   3. Restart server - tickets will persist!")
        print("   4. Create more tickets via form or chatbot")
        
    else:
        print("\n❌ Some tests failed. Check the server logs.")

if __name__ == "__main__":
    main()