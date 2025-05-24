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
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+mysqlconnector://root:@localhost/calora_db?charset=utf8mb4')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Gemini API configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your-gemini-api-key-here')

    # Optional check for API key
    if not GEMINI_API_KEY:
        print("WARNING: GEMINI_API_KEY not found in environment variables or .env file.")