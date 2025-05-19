import os
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from functools import wraps
import json
import hashlib

posts = []
users = []
albums = []

def create_app(test_config=None):
    # Fix static folder path to point to top-level static directory
    static_folder_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')
    template_folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    app = Flask(__name__, instance_relative_config=True, static_folder=static_folder_path, static_url_path='/static', template_folder=template_folder_path)

    # Load default config
    app.config.from_mapping(
        SECRET_KEY='dev',  # override in instance config
        POSTS_FILE=os.path.join(app.instance_path, 'posts.json'),
        USERS_FILE=os.path.join(app.instance_path, 'users.json'),
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.update(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Load posts and users data
    def load_posts():
        global posts
        if os.path.exists(app.config['POSTS_FILE']):
            with open(app.config['POSTS_FILE'], 'r', encoding='utf-8') as f:
                try:
                    posts = json.load(f)
                except json.JSONDecodeError:
                    posts = []
        else:
            posts = []

    def save_posts():
        with open(app.config['POSTS_FILE'], 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)

    def load_users():
        global users
        if os.path.exists(app.config['USERS_FILE']):
            with open(app.config['USERS_FILE'], 'r', encoding='utf-8') as f:
                try:
                    users = json.load(f)
                except json.JSONDecodeError:
                    users = []
        else:
            users = []

    def save_users():
        with open(app.config['USERS_FILE'], 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session:
                return jsonify({'status': 'error', 'message': 'Authentication required'}), 401
            return f(*args, **kwargs)
        return decorated_function

    load_posts()
    load_users()

    # Routes

    @app.route('/')
    def serve_home():
        return render_template('home.html')

    @app.route('/news-hub')
    def news_hub():
        return render_template('news_hub.html')

    @app.route('/history')
    def history():
        return render_template('history.html')

    # Removed gallery and create_album routes as per user request

    # @app.route('/gallery')
    # def gallery():
    #     return render_template('gallery.html')

    # @app.route('/create-album')
    # @login_required
    # def serve_create_album():
    #     return render_template('create_album.html')

    @app.route('/members')
    def members():
        return render_template('members.html')

    @app.route('/login', methods=['GET'])
    def serve_login():
        return render_template('login.html')

    @app.route('/register', methods=['GET'])
    def serve_register():
        return render_template('register.html')

    @app.route('/logout')
    def logout():
        session.pop('username', None)
        return redirect(url_for('serve_home'))

    @app.route('/api/register', methods=['POST'])
    def api_register():
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        if not username or not password:
            return jsonify({'status': 'error', 'message': 'Username and password are required'}), 400
        if any(u['username'] == username for u in users):
            return jsonify({'status': 'error', 'message': 'Username already exists'}), 400
        hashed_pw = hash_password(password)
        users.append({'username': username, 'password': hashed_pw})
        save_users()
        return jsonify({'status': 'success', 'message': 'User registered successfully'})

    @app.route('/api/login', methods=['POST'])
    def api_login():
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        if not username or not password:
            return jsonify({'status': 'error', 'message': 'Username and password are required'}), 400
        user = next((u for u in users if u['username'] == username), None)
        if user and user['password'] == hash_password(password):
            session['username'] = username
            return jsonify({'status': 'success', 'message': 'Logged in successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Invalid username or password'}), 401

    @app.route('/api/logout', methods=['POST'])
    def api_logout():
        session.pop('username', None)
        return jsonify({'status': 'success', 'message': 'Logged out successfully'})

    @app.route('/api/check-auth', methods=['GET'])
    def api_check_auth():
        if 'username' in session:
            return jsonify({'status': 'success', 'authenticated': True, 'username': session['username']})
        else:
            return jsonify({'status': 'success', 'authenticated': False})

    @app.route('/create-post')
    @login_required
    def serve_create_post():
        return render_template('create_post.html')

    return app
