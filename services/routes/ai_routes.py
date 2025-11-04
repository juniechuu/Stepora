from flask import Blueprint, jsonify, request
import openai
import os

# Create blueprint for AI routes
ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/openai', methods=['POST'])
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