import sqlite3
import os
from datetime import datetime
import hashlib
import secrets

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), 'stepora.db')

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn

def init_db():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    # Create sessions table for storing login sessions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create search history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            search_query TEXT NOT NULL,
            search_type TEXT,
            result_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create ratings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_type TEXT NOT NULL,
            item_id TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
            review TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify a password against its hash"""
    return hash_password(password) == password_hash

def generate_session_token():
    """Generate a secure random session token"""
    return secrets.token_urlsafe(32)

# User Management Functions

def create_user(username, email, password, full_name=None):
    """Create a new user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        password_hash = hash_password(password)
        
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

def authenticate_user(username, password):
    """Authenticate a user and create a session"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Find user by username or email
    cursor.execute('''
        SELECT id, username, email, password_hash, full_name, is_active
        FROM users
        WHERE (username = ? OR email = ?) AND is_active = 1
    ''', (username, username))
    
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return {'success': False, 'error': 'Invalid username or password'}
    
    # Verify password
    if not verify_password(password, user['password_hash']):
        conn.close()
        return {'success': False, 'error': 'Invalid username or password'}
    
    # Update last login
    cursor.execute('''
        UPDATE users SET last_login = ? WHERE id = ?
    ''', (datetime.now(), user['id']))
    
    # Create session token
    session_token = generate_session_token()
    expires_at = datetime.now().timestamp() + (7 * 24 * 60 * 60)  # 7 days
    
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
            'full_name': user['full_name']
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
    
    return {
        'success': True,
        'user': {
            'id': session['user_id'],
            'username': session['username'],
            'email': session['email'],
            'full_name': session['full_name']
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

def get_user_by_id(user_id):
    """Get user information by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, email, full_name, created_at, last_login
        FROM users
        WHERE id = ? AND is_active = 1
    ''', (user_id,))
    
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return None
    
    return dict(user)

# Search History Functions

def add_search_history(user_id, search_query, search_type=None, result_count=0):
    """Add a search history entry"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO search_history (user_id, search_query, search_type, result_count)
        VALUES (?, ?, ?, ?)
    ''', (user_id, search_query, search_type, result_count))
    
    conn.commit()
    conn.close()
    
    return {'success': True}

def get_user_search_history(user_id, limit=50):
    """Get user's search history"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, search_query, search_type, result_count, created_at
        FROM search_history
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    ''', (user_id, limit))
    
    searches = cursor.fetchall()
    conn.close()
    
    return [dict(search) for search in searches]

# Rating Functions

def add_rating(user_id, item_type, item_id, rating, review=None):
    """Add or update a rating"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if rating already exists
    cursor.execute('''
        SELECT id FROM user_ratings
        WHERE user_id = ? AND item_type = ? AND item_id = ?
    ''', (user_id, item_type, item_id))
    
    existing = cursor.fetchone()
    
    if existing:
        # Update existing rating
        cursor.execute('''
            UPDATE user_ratings
            SET rating = ?, review = ?
            WHERE id = ?
        ''', (rating, review, existing['id']))
    else:
        # Insert new rating
        cursor.execute('''
            INSERT INTO user_ratings (user_id, item_type, item_id, rating, review)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, item_type, item_id, rating, review))
    
    conn.commit()
    conn.close()
    
    return {'success': True}

def get_user_ratings(user_id, limit=50):
    """Get user's ratings"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, item_type, item_id, rating, review, created_at
        FROM user_ratings
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    ''', (user_id, limit))
    
    ratings = cursor.fetchall()
    conn.close()
    
    return [dict(rating) for rating in ratings]

def get_user_dashboard_stats(user_id):
    """Get dashboard statistics for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get total searches
    cursor.execute('''
        SELECT COUNT(*) as total_searches
        FROM search_history
        WHERE user_id = ?
    ''', (user_id,))
    total_searches = cursor.fetchone()['total_searches']
    
    # Get total ratings
    cursor.execute('''
        SELECT COUNT(*) as total_ratings, AVG(rating) as avg_rating
        FROM user_ratings
        WHERE user_id = ?
    ''', (user_id,))
    rating_stats = cursor.fetchone()
    
    # Get recent activity count (last 7 days)
    cursor.execute('''
        SELECT COUNT(*) as recent_searches
        FROM search_history
        WHERE user_id = ? AND created_at >= datetime('now', '-7 days')
    ''', (user_id,))
    recent_searches = cursor.fetchone()['recent_searches']
    
    conn.close()
    
    return {
        'total_searches': total_searches,
        'total_ratings': rating_stats['total_ratings'] or 0,
        'average_rating': round(rating_stats['avg_rating'], 1) if rating_stats['avg_rating'] else 0,
        'recent_searches': recent_searches
    }

# Initialize database on import
if __name__ == '__main__':
    init_db()
