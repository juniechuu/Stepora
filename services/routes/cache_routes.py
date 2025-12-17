from flask import Blueprint, jsonify, request
from db import (
    find_similar_cached_search,
    cache_search_result,
    get_cache_stats
)

# Create blueprint for cache routes
cache_bp = Blueprint('cache', __name__)

@cache_bp.route('/check', methods=['POST'])
def check_cache():
    """Check if similar search exists in cache"""
    try:
        data = request.json
        query = data.get('query', '').strip()
        search_type = data.get('search_type', 'general')
        similarity_threshold = data.get('similarity_threshold', 0.85)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Find similar cached search
        cached_result = find_similar_cached_search(query, search_type, similarity_threshold)
        
        if cached_result:
            return jsonify({
                'cached': True,
                'query': cached_result['query'],
                'response': cached_result['response'],
                'similarity': cached_result['similarity'],
                'hit_count': cached_result['hit_count']
            }), 200
        else:
            return jsonify({'cached': False}), 200
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@cache_bp.route('/store', methods=['POST'])
def store_cache():
    """Store search result in cache"""
    try:
        data = request.json
        query = data.get('query', '').strip()
        search_type = data.get('search_type', 'general')
        response_data = data.get('response_data')
        
        if not query or not response_data:
            return jsonify({'error': 'Query and response data are required'}), 400
        
        result = cache_search_result(query, search_type, response_data)
        
        if result['success']:
            return jsonify({'message': 'Search result cached successfully'}), 201
        else:
            return jsonify({'error': result.get('error', 'Failed to cache')}), 500
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@cache_bp.route('/stats', methods=['GET'])
def cache_statistics():
    """Get cache statistics"""
    try:
        stats = get_cache_stats()
        
        if stats:
            return jsonify(stats), 200
        else:
            return jsonify({'error': 'Failed to retrieve stats'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500
