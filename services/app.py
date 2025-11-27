from flask import Flask
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv

# Import blueprints
from routes.helper_routes import helper_bp
from routes.ai_routes import ai_bp
from routes.scraper_routes import scraper_bp

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow requests from Angular (different port)

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Blueprints
app.register_blueprint(helper_bp, url_prefix='/api')
app.register_blueprint(ai_bp, url_prefix='/api')
app.register_blueprint(scraper_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
