from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import string
import random
from urllib.parse import urlparse
from functools import wraps
from datetime import datetime

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///url_shortener_auth.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

db = SQLAlchemy(app)

# ==================== DATABASE MODELS ====================

class User(db.Model):
    """User model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(9), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with URLMapping
    urls = db.relationship('URLMapping', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class URLMapping(db.Model):
    """URL mapping model (user-specific)"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    original_url = db.Column(db.String(2048), nullable=False)
    shortened_url = db.Column(db.String(10), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    click_count = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'original_url': self.original_url,
            'shortened_url': self.shortened_url,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'click_count': self.click_count
        }

# ==================== HELPER FUNCTIONS ====================

def generate_short_code(length=6):
    """Generate a random short code"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def is_valid_username(username):
    """Validate username (5-9 characters, alphanumeric)"""
    if not username:
        return False, "Username cannot be empty"
    
    if len(username) < 5 or len(username) > 9:
        return False, "Username must be between 5 to 9 characters long"
    
    if not username.isalnum():
        return False, "Username must contain only alphanumeric characters"
    
    return True, ""


def is_valid_password(password):
    """Validate password"""
    if not password:
        return False, "Password cannot be empty"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    return True, ""


def is_valid_url(url):
    """Validate if the URL is properly formatted"""
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        result = urlparse(url)
        
        if not all([result.scheme, result.netloc]):
            return False, "Invalid URL format"
        
        return True, url
    except Exception as e:
        return False, str(e)


def login_required(f):
    """Decorator to check if user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== AUTHENTICATION ROUTES ====================

@app.route('/')
def index():
    """Home/Login page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('auth.html')


@app.route('/api/signup', methods=['POST'])
def signup():
    """User signup endpoint"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    confirm_password = data.get('confirm_password', '').strip()
    
    # Validate username
    is_valid, error_msg = is_valid_username(username)
    if not is_valid:
        return jsonify({'success': False, 'error': error_msg}), 400
    
    # Check if username already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'error': 'This username already exists...'}), 400
    
    # Validate password
    is_valid, error_msg = is_valid_password(password)
    if not is_valid:
        return jsonify({'success': False, 'error': error_msg}), 400
    
    # Check if passwords match
    if password != confirm_password:
        return jsonify({'success': False, 'error': 'Passwords do not match'}), 400
    
    try:
        # Create new user
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully! Please login.'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({'success': False, 'error': 'Username and password are required'}), 400
    
    # Find user
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        return jsonify({'success': False, 'error': 'Invalid username or password'}), 401
    
    try:
        # Create session
        session['user_id'] = user.id
        session['username'] = user.username
        
        return jsonify({
            'success': True,
            'message': 'Logged in successfully!',
            'username': user.username
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/logout', methods=['POST'])
def logout():
    """User logout endpoint"""
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Logged out successfully!'
    }), 200


@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    """Check if user is logged in"""
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'username': session.get('username')
        }), 200
    return jsonify({'logged_in': False}), 200


# ==================== URL SHORTENING ROUTES ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard page (URL shortener)"""
    return render_template('dashboard.html', username=session.get('username'))


@app.route('/api/shorten', methods=['POST'])
@login_required
def shorten_url():
    """API endpoint to shorten URL"""
    data = request.get_json()
    original_url = data.get('url', '').strip()
    user_id = session.get('user_id')
    
    if not original_url:
        return jsonify({'success': False, 'error': 'URL cannot be empty'}), 400
    
    # Validate URL
    is_valid, processed_url = is_valid_url(original_url)
    if not is_valid:
        return jsonify({'success': False, 'error': processed_url}), 400
    
    try:
        # Check if user already shortened this URL
        existing = URLMapping.query.filter_by(
            user_id=user_id,
            original_url=processed_url
        ).first()
        
        if existing:
            shortened_url = f"http://localhost:5000/s/{existing.shortened_url}"
            return jsonify({
                'success': True,
                'shortened_url': shortened_url,
                'short_code': existing.shortened_url,
                'message': 'URL already shortened'
            }), 200
        
        # Generate unique short code
        while True:
            short_code = generate_short_code()
            if not URLMapping.query.filter_by(shortened_url=short_code).first():
                break
        
        # Create new mapping
        new_mapping = URLMapping(
            user_id=user_id,
            original_url=processed_url,
            shortened_url=short_code
        )
        db.session.add(new_mapping)
        db.session.commit()
        
        shortened_url = f"http://localhost:5000/s/{short_code}"
        
        return jsonify({
            'success': True,
            'shortened_url': shortened_url,
            'short_code': short_code,
            'message': 'New shortened URL created'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Error: {str(e)}'}), 500


@app.route('/api/history', methods=['GET'])
@login_required
def get_history():
    """API endpoint to get user's URLs"""
    try:
        user_id = session.get('user_id')
        urls = URLMapping.query.filter_by(user_id=user_id).order_by(
            URLMapping.created_at.desc()
        ).all()
        
        return jsonify({
            'success': True,
            'data': [url.to_dict() for url in urls]
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/delete/<int:url_id>', methods=['DELETE'])
@login_required
def delete_url(url_id):
    """API endpoint to delete a URL"""
    try:
        user_id = session.get('user_id')
        url_mapping = URLMapping.query.filter_by(
            id=url_id,
            user_id=user_id
        ).first()
        
        if not url_mapping:
            return jsonify({'success': False, 'error': 'URL not found'}), 404
        
        db.session.delete(url_mapping)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'URL deleted successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/clear-history', methods=['DELETE'])
@login_required
def clear_all_history():
    """API endpoint to clear all user's URLs"""
    try:
        user_id = session.get('user_id')
        URLMapping.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'All history cleared'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== REDIRECT ROUTE ====================

@app.route('/s/<short_code>')
def redirect_to_original(short_code):
    """Redirect to original URL"""
    try:
        mapping = URLMapping.query.filter_by(shortened_url=short_code).first()
        
        if not mapping:
            return render_template('404.html'), 404
        
        # Increment click count
        mapping.click_count += 1
        db.session.commit()
        
        from flask import redirect
        return redirect(mapping.original_url, code=302)
    
    except Exception as e:
        return render_template('error.html', error=str(e)), 500


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('error.html', error=str(error)), 500


# ==================== DATABASE INITIALIZATION ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)