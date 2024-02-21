from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from yourapplication.config import Config  # Ensure this path matches your project structure

# Extension instances creation
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    limiter.init_app(app)

    # Configure Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Register blueprints
    from yourapplication.auth.routes import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from yourapplication.main.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Additional configuration or blueprint registration goes here

    return app
