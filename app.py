import os
import logging
from flask import Flask
from extensions import db, migrate, login_manager
from config import config
from routes.prompts import prompts_bp
from routes.main import main_bp
from routes.api import api_bp

def create_app(config_name=None):
    """Application factory pattern for Flask."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Runtime check for SECRET_KEY in production
    if config_name == 'production' and not app.config.get('SECRET_KEY'):
        raise ValueError("No SECRET_KEY set for production environment")
    
    # Configure logging
    if not app.debug:
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Set up user loader for Flask-Login
    from models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(prompts_bp, url_prefix='/prompts')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    return app

# Create app instance for running directly
app = create_app()

if __name__ == '__main__':
    # Use port 5002 to avoid conflict with port 5000 that's already in use
    app.run(debug=os.environ.get('FLASK_DEBUG', 'True').lower() == 'true', port=5002)
