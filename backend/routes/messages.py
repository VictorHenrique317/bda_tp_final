from flask import Blueprint, request, jsonify
from services.database import DatabaseService
from datetime import datetime
import re
from services.language_processing import LanguageProcessingService

language_processing_service = LanguageProcessingService()
messages_bp = Blueprint('messages', __name__)
db_service = DatabaseService()

@messages_bp.route('/chats', methods=['GET'])
def get_chats():
    """Get list of all chats"""
    try:
        chats = db_service.get_chats()
        return jsonify(chats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@messages_bp.route('/<chat_id>', methods=['GET'])
def get_messages(chat_id):
    """Get messages for a specific chat"""
    try:
        limit = request.args.get('limit', type=int)
        messages = db_service.get_messages(chat_id, limit)
        return jsonify(messages)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@messages_bp.route('/<chat_id>/stats', methods=['GET'])
def get_chat_stats(chat_id):
    """Get aggregated statistics for a chat"""
    try:
        stats = db_service.get_chat_stats(chat_id)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@messages_bp.route('', methods=['POST'])
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
        
        processed_data = language_processing_service.process_chat_data(messages)
        # Store in database
        chat_id = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        db_service.store_messages(chat_id, processed_data)
        
        return jsonify({
            'success': True,
            'chat_id': chat_id,
            'message_count': len(messages)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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