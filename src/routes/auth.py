from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from src.models import db
from src.models.member import Member

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Member login endpoint"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        # Find member by username
        member = Member.query.filter_by(username=username).first()
        
        if not member or not member.check_password(password):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        if not member.is_active:
            return jsonify({'error': 'Account is inactive'}), 401
        
        # Create access token
        access_token = create_access_token(identity=str(member.member_id))
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'member': member.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """Member registration endpoint"""
    try:
        data = request.get_json()
        
        required_fields = ['username', 'password', 'first_name', 'last_name', 'email']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if username already exists
        if Member.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 409
        
        # Check if email already exists
        if Member.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 409
        
        # Create new member
        member = Member(
            username=data['username'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data.get('phone'),
            address=data.get('address')
        )
        
        db.session.add(member)
        db.session.commit()
        
        return jsonify({
            'message': 'Registration successful',
            'member': member.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current member profile"""
    try:
        member_id = get_jwt_identity()
        member = Member.query.get(member_id)
        
        if not member:
            return jsonify({'error': 'Member not found'}), 404
        
        return jsonify({'member': member.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current member profile"""
    try:
        member_id = get_jwt_identity()
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
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'member': member.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

