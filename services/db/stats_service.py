"""Statistics service - handles dashboard and analytics statistics."""
from .connection import get_db_connection

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

def get_user_activity_timeline(user_id, days=30):
    """Get user activity timeline for the last N days"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DATE(created_at) as date, COUNT(*) as count
        FROM search_history
        WHERE user_id = ? AND created_at >= datetime('now', '-' || ? || ' days')
        GROUP BY DATE(created_at)
        ORDER BY date DESC
    ''', (user_id, days))
    
    activity = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in activity]

def get_global_stats():
    """Get global platform statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total users
    cursor.execute('SELECT COUNT(*) as total_users FROM users WHERE is_active = 1')
    total_users = cursor.fetchone()['total_users']
    
    # Total searches
    cursor.execute('SELECT COUNT(*) as total_searches FROM search_history')
    total_searches = cursor.fetchone()['total_searches']
    
    # Total ratings
    cursor.execute('SELECT COUNT(*) as total_ratings FROM user_ratings')
    total_ratings = cursor.fetchone()['total_ratings']
    
    # Average rating across platform
    cursor.execute('SELECT AVG(rating) as avg_rating FROM user_ratings')
    avg_rating = cursor.fetchone()['avg_rating']
    
    conn.close()
    
    return {
        'total_users': total_users,
        'total_searches': total_searches,
        'total_ratings': total_ratings,
        'average_rating': round(avg_rating, 2) if avg_rating else 0
    }

def get_popular_searches(limit=10):
    """Get most popular search queries"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT search_query, COUNT(*) as search_count
        FROM search_history
        GROUP BY search_query
        ORDER BY search_count DESC
        LIMIT ?
    ''', (limit,))
    
    searches = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in searches]
