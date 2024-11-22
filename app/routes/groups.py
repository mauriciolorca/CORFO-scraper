from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models.user import Group, User, UserGroup, db
from datetime import datetime

groups = Blueprint('groups', __name__)

@groups.route('/groups/create', methods=['GET', 'POST'])
@login_required
def create_group():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        # Create new group
        new_group = Group(name=name, description=description)
        db.session.add(new_group)
        
        # Add current user as group creator/member
        user_group = UserGroup(user_id=current_user.id, group_id=new_group.id)
        db.session.add(user_group)
        
        db.session.commit()
        
        flash('Group created successfully')
        return redirect(url_for('main.dashboard'))
    
    return render_template('create_group.html')

@groups.route('/groups/<int:group_id>/add_member', methods=['POST'])
@login_required
def add_member(group_id):
    group = Group.query.get_or_404(group_id)
    email = request.form.get('email')
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        flash('User not found')
        return redirect(url_for('groups.group_details', group_id=group_id))
    
    # Check if user is already in the group
    existing_membership = UserGroup.query.filter_by(user_id=user.id, group_id=group_id).first()
    
    if existing_membership:
        flash('User is already a member of this group')
    else:
        user_group = UserGroup(user_id=user.id, group_id=group_id)
        db.session.add(user_group)
        db.session.commit()
        flash('Member added successfully')
    
    return redirect(url_for('groups.group_details', group_id=group_id))

@groups.route('/groups/<int:group_id>')
@login_required
def group_details(group_id):
    group = Group.query.get_or_404(group_id)
    
    # Check if user is a member of the group
    is_member = any(user.id == current_user.id for user in group.members)
    
    if not is_member:
        flash('You are not a member of this group')
        return redirect(url_for('main.dashboard'))
    
    return render_template('group_details.html', group=group)
