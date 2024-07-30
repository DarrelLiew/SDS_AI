from flask import Response, request, jsonify
from app.utils import process_video_cv, file_exists
import os

def init_routes(app):
    @app.route('/')
    def home():
        return "Hello World!"
    
    @app.route('/process_video')
    def process_video():
        # Extract JSON data from the request
        data = request.json
        file_name = data.get('file_name')

        if not file_name:
            return jsonify({'error': 'No file name provided'}), 400
        else: 
            try:
                # Get bucket from app config
                bucket = app.config['GCS_BUCKET']

                if not file_exists(bucket, file_name):
                    return jsonify({'error': 'File does not exist in bucket'}), 400

                # List all blobs (items) in the bucket
                # blobs = bucket.list_blobs()
                # items = [blob.name for blob in blobs]

                # Download video from GCS

                # Define the path to save the temporary file
                project_root = os.path.dirname(os.path.abspath(__file__))  # Root directory of your project
                temp_file_path = os.path.join(project_root, 'temp_video.mp4')


                blob = bucket.blob(file_name)
                blob.download_to_filename(temp_file_path)
                print(f'Temporary file saved at: {temp_file_path}')
                output_file_path, result = process_video_cv(temp_file_path)

                output_file_name = file_name.split('.')[0] + '_AI.mp4'

                output_blob = bucket.blob(output_file_name)
                # output_blob.upload_from_filename("C:/Users/royce/OneDrive/Desktop/Term 5 Service Design Studio/SDS_AI/sit_stand_2.mp4", content_type='video/mp4')
                output_blob.upload_from_filename(output_file_path, content_type='video/mp4')
                print(f'Uploaded processed video to GCS at: {output_file_name}.mp4')

                # Clean up temporary files
                os.remove(temp_file_path)
                os.remove(output_file_path)

                # Return the URL to the processed video
                output_url = output_blob.public_url
                return jsonify({'output_url': output_url, 'result': result}), 200

            except Exception as e:
                return jsonify({'error': str(e)}), 500

    @app.route('/video/<file_name>', methods=['GET'])
    def serve_video(file_name):
        bucket = app.config['GCS_BUCKET']
        blob = bucket.blob(file_name)

        def generate():
            with blob.open("rb") as f:
                while True:
                    chunk = f.read(8192)  # Read file in chunks
                    if not chunk:
                        break
                    yield chunk

        return Response(generate(), content_type='video/mp4')
            

    # def process_video_route():
    #     data = request.json
    #     video_url = data.get('video_url')
    #     result = process_video(video_url)
    #     return jsonify(result)