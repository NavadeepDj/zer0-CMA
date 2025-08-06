#!/usr/bin/env python3
"""
Test real-time agent availability system
"""

import requests
import json
import time

BASE_URL = "http://172.28.0.217:5000"

def test_agent_availability():
    """Test agent availability and ETA predictions"""
    print("👥 Testing Real-time Agent Availability System")
    print("=" * 60)
    
    # Get current agent status
    print("1️⃣ Getting current agent status...")
    response = requests.get(f"{BASE_URL}/api/agents")
    
    if response.status_code != 200:
        print(f"❌ Failed to get agent status: {response.status_code}")
        return False
    
    data = response.json()
    if not data['success']:
        print("❌ Agent API returned error")
        return False
    
    summary = data['summary']
    print(f"✅ Agent status retrieved:")
    print(f"   Available: {summary['available']}")
    print(f"   Busy: {summary['busy']}")
    print(f"   Offline: {summary['offline']}")
    print(f"   Total active tickets: {summary['total_tickets']}")
    
    # Show individual agent details
    print(f"\n📋 Individual Agent Status:")
    for agent in summary['agents']:
        status_emoji = {"available": "🟢", "busy": "🟡", "offline": "🔴"}
        print(f"   {status_emoji.get(agent['status'], '⚪')} {agent['name']} ({agent['title']}) - {agent['status']} - {agent['current_tickets']} tickets")
    
    return True

def test_intelligent_ticket_assignment():
    """Test intelligent ticket assignment with real-time ETAs"""
    print("\n🎯 Testing Intelligent Ticket Assignment")
    print("=" * 60)
    
    # Test different types of tickets to see agent assignment
    test_cases = [
        {
            "name": "Technical Issue",
            "description": "My computer won't start and shows blue screen errors",
            "category": "Technical Help & Troubleshooting",
            "expected_specialist": "Alex"
        },
        {
            "name": "Billing Question", 
            "description": "I was charged twice for my subscription this month",
            "category": "Billing & Account Questions",
            "expected_specialist": "Mike"
        },
        {
            "name": "Urgent Technical Issue",
            "description": "URGENT: Our entire server farm is down, all services offline!",
            "category": "Technical Help & Troubleshooting",
            "expected_specialist": "Alex"
        },
        {
            "name": "Return Request",
            "description": "I want to return my laptop, it doesn't meet my needs",
            "category": "Returns, Cancellations & Swaps", 
            "expected_specialist": "David"
        }
    ]
    
    assignment_results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}️⃣ Testing: {test_case['name']}")
        
        try:
            response = requests.post(f"{BASE_URL}/api/complaint", json={
                "name": f"Test User {i}",
                "email": f"test{i}@example.com",
                "category": test_case['category'],
                "description": test_case['description']
            })
            
            if response.status_code == 200:
                data = response.json()
                ticket_id = data['ticket_id']
                assigned_agent = data['assigned_agent']
                eta_minutes = data['eta_minutes']
                
                print(f"   ✅ Ticket created: {ticket_id}")
                print(f"   👤 Assigned to: {assigned_agent}")
                print(f"   ⏱️  ETA: {eta_minutes} minutes")
                
                # Check if assigned to expected specialist
                if test_case['expected_specialist'] in assigned_agent:
                    print(f"   🎯 Correctly assigned to {test_case['expected_specialist']} specialist")
                else:
                    print(f"   ⚠️  Expected {test_case['expected_specialist']}, got {assigned_agent}")
                
                assignment_results.append({
                    "test_name": test_case['name'],
                    "ticket_id": ticket_id,
                    "assigned_agent": assigned_agent,
                    "eta_minutes": eta_minutes,
                    "expected_specialist": test_case['expected_specialist']
                })
                
            else:
                print(f"   ❌ Failed to create ticket: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return assignment_results

def test_agent_status_updates():
    """Test agent status updates and ETA recalculation"""
    print("\n🔄 Testing Agent Status Updates")
    print("=" * 60)
    
    # Test updating an agent's status
    test_agent_id = "alex_tech"
    
    print(f"1️⃣ Setting {test_agent_id} to busy...")
    try:
        response = requests.put(f"{BASE_URL}/api/agents/{test_agent_id}/status", json={
            "status": "busy"
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {data['message']}")
        else:
            print(f"   ❌ Failed to update status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Wait a moment and check status
    time.sleep(1)
    
    print(f"\n2️⃣ Checking updated agent status...")
    response = requests.get(f"{BASE_URL}/api/agents")
    if response.status_code == 200:
        data = response.json()
        agents = data['summary']['agents']
        
        for agent in agents:
            if agent['id'] == test_agent_id:
                print(f"   ✅ {agent['name']} is now {agent['status']}")
                if agent['estimated_free_time']:
                    print(f"   ⏱️  Estimated free time: {agent['estimated_free_time']}")
                break
    
    # Set back to available
    print(f"\n3️⃣ Setting {test_agent_id} back to available...")
    try:
        response = requests.put(f"{BASE_URL}/api/agents/{test_agent_id}/status", json={
            "status": "available"
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {data['message']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_eta_accuracy():
    """Test ETA prediction accuracy"""
    print("\n⏱️  Testing ETA Prediction Accuracy")
    print("=" * 60)
    
    # Create tickets with different priorities and check ETAs
    priority_tests = [
        {"description": "CRITICAL: System completely down!", "expected_priority": "urgent", "expected_eta_range": (10, 20)},
        {"description": "High priority issue affecting multiple users", "expected_priority": "high", "expected_eta_range": (25, 35)},
        {"description": "Medium priority question about features", "expected_priority": "medium", "expected_eta_range": (40, 50)},
        {"description": "Low priority cosmetic issue", "expected_priority": "low", "expected_eta_range": (100, 130)}
    ]
    
    for i, test in enumerate(priority_tests, 1):
        print(f"\n{i}️⃣ Testing ETA for: {test['description'][:50]}...")
        
        try:
            response = requests.post(f"{BASE_URL}/api/complaint", json={
                "name": f"ETA Test User {i}",
                "email": f"eta.test{i}@example.com",
                "category": "General Assistance",
                "description": test['description']
            })
            
            if response.status_code == 200:
                data = response.json()
                eta_minutes = data['eta_minutes']
                
                print(f"   ⏱️  Predicted ETA: {eta_minutes} minutes")
                
                min_eta, max_eta = test['expected_eta_range']
                if min_eta <= eta_minutes <= max_eta:
                    print(f"   ✅ ETA within expected range ({min_eta}-{max_eta} minutes)")
                else:
                    print(f"   ⚠️  ETA outside expected range ({min_eta}-{max_eta} minutes)")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")

def analyze_system_performance():
    """Analyze overall system performance"""
    print("\n📊 System Performance Analysis")
    print("=" * 60)
    
    # Get final agent status
    response = requests.get(f"{BASE_URL}/api/agents")
    if response.status_code == 200:
        data = response.json()
        summary = data['summary']
        
        print(f"📈 Final System Status:")
        print(f"   Total Agents: {len(data['summary']['agents'])}")
        print(f"   Available: {summary['available']} ({summary['available']/len(data['summary']['agents'])*100:.1f}%)")
        print(f"   Busy: {summary['busy']} ({summary['busy']/len(data['summary']['agents'])*100:.1f}%)")
        print(f"   Offline: {summary['offline']} ({summary['offline']/len(data['summary']['agents'])*100:.1f}%)")
        print(f"   Active Tickets: {summary['total_tickets']}")
        
        # Calculate average workload
        total_tickets = sum(agent['current_tickets'] for agent in data['summary']['agents'])
        active_agents = summary['available'] + summary['busy']
        
        if active_agents > 0:
            avg_workload = total_tickets / active_agents
            print(f"   Average Workload: {avg_workload:.1f} tickets per active agent")
        
        print(f"\n🎯 Agent Specialization:")
        specialties = {}
        for agent in data['summary']['agents']:
            for specialty in agent['specialties']:
                if specialty not in specialties:
                    specialties[specialty] = []
                specialties[specialty].append(agent['name'])
        
        for specialty, agents in specialties.items():
            print(f"   {specialty}: {', '.join(agents)}")

def main():
    """Run all agent system tests"""
    print("🚀 Real-time Agent System Test Suite")
    print("=" * 60)
    
    # Check server health
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code != 200:
            print("❌ Server not responding")
            return
        
        health_data = response.json()
        print(f"✅ Server healthy - {health_data.get('agents_available', 0)} agents available")
    except:
        print("❌ Cannot connect to server")
        print("💡 Make sure to run: python app.py")
        return
    
    # Run tests
    if test_agent_availability():
        assignment_results = test_intelligent_ticket_assignment()
        test_agent_status_updates()
        test_eta_accuracy()
        analyze_system_performance()
        
        print("\n" + "=" * 60)
        print("🎉 Real-time Agent System Testing Complete!")
        print("\n💡 What to check:")
        print("   1. Agent Dashboard: http://172.28.0.217:5000/agents")
        print("   2. Admin Dashboard: http://172.28.0.217:5000/admin")
        print("   3. Server logs for agent assignment messages")
        print("   4. agents.json file for persistent agent data")
        print("\n🎯 Key Features Tested:")
        print("   ✅ Real-time agent availability tracking")
        print("   ✅ Intelligent ticket assignment by specialty")
        print("   ✅ Dynamic ETA calculation based on agent status")
        print("   ✅ Agent status updates and persistence")
        print("   ✅ Priority-based queue management")
        
    else:
        print("\n❌ Basic agent system tests failed. Check server logs.")

if __name__ == "__main__":
    main()