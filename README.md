# WhatsApp Chat Visualizer

An interactive tool for visualizing and analyzing WhatsApp chat histories using vector embeddings and machine learning techniques.

## Features

- **Upload WhatsApp Chat Files**: Parse and process WhatsApp chat exports (.txt files)
- **Timeline Visualization**: View message frequency over time by sender
- **Sentiment Analysis**: Track sentiment trends across conversations
- **Cluster Visualization**: Interactive 2D scatter plot of message clusters using UMAP
- **Vector Search**: Find similar messages using semantic similarity
- **Message Browser**: Search and filter through all messages

## Architecture

- **Backend**: Python Flask with SQLite + sqlite-vec for vector storage
- **Frontend**: Vue.js 3 with Chart.js for visualizations
- **NLP**: Python with sentence-transformers for embeddings and UMAP for dimensionality reduction

## Setup Instructions

### Prerequisites

- Python 3.11+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the Flask server:
   ```bash
   python server.py
   ```

   The backend will be available at `http://localhost:3001`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

## Usage

1. **Upload a Chat**: 
   - Export your WhatsApp chat as a .txt file
   - Upload it through the web interface
   - The system will process the messages and generate embeddings

2. **Explore Visualizations**:
   - **Timeline**: See message patterns over time
   - **Sentiment**: Track emotional trends
   - **Clusters**: Explore message similarity in 2D space
   - **Search**: Find semantically similar messages

3. **Interactive Features**:
   - Click on cluster points to view message details
   - Search for specific topics or phrases
   - Filter messages by sender or date

## API Endpoints

### Backend API

- `POST /api/upload` - Upload WhatsApp chat file
- `GET /api/messages/chats` - List all processed chats
- `GET /api/messages/:chatId` - Get messages for a chat
- `GET /api/messages/:chatId/stats` - Get chat statistics
- `POST /api/embeddings/search` - Search similar messages
- `GET /api/embeddings/:chatId/clusters` - Get cluster coordinates
- `POST /api/embeddings/:chatId/process` - Process chat for embeddings

## File Structure

```
├── backend/
│   ├── server.py              # Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── services/
│   │   ├── database.py        # SQLite database service
│   │   └── generate_embedding.py # Embedding generation
│   └── routes/
│       ├── messages.py        # Message API routes
│       └── embeddings.py      # Embedding API routes
├── frontend/
│   ├── src/
│   │   ├── components/        # Vue components
│   │   ├── services/          # API service
│   │   └── main.js           # Vue app entry
│   ├── package.json          # Frontend dependencies
│   └── vite.config.js        # Vite configuration
└── README.md
```

## Technical Details

### Database Schema

The SQLite database stores:
- **messages**: Individual chat messages with embeddings
- **chats**: Chat metadata and statistics
- **Vector storage**: Using sqlite-vec for similarity search

### Embedding Pipeline

1. Parse WhatsApp chat format
2. Generate sentence embeddings using `all-mpnet-base-v2`
3. Apply UMAP for 2D visualization
4. Store embeddings and cluster coordinates

### Visualization Components

- **TimelineChart**: Line chart showing message frequency over time
- **SentimentChart**: Sentiment trends visualization
- **ClusterView**: Interactive 2D scatter plot with pan/zoom
- **MessageList**: Searchable message browser with pagination

## Development

### Backend Development

```bash
cd backend
python server.py  # Runs in debug mode
```

### Frontend Development

```bash
cd frontend
npm run dev  # Hot reload enabled
```

## Troubleshooting

1. **SQLite-vec not available**: The system will fall back to basic SQLite if the vector extension isn't available
2. **Memory issues**: Large chat files may require more memory for embedding generation
3. **CORS issues**: Ensure the backend is running on port 3001

## License

This project is for educational purposes as part of a university assignment.



