import os
import urllib.parse
import datetime
from dotenv import load_dotenv

# Load variables from .env for local development
load_dotenv() 

class Config:
    # --- Environment Detection ---
    IS_RENDER = os.getenv("RENDER", "False").lower() == "true"

    # --- Database Configuration ---
    if IS_RENDER:
        # PRODUCTION: These come from Render's Dashboard "Environment" tab
        db_user = os.getenv("DB_USER")
        _raw_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_name = os.getenv("DB_NAME")
    else:
        # LOCAL: These are your local MySQL settings
        db_user = os.getenv("DB_USER", "root")
        _raw_password = os.getenv("DB_PASSWORD", "Ba@12345") # Your local MySQL password
        db_host = os.getenv("DB_HOST", "127.0.0.1")
        db_port = os.getenv("DB_PORT", "3306")
        db_name = os.getenv("DB_NAME", "student_portal_db")

    # Encode password to handle special characters (@, #, !, etc.)
    db_password = urllib.parse.quote_plus(_raw_password) if _raw_password else ""

    # Final Connection String
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- File Upload Limit ---
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # --- JWT Settings ---
    JWT_SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-local-key") 
    JWT_TOKEN_LOCATION = ["cookies"]
    
    # Secure cookies ONLY on Render (HTTPS). Localhost (HTTP) needs this to be False.
    JWT_COOKIE_SECURE = IS_RENDER
    
    JWT_COOKIE_HTTPONLY = True
    JWT_COOKIE_SAMESITE = "Lax"
    JWT_COOKIE_CSRF_PROTECT = False 
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=2)

    # --- Frontend URL (used in emails for activation links etc.) ---
    # IMPORTANT: Set FRONTEND_URL in Render's Environment Variables tab.
    # Default is the Render URL. For local dev it reads from .env file.
    FRONTEND_URL = os.getenv("FRONTEND_URL", "https://student-portal-backend-8icb.onrender.com")
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USER")
    MAIL_PASSWORD = os.getenv("MAIL_PASS") 
    MAIL_DEFAULT_SENDER = ('Student Portal Admin', os.getenv("MAIL_USER"))