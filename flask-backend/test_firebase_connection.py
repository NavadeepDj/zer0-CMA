"""
Simple Firebase Connection Test
Tests Firebase integration with mock/local setup
"""

import logging
import os
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_firebase_imports():
    """Test if Firebase modules can be imported"""
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        logger.info("✅ Firebase Admin SDK imported successfully")
        return True
    except ImportError as e:
        logger.error(f"❌ Failed to import Firebase modules: {e}")
        logger.error("Please install firebase-admin: pip install firebase-admin")
        return False

def test_model_imports():
    """Test if our models can be imported"""
    try:
        # Try Firebase models first
        try:
            from models import User, Ticket, Agent, ValidationError
            logger.info("✅ Firebase data models imported successfully")
        except ImportError:
            # Fall back to mock models
            from models_mock import User, Ticket, Agent, ValidationError
            logger.info("✅ Mock data models imported successfully (Firebase not available)")
        return True
    except ImportError as e:
        logger.error(f"❌ Failed to import models: {e}")
        return False

def test_model_validation():
    """Test model validation without Firebase connection"""
    try:
        # Try Firebase models first, fall back to mock
        try:
            from models import User, Ticket, Agent, ValidationError
        except ImportError:
            from models_mock import User, Ticket, Agent, ValidationError
        
        # Test User validation
        user = User()
        user.email = "test@example.com"
        user.full_name = "Test User"
        user.role = "customer"
        user.validate()  # Should not raise exception
        logger.info("✅ User model validation works")
        
        # Test invalid user
        try:
            user.email = "invalid-email"
            user.validate()
            logger.error("❌ User validation should have failed")
            return False
        except ValidationError:
            logger.info("✅ User validation correctly catches invalid data")
        
        # Test Ticket validation
        ticket = Ticket()
        ticket.user_id = "test_user_id"
        ticket.title = "Test ticket title"
        ticket.description = "This is a test ticket description with enough characters"
        ticket.category = "technical"
        ticket.validate()  # Should not raise exception
        logger.info("✅ Ticket model validation works")
        
        # Test Agent validation
        agent = Agent()
        agent.name = "Test Agent"
        agent.email = "agent@example.com"
        agent.title = "Support Specialist"
        agent.skills = ["technical", "billing"]
        agent.validate()  # Should not raise exception
        logger.info("✅ Agent model validation works")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Model validation test failed: {e}")
        return False

def test_ticket_number_generation():
    """Test ticket number generation"""
    try:
        # Try Firebase models first, fall back to mock
        try:
            from models import Ticket
        except ImportError:
            from models_mock import Ticket
        
        ticket = Ticket()
        ticket.generate_ticket_number()
        
        assert ticket.ticket_number is not None
        assert ticket.ticket_number.startswith("ZER0-")
        assert len(ticket.ticket_number) > 10
        
        logger.info(f"✅ Ticket number generation works: {ticket.ticket_number}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ticket number generation test failed: {e}")
        return False

def test_agent_availability_logic():
    """Test agent availability logic"""
    try:
        # Try Firebase models first, fall back to mock
        try:
            from models import Agent
        except ImportError:
            from models_mock import Agent
        
        agent = Agent()
        agent.status = "available"
        agent.max_concurrent_tickets = 3
        agent.current_tickets = []
        
        # Should be available
        assert agent.is_available() == True
        logger.info("✅ Agent availability logic works (available)")
        
        # Add tickets to capacity
        agent.current_tickets = ["ticket1", "ticket2", "ticket3"]
        assert agent.is_available() == False
        logger.info("✅ Agent availability logic works (at capacity)")
        
        # Offline agent should not be available
        agent.current_tickets = []
        agent.status = "offline"
        assert agent.is_available() == False
        logger.info("✅ Agent availability logic works (offline)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Agent availability logic test failed: {e}")
        return False

def test_eta_calculation():
    """Test ETA calculation logic"""
    try:
        # Try Firebase models first, fall back to mock
        try:
            from models import Ticket
        except ImportError:
            from models_mock import Ticket
        
        ticket = Ticket()
        ticket.priority = "urgent"
        ticket.description = "Short description"
        
        eta = ticket.calculate_eta(60)  # 60 minutes base time
        assert eta == 30  # 60 * 0.5 for urgent priority
        logger.info(f"✅ ETA calculation works: {eta} minutes for urgent ticket")
        
        # Test with complex description
        ticket.description = "A" * 600  # Long description
        eta = ticket.calculate_eta(60)
        assert eta == 45  # 30 + 15 for complexity
        logger.info(f"✅ ETA calculation with complexity works: {eta} minutes")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ETA calculation test failed: {e}")
        return False

def run_offline_tests():
    """Run all tests that don't require Firebase connection"""
    logger.info("🧪 Running offline Firebase integration tests...")
    
    tests = [
        ("Firebase imports", test_firebase_imports),
        ("Model imports", test_model_imports),
        ("Model validation", test_model_validation),
        ("Ticket number generation", test_ticket_number_generation),
        ("Agent availability logic", test_agent_availability_logic),
        ("ETA calculation", test_eta_calculation)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Testing {test_name} ---")
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name} PASSED")
            else:
                failed += 1
                logger.error(f"❌ {test_name} FAILED")
        except Exception as e:
            failed += 1
            logger.error(f"❌ {test_name} FAILED with exception: {e}")
    
    logger.info(f"\n{'='*50}")
    logger.info(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        logger.info("🎉 All offline tests passed!")
        logger.info("\nNext steps:")
        logger.info("1. Set up Firebase project and service account")
        logger.info("2. Configure firebase-service-account.json")
        logger.info("3. Run: python init_firebase.py")
        logger.info("4. Run: python test_firebase_integration.py")
        return True
    else:
        logger.error("❌ Some tests failed. Please fix the issues before proceeding.")
        return False

if __name__ == "__main__":
    success = run_offline_tests()
    sys.exit(0 if success else 1)