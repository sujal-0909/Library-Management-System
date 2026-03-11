from datetime import datetime
from . import db
import bcrypt

class Member(db.Model):
    __tablename__ = 'members'
    
    member_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    address = db.Column(db.Text)
    membership_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    borrowings = db.relationship('Borrowing', backref='member', lazy=True, cascade='all, delete-orphan')
    fines = db.relationship('Fine', backref='member', lazy=True, cascade='all, delete-orphan')
    reservations = db.relationship('Reservation', backref='member', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, username, password, first_name, last_name, email, phone=None, address=None):
        self.username = username
        self.set_password(password)
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.address = address
    
    def set_password(self, password):
        """Hash and set the password"""
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check if the provided password matches the hashed password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
    
    def to_dict(self):
        """Convert member object to dictionary"""
        return {
            'member_id': self.member_id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'membership_date': self.membership_date.isoformat() if self.membership_date else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def get_full_name(self):
        """Get member's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<Member {self.username}>'

