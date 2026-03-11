from datetime import datetime, timedelta
from . import db

class Borrowing(db.Model):
    __tablename__ = 'borrowings'
    
    borrowing_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.member_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)
    borrow_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    due_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date)
    is_returned = db.Column(db.Boolean, default=False)
    renewal_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    fines = db.relationship('Fine', backref='borrowing', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, member_id, book_id, borrow_days=14):
        self.member_id = member_id
        self.book_id = book_id
        self.borrow_date = datetime.utcnow().date()
        self.due_date = self.borrow_date + timedelta(days=borrow_days)
    
    def to_dict(self):
        """Convert borrowing object to dictionary"""
        return {
            'borrowing_id': self.borrowing_id,
            'member_id': self.member_id,
            'book_id': self.book_id,
            'borrow_date': self.borrow_date.isoformat() if self.borrow_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'is_returned': self.is_returned,
            'renewal_count': self.renewal_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'book_title': self.book.title if self.book else None,
            'member_name': self.member.get_full_name() if self.member else None
        }
    
    def is_overdue(self):
        """Check if the borrowing is overdue"""
        if self.is_returned:
            return False
        return datetime.utcnow().date() > self.due_date
    
    def days_overdue(self):
        """Calculate number of days overdue"""
        if not self.is_overdue():
            return 0
        return (datetime.utcnow().date() - self.due_date).days
    
    def can_renew(self, max_renewals=2):
        """Check if the borrowing can be renewed"""
        return not self.is_returned and self.renewal_count < max_renewals and not self.is_overdue()
    
    def renew(self, renewal_days=14):
        """Renew the borrowing"""
        if self.can_renew():
            self.due_date = self.due_date + timedelta(days=renewal_days)
            self.renewal_count += 1
            return True
        return False
    
    def return_book(self):
        """Mark the book as returned"""
        if not self.is_returned:
            self.is_returned = True
            self.return_date = datetime.utcnow().date()
            return True
        return False
    
    def __repr__(self):
        return f'<Borrowing {self.borrowing_id}: Member {self.member_id} - Book {self.book_id}>'

