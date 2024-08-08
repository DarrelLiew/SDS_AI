from flask import Flask
from app1.routes import init_routes
from dotenv import load_dotenv
from google.cloud import storage
import os

def create_app():
    app = Flask(__name__)
    # Load configuration from the .env file
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path=dotenv_path)

    # Initialize Google Cloud Storage client
    credentials_path = 'ninkatec-2-223b74173d7a.json'
    storage_client = storage.Client.from_service_account_json(credentials_path)
    app.config['STORAGE_CLIENT'] = storage_client
    
    bucket_name = "ninkatec-bucket-1"
    bucket = storage_client.bucket(bucket_name)
    app.config['GCS_BUCKET'] = bucket
    
    # Initialize routes
    init_routes(app)

    return app