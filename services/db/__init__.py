"""
Database services package.
Provides organized access to all database operations.
"""

# Connection
from .connection import get_db_connection, init_db

# User operations
from .user_service import (
    create_user,
    get_user_by_id,
    get_user_by_username,
    update_user_last_login,
    update_user_profile,
    update_profile_picture,
    remove_profile_picture,
    deactivate_user
)

# Authentication operations
from .auth_service import (
    hash_password,
    verify_password,
    generate_session_token,
    authenticate_user,
    verify_session,
    logout_user,
    cleanup_expired_sessions
)

# Search history operations
from .search_service import (
    add_search_history,
    get_user_search_history,
    delete_search_history,
    clear_user_search_history,
    get_search_stats
)

# Rating operations
from .rating_service import (
    add_rating,
    get_user_ratings,
    get_rating_by_item,
    delete_rating,
    get_rating_stats,
    get_ratings_by_type
)

# Statistics operations
from .stats_service import (
    get_user_dashboard_stats,
    get_user_activity_timeline,
    get_global_stats,
    get_popular_searches
)

# Cache operations
from .cache_service import (
    find_similar_cached_search,
    cache_search_result,
    increment_cache_hit,
    get_cache_stats,
    clear_old_cache
)

# Comment operations
from .comment_service import (
    add_comment,
    get_comments_for_search,
    get_comment_by_id,
    update_comment,
    delete_comment,
    get_comment_count
)

__all__ = [
    # Connection
    'get_db_connection',
    'init_db',
    
    # User operations
    'create_user',
    'get_user_by_id',
    'get_user_by_username',
    'update_user_last_login',
    'update_user_profile',
    'update_profile_picture',
    'remove_profile_picture',
    'deactivate_user',
    
    # Authentication
    'hash_password',
    'verify_password',
    'generate_session_token',
    'authenticate_user',
    'verify_session',
    'logout_user',
    'cleanup_expired_sessions',
    
    # Search history
    'add_search_history',
    'get_user_search_history',
    'delete_search_history',
    'clear_user_search_history',
    'get_search_stats',
    
    # Ratings
    'add_rating',
    'get_user_ratings',
    'get_rating_by_item',
    'delete_rating',
    'get_rating_stats',
    'get_ratings_by_type',
    
    # Statistics
    'get_user_dashboard_stats',
    'get_user_activity_timeline',
    'get_global_stats',
    'get_popular_searches',
    
    # Cache operations
    'find_similar_cached_search',
    'cache_search_result',
    'increment_cache_hit',
    'get_cache_stats',
    'clear_old_cache',
    
    # Comment operations
    'add_comment',
    'get_comments_for_search',
    'get_comment_by_id',
    'update_comment',
    'delete_comment',
    'get_comment_count'
]
