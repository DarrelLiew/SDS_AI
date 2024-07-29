from flask import request, jsonify
from app.utils import process_video

def init_routes(app):
    @app.route('/')
    def home():
        return "Hello World!"
    # def process_video_route():
    #     data = request.json
    #     video_url = data.get('video_url')
    #     result = process_video(video_url)
    #     return jsonify(result)