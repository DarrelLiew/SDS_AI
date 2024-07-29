from flask import Flask
from app.routes import init_routes
from dotenv import load_dotenv
import os

def create_app():
    app = Flask(__name__)
    # Load configuration from the .env file
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path=dotenv_path)
    
    # Initialize routes
    init_routes(app)

    return app