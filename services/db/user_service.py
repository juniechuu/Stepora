"""User service - handles user CRUD operations."""
import sqlite3
from .connection import get_db_connection

def format_profile_picture_url(picture_path):
    """Convert relative profile picture path to full URL"""
    if not picture_path:
        return None
    if picture_path.startswith('http://') or picture_path.startswith('https://'):
        return picture_path
    # For uploaded files, construct full URL
    if picture_path.startswith('/uploads/'):
        return f'http://localhost:5000{picture_path}'
    return picture_path

def create_user(username, email, password_hash, full_name=None):
    """Create a new user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name)
            VALUES (?, ?, ?, ?)
        ''', (username, email, password_hash, full_name))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {'success': True, 'user_id': user_id, 'username': username}
    except sqlite3.IntegrityError as e:
        return {'success': False, 'error': 'Username or email already exists'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_user_by_id(user_id):
    """Get user information by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, email, full_name, profile_picture, created_at, last_login
        FROM users
        WHERE id = ? AND is_active = 1
    ''', (user_id,))
    
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return None
    
    user_dict = dict(user)
    user_dict['profile_picture'] = format_profile_picture_url(user_dict.get('profile_picture'))
    return user_dict

def get_user_by_username(username):
    """Get user by username or email"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, email, password_hash, full_name, profile_picture, is_active
        FROM users
        WHERE (username = ? OR email = ?) AND is_active = 1
    ''', (username, username))
    
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return None
    
    user_dict = dict(user)
    user_dict['profile_picture'] = format_profile_picture_url(user_dict.get('profile_picture'))
    return user_dict

def update_user_last_login(user_id, login_time):
    """Update user's last login timestamp"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users SET last_login = ? WHERE id = ?
    ''', (login_time, user_id))
    
    conn.commit()
    conn.close()
    
    return {'success': True}

def update_user_profile(user_id, full_name=None, email=None):
    """Update user profile information"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if full_name and email:
            cursor.execute('''
                UPDATE users SET full_name = ?, email = ? WHERE id = ?
            ''', (full_name, email, user_id))
        elif full_name:
            cursor.execute('''
                UPDATE users SET full_name = ? WHERE id = ?
            ''', (full_name, user_id))
        elif email:
            cursor.execute('''
                UPDATE users SET email = ? WHERE id = ?
            ''', (email, user_id))
        
        conn.commit()
        conn.close()
        return {'success': True}
    except sqlite3.IntegrityError:
        return {'success': False, 'error': 'Email already exists'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def deactivate_user(user_id):
    """Deactivate a user account"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users SET is_active = 0 WHERE id = ?
    ''', (user_id,))
    
    conn.commit()
    conn.close()
    
    return {'success': True}

def update_profile_picture(user_id, picture_url):
    """Update user's profile picture"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users SET profile_picture = ? WHERE id = ?
    ''', (picture_url, user_id))
    
    conn.commit()
    conn.close()
    
    return {'success': True}

def remove_profile_picture(user_id):
    """Remove user's profile picture"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users SET profile_picture = NULL WHERE id = ?
    ''', (user_id,))
    
    conn.commit()
    conn.close()
    
    return {'success': True}
