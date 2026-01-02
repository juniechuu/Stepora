"""
Migration script to add profile_picture column to existing users table
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
        # Check if profile_picture column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'profile_picture' in columns:
            print("✓ profile_picture column already exists")
        else:
            # Add profile_picture column
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN profile_picture TEXT
            """)
            conn.commit()
            print("✓ Successfully added profile_picture column to users table")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print("\nCurrent users table structure:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        print("\n✓ Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"✗ Migration failed: {e}")

if __name__ == '__main__':
    migrate_database()
