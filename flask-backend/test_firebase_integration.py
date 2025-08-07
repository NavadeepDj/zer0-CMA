"""
Test Firebase Integration and Data Models
Tests Firebase connection, CRUD operations, and data validation
"""

import pytest
import logging
import os
from datetime import datetime, timedelta
from models import User, Ticket, Agent, ValidationError
from firebase_config import initialize_firebase

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestFirebaseIntegration:
    """Test Firebase connection and basic operations"""
    
    @classmethod
    def setup_class(cls):
        """Setup test environment"""
        try:
            # Initialize Firebase
            initialize_firebase()
            logger.info("✅ Firebase initialized for testing")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Firebase: {e}")
            raise
    
    def test_firebase_connection(self):
        """Test Firebase connection"""
        try:
            from firebase_config import get_firebase_db
            db = get_firebase_db()
            
            # Test write operation
            test_ref = db.collection('_test').document('connection_test')
            test_data = {
                'timestamp': datetime.now(),
                'test_message': 'Firebase connection test'
            }
            test_ref.set(test_data)
            
            # Test read operation
            doc = test_ref.get()
            assert doc.exists, "Test document should exist"
            
            data = doc.to_dict()
            assert data['test_message'] == 'Firebase connection test'
            
            # Clean up
            test_ref.delete()
            
            logger.info("✅ Firebase connection test passed")
            
        except Exception as e:
            logger.error(f"❌ Firebase connection test failed: {e}")
            raise

class TestUserModel:
    """Test User model operations"""
    
    def test_user_creation_and_validation(self):
        """Test user creation with validation"""
        # Test valid user
        user = User()
        user.email = "test@example.com"
        user.full_name = "Test User"
        user.phone = "+1234567890"
        user.role = "customer"
        
        # Should not raise exception
        user.validate()
        
        # Test invalid email
        user.email = "invalid-email"
        with pytest.raises(ValidationError):
            user.validate()
        
        # Test invalid role
        user.email = "test@example.com"
        user.role = "invalid_role"
        with pytest.raises(ValidationError):
            user.validate()
        
        logger.info("✅ User validation tests passed")
    
    def test_user_crud_operations(self):
        """Test User CRUD operations"""
        # Create user
        user = User()
        user.email = f"testuser_{datetime.now().timestamp()}@example.com"
        user.full_name = "Test User CRUD"
        user.role = "customer"
        user.validate()
        
        # Save user
        user_id = user.save()
        assert user_id is not None
        assert user.id == user_id
        
        # Read user
        retrieved_user = User.get_by_id(user_id)
        assert retrieved_user is not None
        assert retrieved_user.email == user.email
        assert retrieved_user.full_name == user.full_name
        
        # Update user
        retrieved_user.full_name = "Updated Test User"
        retrieved_user.save()
        
        # Verify update
        updated_user = User.get_by_id(user_id)
        assert updated_user.full_name == "Updated Test User"
        
        # Delete user
        assert updated_user.delete() == True
        
        # Verify deletion
        deleted_user = User.get_by_id(user_id)
        assert deleted_user is None
        
        logger.info("✅ User CRUD operations test passed")
    
    def test_user_get_by_email(self):
        """Test getting user by email"""
        # Create test user
        user = User()
        test_email = f"email_test_{datetime.now().timestamp()}@example.com"
        user.email = test_email
        user.full_name = "Email Test User"
        user.role = "customer"
        user.validate()
        user.save()
        
        # Get by email
        found_user = User.get_by_email(test_email)
        assert found_user is not None
        assert found_user.email == test_email
        
        # Test non-existent email
        not_found = User.get_by_email("nonexistent@example.com")
        assert not_found is None
        
        # Clean up
        found_user.delete()
        
        logger.info("✅ User get by email test passed")
    
    def test_user_permissions(self):
        """Test user role-based permissions"""
        # Test customer permissions
        customer = User()
        customer.role = "customer"
        assert customer.has_permission("view_own_tickets") == True
        assert customer.has_permission("create_tickets") == True
        assert customer.has_permission("view_tickets") == False
        
        # Test agent permissions
        agent = User()
        agent.role = "agent"
        assert agent.has_permission("view_tickets") == True
        assert agent.has_permission("update_tickets") == True
        assert agent.has_permission("admin_access") == False
        
        # Test admin permissions
        admin = User()
        admin.role = "admin"
        assert admin.has_permission("admin_access") == True
        assert admin.has_permission("any_permission") == True
        
        logger.info("✅ User permissions test passed")

class TestTicketModel:
    """Test Ticket model operations"""
    
    def test_ticket_creation_and_validation(self):
        """Test ticket creation with validation"""
        # Create test user first
        user = User()
        user.email = f"ticket_user_{datetime.now().timestamp()}@example.com"
        user.full_name = "Ticket Test User"
        user.role = "customer"
        user.validate()
        user_id = user.save()
        
        # Test valid ticket
        ticket = Ticket()
        ticket.user_id = user_id
        ticket.title = "Test ticket title"
        ticket.description = "This is a test ticket description with enough characters"
        ticket.category = "technical"
        ticket.priority = "medium"
        
        # Should not raise exception
        ticket.validate()
        
        # Test invalid title (too short)
        ticket.title = "Test"
        with pytest.raises(ValidationError):
            ticket.validate()
        
        # Test invalid category
        ticket.title = "Valid title"
        ticket.category = "invalid_category"
        with pytest.raises(ValidationError):
            ticket.validate()
        
        # Clean up
        user.delete()
        
        logger.info("✅ Ticket validation tests passed")
    
    def test_ticket_crud_operations(self):
        """Test Ticket CRUD operations"""
        # Create test user
        user = User()
        user.email = f"ticket_crud_{datetime.now().timestamp()}@example.com"
        user.full_name = "Ticket CRUD User"
        user.role = "customer"
        user.validate()
        user_id = user.save()
        
        # Create ticket
        ticket = Ticket()
        ticket.user_id = user_id
        ticket.title = "CRUD Test Ticket"
        ticket.description = "This is a test ticket for CRUD operations"
        ticket.category = "technical"
        ticket.priority = "high"
        ticket.validate()
        
        # Generate ticket number
        ticket.generate_ticket_number()
        assert ticket.ticket_number is not None
        assert ticket.ticket_number.startswith("ZER0-")
        
        # Save ticket
        ticket_id = ticket.save()
        assert ticket_id is not None
        
        # Read ticket
        retrieved_ticket = Ticket.get_by_id(ticket_id)
        assert retrieved_ticket is not None
        assert retrieved_ticket.title == ticket.title
        assert retrieved_ticket.ticket_number == ticket.ticket_number
        
        # Update ticket status
        retrieved_ticket.update_status("in_progress", "Started working on the issue")
        
        # Verify update
        updated_ticket = Ticket.get_by_id(ticket_id)
        assert updated_ticket.status == "in_progress"
        assert updated_ticket.resolution_notes == "Started working on the issue"
        
        # Test get by ticket number
        found_by_number = Ticket.get_by_ticket_number(ticket.ticket_number)
        assert found_by_number is not None
        assert found_by_number.id == ticket_id
        
        # Clean up
        updated_ticket.delete()
        user.delete()
        
        logger.info("✅ Ticket CRUD operations test passed")
    
    def test_ticket_eta_calculation(self):
        """Test ETA calculation"""
        ticket = Ticket()
        ticket.priority = "urgent"
        ticket.description = "Short description"
        
        eta = ticket.calculate_eta(60)  # 60 minutes base time
        assert eta == 30  # 60 * 0.5 for urgent priority
        
        # Test with complex description
        ticket.description = "A" * 600  # Long description
        eta = ticket.calculate_eta(60)
        assert eta == 45  # 30 + 15 for complexity
        
        logger.info("✅ Ticket ETA calculation test passed")
    
    def test_ticket_overdue_check(self):
        """Test overdue ticket detection"""
        ticket = Ticket()
        ticket.priority = "urgent"
        ticket.created_at = datetime.now() - timedelta(hours=2)  # 2 hours ago
        ticket.status = "registered"
        
        # Should be overdue (urgent SLA is 1 hour)
        assert ticket.is_overdue() == True
        
        # Resolved tickets should not be overdue
        ticket.status = "resolved"
        assert ticket.is_overdue() == False
        
        logger.info("✅ Ticket overdue check test passed")

class TestAgentModel:
    """Test Agent model operations"""
    
    def test_agent_creation_and_validation(self):
        """Test agent creation with validation"""
        # Test valid agent
        agent = Agent()
        agent.name = "Test Agent"
        agent.email = "agent@example.com"
        agent.title = "Support Specialist"
        agent.skills = ["technical", "billing"]
        
        # Should not raise exception
        agent.validate()
        
        # Test invalid email
        agent.email = "invalid-email"
        with pytest.raises(ValidationError):
            agent.validate()
        
        # Test invalid skill
        agent.email = "agent@example.com"
        agent.skills = ["invalid_skill"]
        with pytest.raises(ValidationError):
            agent.validate()
        
        logger.info("✅ Agent validation tests passed")
    
    def test_agent_availability(self):
        """Test agent availability logic"""
        agent = Agent()
        agent.status = "available"
        agent.max_concurrent_tickets = 3
        agent.current_tickets = []
        
        # Should be available
        assert agent.is_available() == True
        
        # Add tickets to capacity
        agent.current_tickets = ["ticket1", "ticket2", "ticket3"]
        assert agent.is_available() == False
        
        # Offline agent should not be available
        agent.current_tickets = []
        agent.status = "offline"
        assert agent.is_available() == False
        
        logger.info("✅ Agent availability test passed")
    
    def test_agent_ticket_assignment(self):
        """Test agent ticket assignment"""
        # Create and save agent
        agent = Agent()
        agent.name = "Assignment Test Agent"
        agent.email = f"assignment_{datetime.now().timestamp()}@example.com"
        agent.title = "Test Agent"
        agent.skills = ["technical"]
        agent.validate()
        agent_id = agent.save()
        
        # Assign ticket
        test_ticket_id = "test_ticket_123"
        agent.assign_ticket(test_ticket_id)
        
        # Verify assignment
        assert test_ticket_id in agent.current_tickets
        assert agent.current_ticket_id == test_ticket_id
        assert agent.current_ticket_start_time is not None
        
        # Complete ticket
        agent.complete_ticket(test_ticket_id, 25)
        
        # Verify completion
        assert test_ticket_id not in agent.current_tickets
        assert agent.current_ticket_id is None
        assert agent.total_tickets_resolved == 1
        
        # Clean up
        agent.delete()
        
        logger.info("✅ Agent ticket assignment test passed")
    
    def test_agent_workload_calculation(self):
        """Test agent workload scoring"""
        agent = Agent()
        agent.max_concurrent_tickets = 4
        agent.current_tickets = ["ticket1", "ticket2"]
        
        score = agent.calculate_workload_score()
        assert score == 0.5  # 2/4 = 0.5
        
        agent.current_tickets = []
        score = agent.calculate_workload_score()
        assert score == 0.0  # 0/4 = 0.0
        
        logger.info("✅ Agent workload calculation test passed")
    
    def test_agent_expertise_matching(self):
        """Test agent expertise matching"""
        agent = Agent()
        agent.skills = ["technical", "billing"]
        
        # Perfect match
        score = agent.get_expertise_match_score("technical")
        assert score == 1.0
        
        # No direct match, but has general
        agent.skills = ["general"]
        score = agent.get_expertise_match_score("warranty")
        assert score == 0.5
        
        # No match at all
        agent.skills = ["billing"]
        score = agent.get_expertise_match_score("warranty")
        assert score == 0.1
        
        logger.info("✅ Agent expertise matching test passed")

def run_all_tests():
    """Run all tests manually"""
    try:
        # Firebase Integration Tests
        firebase_test = TestFirebaseIntegration()
        firebase_test.setup_class()
        firebase_test.test_firebase_connection()
        
        # User Model Tests
        user_test = TestUserModel()
        user_test.test_user_creation_and_validation()
        user_test.test_user_crud_operations()
        user_test.test_user_get_by_email()
        user_test.test_user_permissions()
        
        # Ticket Model Tests
        ticket_test = TestTicketModel()
        ticket_test.test_ticket_creation_and_validation()
        ticket_test.test_ticket_crud_operations()
        ticket_test.test_ticket_eta_calculation()
        ticket_test.test_ticket_overdue_check()
        
        # Agent Model Tests
        agent_test = TestAgentModel()
        agent_test.test_agent_creation_and_validation()
        agent_test.test_agent_availability()
        agent_test.test_agent_ticket_assignment()
        agent_test.test_agent_workload_calculation()
        agent_test.test_agent_expertise_matching()
        
        logger.info("🎉 All tests passed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    # Run tests
    success = run_all_tests()
    if success:
        print("✅ All Firebase integration and model tests passed!")
    else:
        print("❌ Some tests failed. Check the logs for details.")
        exit(1)