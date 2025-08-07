"""
Firebase Initialization Script
Sets up Firebase project with initial data and collections
"""

import logging
import sys
from datetime import datetime
from firebase_config import initialize_firebase
from models import User, Agent, Ticket, create_sample_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_firebase_collections():
    """Set up Firebase collections with proper indexes and security rules"""
    try:
        from firebase_config import get_firebase_db
        db = get_firebase_db()
        
        # Create collections with initial documents to establish structure
        collections_to_create = [
            ('users', {
                'email': 'system@zer0.com',
                'full_name': 'System User',
                'role': 'admin',
                'created_at': datetime.now(),
                'is_active': True,
                'notification_preferences': {
                    'email': True,
                    'sms': False,
                    'push': True
                }
            }),
            ('tickets', {
                'ticket_number': 'ZER0-INIT-001',
                'user_id': 'system',
                'title': 'System Initialization Ticket',
                'description': 'Initial ticket to establish collection structure',
                'category': 'general',
                'priority': 'low',
                'status': 'resolved',
                'created_at': datetime.now(),
                'resolved_at': datetime.now()
            }),
            ('agents', {
                'name': 'System Agent',
                'email': 'system.agent@zer0.com',
                'title': 'System Administrator',
                'skills': ['general'],
                'status': 'offline',
                'max_concurrent_tickets': 1,
                'current_tickets': [],
                'avg_resolution_time': 30,
                'total_tickets_resolved': 0,
                'created_at': datetime.now()
            })
        ]
        
        for collection_name, initial_doc in collections_to_create:
            # Check if collection exists
            docs = list(db.collection(collection_name).limit(1).stream())
            
            if not docs:
                # Create initial document
                doc_ref = db.collection(collection_name).add(initial_doc)
                logger.info(f"✅ Created {collection_name} collection with initial document: {doc_ref[1].id}")
            else:
                logger.info(f"✅ Collection {collection_name} already exists")
        
        logger.info("✅ Firebase collections setup completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to setup Firebase collections: {e}")
        return False

def create_default_agents():
    """Create default agents for the system"""
    try:
        default_agents = [
            {
                "name": "Alex Thompson",
                "email": "alex.thompson@zer0.com",
                "title": "Technical Specialist",
                "skills": ["technical", "setup"],
                "max_concurrent_tickets": 3,
                "avg_resolution_time": 25
            },
            {
                "name": "Sarah Wilson",
                "email": "sarah.wilson@zer0.com",
                "title": "Warranty Expert",
                "skills": ["warranty", "returns"],
                "max_concurrent_tickets": 2,
                "avg_resolution_time": 35
            },
            {
                "name": "Mike Johnson",
                "email": "mike.johnson@zer0.com",
                "title": "Billing Specialist",
                "skills": ["billing", "general"],
                "max_concurrent_tickets": 4,
                "avg_resolution_time": 20
            },
            {
                "name": "Lisa Chen",
                "email": "lisa.chen@zer0.com",
                "title": "Setup Specialist",
                "skills": ["setup", "technical"],
                "max_concurrent_tickets": 3,
                "avg_resolution_time": 30
            },
            {
                "name": "David Rodriguez",
                "email": "david.rodriguez@zer0.com",
                "title": "Returns Manager",
                "skills": ["returns", "shipping"],
                "max_concurrent_tickets": 3,
                "avg_resolution_time": 15
            },
            {
                "name": "Emma Taylor",
                "email": "emma.taylor@zer0.com",
                "title": "Logistics Coordinator",
                "skills": ["shipping", "general"],
                "max_concurrent_tickets": 2,
                "avg_resolution_time": 25
            },
            {
                "name": "Anaya Patel",
                "email": "anaya.patel@zer0.com",
                "title": "General Support",
                "skills": ["general"],
                "max_concurrent_tickets": 5,
                "avg_resolution_time": 20
            }
        ]
        
        created_count = 0
        for agent_data in default_agents:
            # Check if agent already exists
            existing_agent = Agent.get_by_email(agent_data["email"])
            if not existing_agent:
                agent = Agent()
                agent.name = agent_data["name"]
                agent.email = agent_data["email"]
                agent.title = agent_data["title"]
                agent.skills = agent_data["skills"]
                agent.max_concurrent_tickets = agent_data["max_concurrent_tickets"]
                agent.avg_resolution_time = agent_data["avg_resolution_time"]
                agent.status = "available"
                agent.current_tickets = []
                agent.total_tickets_resolved = 0
                
                agent.validate()
                agent.save()
                created_count += 1
                logger.info(f"✅ Created agent: {agent.name}")
            else:
                logger.info(f"✅ Agent already exists: {agent_data['name']}")
        
        logger.info(f"✅ Created {created_count} new agents")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create default agents: {e}")
        return False

def create_admin_user():
    """Create default admin user"""
    try:
        admin_email = "admin@zer0.com"
        
        # Check if admin already exists
        existing_admin = User.get_by_email(admin_email)
        if not existing_admin:
            admin = User()
            admin.email = admin_email
            admin.full_name = "System Administrator"
            admin.role = "admin"
            admin.is_active = True
            admin.notification_preferences = {
                'email': True,
                'sms': True,
                'push': True
            }
            
            admin.validate()
            admin.save()
            logger.info(f"✅ Created admin user: {admin.email}")
        else:
            logger.info(f"✅ Admin user already exists: {admin_email}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create admin user: {e}")
        return False

def verify_firebase_setup():
    """Verify Firebase setup by testing basic operations"""
    try:
        logger.info("🔍 Verifying Firebase setup...")
        
        # Test user operations
        users = User.get_all(limit=5)
        logger.info(f"✅ Found {len(users)} users in database")
        
        # Test agent operations
        agents = Agent.get_all(limit=10)
        logger.info(f"✅ Found {len(agents)} agents in database")
        
        # Test available agents
        available_agents = Agent.get_available_agents()
        logger.info(f"✅ Found {len(available_agents)} available agents")
        
        # Test ticket operations (create a test ticket)
        if users:
            test_ticket = Ticket()
            test_ticket.user_id = users[0].id
            test_ticket.title = "Firebase Setup Verification Ticket"
            test_ticket.description = "This is a test ticket to verify Firebase integration is working correctly"
            test_ticket.category = "technical"
            test_ticket.priority = "low"
            test_ticket.generate_ticket_number()
            test_ticket.validate()
            
            ticket_id = test_ticket.save()
            logger.info(f"✅ Created test ticket: {test_ticket.ticket_number}")
            
            # Clean up test ticket
            test_ticket.delete()
            logger.info(f"✅ Cleaned up test ticket")
        
        logger.info("🎉 Firebase setup verification completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Firebase setup verification failed: {e}")
        return False

def main():
    """Main initialization function"""
    logger.info("🚀 Starting Firebase initialization...")
    
    try:
        # Step 1: Initialize Firebase
        logger.info("Step 1: Initializing Firebase...")
        initialize_firebase()
        logger.info("✅ Firebase initialized successfully")
        
        # Step 2: Setup collections
        logger.info("Step 2: Setting up Firebase collections...")
        if not setup_firebase_collections():
            raise Exception("Failed to setup Firebase collections")
        
        # Step 3: Create admin user
        logger.info("Step 3: Creating admin user...")
        if not create_admin_user():
            raise Exception("Failed to create admin user")
        
        # Step 4: Create default agents
        logger.info("Step 4: Creating default agents...")
        if not create_default_agents():
            raise Exception("Failed to create default agents")
        
        # Step 5: Verify setup
        logger.info("Step 5: Verifying Firebase setup...")
        if not verify_firebase_setup():
            raise Exception("Firebase setup verification failed")
        
        logger.info("🎉 Firebase initialization completed successfully!")
        logger.info("\n" + "="*50)
        logger.info("Firebase is ready for use!")
        logger.info("You can now:")
        logger.info("1. Run the Flask application")
        logger.info("2. Create tickets and assign them to agents")
        logger.info("3. Test the complaint management system")
        logger.info("="*50)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Firebase initialization failed: {e}")
        logger.error("\nPlease check:")
        logger.error("1. Firebase service account credentials are properly configured")
        logger.error("2. Firebase project exists and is accessible")
        logger.error("3. Firestore database is enabled in your Firebase project")
        logger.error("4. Network connectivity to Firebase services")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)