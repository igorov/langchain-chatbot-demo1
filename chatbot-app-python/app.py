from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')
CORS(app)

# Configure external chatbot API
CHATBOT_API_BASE_URL = os.getenv('CHATBOT_API_BASE_URL', 'http://localhost:8080')

# In-memory storage for user sessions
user_sessions = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    
    # Create or get user session
    session['username'] = username
    
    # Get chat history from external API
    try:
        history_response = requests.get(
            f"{CHATBOT_API_BASE_URL}/api/chatbot/history",
            params={'user': username},
            timeout=10
        )
        
        if history_response.status_code == 200:
            history_data = history_response.json()
            messages = history_data.get('messages', [])
        else:
            messages = []
    except Exception as e:
        print(f"Error fetching history: {e}")
        messages = []
    
    return jsonify({
        'success': True,
        'username': username,
        'messages': messages
    })

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'success': True})

@app.route('/api/chat', methods=['POST'])
def chat():
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    user_message = data.get('message', '').strip()
    username = session['username']
    
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400
    
    try:
        # Send message to external chatbot API
        chat_payload = {
            "question": user_message,
            "user": username
        }
        
        chat_response = requests.post(
            f"{CHATBOT_API_BASE_URL}/api/chatbot",
            json=chat_payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if chat_response.status_code == 200:
            response_data = chat_response.json()
            
            if response_data.get('status') == 'success':
                return jsonify({
                    'success': True,
                    'message': response_data.get('response', ''),
                    'timestamp': response_data.get('timestamp')
                })
            else:
                return jsonify({'error': 'Error from chatbot API'}), 500
        else:
            return jsonify({'error': f'API error: {chat_response.status_code}'}), 500
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timeout - chatbot API took too long to respond'}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Connection error - unable to reach chatbot API'}), 503
    except Exception as e:
        print(f"Error in chat: {str(e)}")
        return jsonify({'error': 'Error processing message'}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    username = session['username']
    
    try:
        history_response = requests.get(
            f"{CHATBOT_API_BASE_URL}/api/chatbot/history",
            params={'user': username},
            timeout=10
        )
        
        if history_response.status_code == 200:
            history_data = history_response.json()
            return jsonify({
                'messages': history_data.get('messages', [])
            })
        else:
            return jsonify({'error': f'API error: {history_response.status_code}'}), 500
            
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timeout'}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Connection error'}), 503
    except Exception as e:
        print(f"Error fetching history: {e}")
        return jsonify({'error': 'Error fetching history'}), 500

@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Note: External API doesn't provide clear history endpoint
    # This would need to be implemented in the external API
    # For now, we'll return success but note the limitation
    return jsonify({
        'success': True,
        'note': 'Clear history not implemented in external API'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
