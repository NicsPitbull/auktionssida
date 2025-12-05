# models/user.py
"""
👤 USER MODEL - Användarmodell för autentisering och sessionshantering
"""
from database import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    """
    Användarmodell som ärver från UserMixin för Flask-Login integration
    """
    __tablename__ = 'users'
    
    # Primärnyckel
    id = db.Column(db.Integer, primary_key=True)
    
    # Användarinformation
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    
    # Roller och status
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Tidsstämplar
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)
    
    # Relationer
    bids = db.relationship('Bid', backref='bidder', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hashar och sparar lösenord"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Kontrollerar lösenord mot hash"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        """Returnerar fullständigt namn"""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<User {self.email}>'


# Startdata för användare
STARTDATA_USERS = [
    {
        'email': 'admin@auction.com',
        'password': 'admin123',
        'first_name': 'Admin',
        'last_name': 'User',
        'is_admin': True
    },
    {
        'email': 'user@example.com',
        'password': 'user123',
        'first_name': 'Test',
        'last_name': 'User',
        'is_admin': False
    }
]

def skapa_start_users():
    """Skapar startanvändare om inga finns"""
    antal_users = User.query.count()
    
    if antal_users == 0:
        print("👤 Lägger till startanvändare...")
        
        for data in STARTDATA_USERS:
            ny_user = User(
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                is_admin=data['is_admin']
            )
            ny_user.set_password(data['password'])
            db.session.add(ny_user)
        
        db.session.commit()
        print(f"✓ Lade till {len(STARTDATA_USERS)} användare")
    else:
        print(f"✓ Tabellen 'users' har redan {antal_users} användare.")
