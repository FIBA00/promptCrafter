from flask import Blueprint, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils import build_structured_prompt, build_natural_prompt
from models import db, Prompt, User
from flask_login import current_user
import logging

# Initialize blueprint
api_bp = Blueprint('api', __name__)

# Initialize limiter for rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@api_bp.route('/generate', methods=['POST'])
@limiter.limit("30 per minute")
def api_generate_prompt():
    try:
        # Check for valid JSON payload
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
            
        data = request.json
        role = data.get('role')
        task = data.get('task')
        constraints = data.get('constraints', '')
        output = data.get('output')
        personality = data.get('personality')
        
        # Validate required fields
        if not all([role, task, output, personality]):
            missing_fields = []
            if not role: missing_fields.append('role')
            if not task: missing_fields.append('task')
            if not output: missing_fields.append('output')
            if not personality: missing_fields.append('personality')
            
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400
            
        structured = build_structured_prompt(role, task, constraints, output, personality)
        natural = build_natural_prompt(role, task, constraints, output, personality)
        
        return jsonify({
            'structured_prompt': structured,
            'natural_prompt': natural
        })
    except Exception as e:
        logging.error(f"API error: {str(e)}")
        return jsonify({'error': 'Server error', 'details': str(e)}), 500

@api_bp.route('/prompts', methods=['GET'])
@limiter.limit("100 per minute")
def api_get_prompts():
    """Get public prompts with pagination and filtering options"""
    try:
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 50)  # Cap at 50 items
        
        # Filter parameters
        search = request.args.get('search', '')
        sort = request.args.get('sort', 'newest')
        tag = request.args.get('tag', '')
        
        # Build query
        query = Prompt.query.filter_by(is_public=True)
        
        # Apply search filter
        if search:
            query = query.filter(
                (Prompt.title.contains(search)) |
                (Prompt.role.contains(search)) |
                (Prompt.task.contains(search)) |
                (Prompt.tags.contains(search))
            )
        
        # Apply tag filter
        if tag:
            query = query.filter(Prompt.tags.contains(tag))
        
        # Apply sorting
        if sort == 'oldest':
            query = query.order_by(Prompt.created_at.asc())
        else:
            query = query.order_by(Prompt.created_at.desc())
        
        # Execute pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Format results
        prompts = []
        for prompt in pagination.items:
            author = User.query.get(prompt.user_id)
            prompts.append({
                'id': prompt.id,
                'title': prompt.title,
                'role': prompt.role,
                'task': prompt.task,
                'constraints': prompt.constraints,
                'output': prompt.output,
                'personality': prompt.personality,
                'structured_prompt': prompt.structured_prompt,
                'natural_prompt': prompt.natural_prompt,
                'tags': prompt.tags.split(',') if prompt.tags else [],
                'created_at': prompt.created_at.isoformat(),
                'author': author.username if author else 'Unknown'
            })
        
        return jsonify({
            'prompts': prompts,
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        })
    except Exception as e:
        logging.error(f"API error: {str(e)}")
        return jsonify({'error': 'Server error', 'details': str(e)}), 500

@api_bp.route('/prompt/<int:prompt_id>', methods=['GET'])
def api_get_prompt(prompt_id):
    """Get a single prompt by ID"""
    try:
        prompt = Prompt.query.get_or_404(prompt_id)
        
        # Check if prompt is private
        if not prompt.is_public:
            if not current_user.is_authenticated or prompt.user_id != current_user.id:
                return jsonify({'error': 'Not authorized to view this prompt'}), 403
        
        author = User.query.get(prompt.user_id)
        
        return jsonify({
            'id': prompt.id,
            'title': prompt.title,
            'role': prompt.role,
            'task': prompt.task,
            'constraints': prompt.constraints,
            'output': prompt.output,
            'personality': prompt.personality,
            'structured_prompt': prompt.structured_prompt,
            'natural_prompt': prompt.natural_prompt,
            'tags': prompt.tags.split(',') if prompt.tags else [],
            'is_public': prompt.is_public,
            'created_at': prompt.created_at.isoformat(),
            'updated_at': prompt.updated_at.isoformat() if prompt.updated_at else None,
            'author': author.username if author else 'Unknown'
        })
    except Exception as e:
        logging.error(f"API error: {str(e)}")
        return jsonify({'error': 'Server error', 'details': str(e)}), 500 