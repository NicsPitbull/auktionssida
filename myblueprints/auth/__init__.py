# myblueprints/auth/__init__.py
"""
🔐 AUTH BLUEPRINT - User authentication functionality

SYFTE: Hanterar användarautentisering:
- Användarregistrering
- Inloggning/utloggning
- Sessionshantering
- Användarprofilhantering
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from database import db

# Skapa auth blueprint
auth_bp = Blueprint(
    'auth',
    __name__,
    url_prefix='/auth'
)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password are required.', 'error')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.first_name}!', 'success')
            
            # Redirect to admin dashboard if admin, otherwise to auctions
            next_page = request.args.get('next')
            if user.is_admin:
                return redirect(next_page or url_for('admin.dashboard'))
            else:
                return redirect(next_page or url_for('auctions.browse'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    user_name = current_user.first_name
    logout_user()
    flash(f'Goodbye, {user_name}!', 'info')
    return redirect(url_for('auctions.browse'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        # Validation
        if not all([email, password, confirm_password, first_name, last_name]):
            flash('All fields are required.', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('auth/register.html')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use a different email.', 'error')
            return render_template('auth/register.html')
        
        # Create new user
        try:
            new_user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_admin=False  # Regular users are not admin by default
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')

# Admin required decorator
def admin_required(f):
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin:
            flash('Admin access required.', 'error')
            return redirect(url_for('auctions.browse'))
        
        return f(*args, **kwargs)
    
    return decorated_function
