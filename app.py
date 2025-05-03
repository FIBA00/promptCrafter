import os
import logging
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_mail import Mail

from models import db, User
from config import config
from routes.auth import auth_bp
from routes.prompts import prompts_bp
from routes.main import main_bp
from routes.api import api_bp

# Initialize extensions
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
migrate = Migrate()
csrf = CSRFProtect()
cache = Cache()
mail = Mail()
limiter = Limiter(key_func=get_remote_address)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_name=None):
    """Application factory pattern for Flask."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Configure logging
    if not app.debug:
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    cache.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(prompts_bp, url_prefix='/prompts')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Create tables within app context
    with app.app_context():
        db.create_all()
    
    return app

# Create app instance for running directly
app = create_app()

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', 'True').lower() == 'true')
