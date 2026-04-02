import os
import urllib.parse
import datetime
from dotenv import load_dotenv

# This looks for the file named exactly ".env" in your folder
load_dotenv() 

class Config:
    # --- Database Configuration ---
    # 1. We pull everything from Environment Variables (Render Dashboard)
    # 2. We provide local fallbacks so it still works on your computer
    db_user = os.getenv("DB_USER", "root")
    _raw_password = os.getenv("DB_PASSWORD", "Ba@12345")
    db_password = urllib.parse.quote_plus(_raw_password)
    
    db_host = os.getenv("DB_HOST", "127.0.0.1")
    db_name = os.getenv("DB_NAME", "student_portal_db")
    db_port = os.getenv("DB_PORT", "3306") # Default MySQL port is 3306

    # IMPORTANT: Added {db_user} and {db_port} to the string
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- JWT Settings ---
    JWT_SECRET_KEY = os.getenv("JWT_SECRET", "default_secret_for_local_only") 
    JWT_TOKEN_LOCATION = ["cookies"]
    
    # Render uses HTTPS, so this MUST be True in production
    # We check if we are on Render by looking for the RENDER environment variable
    JWT_COOKIE_SECURE = os.getenv("RENDER", "False").lower() == "true"
    
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