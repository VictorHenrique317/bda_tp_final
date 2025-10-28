from flask import Flask, request, jsonify
from flask_cors import CORS

# Import our services and routes
from routes.messages import messages_bp
from routes.embeddings import embeddings_bp

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(messages_bp, url_prefix='/api/messages')
app.register_blueprint(embeddings_bp, url_prefix='/api/embeddings')

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'OK', 'message': 'WhatsApp Chat Backend is running'})


if __name__ == '__main__':
    app.run(debug=True, port=5002)
