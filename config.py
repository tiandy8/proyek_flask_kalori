# config.py (FIXED)
import os
# --- 1. Import the loader ---
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

# --- 2. Load the .env file ---
# Looks for .env in the same directory and loads variables
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Flask configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev')
    
    # Database configuration - Using SQLite with absolute path
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(basedir, "kalora.db")}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # OpenRouter API configuration
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    if not OPENROUTER_API_KEY:
        print("WARNING: OPENROUTER_API_KEY not found in environment variables or .env file.")