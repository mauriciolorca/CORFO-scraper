from flask import Blueprint, render_template
from flask_login import login_required, current_user
from ..models.user import Group, UserGroup

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    # Get user's groups
    user_groups = Group.query.join(UserGroup).filter(UserGroup.user_id == current_user.id).all()
    
    return render_template('dashboard.html', user_groups=user_groups)
