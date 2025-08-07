"""
Complete Firebase Integration Test
Tests all Firebase functionality including CRUD operations and business logic
"""

import logging
from datetime import datetime
from models import User, Ticket, Agent, ValidationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_complete_firebase_integration():
    """Test complete Firebase integration"""
    
    print("🚀 Starting Complete Firebase Integration Test")
    print("=" * 60)
    
    try:
        # Step 1: Test User Operations
        print("\n📋 Step 1: Testing User Operations")
        
        # Create a test customer
        customer = User()
        customer.email = f"customer_{datetime.now().timestamp()}@example.com"
        customer.full_name = "Test Customer"
        customer.role = "customer"
        customer.phone = "+1234567890"
        customer.validate()
        customer_id = customer.save()
        
        print(f"✅ Created customer: {customer.full_name} (ID: {customer_id})")
        
        # Test user retrieval
        retrieved_customer = User.get_by_id(customer_id)
        assert retrieved_customer is not None
        assert retrieved_customer.email == customer.email
        print(f"✅ Retrieved customer by ID: {retrieved_customer.full_name}")
        
        # Test get by email
        found_by_email = User.get_by_email(customer.email)
        assert found_by_email is not None
        assert found_by_email.id == customer_id
        print(f"✅ Found customer by email: {found_by_email.email}")
        
        # Step 2: Test Agent Operations
        print("\n👥 Step 2: Testing Agent Operations")
        
        # Create a test agent
        agent = Agent()
        agent.name = "Test Agent"
        agent.email = f"agent_{datetime.now().timestamp()}@example.com"
        agent.title = "Test Support Specialist"
        agent.skills = ["technical", "general"]
        agent.status = "available"
        agent.max_concurrent_tickets = 3
        agent.validate()
        agent_id = agent.save()
        
        print(f"✅ Created agent: {agent.name} (ID: {agent_id})")
        
        # Test agent availability
        assert agent.is_available() == True
        print(f"✅ Agent availability check: {agent.is_available()}")
        
        # Test get available agents
        available_agents = Agent.get_available_agents()
        assert len(available_agents) > 0
        print(f"✅ Found {len(available_agents)} available agents")
        
        # Step 3: Test Ticket Operations
        print("\n🎫 Step 3: Testing Ticket Operations")
        
        # Create a test ticket
        ticket = Ticket()
        ticket.user_id = customer_id
        ticket.title = "Firebase Integration Test Issue"
        ticket.description = "This is a comprehensive test ticket to verify Firebase integration is working correctly with all CRUD operations and business logic."
        ticket.category = "technical"
        ticket.priority = "high"
        ticket.source = "web"
        ticket.generate_ticket_number()
        ticket.validate()
        ticket_id = ticket.save()
        
        print(f"✅ Created ticket: {ticket.ticket_number} (ID: {ticket_id})")
        
        # Test ticket retrieval
        retrieved_ticket = Ticket.get_by_id(ticket_id)
        assert retrieved_ticket is not None
        assert retrieved_ticket.title == ticket.title
        print(f"✅ Retrieved ticket by ID: {retrieved_ticket.ticket_number}")
        
        # Test get by ticket number
        found_by_number = Ticket.get_by_ticket_number(ticket.ticket_number)
        assert found_by_number is not None
        assert found_by_number.id == ticket_id
        print(f"✅ Found ticket by number: {found_by_number.ticket_number}")
        
        # Step 4: Test Business Logic Integration
        print("\n🔄 Step 4: Testing Business Logic Integration")
        
        # Test ETA calculation
        eta = ticket.calculate_eta(30)  # 30 minutes base time
        expected_eta = int(30 * 0.7)  # High priority multiplier
        assert eta == expected_eta
        print(f"✅ ETA calculation: {eta} minutes for high priority ticket")
        
        # Test ticket assignment to agent
        ticket.assign_to_agent(agent_id)
        
        # Verify assignment
        updated_ticket = Ticket.get_by_id(ticket_id)
        assert updated_ticket.assigned_agent_id == agent_id
        assert updated_ticket.status == "assigned"
        print(f"✅ Assigned ticket to agent: {agent.name}")
        
        # Test agent ticket assignment
        agent.assign_ticket(ticket_id)
        updated_agent = Agent.get_by_id(agent_id)
        assert ticket_id in updated_agent.current_tickets
        print(f"✅ Agent now has {len(updated_agent.current_tickets)} assigned tickets")
        
        # Test ticket status update
        ticket.update_status("in_progress", "Started working on the issue")
        updated_ticket = Ticket.get_by_id(ticket_id)
        assert updated_ticket.status == "in_progress"
        assert updated_ticket.resolution_notes == "Started working on the issue"
        print(f"✅ Updated ticket status to: {updated_ticket.status}")
        
        # Test ticket completion
        ticket.update_status("resolved", "Issue has been resolved successfully")
        updated_ticket = Ticket.get_by_id(ticket_id)
        assert updated_ticket.status == "resolved"
        assert updated_ticket.resolved_at is not None
        print(f"✅ Resolved ticket at: {updated_ticket.resolved_at}")
        
        # Test agent ticket completion
        agent.complete_ticket(ticket_id, 25)  # 25 minutes resolution time
        updated_agent = Agent.get_by_id(agent_id)
        assert ticket_id not in updated_agent.current_tickets
        assert updated_agent.total_tickets_resolved == 1
        print(f"✅ Agent completed ticket. Total resolved: {updated_agent.total_tickets_resolved}")
        
        # Step 5: Test Query Operations
        print("\n🔍 Step 5: Testing Query Operations")
        
        # Test get tickets by user
        user_tickets = Ticket.get_by_user(customer_id)
        assert len(user_tickets) >= 1
        print(f"✅ Found {len(user_tickets)} tickets for customer")
        
        # Test get tickets by agent
        agent_tickets = Ticket.get_by_agent(agent_id)
        print(f"✅ Found {len(agent_tickets)} tickets assigned to agent")
        
        # Test get users by role
        customers = User.get_by_role("customer")
        assert len(customers) >= 1
        print(f"✅ Found {len(customers)} customers in system")
        
        # Test get agents by skills
        technical_agents = Agent.get_by_skills(["technical"])
        assert len(technical_agents) >= 1
        print(f"✅ Found {len(technical_agents)} agents with technical skills")
        
        # Step 6: Test Validation and Error Handling
        print("\n⚠️ Step 6: Testing Validation and Error Handling")
        
        # Test invalid user validation
        try:
            invalid_user = User()
            invalid_user.email = "invalid-email"
            invalid_user.full_name = "X"  # Too short
            invalid_user.role = "invalid_role"
            invalid_user.validate()
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            print(f"✅ Caught expected validation error: {str(e)[:50]}...")
        
        # Test invalid ticket validation
        try:
            invalid_ticket = Ticket()
            invalid_ticket.user_id = "nonexistent"
            invalid_ticket.title = "X"  # Too short
            invalid_ticket.description = "Short"  # Too short
            invalid_ticket.category = "invalid"
            invalid_ticket.validate()
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            print(f"✅ Caught expected validation error: {str(e)[:50]}...")
        
        # Step 7: Clean Up Test Data
        print("\n🧹 Step 7: Cleaning Up Test Data")
        
        # Delete test records
        ticket.delete()
        print("✅ Deleted test ticket")
        
        agent.delete()
        print("✅ Deleted test agent")
        
        customer.delete()
        print("✅ Deleted test customer")
        
        # Verify deletion
        assert Ticket.get_by_id(ticket_id) is None
        assert Agent.get_by_id(agent_id) is None
        assert User.get_by_id(customer_id) is None
        print("✅ Verified all test data was deleted")
        
        # Final Summary
        print("\n" + "=" * 60)
        print("🎉 COMPLETE FIREBASE INTEGRATION TEST PASSED!")
        print("=" * 60)
        print("\n✅ All Firebase operations working correctly:")
        print("   • User CRUD operations")
        print("   • Agent CRUD operations") 
        print("   • Ticket CRUD operations")
        print("   • Business logic integration")
        print("   • Query operations")
        print("   • Data validation")
        print("   • Error handling")
        print("   • Data cleanup")
        
        print("\n🚀 Firebase integration is ready for production use!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_firebase_integration()
    if not success:
        exit(1)