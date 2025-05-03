import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from dotenv import load_dotenv
import json
from utils import build_structured_prompt, build_natural_prompt

# Load environment variables
load_dotenv()

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///promptcrafter.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize login manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    prompts = db.relationship('Prompt', backref='author', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Prompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    role = db.Column(db.String(200))
    task = db.Column(db.Text)
    constraints = db.Column(db.Text)
    output = db.Column(db.String(100))
    personality = db.Column(db.String(200))
    structured_prompt = db.Column(db.Text)
    natural_prompt = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    return render_template('index.html', prefill=False)

@app.route('/generate', methods=['POST'])
def generate_prompt():
    form = request.form
    role = form['role']
    task = form['task']
    constraints = form['constraints']
    output = form['output']
    personality = form['personality']

    structured = build_structured_prompt(role, task, constraints, output, personality)
    natural = build_natural_prompt(role, task, constraints, output, personality)
    
    # If user is logged in, provide option to save
    save_option = current_user.is_authenticated if hasattr(current_user, 'is_authenticated') else False
    
    return render_template(
        'result.html', 
        structured=structured, 
        natural=natural, 
        save_option=save_option,
        role=role,
        task=task,
        constraints=constraints,
        output=output,
        personality=personality
    )

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Basic validation
        if not username or not email or not password:
            flash('All fields are required')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('home')
        return redirect(next_page)
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/save_prompt', methods=['POST'])
def save_prompt():
    # Check if user is authenticated
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'error': 'User not logged in'}), 401
    
    data = request.form
    
    title = data.get('title', 'Untitled Prompt')
    role = data.get('role')
    task = data.get('task')
    constraints = data.get('constraints')
    output = data.get('output')
    personality = data.get('personality')
    structured_prompt = data.get('structured_prompt')
    natural_prompt = data.get('natural_prompt')
    is_public = data.get('is_public', 'false').lower() == 'true'
    
    prompt = Prompt(
        title=title,
        role=role,
        task=task,
        constraints=constraints,
        output=output,
        personality=personality,
        structured_prompt=structured_prompt,
        natural_prompt=natural_prompt,
        is_public=is_public,
        user_id=current_user.id
    )
    
    db.session.add(prompt)
    db.session.commit()
    
    return jsonify({'success': True, 'prompt_id': prompt.id})

@app.route('/my_prompts')
@login_required
def my_prompts():
    prompts = Prompt.query.filter_by(user_id=current_user.id).order_by(Prompt.created_at.desc()).all()
    return render_template('my_prompts.html', prompts=prompts)

@app.route('/prompt/<int:prompt_id>')
def view_prompt(prompt_id):
    prompt = Prompt.query.get_or_404(prompt_id)
    
    # Check if prompt is private and not owned by current user
    if not prompt.is_public and (not current_user.is_authenticated or prompt.user_id != current_user.id):
        flash('You do not have permission to view this prompt')
        return redirect(url_for('home'))
    
    return render_template('view_prompt.html', prompt=prompt)

@app.route('/public_prompts')
def public_prompts():
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'newest')
    
    query = Prompt.query.filter_by(is_public=True)
    
    # Apply search if provided
    if search:
        query = query.filter(
            (Prompt.role.contains(search)) | 
            (Prompt.task.contains(search)) | 
            (Prompt.personality.contains(search)) |
            (Prompt.title.contains(search))
        )
    
    # Apply sorting
    if sort == 'oldest':
        query = query.order_by(Prompt.created_at.asc())
    else:
        query = query.order_by(Prompt.created_at.desc())
    
    prompts = query.limit(50).all()
    return render_template('public_prompts.html', prompts=prompts)

@app.route('/delete_prompt/<int:prompt_id>')
@login_required
def delete_prompt(prompt_id):
    prompt = Prompt.query.get_or_404(prompt_id)
    
    # Check if the current user owns the prompt
    if prompt.user_id != current_user.id:
        flash('You do not have permission to delete this prompt')
        return redirect(url_for('my_prompts'))
    
    db.session.delete(prompt)
    db.session.commit()
    
    flash('Prompt deleted successfully')
    return redirect(url_for('my_prompts'))

@app.route('/toggle_public/<int:prompt_id>', methods=['POST'])
@login_required
def toggle_public(prompt_id):
    prompt = Prompt.query.get_or_404(prompt_id)
    
    # Check if the current user owns the prompt
    if prompt.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Permission denied'}), 403
    
    data = request.get_json()
    is_public = data.get('is_public', False)
    
    prompt.is_public = is_public
    db.session.commit()
    
    return jsonify({'success': True})

# API Endpoints
@app.route('/api/generate', methods=['POST'])
def api_generate_prompt():
    try:
        data = request.json
        role = data.get('role')
        task = data.get('task')
        constraints = data.get('constraints', '')
        output = data.get('output')
        personality = data.get('personality')
        
        if not all([role, task, output, personality]):
            return jsonify({'error': 'Missing required fields'}), 400
            
        structured = build_structured_prompt(role, task, constraints, output, personality)
        natural = build_natural_prompt(role, task, constraints, output, personality)
        
        return jsonify({
            'structured_prompt': structured,
            'natural_prompt': natural
        })
    except Exception as e:
        app.logger.error(f"API error: {str(e)}")
        return jsonify({'error': 'Server error'}), 500

# Advanced templates route
@app.route('/advanced_templates')
def advanced_templates():
    """Route for displaying advanced prompt templates for specific use cases."""
    return render_template('advanced_templates.html')

@app.route('/generate_template/<template_type>')
def generate_template(template_type):
    """Generate a specialized template based on the template type."""
    # Dictionary of template details
    templates = {
        'code-refactoring': {
            'title': 'Code Refactoring Template',
            'role': 'Senior Software Engineer with refactoring expertise',
            'task': 'Refactor the provided code to improve its quality, maintainability, and performance without changing its functionality.',
            'constraints': 'Maintain backward compatibility. Consider readability and maintainability as primary goals. Adhere to language-specific best practices.',
            'output': 'step-by-step',
            'personality': 'Methodical, educational, and focused on code quality principles'
        },
        'ai-architecture': {
            'title': 'AI System Architecture Template',
            'role': 'AI Systems Architect',
            'task': 'Design a robust architecture for an AI system, including data processing, model training, deployment, and monitoring components.',
            'constraints': 'Consider scalability, maintainability, and cost-effectiveness. Address potential ethical concerns and bias mitigation strategies.',
            'output': 'comparison format',
            'personality': 'Forward-thinking, responsible, and focused on robust engineering practices'
        },
        'technical-docs': {
            'title': 'Technical Documentation Template',
            'role': 'Technical Documentation Specialist',
            'task': 'Create comprehensive technical documentation for the specified system, including usage examples, architecture diagrams, and troubleshooting guides.',
            'constraints': 'Documentation should be clear for both technical and non-technical audiences. Include practical examples and visual aids where appropriate.',
            'output': 'tutorial style',
            'personality': 'Clear, thorough, and focused on user understanding'
        },
        'testing-strategy': {
            'title': 'Testing Strategy Template',
            'role': 'QA Lead and Testing Strategist',
            'task': 'Develop a comprehensive testing strategy for the specified system, including unit tests, integration tests, and end-to-end tests.',
            'constraints': 'Consider test coverage, maintainability of tests, and integration with CI/CD pipelines. Address both functional and non-functional requirements.',
            'output': 'step-by-step',
            'personality': 'Meticulous, quality-focused, and systematic'
        },
        'interview-prep': {
            'title': 'Technical Interview Preparation Template',
            'role': 'Technical Interview Coach',
            'task': 'Prepare a comprehensive guide for technical interview preparation, covering algorithms, data structures, system design, and behavioral questions.',
            'constraints': 'Focus on practical advice and common patterns. Provide example questions and detailed solutions.',
            'output': 'question and answer',
            'personality': 'Encouraging, practical, and focused on building confidence'
        },
        'api-design': {
            'title': 'API Design Template',
            'role': 'API Design Architect',
            'task': 'Design a robust, secure, and scalable API for the specified use case, with clear endpoints, authentication, and error handling.',
            'constraints': 'Follow RESTful principles. Consider versioning, documentation, and developer experience. Address security concerns.',
            'output': 'best practices',
            'personality': 'Detail-oriented, security-conscious, and focused on best practices'
        }
    }
    
    # Check if the template type exists
    if template_type not in templates:
        flash('Template not found')
        return redirect(url_for('advanced_templates'))
    
    # Get the template details
    template = templates[template_type]
    
    # Pre-fill the form with template values
    return render_template(
        'index.html', 
        prefill=True,
        template_title=template['title'],
        role=template['role'],
        task=template['task'],
        constraints=template['constraints'],
        output=template['output'],
        personality=template['personality']
    )

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', 'True').lower() == 'true')
