from app_package import app

@app.route('/api/comment-likes', methods=['GET', 'POST', 'DELETE'])
def api_comment_likes():
    pass