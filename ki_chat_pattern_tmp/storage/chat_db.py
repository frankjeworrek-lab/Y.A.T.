import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path
from core.providers.types import Message, Role

class ChatDatabase:
    """SQLite-basierte Chat-History-Speicherung"""
    
    def __init__(self, db_path: str = "chat_history.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Erstelle Datenbank-Schema falls nicht vorhanden"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversations-Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT,
                provider_id TEXT,
                model_id TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        # Messages-Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT,
                role TEXT,
                content TEXT,
                timestamp TEXT,
                metadata TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_conversation(
        self, 
        conversation_id: str,
        title: str = "New Conversation",
        provider_id: str = "",
        model_id: str = ""
    ) -> str:
        """Erstelle neue Konversation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO conversations (id, title, provider_id, model_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (conversation_id, title, provider_id, model_id, now, now))
        
        conn.commit()
        conn.close()
        
        return conversation_id
    
    def save_message(self, conversation_id: str, message: Message):
        """Speichere einzelne Nachricht"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO messages (conversation_id, role, content, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (
            conversation_id,
            message.role.value,
            message.content,
            message.timestamp.isoformat(),
            json.dumps(message.metadata)
        ))
        
        # Update conversation timestamp
        cursor.execute("""
            UPDATE conversations 
            SET updated_at = ? 
            WHERE id = ?
        """, (datetime.now().isoformat(), conversation_id))
        
        conn.commit()
        conn.close()
    
    def load_messages(self, conversation_id: str) -> List[Message]:
        """Lade alle Nachrichten einer Konversation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT role, content, timestamp, metadata
            FROM messages
            WHERE conversation_id = ?
            ORDER BY timestamp ASC
        """, (conversation_id,))
        
        messages = []
        for row in cursor.fetchall():
            role, content, timestamp_str, metadata_str = row
            
            messages.append(Message(
                role=Role(role),
                content=content,
                timestamp=datetime.fromisoformat(timestamp_str),
                metadata=json.loads(metadata_str) if metadata_str else {}
            ))
        
        conn.close()
        return messages
    
    def get_conversations(self, limit: int = 50) -> List[Dict]:
        """Lade Liste aller Konversationen (neueste zuerst)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, provider_id, model_id, created_at, updated_at
            FROM conversations
            ORDER BY updated_at DESC
            LIMIT ?
        """, (limit,))
        
        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                "id": row[0],
                "title": row[1],
                "provider_id": row[2],
                "model_id": row[3],
                "created_at": row[4],
                "updated_at": row[5]
            })
        
        conn.close()
        return conversations
    
    def delete_conversation(self, conversation_id: str):
        """Lösche Konversation inkl. aller Messages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
        cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
        
        conn.commit()
        conn.close()
    
    def update_conversation_title(self, conversation_id: str, new_title: str):
        """Update Konversations-Titel"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE conversations 
            SET title = ?, updated_at = ?
            WHERE id = ?
        """, (new_title, datetime.now().isoformat(), conversation_id))
        
        conn.commit()
        conn.close()
    
    def get_conversation_preview(self, conversation_id: str) -> Optional[str]:
        """Hole ersten User-Message als Preview"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT content FROM messages
            WHERE conversation_id = ? AND role = 'user'
            ORDER BY timestamp ASC
            LIMIT 1
        """, (conversation_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            # Erste 50 Zeichen
            preview = row[0][:50]
            if len(row[0]) > 50:
                preview += "..."
            return preview
        return None
