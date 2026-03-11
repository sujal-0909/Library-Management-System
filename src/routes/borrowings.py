from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from src.models import db
from src.models.member import Member
from src.models.book import Book
from src.models.borrowing import Borrowing
from src.models.fine import Fine
from src.config import Config

borrowings_bp = Blueprint('borrowings', __name__)

@borrowings_bp.route('/', methods=['GET'])
@jwt_required()
def get_borrowings():
    """Get all borrowings with optional filtering"""
    try:
        member_id = get_jwt_identity()
        member = Member.query.get(member_id)
        
        if not member:
            return jsonify({'error': 'Member not found'}), 404
        
        # Query parameters for filtering
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        overdue_only = request.args.get('overdue_only', 'false').lower() == 'true'
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Build query based on user role
        if member.username == 'admin':
            query = Borrowing.query
        else:
            query = Borrowing.query.filter_by(member_id=member_id)
        
        if active_only:
            query = query.filter(Borrowing.is_returned == False)
        
        if overdue_only:
            query = query.filter(
                Borrowing.is_returned == False,
                Borrowing.due_date < datetime.utcnow().date()
            )
        
        # Paginate results
        borrowings = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'borrowings': [borrowing.to_dict() for borrowing in borrowings.items],
            'total': borrowings.total,
            'pages': borrowings.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@borrowings_bp.route('/<int:borrowing_id>', methods=['GET'])
@jwt_required()
def get_borrowing(borrowing_id):
    """Get a specific borrowing by ID"""
    try:
        member_id = get_jwt_identity()
        member = Member.query.get(member_id)
        
        if not member:
            return jsonify({'error': 'Member not found'}), 404
        
        borrowing = Borrowing.query.get(borrowing_id)
        
        if not borrowing:
            return jsonify({'error': 'Borrowing not found'}), 404
        
        # Check access permissions
        if member.username != 'admin' and borrowing.member_id != member_id:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({'borrowing': borrowing.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@borrowings_bp.route('/borrow', methods=['POST'])
@jwt_required()
def borrow_book():
    """Borrow a book"""
    try:
        member_id = get_jwt_identity()
        member = Member.query.get(member_id)
        
        if not member:
            return jsonify({'error': 'Member not found'}), 404
        
        if not member.is_active:
            return jsonify({'error': 'Account is inactive'}), 403
        
        data = request.get_json()
        
        if not data or not data.get('book_id'):
            return jsonify({'error': 'Book ID is required'}), 400
        
        book_id = data.get('book_id')
        book = Book.query.get(book_id)
        
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        if not book.is_available():
            return jsonify({'error': 'Book is not available'}), 400
        
        # Check if member already has this book borrowed
        existing_borrowing = Borrowing.query.filter_by(
            member_id=member_id,
            book_id=book_id,
            is_returned=False
        ).first()
        
        if existing_borrowing:
            return jsonify({'error': 'You already have this book borrowed'}), 400
        
        # Check if member has unpaid fines
        unpaid_fines = Fine.query.filter_by(member_id=member_id, is_paid=False).all()
        if unpaid_fines:
            total_unpaid = sum(float(fine.fine_amount) for fine in unpaid_fines)
            return jsonify({
                'error': f'Cannot borrow books with unpaid fines. Total unpaid: ${total_unpaid:.2f}'
            }), 400
        
        # Create borrowing record
        borrowing = Borrowing(
            member_id=member_id,
            book_id=book_id,
            borrow_days=Config.MAX_BORROW_DAYS
        )
        
        # Update book availability
        book.borrow_book()
        
        db.session.add(borrowing)
        db.session.commit()
        
        return jsonify({
            'message': 'Book borrowed successfully',
            'borrowing': borrowing.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@borrowings_bp.route('/<int:borrowing_id>/return', methods=['POST'])
@jwt_required()
def return_book(borrowing_id):
    """Return a borrowed book"""
    try:
        member_id = get_jwt_identity()
        member = Member.query.get(member_id)
        
        if not member:
            return jsonify({'error': 'Member not found'}), 404
        
        borrowing = Borrowing.query.get(borrowing_id)
        
        if not borrowing:
            return jsonify({'error': 'Borrowing not found'}), 404
        
        # Check access permissions (admin or book owner)
        if member.username != 'admin' and borrowing.member_id != member_id:
            return jsonify({'error': 'Access denied'}), 403
        
        if borrowing.is_returned:
            return jsonify({'error': 'Book already returned'}), 400
        
        # Calculate fine if overdue
        if borrowing.is_overdue():
            days_overdue = borrowing.days_overdue()
            fine_amount = Fine.calculate_overdue_fine(
                days_overdue, 
                Config.FINE_PER_DAY, 
                Config.GRACE_PERIOD_DAYS
            )
            
            # Create fine record if amount > 0
            if fine_amount > 0:
                fine = Fine(
                    borrowing_id=borrowing_id,
                    member_id=borrowing.member_id,
                    fine_amount=fine_amount,
                    fine_reason=f'Overdue return - {days_overdue} days late'
                )
                db.session.add(fine)
        
        # Return the book
        borrowing.return_book()
        borrowing.book.return_book()
        
        db.session.commit()
        
        response_data = {
            'message': 'Book returned successfully',
            'borrowing': borrowing.to_dict()
        }
        
        if borrowing.is_overdue():
            response_data['fine_applied'] = {
                'amount': float(fine_amount),
                'days_overdue': days_overdue,
                'reason': fine.fine_reason
            }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@borrowings_bp.route('/<int:borrowing_id>/renew', methods=['POST'])
@jwt_required()
def renew_borrowing(borrowing_id):
    """Renew a borrowing"""
    try:
        member_id = get_jwt_identity()
        member = Member.query.get(member_id)
        
        if not member:
            return jsonify({'error': 'Member not found'}), 404
        
        borrowing = Borrowing.query.get(borrowing_id)
        
        if not borrowing:
            return jsonify({'error': 'Borrowing not found'}), 404
        
        # Check access permissions
        if member.username != 'admin' and borrowing.member_id != member_id:
            return jsonify({'error': 'Access denied'}), 403
        
        if borrowing.is_returned:
            return jsonify({'error': 'Cannot renew returned book'}), 400
        
        if not borrowing.can_renew(Config.MAX_RENEWALS):
            if borrowing.renewal_count >= Config.MAX_RENEWALS:
                return jsonify({'error': f'Maximum renewals ({Config.MAX_RENEWALS}) reached'}), 400
            elif borrowing.is_overdue():
                return jsonify({'error': 'Cannot renew overdue book'}), 400
        
        # Check if member has unpaid fines
        unpaid_fines = Fine.query.filter_by(member_id=borrowing.member_id, is_paid=False).all()
        if unpaid_fines:
            total_unpaid = sum(float(fine.fine_amount) for fine in unpaid_fines)
            return jsonify({
                'error': f'Cannot renew with unpaid fines. Total unpaid: ${total_unpaid:.2f}'
            }), 400
        
        # Renew the borrowing
        borrowing.renew(Config.MAX_BORROW_DAYS)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Book renewed successfully',
            'borrowing': borrowing.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@borrowings_bp.route('/overdue', methods=['GET'])
@jwt_required()
def get_overdue_borrowings():
    """Get all overdue borrowings"""
    try:
        member_id = get_jwt_identity()
        member = Member.query.get(member_id)
        
        if not member:
            return jsonify({'error': 'Member not found'}), 404
        
        # Build query based on user role
        if member.username == 'admin':
            query = Borrowing.query
        else:
            query = Borrowing.query.filter_by(member_id=member_id)
        
        # Filter for overdue borrowings
        overdue_borrowings = query.filter(
            Borrowing.is_returned == False,
            Borrowing.due_date < datetime.utcnow().date()
        ).all()
        
        return jsonify({
            'overdue_borrowings': [borrowing.to_dict() for borrowing in overdue_borrowings],
            'count': len(overdue_borrowings)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@borrowings_bp.route('/due-soon', methods=['GET'])
@jwt_required()
def get_due_soon_borrowings():
    """Get borrowings due within the next 3 days"""
    try:
        member_id = get_jwt_identity()
        member = Member.query.get(member_id)
        
        if not member:
            return jsonify({'error': 'Member not found'}), 404
        
        # Calculate date range (next 3 days)
        today = datetime.utcnow().date()
        due_soon_date = today + timedelta(days=3)
        
        # Build query based on user role
        if member.username == 'admin':
            query = Borrowing.query
        else:
            query = Borrowing.query.filter_by(member_id=member_id)
        
        # Filter for borrowings due soon
        due_soon_borrowings = query.filter(
            Borrowing.is_returned == False,
            Borrowing.due_date >= today,
            Borrowing.due_date <= due_soon_date
        ).all()
        
        return jsonify({
            'due_soon_borrowings': [borrowing.to_dict() for borrowing in due_soon_borrowings],
            'count': len(due_soon_borrowings)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

