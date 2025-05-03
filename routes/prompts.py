from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Prompt
from utils import build_structured_prompt, build_natural_prompt
from sqlalchemy import or_

# Initialize blueprint
prompts_bp = Blueprint('prompts', __name__)

# Constants
PROMPTS_PER_PAGE = 10

@prompts_bp.route('/generate', methods=['POST'])
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

@prompts_bp.route('/save_prompt', methods=['POST'])
@login_required
def save_prompt():
    data = request.form
    
    # Validate required fields
    required_fields = ['role', 'task', 'output', 'personality', 'structured_prompt', 'natural_prompt']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
    
    title = data.get('title', 'Untitled Prompt')
    role = data.get('role')
    task = data.get('task')
    constraints = data.get('constraints', '')
    output = data.get('output')
    personality = data.get('personality')
    structured_prompt = data.get('structured_prompt')
    natural_prompt = data.get('natural_prompt')
    is_public = data.get('is_public', 'false').lower() == 'true'
    tags = data.get('tags', '')
    
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
        tags=tags,
        user_id=current_user.id
    )
    
    db.session.add(prompt)
    db.session.commit()
    
    return jsonify({'success': True, 'prompt_id': prompt.id})

@prompts_bp.route('/my_prompts')
@login_required
def my_prompts():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Prompt.query.filter_by(user_id=current_user.id)
    
    # Apply search if provided
    if search:
        query = query.filter(
            or_(
                Prompt.title.contains(search),
                Prompt.role.contains(search),
                Prompt.task.contains(search),
                Prompt.tags.contains(search)
            )
        )
    
    # Apply pagination
    pagination = query.order_by(Prompt.created_at.desc()).paginate(
        page=page, 
        per_page=PROMPTS_PER_PAGE,
        error_out=False
    )
    
    prompts = pagination.items
    
    return render_template(
        'my_prompts.html', 
        prompts=prompts, 
        pagination=pagination,
        search=search
    )

@prompts_bp.route('/prompt/<int:prompt_id>')
def view_prompt(prompt_id):
    prompt = Prompt.query.get_or_404(prompt_id)
    
    # Check if prompt is private and not owned by current user
    if not prompt.is_public and (not current_user.is_authenticated or prompt.user_id != current_user.id):
        flash('You do not have permission to view this prompt')
        return redirect(url_for('main.home'))
    
    return render_template('view_prompt.html', prompt=prompt)

@prompts_bp.route('/edit_prompt/<int:prompt_id>', methods=['GET', 'POST'])
@login_required
def edit_prompt(prompt_id):
    prompt = Prompt.query.get_or_404(prompt_id)
    
    # Check if the current user owns the prompt
    if prompt.user_id != current_user.id:
        flash('You do not have permission to edit this prompt')
        return redirect(url_for('prompts.my_prompts'))
    
    if request.method == 'POST':
        # Update prompt with form data
        prompt.title = request.form.get('title', 'Untitled Prompt')
        prompt.role = request.form.get('role')
        prompt.task = request.form.get('task')
        prompt.constraints = request.form.get('constraints', '')
        prompt.output = request.form.get('output')
        prompt.personality = request.form.get('personality')
        prompt.is_public = request.form.get('is_public', 'false').lower() == 'true'
        prompt.tags = request.form.get('tags', '')
        
        # Regenerate prompt texts
        prompt.structured_prompt = build_structured_prompt(
            prompt.role, prompt.task, prompt.constraints, prompt.output, prompt.personality
        )
        prompt.natural_prompt = build_natural_prompt(
            prompt.role, prompt.task, prompt.constraints, prompt.output, prompt.personality
        )
        
        db.session.commit()
        flash('Prompt updated successfully')
        return redirect(url_for('prompts.view_prompt', prompt_id=prompt.id))
    
    return render_template('edit_prompt.html', prompt=prompt)

@prompts_bp.route('/delete_prompt/<int:prompt_id>', methods=['GET', 'POST'])
@login_required
def delete_prompt(prompt_id):
    prompt = Prompt.query.get_or_404(prompt_id)
    
    # Check if the current user owns the prompt
    if prompt.user_id != current_user.id:
        flash('You do not have permission to delete this prompt')
        return redirect(url_for('prompts.my_prompts'))
    
    if request.method == 'POST':
        db.session.delete(prompt)
        db.session.commit()
        flash('Prompt deleted successfully')
        return redirect(url_for('prompts.my_prompts'))
    
    # Confirm deletion page
    return render_template('confirm_delete.html', prompt=prompt)

@prompts_bp.route('/toggle_public/<int:prompt_id>', methods=['POST'])
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

@prompts_bp.route('/public_prompts')
def public_prompts():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'newest')
    tag_filter = request.args.get('tag', '')
    
    query = Prompt.query.filter_by(is_public=True)
    
    # Apply search if provided
    if search:
        query = query.filter(
            or_(
                Prompt.role.contains(search),
                Prompt.task.contains(search),
                Prompt.personality.contains(search),
                Prompt.title.contains(search)
            )
        )
    
    # Apply tag filter if provided
    if tag_filter:
        query = query.filter(Prompt.tags.contains(tag_filter))
    
    # Apply sorting
    if sort == 'oldest':
        query = query.order_by(Prompt.created_at.asc())
    else:
        query = query.order_by(Prompt.created_at.desc())
    
    # Apply pagination
    pagination = query.paginate(
        page=page, 
        per_page=PROMPTS_PER_PAGE,
        error_out=False
    )
    
    prompts = pagination.items
    
    # Get all unique tags for filtering
    all_tags = set()
    for prompt in Prompt.query.filter_by(is_public=True).all():
        if prompt.tags:
            tags = [tag.strip() for tag in prompt.tags.split(',')]
            all_tags.update(tags)
    
    return render_template(
        'public_prompts.html', 
        prompts=prompts,
        pagination=pagination,
        search=search,
        sort=sort,
        tag_filter=tag_filter,
        all_tags=sorted(all_tags)
    ) 