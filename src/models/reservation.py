from datetime import datetime
from . import db

class Reservation(db.Model):
    __tablename__ = 'reservations'
    
    reservation_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.member_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)
    reservation_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    status = db.Column(db.Enum('active', 'fulfilled', 'cancelled', name='reservation_status'), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, member_id, book_id):
        self.member_id = member_id
        self.book_id = book_id
        self.reservation_date = datetime.utcnow().date()
    
    def to_dict(self):
        """Convert reservation object to dictionary"""
        return {
            'reservation_id': self.reservation_id,
            'member_id': self.member_id,
            'book_id': self.book_id,
            'reservation_date': self.reservation_date.isoformat() if self.reservation_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'book_title': self.book.title if self.book else None,
            'member_name': self.member.get_full_name() if self.member else None
        }
    
    def fulfill(self):
        """Mark reservation as fulfilled"""
        if self.status == 'active':
            self.status = 'fulfilled'
            return True
        return False
    
    def cancel(self):
        """Cancel the reservation"""
        if self.status == 'active':
            self.status = 'cancelled'
            return True
        return False
    
    def __repr__(self):
        return f'<Reservation {self.reservation_id}: Member {self.member_id} - Book {self.book_id}>'

