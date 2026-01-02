from flask import Blueprint, jsonify, request
from db import (
    create_user,
    authenticate_user,
    verify_session,
    logout_user,
    hash_password
)

# Create blueprint for auth routes
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.json
        
        # Validate required fields
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        
        if not username or not email or not password:
            return jsonify({'error': 'Username, email, and password are required'}), 400
        
        # Validate username length
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters'}), 400
        
        # Validate password length
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Create user
        password_hashed = hash_password(password)
        result = create_user(username, email, password_hashed, full_name)
        
        if result['success']:
            return jsonify({
                'message': 'User registered successfully',
                'user': {
                    'id': result['user_id'],
                    'username': result['username']
                }
            }), 201
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login a user"""
    try:
        data = request.json
        
        # Validate required fields
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Authenticate user
        result = authenticate_user(username, password)
        
        if result['success']:
            return jsonify({
                'message': 'Login successful',
                'session_token': result['session_token'],
                'user': result['user']
            }), 200
        else:
            return jsonify({'error': result['error']}), 401
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@auth_bp.route('/verify', methods=['GET'])
def verify():
    """Verify a session token"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Invalid authorization header'}), 401
        
        session_token = auth_header.replace('Bearer ', '')
        
        # Verify session
        result = verify_session(session_token)
        
        if result['success']:
            return jsonify({
                'valid': True,
                'user': result['user']
            }), 200
        else:
            return jsonify({'valid': False, 'error': result['error']}), 401
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout a user"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Invalid authorization header'}), 401
        
        session_token = auth_header.replace('Bearer ', '')
        
        # Logout user
        result = logout_user(session_token)
        
        if result['success']:
            return jsonify({'message': 'Logout successful'}), 200
        else:
            return jsonify({'error': 'Logout failed'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current user information"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Invalid authorization header'}), 401
        
        session_token = auth_header.replace('Bearer ', '')
        
        # Verify session and get user
        result = verify_session(session_token)
        
        if result['success']:
            return jsonify({'user': result['user']}), 200
        else:
            return jsonify({'error': result['error']}), 401
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500
