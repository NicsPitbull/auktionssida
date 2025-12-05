from typing import List, Optional
from models.user import User
from database import db
from werkzeug.security import generate_password_hash

class UserRepository:
    """Repository for User model operations using SQLAlchemy ORM"""
    
    def get_all(self) -> List[User]:
        """Get all users"""
        return User.query.order_by(User.created_at.desc()).all()
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return User.query.filter_by(id=user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return User.query.filter_by(email=email).first()
    
    def create(self, user: User) -> User:
        """Create new user"""
        db.session.add(user)
        db.session.commit()
        return user
    
    def update(self, user: User) -> User:
        """Update user"""
        db.session.commit()
        return user
    
    def delete(self, user_id: int) -> bool:
        """Delete user"""
        user = self.get_by_id(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False
    
    def get_admins(self) -> List[User]:
        """Get all admin users"""
        return User.query.filter_by(is_admin=True).order_by(User.created_at.desc()).all()
    
    def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        return User.query.filter_by(email=email).first() is not None
