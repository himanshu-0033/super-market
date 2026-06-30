import os
from flask import Flask, flash, redirect, url_for
from flask_login import LoginManager
from backend.models import db, User
from backend.config import Config

login_manager = LoginManager()

def create_app():
    # Set the template and static folders to the new frontend directory
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    template_dir = os.path.join(base_dir, 'frontend', 'templates')
    static_dir = os.path.join(base_dir, 'frontend', 'static')

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(Config)

    # Make the database path point to instance folder in the root directory (so it doesn't try to create one inside backend/)
    # Wait, Config class uses os.environ.get("DATABASE_URL", "sqlite:///pos.db") which will just create it in the instance folder of the app context.
    # We should make sure the instance folder stays at the root. Flask defaults instance_path to next to the package.
    # Let's specify instance_path to be in the root directory
    app.instance_path = os.path.join(base_dir, 'instance')
    
    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import routes
    from backend.routes.auth import auth_bp
    from backend.routes.inventory import inventory_bp
    from backend.routes.pos import pos_bp
    from backend.routes.dashboard import dashboard_bp

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(pos_bp)
    app.register_blueprint(dashboard_bp)

    return app
