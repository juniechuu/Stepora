"""Comment service - handles comments and replies on search results."""
import sqlite3
from datetime import datetime
from .connection import get_db_connection

def add_comment(user_id, search_query, search_type, comment_text, parent_id=None):
    """Add a comment or reply to a search result"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO comments (user_id, search_query, search_type, comment_text, parent_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, search_query, search_type, comment_text, parent_id))
        
        comment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {'success': True, 'comment_id': comment_id}
        
    except Exception as e:
        print(f"Error adding comment: {e}")
        return {'success': False, 'error': str(e)}

def get_comments_for_search(search_query, search_type, limit=100):
    """Get all comments for a specific search query"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                c.id,
                c.user_id,
                c.search_query,
                c.search_type,
                c.comment_text,
                c.parent_id,
                c.created_at,
                u.username,
                u.profile_picture
            FROM comments c
            JOIN users u ON c.user_id = u.id
            WHERE LOWER(c.search_query) = LOWER(?) 
            AND c.search_type = ?
            ORDER BY c.created_at ASC
            LIMIT ?
        ''', (search_query, search_type, limit))
        
        comments = cursor.fetchall()
        conn.close()
        
        # Convert to dict and organize into threads
        comment_list = []
        for comment in comments:
            comment_dict = dict(comment)
            comment_list.append(comment_dict)
        
        return comment_list
        
    except Exception as e:
        print(f"Error getting comments: {e}")
        return []

def get_comment_by_id(comment_id):
    """Get a specific comment by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                c.id,
                c.user_id,
                c.search_query,
                c.search_type,
                c.comment_text,
                c.parent_id,
                c.created_at,
                u.username,
                u.profile_picture
            FROM comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.id = ?
        ''', (comment_id,))
        
        comment = cursor.fetchone()
        conn.close()
        
        return dict(comment) if comment else None
        
    except Exception as e:
        print(f"Error getting comment: {e}")
        return None

def update_comment(comment_id, user_id, comment_text):
    """Update a comment (only by the owner)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify ownership
        cursor.execute('SELECT user_id FROM comments WHERE id = ?', (comment_id,))
        comment = cursor.fetchone()
        
        if not comment or comment['user_id'] != user_id:
            conn.close()
            return {'success': False, 'error': 'Not authorized to edit this comment'}
        
        cursor.execute('''
            UPDATE comments
            SET comment_text = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (comment_text, comment_id))
        
        conn.commit()
        conn.close()
        
        return {'success': True}
        
    except Exception as e:
        print(f"Error updating comment: {e}")
        return {'success': False, 'error': str(e)}

def delete_comment(comment_id, user_id):
    """Delete a comment (only by the owner)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify ownership
        cursor.execute('SELECT user_id FROM comments WHERE id = ?', (comment_id,))
        comment = cursor.fetchone()
        
        if not comment or comment['user_id'] != user_id:
            conn.close()
            return {'success': False, 'error': 'Not authorized to delete this comment'}
        
        # Delete the comment and all its replies
        cursor.execute('DELETE FROM comments WHERE id = ? OR parent_id = ?', (comment_id, comment_id))
        
        conn.commit()
        conn.close()
        
        return {'success': True}
        
    except Exception as e:
        print(f"Error deleting comment: {e}")
        return {'success': False, 'error': str(e)}

def get_comment_count(search_query, search_type):
    """Get total comment count for a search"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM comments
            WHERE LOWER(search_query) = LOWER(?) AND search_type = ?
        ''', (search_query, search_type))
        
        result = cursor.fetchone()
        conn.close()
        
        return result['count'] if result else 0
        
    except Exception as e:
        print(f"Error getting comment count: {e}")
        return 0
