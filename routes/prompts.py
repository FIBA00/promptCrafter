from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from extensions import db
from models import Prompt
from utils import build_structured_prompt, build_natural_prompt
from sqlalchemy import or_

# Initialize blueprint
prompts_bp = Blueprint('prompts', __name__)

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

    return render_template(
        'result.html',
        structured=structured,
        natural=natural,
        role=role,
        task=task,
        constraints=constraints,
        output=output,
        personality=personality
    )

@prompts_bp.route('/public_prompts')
def public_prompts():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'newest')
    tag_filter = request.args.get('tag', '')

    query = Prompt.query.filter_by(is_public=True)

    if search:
        query = query.filter(
            or_(
                Prompt.role.contains(search),
                Prompt.task.contains(search),
                Prompt.personality.contains(search),
                Prompt.title.contains(search),
                Prompt.tags.contains(search)
            )
        )

    if tag_filter:
        query = query.filter(Prompt.tags.contains(tag_filter))

    if sort == 'oldest':
        query = query.order_by(Prompt.created_at.asc())
    else:
        query = query.order_by(Prompt.created_at.desc())

    pagination = query.paginate(
        page=page,
        per_page=10,
        error_out=False
    )

    prompts = pagination.items

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