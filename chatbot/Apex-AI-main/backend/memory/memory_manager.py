import sqlite3
import json
import os

class MemoryManager:
    def __init__(self, db_path="memory.db"):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS conversation_memory 
                            (session_id TEXT, role TEXT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
            
    def add_message(self, session_id: str, role: str, content: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO conversation_memory (session_id, role, content) VALUES (?, ?, ?)", 
                         (session_id, role, content))
            
    def get_context(self, session_id: str, limit: int = 10):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT role, content FROM conversation_memory WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?", 
                                  (session_id, limit))
            return [{"role": row[0], "content": row[1]} for row in reversed(cursor.fetchall())]
