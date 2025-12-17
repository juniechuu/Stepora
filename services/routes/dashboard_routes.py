from flask import Blueprint, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
import os
import uuid
from db import (
    verify_session,
    get_user_by_id,
    get_user_search_history,
    get_user_ratings,
    get_user_dashboard_stats,
    add_search_history,
    add_rating,
    update_profile_picture,
    remove_profile_picture
)

# Create blueprint for user dashboard routes
dashboard_bp = Blueprint('dashboard', __name__)

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

@dashboard_bp.route('/profile', methods=['GET'])
def get_user_profile():
    """Get user profile information"""
    try:
        user, error = get_user_from_token()
        if error:
            return jsonify(error), 401
        
        # Get full user details
        user_details = get_user_by_id(user['id'])
        
        if not user_details:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(user_details), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@dashboard_bp.route('/stats', methods=['GET'])
def get_dashboard_stats():
    """Get user dashboard statistics"""
    try:
        user, error = get_user_from_token()
        if error:
            return jsonify(error), 401
        
        stats = get_user_dashboard_stats(user['id'])
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@dashboard_bp.route('/search-history', methods=['GET'])
def get_search_history():
    """Get user's search history"""
    try:
        user, error = get_user_from_token()
        if error:
            return jsonify(error), 401
        
        limit = request.args.get('limit', 50, type=int)
        history = get_user_search_history(user['id'], limit)
        
        return jsonify({'history': history}), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@dashboard_bp.route('/search-history', methods=['POST'])
def add_search():
    """Add a search to user's history"""
    try:
        user, error = get_user_from_token()
        if error:
            return jsonify(error), 401
        
        data = request.json
        search_query = data.get('search_query', '').strip()
        search_type = data.get('search_type', 'general')
        result_count = data.get('result_count', 0)
        
        if not search_query:
            return jsonify({'error': 'Search query is required'}), 400
        
        add_search_history(user['id'], search_query, search_type, result_count)
        
        return jsonify({'message': 'Search added to history'}), 201
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@dashboard_bp.route('/ratings', methods=['GET'])
def get_ratings():
    """Get user's ratings"""
    try:
        user, error = get_user_from_token()
        if error:
            return jsonify(error), 401
        
        limit = request.args.get('limit', 50, type=int)
        ratings = get_user_ratings(user['id'], limit)
        
        return jsonify({'ratings': ratings}), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@dashboard_bp.route('/ratings', methods=['POST'])
def add_user_rating():
    """Add or update a rating"""
    try:
        user, error = get_user_from_token()
        if error:
            return jsonify(error), 401
        
        data = request.json
        item_type = data.get('item_type', '').strip()
        item_id = data.get('item_id', '').strip()
        rating = data.get('rating')
        review = data.get('review', '').strip()
        
        if not item_type or not item_id:
            return jsonify({'error': 'Item type and ID are required'}), 400
        
        if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        
        add_rating(user['id'], item_type, item_id, rating, review if review else None)
        
        return jsonify({'message': 'Rating added successfully'}), 201
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@dashboard_bp.route('/ratings/<item_type>/<item_id>/stats', methods=['GET'])
def get_item_ratings_stats(item_type, item_id):
    """Get aggregate rating statistics for a specific item"""
    try:
        from db.rating_service import get_item_rating_stats
        
        stats = get_item_rating_stats(item_type, item_id)
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@dashboard_bp.route('/ratings/top-articles', methods=['GET'])
def get_top_rated_articles():
    """Get top rated articles across all types"""
    try:
        from db.rating_service import get_top_rated_articles
        
        limit = request.args.get('limit', 100, type=int)
        articles = get_top_rated_articles(limit)
        return jsonify({'articles': articles}), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

# Upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'profile_pictures')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@dashboard_bp.route('/profile-picture/upload', methods=['POST'])
def upload_profile_picture():
    """Upload a profile picture file"""
    try:
        user, error = get_user_from_token()
        if error:
            return jsonify(error), 401
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif, webp'}), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': 'File too large. Maximum size is 5MB'}), 400
        
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{user['id']}_{uuid.uuid4().hex}.{file_extension}"
        
        # Delete old profile picture file if it exists
        old_user = get_user_by_id(user['id'])
        if old_user and old_user.get('profile_picture') and old_user['profile_picture'].startswith('/uploads/'):
            old_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), old_user['profile_picture'].lstrip('/'))
            if os.path.exists(old_file_path):
                try:
                    os.remove(old_file_path)
                except:
                    pass  # Continue even if deletion fails
        
        # Save file
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        
        # Update database with relative URL
        picture_url = f"/uploads/profile_pictures/{unique_filename}"
        update_profile_picture(user['id'], picture_url)
        
        # Return full URL to frontend
        full_url = f"http://localhost:5000{picture_url}"
        
        return jsonify({
            'message': 'Profile picture uploaded successfully',
            'picture_url': full_url
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@dashboard_bp.route('/profile-picture', methods=['POST'])
def update_user_profile_picture():
    """Update user's profile picture with URL"""
    try:
        user, error = get_user_from_token()
        if error:
            return jsonify(error), 401
        
        data = request.json
        picture_url = data.get('picture_url', '').strip()
        
        if not picture_url:
            return jsonify({'error': 'Picture URL is required'}), 400
        
        update_profile_picture(user['id'], picture_url)
        
        return jsonify({'message': 'Profile picture updated successfully', 'picture_url': picture_url}), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@dashboard_bp.route('/profile-picture', methods=['DELETE'])
def delete_profile_picture():
    """Remove user's profile picture"""
    try:
        user, error = get_user_from_token()
        if error:
            return jsonify(error), 401
        
        # Delete file if it exists
        old_user = get_user_by_id(user['id'])
        if old_user and old_user.get('profile_picture') and old_user['profile_picture'].startswith('/uploads/'):
            old_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), old_user['profile_picture'].lstrip('/'))
            if os.path.exists(old_file_path):
                try:
                    os.remove(old_file_path)
                except:
                    pass  # Continue even if deletion fails
        
        remove_profile_picture(user['id'])
        
        return jsonify({'message': 'Profile picture removed successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500
