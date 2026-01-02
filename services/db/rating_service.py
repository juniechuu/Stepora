"""Rating service - handles user ratings and reviews."""
from .connection import get_db_connection

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

def get_rating_by_item(user_id, item_type, item_id):
    """Get a specific rating by user and item"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, rating, review, created_at
        FROM user_ratings
        WHERE user_id = ? AND item_type = ? AND item_id = ?
    ''', (user_id, item_type, item_id))
    
    rating = cursor.fetchone()
    conn.close()
    
    if not rating:
        return None
    
    return dict(rating)

def delete_rating(user_id, rating_id):
    """Delete a specific rating"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM user_ratings
        WHERE id = ? AND user_id = ?
    ''', (rating_id, user_id))
    
    conn.commit()
    conn.close()
    
    return {'success': True}

def get_rating_stats(user_id):
    """Get rating statistics for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            COUNT(*) as total_ratings, 
            AVG(rating) as avg_rating,
            MIN(rating) as min_rating,
            MAX(rating) as max_rating
        FROM user_ratings
        WHERE user_id = ?
    ''', (user_id,))
    
    stats = cursor.fetchone()
    conn.close()
    
    return {
        'total_ratings': stats['total_ratings'] or 0,
        'average_rating': round(stats['avg_rating'], 2) if stats['avg_rating'] else 0,
        'min_rating': stats['min_rating'] or 0,
        'max_rating': stats['max_rating'] or 0
    }

def get_ratings_by_type(user_id, item_type):
    """Get all ratings for a specific item type"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, item_id, rating, review, created_at
        FROM user_ratings
        WHERE user_id = ? AND item_type = ?
        ORDER BY created_at DESC
    ''', (user_id, item_type))
    
    ratings = cursor.fetchall()
    conn.close()
    
    return [dict(rating) for rating in ratings]

def get_item_rating_stats(item_type, item_id):
    """Get aggregate rating statistics for a specific item"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            COUNT(*) as total_ratings, 
            AVG(rating) as avg_rating,
            MIN(rating) as min_rating,
            MAX(rating) as max_rating
        FROM user_ratings
        WHERE item_type = ? AND item_id = ?
    ''', (item_type, item_id))
    
    stats = cursor.fetchone()
    conn.close()
    
    return {
        'total_ratings': stats['total_ratings'] or 0,
        'average_rating': round(stats['avg_rating'], 1) if stats['avg_rating'] else 0,
        'min_rating': stats['min_rating'] or 0,
        'max_rating': stats['max_rating'] or 0
    }

def get_top_rated_articles(limit=100):
    """Get top rated articles/items for teen-adult type only"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            item_type,
            item_id,
            COUNT(*) as total_ratings,
            AVG(rating) as avg_rating,
            MAX(created_at) as last_rated
        FROM user_ratings
        WHERE item_type = 'teen-adult'
        GROUP BY item_type, item_id
        HAVING COUNT(*) >= 1
        ORDER BY avg_rating DESC, total_ratings DESC
        LIMIT ?
    ''', (limit,))
    
    articles = cursor.fetchall()
    conn.close()
    
    return [{
        'item_type': article['item_type'],
        'item_id': article['item_id'],
        'total_ratings': article['total_ratings'],
        'average_rating': round(article['avg_rating'], 1),
        'last_rated': article['last_rated']
    } for article in articles]
