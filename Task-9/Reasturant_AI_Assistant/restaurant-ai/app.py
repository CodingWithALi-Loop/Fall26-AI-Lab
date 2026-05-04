from pathlib import Path
from flask import Flask, request, jsonify, render_template
from inventory.conversation_manager import ConversationManager
import sqlite3
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production-12345')
conversation_manager = ConversationManager()

# Database initialization
def init_db():
    """Initialize the database with users table."""
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      email TEXT UNIQUE NOT NULL,
                      password_hash TEXT NOT NULL,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error initializing database: {e}")

# Initialize database on startup
init_db()

def hash_password(password):
    """Hash a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token(user_id, user_email):
    """Generate a JWT token."""
    payload = {
        'user_id': user_id,
        'email': user_email,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    """Verify a JWT token."""
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except:
        return None

@app.route("/auth/login", methods=["POST"])
def login():
    """Login endpoint."""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT id, name, email, password_hash FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()
        
        if not user:
            return jsonify({'message': 'Invalid email or password'}), 401
        
        user_id, name, user_email, password_hash = user
        if hash_password(password) != password_hash:
            return jsonify({'message': 'Invalid email or password'}), 401
        
        token = generate_token(user_id, user_email)
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user_id,
                'name': name,
                'email': user_email
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Server error: {str(e)}'}), 500

@app.route("/auth/signup", methods=["POST"])
def signup():
    """Signup endpoint."""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not name or not email or not password:
            return jsonify({'message': 'Name, email, and password are required'}), 400
        
        if len(password) < 6:
            return jsonify({'message': 'Password must be at least 6 characters'}), 400
        
        if '@' not in email:
            return jsonify({'message': 'Invalid email format'}), 400
        
        password_hash = hash_password(password)
        
        try:
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute('INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
                     (name, email, password_hash))
            conn.commit()
            user_id = c.lastrowid
            conn.close()
            
            token = generate_token(user_id, email)
            return jsonify({
                'message': 'Account created successfully',
                'token': token,
                'user': {
                    'id': user_id,
                    'name': name,
                    'email': email
                }
            }), 201
            
        except sqlite3.IntegrityError:
            return jsonify({'message': 'Email already registered'}), 409
            
    except Exception as e:
        return jsonify({'message': f'Server error: {str(e)}'}), 500

@app.route("/auth/validate", methods=["POST"])
def validate_auth():
    """Validate user token."""
    try:
        data = request.get_json()
        token = data.get('token', '')
        
        if not token:
            return jsonify({'valid': False}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'valid': False}), 401
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT id, name, email FROM users WHERE id = ?', (payload['user_id'],))
        user = c.fetchone()
        conn.close()
        
        if user:
            user_id, name, email = user
            return jsonify({
                'valid': True,
                'user': {
                    'id': user_id,
                    'name': name,
                    'email': email
                }
            }), 200
        else:
            return jsonify({'valid': False}), 401
            
    except Exception as e:
        return jsonify({'valid': False, 'message': str(e)}), 401

@app.route("/login", methods=["GET"])
def login_page():
    """Serve login page."""
    return render_template("login.html")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}
    user_query = payload.get("query") or request.form.get("query", "")
    session_id = payload.get("session_id", "default_session")

    if not user_query or not user_query.strip():
        return jsonify({"message": "Please provide a query."}), 400

    response = conversation_manager.process_message(session_id, user_query)
    return jsonify(response)

@app.route("/team/orders", methods=["GET"])
def get_pending_orders():
    """Endpoint for team to see pending orders."""
    orders = conversation_manager.order_manager.get_pending_orders()
    return jsonify({"pending_orders": orders})

@app.route("/team/completed", methods=["GET"])
def get_completed_orders():
    """Endpoint for team to see completed orders."""
    orders = conversation_manager.order_manager.get_completed_orders()
    return jsonify({"completed_orders": orders})

@app.route("/validate-order", methods=["POST"])
def validate_order():
    # Keep for backward compatibility
    payload = request.get_json(silent=True) or {}
    user_query = payload.get("query") or request.form.get("query", "")

    if not user_query or not user_query.strip():
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Please provide an order query such as 'I want 2 pizzas and 1 fries'.",
                }
            ),
            400,
        )

    # Simple validation for API compatibility
    from inventory.order_validator import validate_order_query
    validation = validate_order_query(user_query)
    return jsonify(validation)

if __name__ == "__main__":
    app.run(debug=True)
