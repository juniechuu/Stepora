"""Authentication service - handles login, sessions, and password management."""
import hashlib
import secrets
from datetime import datetime
from .connection import get_db_connection
from .user_service import get_user_by_username, update_user_last_login

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify a password against its hash"""
    return hash_password(password) == password_hash

def generate_session_token():
    """Generate a secure random session token"""
    return secrets.token_urlsafe(32)

def authenticate_user(username, password):
    """Authenticate a user and create a session"""
    # Find user by username or email
    user = get_user_by_username(username)
    
    if not user:
        return {'success': False, 'error': 'Invalid username or password'}
    
    # Verify password
    if not verify_password(password, user['password_hash']):
        return {'success': False, 'error': 'Invalid username or password'}
    
    # Update last login
    update_user_last_login(user['id'], datetime.now())
    
    # Create session token
    session_token = generate_session_token()
    expires_at = datetime.now().timestamp() + (7 * 24 * 60 * 60)  # 7 days
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO user_sessions (user_id, session_token, expires_at)
        VALUES (?, ?, ?)
    ''', (user['id'], session_token, datetime.fromtimestamp(expires_at)))
    
    conn.commit()
    conn.close()
    
    return {
        'success': True,
        'session_token': session_token,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'full_name': user['full_name'],
            'profile_picture': user.get('profile_picture')
        }
    }

def verify_session(session_token):
    """Verify a session token and return user info"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT us.id, us.user_id, us.expires_at, u.username, u.email, u.full_name
        FROM user_sessions us
        JOIN users u ON us.user_id = u.id
        WHERE us.session_token = ? AND us.is_active = 1
    ''', (session_token,))
    
    session = cursor.fetchone()
    conn.close()
    
    if not session:
        return {'success': False, 'error': 'Invalid session'}
    
    # Check if session is expired
    expires_at = datetime.fromisoformat(session['expires_at'])
    if datetime.now() > expires_at:
        return {'success': False, 'error': 'Session expired'}
    
    # Get profile picture
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT profile_picture FROM users WHERE id = ?', (session['user_id'],))
    user_data = cursor.fetchone()
    conn.close()
    
    return {
        'success': True,
        'user': {
            'id': session['user_id'],
            'username': session['username'],
            'email': session['email'],
            'full_name': session['full_name'],
            'profile_picture': user_data['profile_picture'] if user_data else None
        }
    }

def logout_user(session_token):
    """Logout a user by invalidating their session"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE user_sessions
        SET is_active = 0
        WHERE session_token = ?
    ''', (session_token,))
    
    conn.commit()
    conn.close()
    
    return {'success': True}

def cleanup_expired_sessions():
    """Remove expired sessions from the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM user_sessions
        WHERE expires_at < ?
    ''', (datetime.now(),))
    
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    return {'success': True, 'deleted_count': deleted_count}
