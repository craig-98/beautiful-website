import os
from flask import Flask, send_file, jsonify, request, session, redirect, url_for
from functools import wraps
import json
import hashlib

posts = []
users = []
albums = []

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True, static_folder='static', static_url_path='/static')

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
        return send_file(os.path.join(app.root_path, 'templates', 'home.html'))

    @app.route('/login', methods=['GET'])
    def serve_login():
        return send_file(os.path.join(app.root_path, 'templates', 'login.html'))

    @app.route('/register', methods=['GET'])
    def serve_register():
        return send_file(os.path.join(app.root_path, 'templates', 'register.html'))

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
        return send_file(os.path.join(app.root_path, 'templates', 'create_post.html'))

    @app.route('/create-album')
    @login_required
    def serve_create_album():
        return send_file(os.path.join(app.root_path, 'templates', 'create_album.html'))

    @app.route('/api/posts', methods=['GET', 'POST'])
    @login_required
    def api_posts():
        global posts
        if request.method == 'POST':
            data = request.get_json()
            content = data.get('content', '')
            if content:
                post = {
                    'id': len(posts) + 1,
                    'content': content
                }
                posts.append(post)
                save_posts()
                return jsonify({'status': 'success', 'post': post}), 201
            else:
                return jsonify({'status': 'error', 'message': 'Content is required'}), 400
        else:
            return jsonify({'status': 'success', 'posts': posts})

    @app.route('/api/posts/<int:post_id>', methods=['GET'])
    @login_required
    def get_post(post_id):
        global posts
        post = next((p for p in posts if p['id'] == post_id), None)
        if post:
            return jsonify({'status': 'success', 'post': post})
        else:
            return jsonify({'status': 'error', 'message': 'Post not found'}), 404

    @app.route('/api/posts/search', methods=['GET'])
    @login_required
    def search_posts():
        global posts
        query = request.args.get('q', '').lower()
        if not query:
            return jsonify({'status': 'error', 'message': 'Query parameter q is required'}), 400
        filtered = [p for p in posts if query in p['content'].lower()]
        return jsonify({'status': 'success', 'posts': filtered})

    @app.route('/api/albums', methods=['GET', 'POST'])
    @login_required
    def api_albums():
        global albums
        if request.method == 'POST':
            data = request.get_json()
            album_posts = data.get('posts', [])
            if not album_posts or len(album_posts) == 0:
                return jsonify({'status': 'error', 'message': 'Album must contain at least one post'}), 400
            if len(album_posts) > 10:
                return jsonify({'status': 'error', 'message': 'Album cannot contain more than 10 posts'}), 400
            album_id = len(albums) + 1
            album = {
                'id': album_id,
                'posts': []
            }
            for idx, post in enumerate(album_posts):
                content = post.get('content', '')
                caption = post.get('caption', '')
                if not content:
                    return jsonify({'status': 'error', 'message': f'Post {idx+1} content is required'}), 400
                album['posts'].append({
                    'id': idx + 1,
                    'content': content,
                    'caption': caption
                })
            albums.append(album)
            return jsonify({'status': 'success', 'album': album}), 201
        else:
            return jsonify({'status': 'success', 'albums': albums})

    @app.route('/list-static')
    def list_static():
        files = os.listdir(app.static_folder)
        return jsonify({'static_files': files})

    @app.route('/api/debug/albums', methods=['GET'])
    def debug_albums():
        global albums
        return jsonify({'status': 'success', 'albums': albums})

    return app
