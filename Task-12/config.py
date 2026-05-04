"""
Configuration file for Hadith Search Engine Flask application
"""

import os
from datetime import timedelta

class Config:
    """Base configuration"""
    
    # Application Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Flask Settings
    JSON_SORT_KEYS = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # File Upload Settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Search Settings
    DEFAULT_SEARCH_LIMIT = 10
    MAX_SEARCH_LIMIT = 100
    SEARCH_TIMEOUT = 30  # seconds
    
    # FAISS Settings
    FAISS_INDEX_PATH = 'faiss_index.faiss'
    HADITH_DATA_PATH = 'cleaned_hadith.csv'
    EMBEDDINGS_PATH = 'embeddings.npy'
    
    # Model Settings
    SENTENCE_TRANSFORMER_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
    EMBEDDING_DIMENSION = 384  # for all-MiniLM-L6-v2
    
    # Caching (if implemented)
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'hadith_search.log'


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True  # Requires HTTPS
    
    # In production, set these environment variables:
    # - SECRET_KEY
    # - DATABASE_URL (if using database)
    # - FLASK_ENV=production


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    FAISS_INDEX_PATH = 'test_faiss_index.faiss'
    HADITH_DATA_PATH = 'test_cleaned_hadith.csv'
    SESSION_COOKIE_SECURE = False


# Configuration dictionary
config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """Get configuration based on environment"""
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    return config_dict.get(env, config_dict['default'])
