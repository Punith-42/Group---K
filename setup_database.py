#!/usr/bin/env python3
"""
Database setup script for web activity tracking system.
This script creates the database and tables needed for the application.
"""

import pymysql
import os
from dotenv import load_dotenv
from config import DATABASE_CONFIG

# Load environment variables
load_dotenv()

def create_database():
    """Create the web_activity_db database if it doesn't exist."""
    try:
        # Connect to MySQL server (not to a specific database)
        conn = pymysql.connect(
            host=DATABASE_CONFIG['host'],
            user=DATABASE_CONFIG['user'],
            password=DATABASE_CONFIG['password'],
            port=int(DATABASE_CONFIG['port']),
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SHOW DATABASES LIKE %s", (DATABASE_CONFIG['database'],))
        exists = cursor.fetchone()
        
        if not exists:
            # Create database
            cursor.execute(f"CREATE DATABASE {DATABASE_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"Database '{DATABASE_CONFIG['database']}' created successfully!")
        else:
            print(f"Database '{DATABASE_CONFIG['database']}' already exists.")
            
        cursor.close()
        conn.close()
        
    except pymysql.Error as e:
        print(f"Error creating database: {e}")
        return False
    
    return True

def create_tables():
    """Create the web_activity table."""
    try:
        # Connect to the web_activity_db database
        conn = pymysql.connect(
            host=DATABASE_CONFIG['host'],
            database=DATABASE_CONFIG['database'],
            user=DATABASE_CONFIG['user'],
            password=DATABASE_CONFIG['password'],
            port=int(DATABASE_CONFIG['port']),
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        
        # Create web_activity table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS web_activity (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                website_name VARCHAR(255) NOT NULL,
                time_spent INT NOT NULL COMMENT 'time in minutes',
                activity_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        
        # Create index for better query performance (if not exists)
        try:
            cursor.execute("""
                CREATE INDEX idx_web_activity_user_date 
                ON web_activity(user_id, activity_date)
            """)
        except pymysql.Error:
            pass  # Index already exists
        
        # Create GitHub activity table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS github_activity (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                github_username VARCHAR(255) NOT NULL,
                activity_type ENUM('commit', 'pull_request', 'issue', 'push', 'repository') NOT NULL,
                repository_name VARCHAR(255),
                activity_description TEXT,
                commit_count INT DEFAULT 0,
                activity_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        
        # Create indexes for GitHub activity table (if not exists)
        try:
            cursor.execute("""
                CREATE INDEX idx_github_activity_user_date 
                ON github_activity(user_id, activity_date)
            """)
        except pymysql.Error:
            pass  # Index already exists
        
        try:
            cursor.execute("""
                CREATE INDEX idx_github_activity_type 
                ON github_activity(activity_type)
            """)
        except pymysql.Error:
            pass  # Index already exists
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Table 'web_activity' created successfully!")
        print("Table 'github_activity' created successfully!")
        print("Indexes created for better query performance!")
        
    except pymysql.Error as e:
        print(f"Error creating tables: {e}")
        return False
    
    return True

def test_connection():
    """Test database connection."""
    try:
        # First test connection to MySQL server without specific database
        conn = pymysql.connect(
            host=DATABASE_CONFIG['host'],
            user=DATABASE_CONFIG['user'],
            password=DATABASE_CONFIG['password'],
            port=int(DATABASE_CONFIG['port']),
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"Database connection successful!")
        print(f"MySQL version: {version[0]}")
        cursor.close()
        conn.close()
        return True
        
    except pymysql.Error as e:
        print(f"Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("Setting up Web Activity Database...")
    print("=" * 50)
    
    # Test initial connection
    print("1. Testing database connection...")
    if not test_connection():
        print("Cannot connect to MySQL. Please check your configuration.")
        exit(1)
    
    # Create database
    print("\n2. Creating database...")
    if not create_database():
        print("Failed to create database.")
        exit(1)
    
    # Create tables
    print("\n3. Creating tables...")
    if not create_tables():
        print("Failed to create tables.")
        exit(1)
    
    # Final connection test
    print("\n4. Final connection test...")
    if test_connection():
        print("\nDatabase setup completed successfully!")
        print("You can now run the Flask application.")
    else:
        print("\nSetup completed but connection test failed.")
