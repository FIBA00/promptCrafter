import os
import logging
from flask import Flask
from extensions import db, migrate, login_manager
from config import config
from routes.prompts import prompts_bp
from routes.main import main_bp
from routes.api import api_bp
from threading import Thread
import waitress
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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

def run_development_server():
    """Run the development server"""
    app = create_app('development')
    port = app.config.get('PORT', 5002)
    app.run(debug=app.config.get('DEBUG', True), port=port)

def run_production_server():
    """Run the production waitress server"""
    app = create_app('production')
    
    # Get configuration from environment variables
    port = app.config.get('PORT', 5002)
    host = os.environ.get('WAITRESS_HOST', '0.0.0.0')
    threads = int(os.environ.get('WAITRESS_THREADS', 4))
    
    # Print server information
    print(f"Starting production server on {host}:{port} with {threads} threads")
    
    # Explicit production server configuration
    waitress.serve(
        app,
        host=host, 
        port=port,
        threads=threads,
        ident=None  # Disables server identification
    )

if __name__ == '__main__':
    # Use the environment to determine which server to run
    env = os.environ.get('FLASK_ENV', 'production')
    
    if env.lower() == 'development':
        run_development_server()
    else:
        run_production_server()
 