from datetime import datetime
from . import db

class Book(db.Model):
    __tablename__ = 'books'
    
    book_id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), unique=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    publisher = db.Column(db.String(100))
    publication_year = db.Column(db.Integer)
    category = db.Column(db.String(50))
    total_copies = db.Column(db.Integer, nullable=False, default=1)
    available_copies = db.Column(db.Integer, nullable=False, default=1)
    shelf_location = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    borrowings = db.relationship('Borrowing', backref='book', lazy=True, cascade='all, delete-orphan')
    reservations = db.relationship('Reservation', backref='book', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, title, author, isbn=None, publisher=None, publication_year=None, 
                 category=None, total_copies=1, shelf_location=None):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.publisher = publisher
        self.publication_year = publication_year
        self.category = category
        self.total_copies = total_copies
        self.available_copies = total_copies
        self.shelf_location = shelf_location
    
    def to_dict(self):
        """Convert book object to dictionary"""
        return {
            'book_id': self.book_id,
            'isbn': self.isbn,
            'title': self.title,
            'author': self.author,
            'publisher': self.publisher,
            'publication_year': self.publication_year,
            'category': self.category,
            'total_copies': self.total_copies,
            'available_copies': self.available_copies,
            'shelf_location': self.shelf_location,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def is_available(self):
        """Check if book is available for borrowing"""
        return self.available_copies > 0
    
    def borrow_book(self):
        """Decrease available copies when book is borrowed"""
        if self.available_copies > 0:
            self.available_copies -= 1
            return True
        return False
    
    def return_book(self):
        """Increase available copies when book is returned"""
        if self.available_copies < self.total_copies:
            self.available_copies += 1
            return True
        return False
    
    def __repr__(self):
        return f'<Book {self.title} by {self.author}>'

