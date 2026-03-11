from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import db
from src.models.member import Member

members_bp = Blueprint('members', __name__)

@members_bp.route('/', methods=['GET'])
@jwt_required()
def get_members():
    """Get all members (admin only)"""
    try:
        # Check if user is admin
        member_id = get_jwt_identity()
        member = Member.query.get(member_id)
        
        if not member or member.username != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Query parameters for filtering
        search = request.args.get('search', '')
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Build query
        query = Member.query
        
        if search:
            query = query.filter(
                (Member.username.contains(search)) |
                (Member.first_name.contains(search)) |
                (Member.last_name.contains(search)) |
                (Member.email.contains(search))
            )
        
        if active_only:
            query = query.filter(Member.is_active == True)
        
        # Paginate results
        members = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'members': [member.to_dict() for member in members.items],
            'total': members.total,
            'pages': members.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@members_bp.route('/<int:member_id>', methods=['GET'])
@jwt_required()
def get_member(member_id):
    """Get a specific member by ID"""
    try:
        # Check if user is admin or requesting their own info
        current_member_id = get_jwt_identity()
        current_member = Member.query.get(current_member_id)
        
        if not current_member:
            return jsonify({'error': 'Current member not found'}), 404
        
        if current_member.username != 'admin' and current_member_id != member_id:
            return jsonify({'error': 'Access denied'}), 403
        
        member = Member.query.get(member_id)
        
        if not member:
            return jsonify({'error': 'Member not found'}), 404
        
        return jsonify({'member': member.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@members_bp.route('/<int:member_id>', methods=['PUT'])
@jwt_required()
def update_member(member_id):
    """Update a member's information (admin only)"""
    try:
        # Check if user is admin
        current_member_id = get_jwt_identity()
        current_member = Member.query.get(current_member_id)
        
        if not current_member or current_member.username != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        member = Member.query.get(member_id)
        
        if not member:
            return jsonify({'error': 'Member not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if data.get('first_name'):
            member.first_name = data['first_name']
        if data.get('last_name'):
            member.last_name = data['last_name']
        if data.get('email'):
            # Check if email is already taken by another member
            existing_member = Member.query.filter_by(email=data['email']).first()
            if existing_member and existing_member.member_id != member_id:
                return jsonify({'error': 'Email already exists'}), 409
            member.email = data['email']
        if data.get('phone'):
            member.phone = data['phone']
        if data.get('address'):
            member.address = data['address']
        if 'is_active' in data:
            member.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Member updated successfully',
            'member': member.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@members_bp.route('/<int:member_id>', methods=['DELETE'])
@jwt_required()
def delete_member(member_id):
    """Delete a member (admin only)"""
    try:
        # Check if user is admin
        current_member_id = get_jwt_identity()
        current_member = Member.query.get(current_member_id)
        
        if not current_member or current_member.username != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        member = Member.query.get(member_id)
        
        if not member:
            return jsonify({'error': 'Member not found'}), 404
        
        # Prevent admin from deleting themselves
        if member_id == current_member_id:
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        # Check if member has active borrowings
        active_borrowings = [b for b in member.borrowings if not b.is_returned]
        if active_borrowings:
            return jsonify({'error': 'Cannot delete member with active borrowings'}), 400
        
        # Check if member has unpaid fines
        unpaid_fines = [f for f in member.fines if not f.is_paid]
        if unpaid_fines:
            return jsonify({'error': 'Cannot delete member with unpaid fines'}), 400
        
        db.session.delete(member)
        db.session.commit()
        
        return jsonify({'message': 'Member deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@members_bp.route('/<int:member_id>/borrowing-history', methods=['GET'])
@jwt_required()
def get_member_borrowing_history(member_id):
    """Get a member's borrowing history"""
    try:
        # Check if user is admin or requesting their own info
        current_member_id = get_jwt_identity()
        current_member = Member.query.get(current_member_id)
        
        if not current_member:
            return jsonify({'error': 'Current member not found'}), 404
        
        if current_member.username != 'admin' and current_member_id != member_id:
            return jsonify({'error': 'Access denied'}), 403
        
        member = Member.query.get(member_id)
        
        if not member:
            return jsonify({'error': 'Member not found'}), 404
        
        # Get borrowing history
        borrowings = [borrowing.to_dict() for borrowing in member.borrowings]
        
        return jsonify({
            'member': member.to_dict(),
            'borrowings': borrowings
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@members_bp.route('/<int:member_id>/fines', methods=['GET'])
@jwt_required()
def get_member_fines(member_id):
    """Get a member's fines"""
    try:
        # Check if user is admin or requesting their own info
        current_member_id = get_jwt_identity()
        current_member = Member.query.get(current_member_id)
        
        if not current_member:
            return jsonify({'error': 'Current member not found'}), 404
        
        if current_member.username != 'admin' and current_member_id != member_id:
            return jsonify({'error': 'Access denied'}), 403
        
        member = Member.query.get(member_id)
        
        if not member:
            return jsonify({'error': 'Member not found'}), 404
        
        # Get fines
        fines = [fine.to_dict() for fine in member.fines]
        
        return jsonify({
            'member': member.to_dict(),
            'fines': fines
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

