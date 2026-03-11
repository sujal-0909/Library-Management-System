from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from src.models import db
from src.models.member import Member
from src.models.fine import Fine
from src.models.borrowing import Borrowing

fines_bp = Blueprint('fines', __name__)

@fines_bp.route('/', methods=['GET'])
@jwt_required()
def get_fines():
    """Get all fines with optional filtering"""
    try:
        member_id = get_jwt_identity()
        member = Member.query.get(member_id)
        
        if not member:
            return jsonify({'error': 'Member not found'}), 404
        
        # Query parameters for filtering
        unpaid_only = request.args.get('unpaid_only', 'false').lower() == 'true'
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Build query based on user role
        if member.username == 'admin':
            query = Fine.query
        else:
            query = Fine.query.filter_by(member_id=member_id)
        
        if unpaid_only:
            query = query.filter(Fine.is_paid == False)
        
        # Paginate results
        fines = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'fines': [fine.to_dict() for fine in fines.items],
            'total': fines.total,
            'pages': fines.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fines_bp.route('/<int:fine_id>', methods=['GET'])
@jwt_required()
def get_fine(fine_id):
    """Get a specific fine by ID"""
    try:
        member_id = get_jwt_identity()
        member = Member.query.get(member_id)
        
        if not member:
            return jsonify({'error': 'Member not found'}), 404
        
        fine = Fine.query.get(fine_id)
        
        if not fine:
            return jsonify({'error': 'Fine not found'}), 404
        
        # Check access permissions
        if member.username != 'admin' and fine.member_id != member_id:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({'fine': fine.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fines_bp.route('/<int:fine_id>/pay', methods=['POST'])
@jwt_required()
def pay_fine(fine_id):
    """Pay a fine"""
    try:
        member_id = get_jwt_identity()
        member = Member.query.get(member_id)
        
        if not member:
            return jsonify({'error': 'Member not found'}), 404
        
        fine = Fine.query.get(fine_id)
        
        if not fine:
            return jsonify({'error': 'Fine not found'}), 404
        
        # Check access permissions (admin or fine owner)
        if member.username != 'admin' and fine.member_id != member_id:
            return jsonify({'error': 'Access denied'}), 403
        
        if fine.is_paid:
            return jsonify({'error': 'Fine already paid'}), 400
        
        # Pay the fine
        fine.pay_fine()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Fine paid successfully',
            'fine': fine.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@fines_bp.route('/member/<int:member_id>/summary', methods=['GET'])
@jwt_required()
def get_member_fine_summary(member_id):
    """Get fine summary for a specific member"""
    try:
        current_member_id = get_jwt_identity()
        current_member = Member.query.get(current_member_id)
        
        if not current_member:
            return jsonify({'error': 'Current member not found'}), 404
        
        # Check access permissions
        if current_member.username != 'admin' and current_member_id != member_id:
            return jsonify({'error': 'Access denied'}), 403
        
        target_member = Member.query.get(member_id)
        
        if not target_member:
            return jsonify({'error': 'Member not found'}), 404
        
        # Get all fines for the member
        all_fines = Fine.query.filter_by(member_id=member_id).all()
        unpaid_fines = [fine for fine in all_fines if not fine.is_paid]
        paid_fines = [fine for fine in all_fines if fine.is_paid]
        
        # Calculate totals
        total_unpaid = sum(float(fine.fine_amount) for fine in unpaid_fines)
        total_paid = sum(float(fine.fine_amount) for fine in paid_fines)
        total_all_time = total_unpaid + total_paid
        
        return jsonify({
            'member': target_member.to_dict(),
            'fine_summary': {
                'total_unpaid': total_unpaid,
                'total_paid': total_paid,
                'total_all_time': total_all_time,
                'unpaid_count': len(unpaid_fines),
                'paid_count': len(paid_fines),
                'total_count': len(all_fines)
            },
            'unpaid_fines': [fine.to_dict() for fine in unpaid_fines],
            'recent_paid_fines': [fine.to_dict() for fine in paid_fines[-5:]]  # Last 5 paid fines
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fines_bp.route('/create', methods=['POST'])
@jwt_required()
def create_fine():
    """Create a manual fine (admin only)"""
    try:
        member_id = get_jwt_identity()
        member = Member.query.get(member_id)
        
        if not member or member.username != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        required_fields = ['member_id', 'fine_amount', 'fine_reason']
        for field in required_fields:
            if not data or data.get(field) is None:
                return jsonify({'error': f'{field} is required'}), 400
        
        target_member = Member.query.get(data['member_id'])
        if not target_member:
            return jsonify({'error': 'Target member not found'}), 404
        
        # Create fine (without borrowing_id for manual fines)
        fine = Fine(
            borrowing_id=data.get('borrowing_id'),  # Optional for manual fines
            member_id=data['member_id'],
            fine_amount=data['fine_amount'],
            fine_reason=data['fine_reason']
        )
        
        db.session.add(fine)
        db.session.commit()
        
        return jsonify({
            'message': 'Fine created successfully',
            'fine': fine.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@fines_bp.route('/<int:fine_id>', methods=['DELETE'])
@jwt_required()
def delete_fine(fine_id):
    """Delete a fine (admin only)"""
    try:
        member_id = get_jwt_identity()
        member = Member.query.get(member_id)
        
        if not member or member.username != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        fine = Fine.query.get(fine_id)
        
        if not fine:
            return jsonify({'error': 'Fine not found'}), 404
        
        db.session.delete(fine)
        db.session.commit()
        
        return jsonify({'message': 'Fine deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@fines_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_fine_statistics():
    """Get fine statistics (admin only)"""
    try:
        member_id = get_jwt_identity()
        member = Member.query.get(member_id)
        
        if not member or member.username != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get all fines
        all_fines = Fine.query.all()
        unpaid_fines = [fine for fine in all_fines if not fine.is_paid]
        paid_fines = [fine for fine in all_fines if fine.is_paid]
        
        # Calculate statistics
        total_unpaid = sum(float(fine.fine_amount) for fine in unpaid_fines)
        total_paid = sum(float(fine.fine_amount) for fine in paid_fines)
        total_revenue = total_paid
        
        # Get members with unpaid fines
        members_with_unpaid_fines = len(set(fine.member_id for fine in unpaid_fines))
        
        return jsonify({
            'statistics': {
                'total_fines': len(all_fines),
                'unpaid_fines': len(unpaid_fines),
                'paid_fines': len(paid_fines),
                'total_unpaid_amount': total_unpaid,
                'total_paid_amount': total_paid,
                'total_revenue': total_revenue,
                'members_with_unpaid_fines': members_with_unpaid_fines
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

