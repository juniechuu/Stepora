"""Search history service - handles search tracking and retrieval."""
from .connection import get_db_connection

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

def delete_search_history(user_id, search_id):
    """Delete a specific search history entry"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM search_history
        WHERE id = ? AND user_id = ?
    ''', (search_id, user_id))
    
    conn.commit()
    conn.close()
    
    return {'success': True}

def clear_user_search_history(user_id):
    """Clear all search history for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM search_history
        WHERE user_id = ?
    ''', (user_id,))
    
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    return {'success': True, 'deleted_count': deleted_count}

def get_search_stats(user_id):
    """Get search statistics for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total searches
    cursor.execute('''
        SELECT COUNT(*) as total_searches
        FROM search_history
        WHERE user_id = ?
    ''', (user_id,))
    total_searches = cursor.fetchone()['total_searches']
    
    # Searches by type
    cursor.execute('''
        SELECT search_type, COUNT(*) as count
        FROM search_history
        WHERE user_id = ?
        GROUP BY search_type
    ''', (user_id,))
    by_type = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        'total_searches': total_searches,
        'by_type': by_type
    }
