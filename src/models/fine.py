from datetime import datetime
from . import db

class Fine(db.Model):
    __tablename__ = 'fines'
    
    fine_id = db.Column(db.Integer, primary_key=True)
    borrowing_id = db.Column(db.Integer, db.ForeignKey('borrowings.borrowing_id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('members.member_id'), nullable=False)
    fine_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    fine_reason = db.Column(db.String(100), nullable=False)
    fine_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    is_paid = db.Column(db.Boolean, default=False)
    payment_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, borrowing_id, member_id, fine_amount, fine_reason):
        self.borrowing_id = borrowing_id
        self.member_id = member_id
        self.fine_amount = fine_amount
        self.fine_reason = fine_reason
        self.fine_date = datetime.utcnow().date()
    
    def to_dict(self):
        """Convert fine object to dictionary"""
        return {
            'fine_id': self.fine_id,
            'borrowing_id': self.borrowing_id,
            'member_id': self.member_id,
            'fine_amount': float(self.fine_amount),
            'fine_reason': self.fine_reason,
            'fine_date': self.fine_date.isoformat() if self.fine_date else None,
            'is_paid': self.is_paid,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'member_name': self.member.get_full_name() if self.member else None,
            'book_title': self.borrowing.book.title if self.borrowing and self.borrowing.book else None
        }
    
    def pay_fine(self):
        """Mark the fine as paid"""
        if not self.is_paid:
            self.is_paid = True
            self.payment_date = datetime.utcnow().date()
            return True
        return False
    
    @staticmethod
    def calculate_overdue_fine(days_overdue, fine_per_day=1.00, grace_period_days=0):
        """Calculate fine amount based on days overdue minus grace period"""
        billable_days = max(0, days_overdue - grace_period_days)
        return billable_days * fine_per_day
    
    def __repr__(self):
        return f'<Fine {self.fine_id}: ${self.fine_amount} for Member {self.member_id}>'

