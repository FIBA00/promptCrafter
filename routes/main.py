from flask import Blueprint, render_template, request
from flask_login import current_user

# Initialize blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('index.html', prefill=False)

@main_bp.route('/advanced_templates')
def advanced_templates():
    """Route for displaying advanced prompt templates for specific use cases."""
    return render_template('advanced_templates.html')

@main_bp.route('/generate_template/<template_type>')
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
        return redirect(url_for('main.advanced_templates'))
    
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
@main_bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@main_bp.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500 