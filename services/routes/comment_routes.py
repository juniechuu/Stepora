from flask import Blueprint, jsonify, request
from db import (
    verify_session,
    add_comment,
    get_comments_for_search,
    get_comment_by_id,
    update_comment,
    delete_comment,
    get_comment_count
)

# Create blueprint for comment routes
comment_bp = Blueprint('comments', __name__)

def get_user_from_token():
    """Helper function to get user from authorization token"""
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return None, {'error': 'Invalid authorization header'}
    
    session_token = auth_header.replace('Bearer ', '')
    result = verify_session(session_token)
    
    if not result['success']:
        return None, {'error': result['error']}
    
    return result['user'], None

@comment_bp.route('/', methods=['POST'])
def create_comment():
    """Add a new comment or reply"""
    try:
        user, error = get_user_from_token()
        if error:
            return jsonify(error), 401
        
        data = request.json
        search_query = data.get('search_query', '').strip()
        search_type = data.get('search_type', 'toddler')
        comment_text = data.get('comment_text', '').strip()
        parent_id = data.get('parent_id')
        
        if not search_query or not comment_text:
            return jsonify({'error': 'Search query and comment text are required'}), 400
        
        result = add_comment(user['id'], search_query, search_type, comment_text, parent_id)
        
        if result['success']:
            # Get the created comment with user info
            comment = get_comment_by_id(result['comment_id'])
            return jsonify({
                'message': 'Comment added successfully',
                'comment': comment
            }), 201
        else:
            return jsonify({'error': result.get('error', 'Failed to add comment')}), 500
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@comment_bp.route('/<search_type>/<path:search_query>', methods=['GET'])
def get_comments(search_type, search_query):
    """Get all comments for a search query"""
    try:
        limit = request.args.get('limit', 100, type=int)
        comments = get_comments_for_search(search_query, search_type, limit)
        
        return jsonify({'comments': comments}), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@comment_bp.route('/<int:comment_id>', methods=['PUT'])
def edit_comment(comment_id):
    """Update a comment"""
    try:
        user, error = get_user_from_token()
        if error:
            return jsonify(error), 401
        
        data = request.json
        comment_text = data.get('comment_text', '').strip()
        
        if not comment_text:
            return jsonify({'error': 'Comment text is required'}), 400
        
        result = update_comment(comment_id, user['id'], comment_text)
        
        if result['success']:
            return jsonify({'message': 'Comment updated successfully'}), 200
        else:
            return jsonify({'error': result.get('error', 'Failed to update comment')}), 403
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@comment_bp.route('/<int:comment_id>', methods=['DELETE'])
def remove_comment(comment_id):
    """Delete a comment"""
    try:
        user, error = get_user_from_token()
        if error:
            return jsonify(error), 401
        
        result = delete_comment(comment_id, user['id'])
        
        if result['success']:
            return jsonify({'message': 'Comment deleted successfully'}), 200
        else:
            return jsonify({'error': result.get('error', 'Failed to delete comment')}), 403
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@comment_bp.route('/count/<search_type>/<path:search_query>', methods=['GET'])
def comment_count(search_type, search_query):
    """Get comment count for a search"""
    try:
        count = get_comment_count(search_query, search_type)
        return jsonify({'count': count}), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500
