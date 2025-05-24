# config.py (FIXED)
import os
# --- 1. Import the loader ---
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

# --- 2. Load the .env file ---
# Looks for .env in the same directory and loads variables
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or b'\xe1\x86\xa1\x83\x84r\xde\x0bu\x84\xb5\xfc\xd7\xf0y\xa8L!\xc7\xcd\x1f\xd4-\x9a'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+mysqlconnector://root:@localhost/calora_db?charset=utf8mb4' # Kept charset
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- 3. Read Gemini Key from Environment (Now loaded from .env) ---
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

    # --- Optional check (Good to keep) ---
    if not GEMINI_API_KEY:
        print("WARNING: GEMINI_API_KEY not found in environment variables or .env file.")
        # raise ValueError("No GEMINI_API_KEY set for Flask application")