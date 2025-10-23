import sqlite3
import sqlite_vec
import json
import numpy as np
from datetime import datetime
import os

class DatabaseService:
    def __init__(self, db_path='chat_data.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with sqlite-vec extension"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)
        
        # Create messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                sender TEXT NOT NULL,
                message TEXT NOT NULL,
                sentiment REAL,
                embedding BLOB,
                cluster_x REAL,
                cluster_y REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create chats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                id TEXT PRIMARY KEY,
                name TEXT,
                message_count INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_id ON messages(chat_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON messages(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sender ON messages(sender)')
        
        conn.commit()
        conn.close()
    
    def store_messages(self, chat_id, messages, embeddings):
        """Store messages and their embeddings in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Store chat info
            cursor.execute('''
                INSERT OR REPLACE INTO chats (id, name, message_count)
                VALUES (?, ?, ?)
            ''', (chat_id, f"Chat {chat_id}", len(messages)))
            
            # Store messages
            for i, (msg, embedding) in enumerate(zip(messages, embeddings)):
                # Convert embedding to binary
                embedding_blob = np.array(embedding).tobytes()
                
                cursor.execute('''
                    INSERT INTO messages (chat_id, timestamp, sender, message, embedding)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    chat_id,
                    msg['timestamp'],
                    msg['sender'],
                    msg['message'],
                    embedding_blob
                ))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_chats(self):
        """Get list of all chats"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, message_count, created_at
            FROM chats
            ORDER BY created_at DESC
        ''')
        
        chats = []
        for row in cursor.fetchall():
            chats.append({
                'id': row[0],
                'name': row[1],
                'message_count': row[2],
                'created_at': row[3]
            })
        
        conn.close()
        return chats
    
    def get_messages(self, chat_id, limit=None):
        """Get messages for a specific chat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT id, timestamp, sender, message, sentiment, cluster_x, cluster_y
            FROM messages
            WHERE chat_id = ?
            ORDER BY timestamp
        '''
        
        if limit:
            query += f' LIMIT {limit}'
        
        cursor.execute(query, (chat_id,))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'id': row[0],
                'timestamp': row[1],
                'sender': row[2],
                'message': row[3],
                'sentiment': row[4],
                'cluster_x': row[5],
                'cluster_y': row[6]
            })
        
        conn.close()
        return messages
    
    def get_chat_stats(self, chat_id):
        """Get aggregated statistics for a chat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Message count by sender
        cursor.execute('''
            SELECT sender, COUNT(*) as count
            FROM messages
            WHERE chat_id = ?
            GROUP BY sender
            ORDER BY count DESC
        ''', (chat_id,))
        
        sender_stats = []
        for row in cursor.fetchall():
            sender_stats.append({
                'sender': row[0],
                'count': row[1]
            })
        
        # Total message count
        cursor.execute('SELECT COUNT(*) FROM messages WHERE chat_id = ?', (chat_id,))
        total_messages = cursor.fetchone()[0]
        
        # Date range
        cursor.execute('''
            SELECT MIN(timestamp), MAX(timestamp)
            FROM messages
            WHERE chat_id = ?
        ''', (chat_id,))
        
        date_range = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_messages': total_messages,
            'sender_stats': sender_stats,
            'date_range': {
                'start': date_range[0],
                'end': date_range[1]
            }
        }
    
    def search_similar_messages(self, chat_id, query_embedding, limit=10):
        """Search for similar messages using vector similarity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all messages with embeddings for this chat
        cursor.execute('''
            SELECT id, timestamp, sender, message, embedding
            FROM messages
            WHERE chat_id = ? AND embedding IS NOT NULL
        ''', (chat_id,))
        
        messages = []
        similarities = []
        
        query_embedding = np.array(query_embedding)
        
        for row in cursor.fetchall():
            msg_id, timestamp, sender, message, embedding_blob = row
            
            # Convert blob back to numpy array
            stored_embedding = np.frombuffer(embedding_blob, dtype=np.float32)
            
            # Calculate cosine similarity
            similarity = np.dot(query_embedding, stored_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(stored_embedding)
            )
            
            messages.append({
                'id': msg_id,
                'timestamp': timestamp,
                'sender': sender,
                'message': message,
                'similarity': float(similarity)
            })
            similarities.append(similarity)
        
        # Sort by similarity and return top results
        sorted_messages = sorted(messages, key=lambda x: x['similarity'], reverse=True)
        
        conn.close()
        return sorted_messages[:limit]
    
    def get_cluster_coordinates(self, chat_id):
        """Get cluster coordinates for visualization"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, sender, message, cluster_x, cluster_y, sentiment
            FROM messages
            WHERE chat_id = ? AND cluster_x IS NOT NULL AND cluster_y IS NOT NULL
            ORDER BY timestamp
        ''', (chat_id,))
        
        clusters = []
        for row in cursor.fetchall():
            clusters.append({
                'id': row[0],
                'sender': row[1],
                'message': row[2],
                'x': row[3],
                'y': row[4],
                'sentiment': row[5]
            })
        
        conn.close()
        return clusters
    
    def update_cluster_coordinates(self, chat_id, coordinates):
        """Update cluster coordinates for messages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            for coord in coordinates:
                cursor.execute('''
                    UPDATE messages
                    SET cluster_x = ?, cluster_y = ?
                    WHERE id = ?
                ''', (coord['x'], coord['y'], coord['id']))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def update_message_embedding(self, message_id, embedding, sentiment, cluster_x, cluster_y):
        """Update a specific message with embedding and cluster data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            embedding_blob = np.array(embedding).tobytes()
            cursor.execute('''
                UPDATE messages
                SET embedding = ?, sentiment = ?, cluster_x = ?, cluster_y = ?
                WHERE id = ?
            ''', (embedding_blob, sentiment, cluster_x, cluster_y, message_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
