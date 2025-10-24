import time
import threading

class Stats:
    def __init__(self):
        self.lock = threading.Lock()
        self.start_time = time.time()
        self.data = {
            "received": 0,
            "unique_processed": 0,
            "duplicate_dropped": 0
        }

    def increment_received(self):
        with self.lock:
            self.data["received"] += 1

    def increment_unique(self):
        with self.lock:
            self.data["unique_processed"] += 1

    def increment_duplicates(self):
        with self.lock:
            self.data["duplicate_dropped"] += 1

    def get_stats(self):
        with self.lock:
            uptime = time.time() - self.start_time
            return {
                "received": self.data["received"],
                "unique_processed": self.data["unique_processed"],
                "duplicate_dropped": self.data["duplicate_dropped"],
                "uptime": round(uptime, 2)
            }
