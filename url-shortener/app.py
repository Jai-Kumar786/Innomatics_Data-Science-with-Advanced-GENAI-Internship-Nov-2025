from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import string
import random
from urllib.parse import urlparse
import requests

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///url_shortener.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Model
class URLMapping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(2048), nullable=False)
    shortened_url = db.Column(db.String(10), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    click_count = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'original_url': self.original_url,
            'shortened_url': self.shortened_url,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'click_count': self.click_count
        }

# Helper Functions
def generate_short_code(length=6):
    """Generate a random short code"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def is_valid_url(url):
    """Validate if the URL is properly formatted and accessible"""
    try:
        # Check if URL has proper scheme
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Parse the URL
        result = urlparse(url)
        
        # Check if it has both scheme and netloc (domain)
        if not all([result.scheme, result.netloc]):
            return False, "Invalid URL format"
        
        # Optional: Check if URL is reachable (commented out for performance)
        # try:
        #     response = requests.head(url, timeout=5, allow_redirects=True)
        #     if response.status_code < 400:
        #         return True, url
        #     else:
        #         return False, "URL returned error status code"
        # except requests.RequestException:
        #     return False, "URL is not reachable"
        
        return True, url
    except Exception as e:
        return False, str(e)

def get_or_create_short_url(original_url):
    """Get existing shortened URL or create a new one"""
    # Check if URL already exists
    existing = URLMapping.query.filter_by(original_url=original_url).first()
    if existing:
        return existing.shortened_url, False  # False = not newly created
    
    # Generate unique short code
    while True:
        short_code = generate_short_code()
        if not URLMapping.query.filter_by(shortened_url=short_code).first():
            break
    
    # Create new mapping
    new_mapping = URLMapping(original_url=original_url, shortened_url=short_code)
    db.session.add(new_mapping)
    db.session.commit()
    
    return short_code, True  # True = newly created

# Routes
@app.route('/')
def home():
    """Home page"""
    return render_template('index.html')

@app.route('/history')
def history():
    """History page"""
    return render_template('history.html')

@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    """API endpoint to shorten URL"""
    data = request.get_json()
    original_url = data.get('url', '').strip()
    
    if not original_url:
        return jsonify({'success': False, 'error': 'URL cannot be empty'}), 400
    
    # Validate URL
    is_valid, processed_url = is_valid_url(original_url)
    if not is_valid:
        return jsonify({'success': False, 'error': processed_url}), 400
    
    try:
        # Get or create shortened URL
        short_code, is_new = get_or_create_short_url(processed_url)
        
        # Get the full shortened URL (in production, use your domain)
        shortened_url = f"http://localhost:5000/s/{short_code}"
        
        status_msg = "New shortened URL created" if is_new else "URL already shortened"
        
        return jsonify({
            'success': True,
            'shortened_url': shortened_url,
            'short_code': short_code,
            'message': status_msg
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error: {str(e)}'}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """API endpoint to get all shortened URLs"""
    try:
        urls = URLMapping.query.order_by(URLMapping.created_at.desc()).all()
        return jsonify({
            'success': True,
            'data': [url.to_dict() for url in urls]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

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
        
        # Redirect to original URL
        from flask import redirect
        return redirect(mapping.original_url, code=302)
    
    except Exception as e:
        return render_template('error.html', error=str(e)), 500

@app.route('/api/delete/<int:url_id>', methods=['DELETE'])
def delete_url(url_id):
    """Delete a shortened URL from history"""
    try:
        url_mapping = URLMapping.query.get(url_id)
        
        if not url_mapping:
            return jsonify({'success': False, 'error': 'URL not found'}), 404
        
        db.session.delete(url_mapping)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'URL deleted successfully'}), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/clear-history', methods=['DELETE'])
def clear_all_history():
    """Clear all history"""
    try:
        URLMapping.query.delete()
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'All history cleared'}), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)