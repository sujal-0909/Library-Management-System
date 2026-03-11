from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from src.models import db
from src.models.member import Member
from src.models.book import Book
from src.models.borrowing import Borrowing
from src.models.fine import Fine

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    """Get advanced analytics for the library (Admin Only)"""
    try:
        member_id = get_jwt_identity()
        member = Member.query.get(member_id)
        
        if not member or member.username != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        # 1. Members Statistics
        total_members = Member.query.count()
        active_members_count = Member.query.filter_by(is_active=True).count()

        # 2. Book Statistics
        total_books_sum = db.session.query(func.sum(Book.total_copies)).scalar() or 0
        currently_borrowed_sum = db.session.query(
            func.sum(Book.total_copies - Book.available_copies)
        ).scalar() or 0

        # 3. Financial Statistics
        total_unpaid_fines = db.session.query(func.sum(Fine.fine_amount)).filter_by(is_paid=False).scalar() or 0.0

        # 4. Top 5 Most Frequently Borrowed Books
        top_borrowed_query = db.session.query(
            Borrowing.book_id,
            func.count(Borrowing.borrowing_id).label('borrow_count')
        ).group_by(Borrowing.book_id).order_by(db.desc('borrow_count')).limit(5).all()

        top_books_data = []
        for book_id, count in top_borrowed_query:
            book = Book.query.get(book_id)
            if book:
                top_books_data.append({
                    "title": book.title,
                    "author": book.author,
                    "borrow_count": count
                })

        return jsonify({
            "status": "success",
            "data": {
                "members": {
                    "total": total_members,
                    "active": active_members_count
                },
                "inventory": {
                    "total_books": int(total_books_sum),
                    "currently_borrowed": int(currently_borrowed_sum)
                },
                "financials": {
                    "total_unpaid_fines": float(total_unpaid_fines)
                },
                "top_books": top_books_data
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
