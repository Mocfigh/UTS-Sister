import sqlite3
import threading
import json  # ← Tambahkan import ini
from pathlib import Path
from typing import Optional

class DedupStore:
    def __init__(self, db_path: Optional[str] = None):
        """
        db_path: path ke SQLite file; jika None, gunakan in-memory store saja
        """
        self.db_path = db_path
        self.lock = threading.Lock()
        self.store = {}  # in-memory store {topic: set(event_id)}

        if self.db_path:
            self._init_db()

    def _init_db(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processed_events (
                    topic TEXT NOT NULL,
                    event_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    source TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (topic, event_id)
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_topic ON processed_events(topic)")
            conn.commit()

    # =========================
    # Dedup logic
    # =========================
    def is_duplicate(self, topic: str, event_id: str) -> bool:
        if topic in self.store and event_id in self.store[topic]:
            return True
        if self.db_path:
            with self.lock, sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT 1 FROM processed_events WHERE topic = ? AND event_id = ?",
                    (topic, event_id)
                )
                return cursor.fetchone() is not None
        return False

    def add_event(self, topic: str, event_id: str):
        if topic not in self.store:
            self.store[topic] = set()
        self.store[topic].add(event_id)

    def store_event(self, topic: str, event_id: str, timestamp: str,
                    source: str, payload: str) -> bool:  # ← payload harus string JSON
        """
        Simpan event ke SQLite (jika db_path ada) dan in-memory store.
        Return True jika event berhasil disimpan (unik), False jika duplicate.
        
        Args:
            payload: JSON string dari event payload (bukan dict!)
        """
        if self.is_duplicate(topic, event_id):
            return False

        # simpan ke memori
        self.add_event(topic, event_id)

        # simpan ke SQLite
        if self.db_path:
            try:
                with self.lock, sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT INTO processed_events (topic, event_id, timestamp, source, payload)
                        VALUES (?, ?, ?, ?, ?)
                    """, (topic, event_id, timestamp, source, payload))
                    conn.commit()
            except sqlite3.IntegrityError:
                return False

        return True

    # =========================
    # Query helper
    # =========================
    def get_events(self, topic: Optional[str] = None) -> list:
        if self.db_path:
            with self.lock, sqlite3.connect(self.db_path) as conn:
                if topic:
                    cursor = conn.execute(
                        "SELECT topic, event_id, timestamp, source, payload FROM processed_events WHERE topic = ?",
                        (topic,)
                    )
                else:
                    cursor = conn.execute(
                        "SELECT topic, event_id, timestamp, source, payload FROM processed_events"
                    )
                return cursor.fetchall()
        else:
            # fallback ke memori
            results = []
            for t, ids in self.store.items():
                if topic and t != topic:
                    continue
                for eid in ids:
                    results.append((t, eid, "", "", "{}"))
            return results

    def get_all_topics(self) -> list[str]:
        if self.db_path:
            with self.lock, sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT DISTINCT topic FROM processed_events")
                return [row[0] for row in cursor.fetchall()]
        else:
            return list(self.store.keys())

    # =========================
    # Testing / cleanup
    # =========================
    def clear(self):
        """Hapus semua data, untuk testing"""
        self.store.clear()
        if self.db_path:
            with self.lock, sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM processed_events")
                conn.commit()