from flask import Blueprint, request, jsonify
from services.database import DatabaseService
from services.language_processing import LanguageProcessingService

embeddings_bp = Blueprint('embeddings', __name__)
db_service = DatabaseService()
lp_service = LanguageProcessingService()

@embeddings_bp.route('/search', methods=['POST'])
def search_messages():
    """Search for similar messages using vector similarity"""
    try:
        data = request.get_json()
        query = data.get('query')
        chat_id = data.get('chat_id')
        limit = data.get('limit', 10)
        
        if not query or not chat_id:
            return jsonify({'error': 'Query and chat_id are required'}), 400
        
        # Generate embedding for search query
        query_embedding = lp_service.generate_embeddings([query])[0]
        
        # Search similar messages
        results = db_service.search_similar_messages(chat_id, query_embedding, limit)
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@embeddings_bp.route('/<chat_id>/clusters', methods=['GET'])
def get_clusters(chat_id):
    """Get cluster coordinates for visualization"""
    try:
        clusters = db_service.get_cluster_coordinates(chat_id)
        return jsonify(clusters)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# @embeddings_bp.route('/<chat_id>/process', methods=['POST'])
# def process_chat_embeddings(chat_id):
#     """Process chat messages to generate embeddings and clusters"""
#     try:
#         # Get messages for the chat
#         messages = db_service.get_messages(chat_id)
        
#         if not messages:
#             return jsonify({'error': 'No messages found for this chat'}), 404
        
#         # Process messages to generate embeddings, clusters, and sentiment
#         processed_data = lp_service.process_chat_data(messages)
        
#         # Update database with new embeddings and clusters
#         for data in processed_data:
#             db_service.update_message_embedding(
#                 data['id'], 
#                 data['embedding'], 
#                 data['sentiment'],
#                 data['cluster_x'],
#                 data['cluster_y']
#             )
        
#         return jsonify({
#             'success': True,
#             'processed_count': len(processed_data)
#         })
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

