from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import db
from src.models.book import Book
from src.models.member import Member

books_bp = Blueprint('books', __name__)

@books_bp.route('/', methods=['GET'])
@jwt_required()
def get_books():
    """Get all books with optional filtering"""
    try:
        # Query parameters for filtering
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        available_only = request.args.get('available_only', 'false').lower() == 'true'
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Build query
        query = Book.query
        
        if search:
            query = query.filter(
                (Book.title.contains(search)) |
                (Book.author.contains(search)) |
                (Book.isbn.contains(search))
            )
        
        if category:
            query = query.filter(Book.category == category)
        
        if available_only:
            query = query.filter(Book.available_copies > 0)
        
        # Paginate results
        books = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'books': [book.to_dict() for book in books.items],
            'total': books.total,
            'pages': books.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@books_bp.route('/<int:book_id>', methods=['GET'])
@jwt_required()
def get_book(book_id):
    """Get a specific book by ID"""
    try:
        book = Book.query.get(book_id)
        
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        return jsonify({'book': book.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@books_bp.route('/', methods=['POST'])
@jwt_required()
def add_book():
    """Add a new book to the library"""
    try:
        # Check if user is admin (for simplicity, we'll check if username is 'admin')
        member_id = get_jwt_identity()
        member = Member.query.get(member_id)
        
        if not member or member.username != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        required_fields = ['title', 'author']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if ISBN already exists
        if data.get('isbn') and Book.query.filter_by(isbn=data['isbn']).first():
            return jsonify({'error': 'Book with this ISBN already exists'}), 409
        
        # Create new book
        book = Book(
            title=data['title'],
            author=data['author'],
            isbn=data.get('isbn'),
            publisher=data.get('publisher'),
            publication_year=data.get('publication_year'),
            category=data.get('category'),
            total_copies=data.get('total_copies', 1),
            shelf_location=data.get('shelf_location')
        )
        
        db.session.add(book)
        db.session.commit()
        
        return jsonify({
            'message': 'Book added successfully',
            'book': book.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@books_bp.route('/<int:book_id>', methods=['PUT'])
@jwt_required()
def update_book(book_id):
    """Update a book's information"""
    try:
        # Check if user is admin
        member_id = get_jwt_identity()
        member = Member.query.get(member_id)
        
        if not member or member.username != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        book = Book.query.get(book_id)
        
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if data.get('title'):
            book.title = data['title']
        if data.get('author'):
            book.author = data['author']
        if data.get('isbn'):
            # Check if ISBN is already taken by another book
            existing_book = Book.query.filter_by(isbn=data['isbn']).first()
            if existing_book and existing_book.book_id != book_id:
                return jsonify({'error': 'ISBN already exists'}), 409
            book.isbn = data['isbn']
        if data.get('publisher'):
            book.publisher = data['publisher']
        if data.get('publication_year'):
            book.publication_year = data['publication_year']
        if data.get('category'):
            book.category = data['category']
        if data.get('total_copies') is not None:
            # Ensure available copies don't exceed total copies
            new_total = data['total_copies']
            borrowed_copies = book.total_copies - book.available_copies
            if new_total < borrowed_copies:
                return jsonify({'error': 'Cannot reduce total copies below currently borrowed copies'}), 400
            book.available_copies = new_total - borrowed_copies
            book.total_copies = new_total
        if data.get('shelf_location'):
            book.shelf_location = data['shelf_location']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Book updated successfully',
            'book': book.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@books_bp.route('/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    """Delete a book from the library"""
    try:
        # Check if user is admin
        member_id = get_jwt_identity()
        member = Member.query.get(member_id)
        
        if not member or member.username != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        book = Book.query.get(book_id)
        
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        # Check if book has active borrowings
        if book.available_copies < book.total_copies:
            return jsonify({'error': 'Cannot delete book with active borrowings'}), 400
        
        db.session.delete(book)
        db.session.commit()
        
        return jsonify({'message': 'Book deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@books_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Get all book categories"""
    try:
        categories = db.session.query(Book.category).distinct().filter(Book.category.isnot(None)).all()
        category_list = [cat[0] for cat in categories if cat[0]]
        
        return jsonify({'categories': category_list}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

