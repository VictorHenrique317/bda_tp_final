from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime
import sqlite3
import re

# Import our services and routes
from services.database import DatabaseService
from services.generate_embedding import EmbeddingService
from routes.messages import messages_bp
from routes.embeddings import embeddings_bp

app = Flask(__name__)
CORS(app)

# Initialize services
db_service = DatabaseService()
embedding_service = EmbeddingService()

# Register blueprints
app.register_blueprint(messages_bp, url_prefix='/api/messages')
app.register_blueprint(embeddings_bp, url_prefix='/api/embeddings')

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'OK', 'message': 'WhatsApp Chat Backend is running'})

@app.route('/api/upload', methods=['POST'])
def upload_chat():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read and parse WhatsApp chat file
        content = file.read().decode('utf-8')
        messages = parse_whatsapp_chat(content)
        
        # Generate embeddings
        embeddings = embedding_service.generate_embeddings([msg['message'] for msg in messages])
        
        # Store in database
        chat_id = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        db_service.store_messages(chat_id, messages, embeddings)
        
        return jsonify({
            'success': True,
            'chat_id': chat_id,
            'message_count': len(messages)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Routes are now handled by blueprints

def parse_whatsapp_chat(content):
    """Parse WhatsApp chat export format"""
    messages = []
    lines = content.split('\n')
    
    # WhatsApp format: [DD/MM/YYYY, HH:MM:SS] Sender: Message
    pattern = r'\[(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}:\d{2})\] ([^:]+): (.+)'
    
    for line in lines:
        match = re.match(pattern, line)
        if match:
            date_str, time_str, sender, message = match.groups()
            
            # Parse datetime
            datetime_str = f"{date_str} {time_str}"
            try:
                timestamp = datetime.strptime(datetime_str, '%d/%m/%Y %H:%M:%S')
            except ValueError:
                continue
            
            messages.append({
                'timestamp': timestamp.isoformat(),
                'sender': sender.strip(),
                'message': message.strip()
            })
    
    return messages

if __name__ == '__main__':
    app.run(debug=True, port=5002)
