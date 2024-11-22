from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models.user import Expense, Group, Balance, db
from datetime import datetime

expenses = Blueprint('expenses', __name__)

@expenses.route('/groups/<int:group_id>/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense(group_id):
    group = Group.query.get_or_404(group_id)
    
    # Verify user is a group member
    if current_user not in group.members:
        flash('You are not a member of this group')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        description = request.form.get('description')
        amount = float(request.form.get('amount'))
        split_type = request.form.get('split_type')
        
        # Create new expense
        new_expense = Expense(
            description=description,
            amount=amount,
            date=datetime.utcnow(),
            paid_by=current_user,
            group=group
        )
        db.session.add(new_expense)
        
        # Split expense based on type
        if split_type == 'equal':
            split_amount = amount / len(group.members)
            for member in group.members:
                if member != current_user:
                    balance = Balance.query.filter_by(user=member, group=group).first()
                    if not balance:
                        balance = Balance(user=member, group=group, amount_owed=0)
                        db.session.add(balance)
                    balance.amount_owed += split_amount
        
        db.session.commit()
        flash('Expense added successfully')
        return redirect(url_for('groups.group_details', group_id=group_id))
    
    return render_template('add_expense.html', group=group)

@expenses.route('/groups/<int:group_id>/settle_up')
@login_required
def settle_up(group_id):
    group = Group.query.get_or_404(group_id)
    
    # Calculate balances
    balances = Balance.query.filter_by(group=group, user=current_user).all()
    
    return render_template('settle_up.html', group=group, balances=balances)

@expenses.route('/groups/<int:group_id>/clear_balance/<int:balance_id>', methods=['POST'])
@login_required
def clear_balance(group_id, balance_id):
    group = Group.query.get_or_404(group_id)
    balance = Balance.query.get_or_404(balance_id)
    
    # Verify current user owns this balance
    if balance.user != current_user:
        flash('Unauthorized')
        return redirect(url_for('main.dashboard'))
    
    # Clear balance
    balance.amount_owed = 0
    db.session.commit()
    
    flash('Balance cleared')
    return redirect(url_for('expenses.settle_up', group_id=group_id))
