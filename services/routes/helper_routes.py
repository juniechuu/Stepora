from flask import Blueprint, jsonify, request

# Create blueprint for helper routes
helper_bp = Blueprint('helper', __name__)

@helper_bp.route('/hello', methods=['GET'])
def hello():
    return jsonify(message="Hello from Flask!")

