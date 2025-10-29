import pysqlite3 as sqlite3
import sqlite_vec
import numpy as np
import datetime

class DatabaseService:  
    def __init__(self, db_path='chat_data.db'):
        self.db_path = db_path
        self.init_database()
    
    def _connect(self):
        """Create a new SQLite connection with sqlite-vec loaded."""
        conn = sqlite3.connect(self.db_path)
        # Load sqlite-vec extension for each new connection to ensure vec0 is available
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)
        return conn

    def init_database(self):
        """Initialize database"""
        conn = self._connect()
        cursor = conn.cursor()
        
        # Create messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                sender TEXT NOT NULL,
                message TEXT NOT NULL,
                sentiment REAL,
                cluster_x REAL,
                cluster_y REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Ensure vector table exists with correct embedding dimension
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS message_embeddings
            USING vec0(
                id INTEGER PRIMARY KEY,
                embedding FLOAT[768]
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
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_id ON messages(chat_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON messages(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sender ON messages(sender)')
        
        conn.commit()
        conn.close()
    
    def store_messages(self, chat_id, processed_data):
        """Store messages and their embeddings in the database"""
        conn = self._connect()
        cursor = conn.cursor()
        
        try:
            # Store chat info
            cursor.execute('''
                INSERT OR REPLACE INTO chats (id, name, message_count)
                VALUES (?, ?, ?)
            ''', (chat_id, f"Chat {chat_id}", len(processed_data)))
            
            # Store messages
            for data in processed_data:
                embedding = np.array(data['embedding'], dtype=np.float32)
                embedding_blob = embedding.tobytes()
                
                cursor.execute('''
                    INSERT INTO messages (chat_id, timestamp, sender, message, sentiment, cluster_x, cluster_y)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    chat_id,
                    data['timestamp'],
                    data['sender'],
                    data['message'],
                    data['sentiment'],
                    data['cluster_x'],
                    data['cluster_y']
                ))
    
                message_id = cursor.lastrowid
                cursor.execute('INSERT INTO message_embeddings (id, embedding) VALUES (?, ?)', (message_id, embedding_blob))

            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_chats(self):
        """Get list of all chats"""
        conn = self._connect()
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
        conn = self._connect()
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
        conn = self._connect()
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
        """Search for similar messages using sqlite-vec vector index"""
        conn = self._connect()
        cursor = conn.cursor()

        query_blob = np.array(query_embedding, dtype=np.float32).tobytes()

        cursor.execute('''
            SELECT 
                m.id,
                m.timestamp,
                m.sender,
                m.message,
                v.distance
            FROM message_embeddings v
            JOIN messages m ON m.id = v.id
            WHERE v.embedding MATCH ? AND m.chat_id = ? AND v.k = ?
            ORDER BY v.distance ASC
        ''', (query_blob, chat_id, limit))

        results = [
            {
                'id': row[0],
                'timestamp': row[1],
                'sender': row[2],
                'message': row[3],
                'distance': float(row[4])
            }
            for row in cursor.fetchall()
        ]

        conn.close()
        return results


    def get_message_embedding(self, message_id):
        """Fetch the raw embedding blob for a given message id."""
        conn = self._connect()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT embedding FROM message_embeddings WHERE id = ?', (message_id,))
            row = cursor.fetchone()
            return row[0] if row else None
        finally:
            conn.close()

    def search_similar_messages_by_id(self, chat_id, message_id, limit=10):
        """Search for similar messages using the embedding of an existing message id."""
        embedding_blob = self.get_message_embedding(message_id)
        if embedding_blob is None:
            return []

        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 
                m.id,
                m.timestamp,
                m.sender,
                m.message,
                v.distance
            FROM message_embeddings v
            JOIN messages m ON m.id = v.id
            WHERE v.embedding MATCH ? AND m.chat_id = ? AND v.k = ? AND m.id != ?
            ORDER BY v.distance ASC
        ''', (embedding_blob, chat_id, limit, message_id))

        results = [
            {
                'id': row[0],
                'timestamp': row[1],
                'sender': row[2],
                'message': row[3],
                'distance': float(row[4])
            }
            for row in cursor.fetchall()
        ]

        conn.close()
        return results

    def get_cluster_coordinates(self, chat_id):
        """Get cluster coordinates for visualization"""
        conn = self._connect()
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
        conn = self._connect()
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
        conn = self._connect()
        cursor = conn.cursor()
        
        try:
            # Update message metadata
            cursor.execute('''
                UPDATE messages
                SET sentiment = ?, cluster_x = ?, cluster_y = ?
                WHERE id = ?
            ''', (sentiment, cluster_x, cluster_y, message_id))

            # Upsert embedding in vector table
            embedding_blob = np.array(embedding, dtype=np.float32).tobytes()
            cursor.execute('''
                INSERT INTO message_embeddings (id, embedding)
                VALUES (?, ?)
                ON CONFLICT(id) DO UPDATE SET embedding = excluded.embedding
            ''', (message_id, embedding_blob))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

if __name__ == "__main__":
    db = DatabaseService()
    
    print("Welcome to the Chat Database REPL!")
    print("Available commands: help, list_chats, list_messages <chat_id>, stats <chat_id>, add_message, search <chat_id>, exit")
    
    while True:
        cmd = input(">> ").strip()
        if not cmd:
            continue
        
        parts = cmd.split()
        action = parts[0].lower()
        
        if action == "help":
            print("""
Available commands:
    help                        - Show this help
    list_chats                  - List all chats
    list_messages <chat_id>     - List messages for a chat
    stats <chat_id>             - Show chat statistics
    add_message                 - Add a test message interactively
    search <chat_id>            - Search similar messages
    cli                         - Use sqlite freely
    exit                        - Quit
            """)
        
        elif action == "list_chats":
            chats = db.get_chats()
            for c in chats:
                print(f"{c['id']} | {c['name']} | {c['message_count']} messages | created {c['created_at']}")
        
        elif action == "list_messages":
            if len(parts) < 2:
                print("Usage: list_messages <chat_id>")
                continue
            chat_id = parts[1]
            messages = db.get_messages(chat_id)
            for m in messages:
                print(f"{m['id']} | {m['timestamp']} | {m['sender']} | {m['message']} | sentiment: {m['sentiment']}")
        
        elif action == "stats":
            if len(parts) < 2:
                print("Usage: stats <chat_id>")
                continue
            chat_id = parts[1]
            stats = db.get_chat_stats(chat_id)
            print(f"Total messages: {stats['total_messages']}")
            print("Message count by sender:")
            for s in stats['sender_stats']:
                print(f"  {s['sender']}: {s['count']}")
            print(f"Date range: {stats['date_range']['start']} → {stats['date_range']['end']}")
        
        elif action == "add_message":
            chat_id = input("Chat ID: ")
            sender = input("Sender: ")
            message = input("Message: ")
            timestamp = datetime.datetime.now().isoformat()
            sentiment = float(input("Sentiment (-1 to 1): "))
            cluster_x = float(input("Cluster X: "))
            cluster_y = float(input("Cluster Y: "))
            embedding = np.random.rand(768).tolist()  # random embedding for demo
            
            db.store_messages(chat_id, [{
                'timestamp': timestamp,
                'sender': sender,
                'message': message,
                'sentiment': sentiment,
                'cluster_x': cluster_x,
                'cluster_y': cluster_y,
                'embedding': embedding
            }])
            print("Message added.")
        
        elif action == "search":
            if len(parts) < 2:
                print("Usage: search <chat_id> [message_id]")
                continue
            chat_id = parts[1]
            if len(parts) == 3:
                try:
                    message_id = int(parts[2])
                except ValueError:
                    print("message_id must be an integer")
                    continue
                results = db.search_similar_messages_by_id(chat_id, message_id)
            print("Top similar messages:")
            for r in results:
                print(f"{r['id']} | {r['timestamp']} | {r['sender']} | {r['message']} | distance: {r['distance']}")
        
        elif action == 'cli':
            conn = db._connect()
            cursor = conn.cursor()
            print("Entering interactive SQLite CLI (type 'exit' to leave)...")
            
            while True:
                sql = input("sqlite> ").strip()
                if sql.lower() in ('exit', 'quit'):
                    break
                if not sql:
                    continue
                try:
                    cursor.execute(sql)
                    if sql.lower().startswith("select"):
                        rows = cursor.fetchall()
                        for row in rows:
                            print(row)
                    else:
                        conn.commit()
                        print("OK")
                except Exception as e:
                    print(f"Error: {e}")
            
            conn.close()


        elif action == "exit":
            print("Goodbye!")
            break
        
        else:
            print("Unknown command. Type 'help' for list of commands.")