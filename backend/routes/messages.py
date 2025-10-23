from flask import Blueprint, request, jsonify
from services.database import DatabaseService

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
