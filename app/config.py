import os
import urllib.parse
import datetime
from dotenv import load_dotenv

# This looks for the file named exactly ".env" in your folder
load_dotenv() 

class Config:
    # --- Database Configuration ---
    # Fetch from .env, fallback to 'localhost' if not found
    _raw_password = os.getenv("DB_PASSWORD", "Ba@12345")
    db_password = urllib.parse.quote_plus(_raw_password)
    
    _db_host = os.getenv("DB_HOST", "127.0.0.1")
    _db_name = os.getenv("DB_NAME", "student_portal_db")

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:{db_password}@{_db_host}/{_db_name}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- JWT Settings ---
    # Use the secret from .env
    JWT_SECRET_KEY = os.getenv("JWT_SECRET", "default_secret_for_local_only") 
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = False  # Set to True only when you have HTTPS (Deployment)
    JWT_COOKIE_HTTPONLY = True
    JWT_COOKIE_SAMESITE = "Lax"
    JWT_COOKIE_CSRF_PROTECT = False 
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=2)

    # --- Flask-Mail Configuration ---
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USER")
    MAIL_PASSWORD = os.getenv("MAIL_PASS") 
    MAIL_DEFAULT_SENDER = ('Student Portal Admin', os.getenv("MAIL_USER"))
