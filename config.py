"""
Configuration management for local web activity tracking system.
Simple configuration for local development only.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Simple configuration for local development."""
    
    # Database configuration - MySQL
    DATABASE_HOST = os.getenv('DB_HOST', 'localhost')
    DATABASE_NAME = os.getenv('DB_NAME', 'web_activity_db')
    DATABASE_USER = os.getenv('DB_USER', 'root')
    DATABASE_PASSWORD = os.getenv('DB_PASSWORD', '')
    DATABASE_PORT = os.getenv('DB_PORT', '3306')
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'local-development-key')
    DEBUG = True
    
    # API configuration
    API_HOST = '127.0.0.1'
    API_PORT = 5001
    
    @classmethod
    def get_database_config(cls) -> Dict[str, Any]:
        """Get database configuration as a dictionary."""
        return {
            'host': cls.DATABASE_HOST,
            'database': cls.DATABASE_NAME,
            'user': cls.DATABASE_USER,
            'password': cls.DATABASE_PASSWORD,
            'port': cls.DATABASE_PORT
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Simple validation for local development."""
        return True

# Export the database configuration for easy access
DATABASE_CONFIG = Config.get_database_config()
