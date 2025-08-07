"""
Data Models for Complaint Management System
Implements User, Ticket, and Agent models with Firebase Firestore integration
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid
import re
import logging
from firebase_admin import firestore
from firebase_config import get_firebase_db

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for data validation errors"""
    pass

class BaseModel:
    """Base model class with common Firebase operations"""
    
    def __init__(self):
        self.db = get_firebase_db()
        self.collection_name = None  # To be set by subclasses
        self.id = None
        self.created_at = None
        self.updated_at = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for Firebase storage"""
        data = {}
        for key, value in self.__dict__.items():
            if key != 'db' and not key.startswith('_'):
                if isinstance(value, datetime):
                    data[key] = value
                else:
                    data[key] = value
        return data
    
    def from_dict(self, data: Dict[str, Any], doc_id: str = None):
        """Load model from dictionary (Firebase document)"""
        if doc_id:
            self.id = doc_id
        
        for key, value in data.items():
            if hasattr(self, key) and key != 'id':  # Don't overwrite ID from data
                setattr(self, key, value)
        
        return self
    
    def save(self) -> str:
        """Save model to Firebase"""
        if not self.collection_name:
            raise ValueError("Collection name not set")
        
        data = self.to_dict()
        data['updated_at'] = datetime.now()
        
        if not self.id:
            # Create new document
            data['created_at'] = datetime.now()
            doc_ref = self.db.collection(self.collection_name).add(data)
            self.id = doc_ref[1].id
            logger.info(f"✅ Created new {self.__class__.__name__} with ID: {self.id}")
        else:
            # Update existing document
            self.db.collection(self.collection_name).document(self.id).set(data)
            logger.info(f"✅ Updated {self.__class__.__name__} with ID: {self.id}")
        
        return self.id
    
    def delete(self) -> bool:
        """Delete model from Firebase"""
        if not self.id:
            return False
        
        try:
            self.db.collection(self.collection_name).document(self.id).delete()
            logger.info(f"✅ Deleted {self.__class__.__name__} with ID: {self.id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete {self.__class__.__name__}: {e}")
            return False
    
    @classmethod
    def get_by_id(cls, doc_id: str):
        """Get model by document ID"""
        instance = cls()
        try:
            doc = instance.db.collection(instance.collection_name).document(doc_id).get()
            if doc.exists:
                return instance.from_dict(doc.to_dict(), doc.id)
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get {cls.__name__} by ID {doc_id}: {e}")
            return None
    
    @classmethod
    def get_all(cls, limit: int = None) -> List:
        """Get all documents from collection"""
        instance = cls()
        try:
            query = instance.db.collection(instance.collection_name)
            if limit:
                query = query.limit(limit)
            
            docs = query.stream()
            results = []
            for doc in docs:
                model_instance = cls()
                results.append(model_instance.from_dict(doc.to_dict(), doc.id))
            
            return results
        except Exception as e:
            logger.error(f"❌ Failed to get all {cls.__name__}: {e}")
            return []

class User(BaseModel):
    """User model with role-based access control"""
    
    def __init__(self):
        super().__init__()
        self.collection_name = 'users'
        
        # User fields
        self.email = None
        self.full_name = None
        self.phone = None
        self.role = 'customer'  # customer, agent, admin
        self.is_active = True
        self.last_login = None
        
        # Preferences
        self.notification_preferences = {
            'email': True,
            'sms': False,
            'push': True
        }
        
        # Role-specific fields
        self.agent_skills = []  # For agents
        self.admin_permissions = []  # For admins
    
    def validate(self):
        """Validate user data"""
        errors = []
        
        # Required fields
        if not self.email:
            errors.append("Email is required")
        elif not self._is_valid_email(self.email):
            errors.append("Invalid email format")
        
        if not self.full_name or len(self.full_name.strip()) < 2:
            errors.append("Full name must be at least 2 characters")
        
        # Role validation
        valid_roles = ['customer', 'agent', 'admin']
        if self.role not in valid_roles:
            errors.append(f"Role must be one of: {', '.join(valid_roles)}")
        
        # Phone validation (optional)
        if self.phone and not self._is_valid_phone(self.phone):
            errors.append("Invalid phone number format")
        
        if errors:
            raise ValidationError("; ".join(errors))
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _is_valid_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        # Check if it's a valid length (10-15 digits)
        return 10 <= len(digits_only) <= 15
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        if self.role == 'admin':
            return True  # Admins have all permissions
        
        if self.role == 'agent':
            agent_permissions = ['view_tickets', 'update_tickets', 'communicate_customers']
            return permission in agent_permissions
        
        if self.role == 'customer':
            customer_permissions = ['view_own_tickets', 'create_tickets']
            return permission in customer_permissions
        
        return False
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.now()
        return self.save()
    
    @classmethod
    def get_by_email(cls, email: str):
        """Get user by email address"""
        instance = cls()
        try:
            query = instance.db.collection(instance.collection_name).where('email', '==', email).limit(1)
            docs = list(query.stream())
            
            if docs:
                doc = docs[0]
                user_instance = cls()
                return user_instance.from_dict(doc.to_dict(), doc.id)
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get user by email {email}: {e}")
            return None
    
    @classmethod
    def get_by_role(cls, role: str) -> List:
        """Get all users by role"""
        instance = cls()
        try:
            query = instance.db.collection(instance.collection_name).where('role', '==', role)
            docs = query.stream()
            
            results = []
            for doc in docs:
                user_instance = cls()
                results.append(user_instance.from_dict(doc.to_dict(), doc.id))
            
            return results
        except Exception as e:
            logger.error(f"❌ Failed to get users by role {role}: {e}")
            return []

class Ticket(BaseModel):
    """Ticket model for complaint management"""
    
    def __init__(self):
        super().__init__()
        self.collection_name = 'tickets'
        
        # Ticket fields
        self.ticket_number = None
        self.user_id = None
        self.title = None
        self.description = None
        self.category = None
        self.priority = 'medium'  # urgent, high, medium, low
        self.status = 'registered'  # registered, assigned, in_progress, resolved, closed
        self.assigned_agent_id = None
        self.resolved_at = None
        self.eta_minutes = None
        
        # Additional fields
        self.tags = []
        self.attachments = []
        self.resolution_notes = None
        self.customer_satisfaction = None  # 1-5 rating
        
        # Tracking fields
        self.source = 'web'  # web, jotform, email, phone
        self.escalation_level = 0
        self.sla_breach = False
    
    def validate(self):
        """Validate ticket data"""
        errors = []
        
        # Required fields
        if not self.user_id:
            errors.append("User ID is required")
        
        if not self.title or len(self.title.strip()) < 5:
            errors.append("Title must be at least 5 characters")
        
        if not self.description or len(self.description.strip()) < 10:
            errors.append("Description must be at least 10 characters")
        
        # Category validation
        valid_categories = [
            'technical', 'billing', 'warranty', 'setup', 
            'returns', 'shipping', 'general'
        ]
        if self.category and self.category not in valid_categories:
            errors.append(f"Category must be one of: {', '.join(valid_categories)}")
        
        # Priority validation
        valid_priorities = ['urgent', 'high', 'medium', 'low']
        if self.priority not in valid_priorities:
            errors.append(f"Priority must be one of: {', '.join(valid_priorities)}")
        
        # Status validation
        valid_statuses = ['registered', 'assigned', 'in_progress', 'resolved', 'closed']
        if self.status not in valid_statuses:
            errors.append(f"Status must be one of: {', '.join(valid_statuses)}")
        
        if errors:
            raise ValidationError("; ".join(errors))
    
    def generate_ticket_number(self):
        """Generate unique ticket number"""
        if not self.ticket_number:
            timestamp = datetime.now().strftime("%Y%m%d")
            random_suffix = str(uuid.uuid4())[:8].upper()
            self.ticket_number = f"ZER0-{timestamp}-{random_suffix}"
    
    def assign_to_agent(self, agent_id: str):
        """Assign ticket to an agent"""
        self.assigned_agent_id = agent_id
        self.status = 'assigned'
        self.updated_at = datetime.now()
        return self.save()
    
    def update_status(self, new_status: str, notes: str = None):
        """Update ticket status"""
        valid_statuses = ['registered', 'assigned', 'in_progress', 'resolved', 'closed']
        if new_status not in valid_statuses:
            raise ValidationError(f"Invalid status: {new_status}")
        
        old_status = self.status
        self.status = new_status
        
        if new_status == 'resolved':
            self.resolved_at = datetime.now()
        
        if notes:
            self.resolution_notes = notes
        
        self.save()
        logger.info(f"✅ Ticket {self.ticket_number} status changed from {old_status} to {new_status}")
    
    def calculate_eta(self, agent_avg_resolution_time: int = 30) -> int:
        """Calculate estimated time to resolution"""
        base_time = agent_avg_resolution_time
        
        # Priority multipliers
        priority_multipliers = {
            'urgent': 0.5,
            'high': 0.7,
            'medium': 1.0,
            'low': 1.5
        }
        
        multiplier = priority_multipliers.get(self.priority, 1.0)
        eta = int(base_time * multiplier)
        
        # Add complexity factor based on description length
        if len(self.description) > 500:
            eta += 15  # Complex issue
        
        self.eta_minutes = max(eta, 5)  # Minimum 5 minutes
        return self.eta_minutes
    
    def add_tag(self, tag: str):
        """Add tag to ticket"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.save()
    
    def is_overdue(self) -> bool:
        """Check if ticket is overdue based on SLA"""
        if self.status in ['resolved', 'closed']:
            return False
        
        sla_hours = {
            'urgent': 1,
            'high': 4,
            'medium': 24,
            'low': 72
        }
        
        max_hours = sla_hours.get(self.priority, 24)
        deadline = self.created_at + timedelta(hours=max_hours)
        
        return datetime.now() > deadline
    
    @classmethod
    def get_by_user(cls, user_id: str) -> List:
        """Get all tickets for a user"""
        instance = cls()
        try:
            query = instance.db.collection(instance.collection_name).where('user_id', '==', user_id)
            docs = query.stream()
            
            results = []
            for doc in docs:
                ticket_instance = cls()
                results.append(ticket_instance.from_dict(doc.to_dict(), doc.id))
            
            return results
        except Exception as e:
            logger.error(f"❌ Failed to get tickets for user {user_id}: {e}")
            return []
    
    @classmethod
    def get_by_agent(cls, agent_id: str) -> List:
        """Get all tickets assigned to an agent"""
        instance = cls()
        try:
            query = instance.db.collection(instance.collection_name).where('assigned_agent_id', '==', agent_id)
            docs = query.stream()
            
            results = []
            for doc in docs:
                ticket_instance = cls()
                results.append(ticket_instance.from_dict(doc.to_dict(), doc.id))
            
            return results
        except Exception as e:
            logger.error(f"❌ Failed to get tickets for agent {agent_id}: {e}")
            return []
    
    @classmethod
    def get_by_ticket_number(cls, ticket_number: str):
        """Get ticket by ticket number"""
        instance = cls()
        try:
            query = instance.db.collection(instance.collection_name).where('ticket_number', '==', ticket_number).limit(1)
            docs = list(query.stream())
            
            if docs:
                doc = docs[0]
                ticket_instance = cls()
                return ticket_instance.from_dict(doc.to_dict(), doc.id)
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get ticket by number {ticket_number}: {e}")
            return None

class Agent(BaseModel):
    """Agent model for support staff"""
    
    def __init__(self):
        super().__init__()
        self.collection_name = 'agents'
        
        # Agent fields
        self.user_id = None  # Reference to User document
        self.name = None
        self.email = None
        self.title = None
        self.skills = []  # List of specialties
        self.status = 'available'  # available, busy, offline
        
        # Workload management
        self.current_ticket_id = None
        self.current_ticket_start_time = None
        self.max_concurrent_tickets = 3
        self.current_tickets = []
        
        # Performance metrics
        self.avg_resolution_time = 30  # minutes
        self.total_tickets_resolved = 0
        self.customer_satisfaction_avg = 0.0
        
        # Schedule
        self.work_schedule = {
            'monday': {'start': '09:00', 'end': '17:00'},
            'tuesday': {'start': '09:00', 'end': '17:00'},
            'wednesday': {'start': '09:00', 'end': '17:00'},
            'thursday': {'start': '09:00', 'end': '17:00'},
            'friday': {'start': '09:00', 'end': '17:00'},
            'saturday': {'start': '10:00', 'end': '14:00'},
            'sunday': {'start': 'off', 'end': 'off'}
        }
        
        # Real-time fields
        self.last_activity = None
        self.estimated_available_at = None
    
    def validate(self):
        """Validate agent data"""
        errors = []
        
        # Required fields
        if not self.name or len(self.name.strip()) < 2:
            errors.append("Name must be at least 2 characters")
        
        if not self.email:
            errors.append("Email is required")
        elif not self._is_valid_email(self.email):
            errors.append("Invalid email format")
        
        # Status validation
        valid_statuses = ['available', 'busy', 'offline']
        if self.status not in valid_statuses:
            errors.append(f"Status must be one of: {', '.join(valid_statuses)}")
        
        # Skills validation
        valid_skills = [
            'technical', 'billing', 'warranty', 'setup', 
            'returns', 'shipping', 'general'
        ]
        for skill in self.skills:
            if skill not in valid_skills:
                errors.append(f"Invalid skill: {skill}")
        
        if errors:
            raise ValidationError("; ".join(errors))
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def is_available(self) -> bool:
        """Check if agent is available for new tickets"""
        if self.status != 'available':
            return False
        
        return len(self.current_tickets) < self.max_concurrent_tickets
    
    def assign_ticket(self, ticket_id: str):
        """Assign a ticket to this agent"""
        if not self.is_available():
            raise ValidationError("Agent is not available for new tickets")
        
        if ticket_id not in self.current_tickets:
            self.current_tickets.append(ticket_id)
        
        # Set as current ticket if it's the first one
        if not self.current_ticket_id:
            self.current_ticket_id = ticket_id
            self.current_ticket_start_time = datetime.now()
        
        # Update status if at capacity
        if len(self.current_tickets) >= self.max_concurrent_tickets:
            self.status = 'busy'
        
        # Estimate when agent will be available
        self.estimated_available_at = datetime.now() + timedelta(minutes=self.avg_resolution_time)
        self.last_activity = datetime.now()
        
        self.save()
        logger.info(f"✅ Assigned ticket {ticket_id} to agent {self.name}")
    
    def complete_ticket(self, ticket_id: str, resolution_time_minutes: int = None):
        """Mark a ticket as completed by this agent"""
        if ticket_id in self.current_tickets:
            self.current_tickets.remove(ticket_id)
        
        # Update current ticket if this was the active one
        if self.current_ticket_id == ticket_id:
            self.current_ticket_id = None
            self.current_ticket_start_time = None
            
            # Set next ticket as current if available
            if self.current_tickets:
                self.current_ticket_id = self.current_tickets[0]
                self.current_ticket_start_time = datetime.now()
        
        # Update performance metrics
        self.total_tickets_resolved += 1
        
        if resolution_time_minutes:
            # Update average resolution time (weighted average)
            total_time = self.avg_resolution_time * (self.total_tickets_resolved - 1) + resolution_time_minutes
            self.avg_resolution_time = total_time / self.total_tickets_resolved
        
        # Update availability status
        if len(self.current_tickets) < self.max_concurrent_tickets:
            self.status = 'available'
            self.estimated_available_at = None
        
        self.last_activity = datetime.now()
        self.save()
        logger.info(f"✅ Agent {self.name} completed ticket {ticket_id}")
    
    def update_status(self, new_status: str):
        """Update agent status"""
        valid_statuses = ['available', 'busy', 'offline']
        if new_status not in valid_statuses:
            raise ValidationError(f"Invalid status: {new_status}")
        
        old_status = self.status
        self.status = new_status
        self.last_activity = datetime.now()
        
        if new_status == 'offline':
            # Estimate when agent will be back (default 2 hours)
            self.estimated_available_at = datetime.now() + timedelta(hours=2)
        elif new_status == 'available':
            self.estimated_available_at = None
        
        self.save()
        logger.info(f"✅ Agent {self.name} status changed from {old_status} to {new_status}")
    
    def calculate_workload_score(self) -> float:
        """Calculate agent workload score (0.0 = free, 1.0 = at capacity)"""
        return len(self.current_tickets) / self.max_concurrent_tickets
    
    def get_expertise_match_score(self, ticket_category: str) -> float:
        """Get expertise match score for a ticket category"""
        if ticket_category in self.skills:
            return 1.0
        elif 'general' in self.skills:
            return 0.5
        else:
            return 0.1
    
    @classmethod
    def get_available_agents(cls) -> List:
        """Get all available agents"""
        instance = cls()
        try:
            query = instance.db.collection(instance.collection_name).where('status', '==', 'available')
            docs = query.stream()
            
            results = []
            for doc in docs:
                agent_instance = cls()
                agent = agent_instance.from_dict(doc.to_dict(), doc.id)
                if agent.is_available():  # Double-check availability
                    results.append(agent)
            
            return results
        except Exception as e:
            logger.error(f"❌ Failed to get available agents: {e}")
            return []
    
    @classmethod
    def get_by_email(cls, email: str):
        """Get agent by email address"""
        instance = cls()
        try:
            query = instance.db.collection(instance.collection_name).where('email', '==', email).limit(1)
            docs = list(query.stream())
            
            if docs:
                doc = docs[0]
                return instance.from_dict(doc.to_dict(), doc.id)
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get agent by email {email}: {e}")
            return None
    
    @classmethod
    def get_by_skills(cls, skills: List[str]) -> List:
        """Get agents by skills"""
        instance = cls()
        try:
            query = instance.db.collection(instance.collection_name).where('skills', 'array_contains_any', skills)
            docs = query.stream()
            
            results = []
            for doc in docs:
                agent_instance = cls()
                results.append(agent_instance.from_dict(doc.to_dict(), doc.id))
            
            return results
        except Exception as e:
            logger.error(f"❌ Failed to get agents by skills {skills}: {e}")
            return []

# Utility functions for model operations
def create_sample_data():
    """Create sample data for testing"""
    try:
        # Create sample users
        admin_user = User()
        admin_user.email = "admin@zer0.com"
        admin_user.full_name = "System Administrator"
        admin_user.role = "admin"
        admin_user.validate()
        admin_user.save()
        
        # Create sample agents
        agent_data = [
            {
                "name": "Alex Thompson",
                "email": "alex@zer0.com",
                "title": "Technical Specialist",
                "skills": ["technical", "setup"]
            },
            {
                "name": "Sarah Wilson",
                "email": "sarah@zer0.com", 
                "title": "Warranty Expert",
                "skills": ["warranty", "returns"]
            },
            {
                "name": "Mike Johnson",
                "email": "mike@zer0.com",
                "title": "Billing Specialist", 
                "skills": ["billing", "general"]
            }
        ]
        
        for agent_info in agent_data:
            agent = Agent()
            agent.name = agent_info["name"]
            agent.email = agent_info["email"]
            agent.title = agent_info["title"]
            agent.skills = agent_info["skills"]
            agent.validate()
            agent.save()
        
        logger.info("✅ Sample data created successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to create sample data: {e}")

if __name__ == "__main__":
    # Test the models
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Test Firebase connection
        from firebase_config import initialize_firebase
        initialize_firebase()
        
        # Create sample data
        create_sample_data()
        
        # Test model operations
        users = User.get_all()
        print(f"Total users: {len(users)}")
        
        agents = Agent.get_all()
        print(f"Total agents: {len(agents)}")
        
    except Exception as e:
        print(f"Error: {e}")