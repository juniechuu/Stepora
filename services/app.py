from flask import Flask, jsonify, request
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow requests from Angular (different port)

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify(message="Hello from Flask!")

@app.route('/api/data', methods=['POST'])
def get_data():
    data = request.json
    return jsonify(received=data)

# --BEGIN: OpenAI Endpoints
@app.route('/api/openai', methods=['POST'])
def openai_prompt():
    try:
        # Get the prompt from the request
        data = request.json
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        # Extract the response
        ai_response = response.choices[0].message.content
        
        return jsonify({
            'prompt': prompt,
            'response': ai_response,
            'status': 'success'
        })
        
    except openai.error.AuthenticationError:
        return jsonify({'error': 'Invalid OpenAI API key'}), 401
    except openai.error.RateLimitError:
        return jsonify({'error': 'OpenAI rate limit exceeded'}), 429
    except openai.error.APIError as e:
        return jsonify({'error': f'OpenAI API error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500
# --END: OpenAI Endpoints

if __name__ == '__main__':
    app.run(debug=True, port=5000)
