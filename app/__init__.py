import os
from flask import Flask, jsonify, render_template
from .config import Config
from flask_cors import CORS
from .extensions import db, jwt, cors, mail
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
    # Point to the 'frontend' folder sitting outside the 'app' folder
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

    # Auto-migrate (Kept your logic but wrapped in app_context)
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE user ADD COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1"))
                conn.commit()
        except Exception:
            pass 
        try:
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE user ADD COLUMN activation_token VARCHAR(100) NULL"))
                conn.commit()
        except Exception:
            pass 
    
    # Update CORS for production (Allow your Render URL)
    CORS(
        app,
        supports_credentials=True,
        resources={r"/*": {"origins": ["*"]}} # Change this to your specific Render URL later for security
    )

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

    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({"error": "The file is too large! Max 20MB."}), 413

    # --- UI ROUTES ---
    @app.route("/")
    def home():
        # This will now look for index.html inside the frontend folder
        return render_template("index.html")

    @app.route('/login')
    def serve_login():
        return render_template('login.html')

    return app