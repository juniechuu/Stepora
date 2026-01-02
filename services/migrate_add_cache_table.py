"""
Migration script to add cached_searches table for intelligent caching with RAG
Run this once to update your existing database
"""
import sqlite3
import os

def migrate_database():
    # Get the database path
    db_path = os.path.join(os.path.dirname(__file__), 'stepora.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    print(f"Migrating database at {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if cached_searches table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cached_searches'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✓ cached_searches table already exists")
        else:
            # Create cached_searches table
            cursor.execute('''
                CREATE TABLE cached_searches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    search_query TEXT NOT NULL,
                    normalized_query TEXT NOT NULL,
                    search_type TEXT NOT NULL,
                    response_data TEXT NOT NULL,
                    embedding TEXT,
                    hit_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes
            cursor.execute('''
                CREATE INDEX idx_normalized_query 
                ON cached_searches(normalized_query)
            ''')
            
            cursor.execute('''
                CREATE INDEX idx_search_type 
                ON cached_searches(search_type)
            ''')
            
            conn.commit()
            print("✓ Successfully created cached_searches table with indexes")
        
        # Verify the table was created
        cursor.execute("PRAGMA table_info(cached_searches)")
        columns = cursor.fetchall()
        print("\nCached searches table structure:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        print("\n✓ Migration completed successfully!")
        print("🚀 Smart caching with RAG is now enabled!")
        
    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"✗ Migration failed: {e}")

if __name__ == '__main__':
    migrate_database()
