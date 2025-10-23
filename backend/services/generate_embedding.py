import numpy as np
from sentence_transformers import SentenceTransformer
import umap
from sklearn.cluster import KMeans
import json
import sys

class EmbeddingService:
    def __init__(self, model_name="all-mpnet-base-v2"):
        """Initialize the embedding service with a pre-trained model"""
        self.model = SentenceTransformer(model_name)
        self.umap_reducer = None
        self.kmeans = None
    
    def generate_embeddings(self, texts):
        """Generate embeddings for a list of texts"""
        if not texts:
            return []
        
        # Generate embeddings using sentence-transformers
        embeddings = self.model.encode(texts, convert_to_tensor=False)
        return embeddings.tolist()
    
    def generate_clusters(self, embeddings, n_clusters=5):
        """Generate cluster coordinates using UMAP and KMeans"""
        if len(embeddings) < 2:
            return []
        
        embeddings_array = np.array(embeddings)
        
        # Apply UMAP for dimensionality reduction
        self.umap_reducer = umap.UMAP(
            n_neighbors=min(5, len(embeddings) - 1),
            n_components=2,
            random_state=42
        )
        
        # Reduce to 2D
        reduced_embeddings = self.umap_reducer.fit_transform(embeddings_array)
        
        # Apply KMeans clustering
        n_clusters = min(n_clusters, len(embeddings))
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = self.kmeans.fit_predict(reduced_embeddings)
        
        # Return coordinates and cluster assignments
        coordinates = []
        for i, (x, y) in enumerate(reduced_embeddings):
            coordinates.append({
                'id': i,
                'x': float(x),
                'y': float(y),
                'cluster': int(cluster_labels[i])
            })
        
        return coordinates
    
    def calculate_sentiment(self, texts):
        """Calculate sentiment scores for texts (simple approach)"""
        # Simple sentiment calculation based on positive/negative words
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'happy', 'joy', 'smile']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'sad', 'angry', 'frustrated', 'disappointed', 'worried', 'scared']
        
        sentiments = []
        for text in texts:
            text_lower = text.lower()
            pos_count = sum(1 for word in positive_words if word in text_lower)
            neg_count = sum(1 for word in negative_words if word in text_lower)
            
            if pos_count + neg_count == 0:
                sentiment = 0.0  # Neutral
            else:
                sentiment = (pos_count - neg_count) / (pos_count + neg_count)
            
            sentiments.append(sentiment)
        
        return sentiments
    
    def process_chat_data(self, messages):
        """Process chat data to generate embeddings, clusters, and sentiment"""
        texts = [msg['message'] for msg in messages]
        
        # Generate embeddings
        embeddings = self.generate_embeddings(texts)
        
        # Generate cluster coordinates
        cluster_coords = self.generate_clusters(embeddings)
        
        # Calculate sentiment
        sentiments = self.calculate_sentiment(texts)
        
        # Combine results
        processed_data = []
        for i, msg in enumerate(messages):
            processed_data.append({
                'id': i,
                'timestamp': msg['timestamp'],
                'sender': msg['sender'],
                'message': msg['message'],
                'embedding': embeddings[i],
                'sentiment': sentiments[i],
                'cluster_x': cluster_coords[i]['x'] if i < len(cluster_coords) else None,
                'cluster_y': cluster_coords[i]['y'] if i < len(cluster_coords) else None,
                'cluster': cluster_coords[i]['cluster'] if i < len(cluster_coords) else None
            })
        
        return processed_data

def main():
    """Command line interface for processing chat data"""
    if len(sys.argv) != 2:
        print("Usage: python generate_embedding.py <input_json>")
        sys.exit(1)
    
    try:
        # Read input JSON
        input_data = json.loads(sys.argv[1])
        messages = input_data.get('messages', [])
        
        # Process data
        service = EmbeddingService()
        processed_data = service.process_chat_data(messages)
        
        # Output results
        output = {
            'embeddings': [item['embedding'] for item in processed_data],
            'sentiments': [item['sentiment'] for item in processed_data],
            'clusters': [
                {
                    'id': item['id'],
                    'x': item['cluster_x'],
                    'y': item['cluster_y'],
                    'cluster': item['cluster']
                }
                for item in processed_data
            ]
        }
        
        print(json.dumps(output))
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
