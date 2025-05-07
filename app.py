from flask import Flask, send_from_directory, request, jsonify

app = Flask(__name__, static_folder='beautiful_website')

posts = []
albums = []

@app.route('/')
def serve_home():
    return send_from_directory('', 'home.html')

@app.route('/history')
def serve_history():
    return send_from_directory('', 'history.html')

@app.route('/create-post')
def serve_create_post():
    return send_from_directory('', 'create_post.html')

@app.route('/create-album')
def serve_create_album():
    return send_from_directory('', 'create_album.html')

@app.route('/gallery')
def serve_gallery():
    return send_from_directory('', 'gallery.html')

@app.route('/members')
def serve_members():
    return send_from_directory('', 'members.html')

@app.route('/api/posts', methods=['GET', 'POST'])
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
            return jsonify({'status': 'success', 'post': post}), 201
        else:
            return jsonify({'status': 'error', 'message': 'Content is required'}), 400
    else:
        return jsonify({'status': 'success', 'posts': posts})

@app.route('/api/albums', methods=['GET', 'POST'])
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

if __name__ == '__main__':
    app.run(debug=True)
