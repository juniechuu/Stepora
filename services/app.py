from flask import Flask, send_from_directory
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv

# Import blueprints
from routes.helper_routes import helper_bp
from routes.ai_routes import ai_bp
from routes.scraper_routes import scraper_bp
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp

# Import database
from db import init_db

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow requests from Angular (different port)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize database
init_db()

# Serve uploaded files
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Blueprints
app.register_blueprint(helper_bp, url_prefix='/api')
app.register_blueprint(ai_bp, url_prefix='/api')
app.register_blueprint(scraper_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
