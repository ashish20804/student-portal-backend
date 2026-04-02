import os
from flask import Flask, jsonify, render_template, send_from_directory
from .config import Config
from flask_cors import CORS
from .extensions import db, jwt, mail # Removed 'cors' from extensions as we initialize it here
from .routes.auth_routes import auth_bp
from .routes.test_routes import test_bp
from app.routes.student_routes import student_bp
from app.routes.placement_routes import placement_bp
from app.routes.higherstudies_routes import higherstudies_bp
from app.routes.activity_routes import activity_bp
from app.routes.committee_routes import committee_bp
from app.routes.message_routes import message_bp
from app.routes.dashboard_routes import dashboard_bp
from app.routes.faculty_routes import faculty_bp
from app.routes.admin_routes import admin_bp
from app.routes.report_routes import report_bp
from app.routes.testimonial_routes import testimonial_bp
from app.routes.announcement_routes import announcement_bp

def create_app():
    # --- UI PATH CONFIGURATION ---
    # Find the 'frontend' folder relative to this file
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

    app = Flask(__name__, 
                template_folder=frontend_dir, 
                static_folder=frontend_dir, 
                static_url_path='') 

    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    # --- SAFE DATABASE MIGRATIONS ---
    # We wrap this in a broader try block to prevent the app from crashing on Render 
    # if the database connection isn't ready immediately.
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                # Use text() for raw SQL and commit explicitly
                conn.execute(db.text("ALTER TABLE user ADD COLUMN IF NOT EXISTS is_active TINYINT(1) NOT NULL DEFAULT 1"))
                conn.execute(db.text("ALTER TABLE user ADD COLUMN IF NOT EXISTS activation_token VARCHAR(100) NULL"))
                conn.commit()
        except Exception as e:
            # We log the error but don't stop the app from starting
            print(f"Migration skipped or failed: {e}")
    
    # Update CORS for production (Allowing all for now to ensure UI connectivity)
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(test_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(placement_bp)
    app.register_blueprint(higherstudies_bp)
    app.register_blueprint(activity_bp)
    app.register_blueprint(committee_bp)
    app.register_blueprint(message_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(faculty_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(testimonial_bp)
    app.register_blueprint(announcement_bp)

    # --- ERROR HANDLERS ---
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({"error": "The file is too large! Max 20MB."}), 413

    # --- UI & STATIC FILE ROUTES ---
    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route('/login')
    def serve_login():
        return render_template('login.html')

    # Catch-all to serve other HTML files directly if they exist in /frontend
    @app.route('/<path:path>')
    def serve_static(path):
        if path.endswith(".html"):
            return render_template(path)
        return send_from_directory(frontend_dir, path)

    return app