"""Cache service - handles search result caching with semantic similarity."""
import sqlite3
import json
import openai
import os
from datetime import datetime
from .connection import get_db_connection

def get_embedding(text):
    """Get OpenAI embedding for text"""
    try:
        # Try new API (v1.0+)
        try:
            client = openai.OpenAI()
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except AttributeError:
            # Fall back to old API (pre-v1.0)
            response = openai.Embedding.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response['data'][0]['embedding']
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return None

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors"""
    if not vec1 or not vec2:
        return 0
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = sum(a * a for a in vec1) ** 0.5
    magnitude2 = sum(b * b for b in vec2) ** 0.5
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0
    
    return dot_product / (magnitude1 * magnitude2)

def find_similar_cached_search(query, search_type, similarity_threshold=0.85):
    """Find similar cached search using embeddings"""
    try:
        # Get embedding for the query
        query_embedding = get_embedding(query.lower().strip())
        if not query_embedding:
            return None
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all cached searches of the same type
        cursor.execute('''
            SELECT id, search_query, embedding, response_data, hit_count
            FROM cached_searches
            WHERE search_type = ?
            ORDER BY created_at DESC
            LIMIT 100
        ''', (search_type,))
        
        cached_searches = cursor.fetchall()
        conn.close()
        
        best_match = None
        best_similarity = 0
        
        for cache in cached_searches:
            cached_embedding = json.loads(cache['embedding']) if cache['embedding'] else None
            if cached_embedding:
                similarity = cosine_similarity(query_embedding, cached_embedding)
                if similarity > best_similarity and similarity >= similarity_threshold:
                    best_similarity = similarity
                    best_match = {
                        'id': cache['id'],
                        'query': cache['search_query'],
                        'response': json.loads(cache['response_data']),
                        'hit_count': cache['hit_count'],
                        'similarity': similarity
                    }
        
        if best_match:
            # Update hit count and last accessed
            increment_cache_hit(best_match['id'])
        
        return best_match
        
    except Exception as e:
        print(f"Error finding similar cache: {e}")
        return None

def cache_search_result(query, search_type, response_data):
    """Cache a search result with embedding"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get embedding for the query
        query_embedding = get_embedding(query.lower().strip())
        embedding_json = json.dumps(query_embedding) if query_embedding else None
        
        # Store normalized query for exact matching
        normalized_query = query.lower().strip()
        
        cursor.execute('''
            INSERT INTO cached_searches 
            (search_query, normalized_query, search_type, response_data, embedding, hit_count)
            VALUES (?, ?, ?, ?, ?, 0)
        ''', (query, normalized_query, search_type, json.dumps(response_data), embedding_json))
        
        cache_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {'success': True, 'cache_id': cache_id}
        
    except Exception as e:
        print(f"Error caching search: {e}")
        return {'success': False, 'error': str(e)}

def increment_cache_hit(cache_id):
    """Increment hit count for a cached search"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE cached_searches
            SET hit_count = hit_count + 1,
                last_accessed = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (cache_id,))
        
        conn.commit()
        conn.close()
        
        return {'success': True}
        
    except Exception as e:
        print(f"Error incrementing cache hit: {e}")
        return {'success': False, 'error': str(e)}

def get_cache_stats():
    """Get cache statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_cached,
                SUM(hit_count) as total_hits,
                search_type,
                COUNT(*) as count_by_type
            FROM cached_searches
            GROUP BY search_type
        ''')
        
        stats = cursor.fetchall()
        
        cursor.execute('SELECT COUNT(*) as total FROM cached_searches')
        total = cursor.fetchone()
        
        cursor.execute('SELECT SUM(hit_count) as total_hits FROM cached_searches')
        total_hits = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_cached': total['total'] if total else 0,
            'total_hits': total_hits['total_hits'] if total_hits['total_hits'] else 0,
            'by_type': [dict(row) for row in stats]
        }
        
    except Exception as e:
        print(f"Error getting cache stats: {e}")
        return None

def clear_old_cache(days=30):
    """Clear cache entries older than specified days that haven't been accessed"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM cached_searches
            WHERE hit_count = 0 
            AND created_at < datetime('now', '-' || ? || ' days')
        ''', (days,))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return {'success': True, 'deleted': deleted}
        
    except Exception as e:
        print(f"Error clearing cache: {e}")
        return {'success': False, 'error': str(e)}
