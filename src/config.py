import os

class Config:
    DATABASE_PATH = os.getenv("DATABASE_PATH", "data/events.db")
    QUEUE_SIZE = int(os.getenv("QUEUE_SIZE", "10000"))
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8080"))
    TARGET_URL = "http://event-consumer:8080/events"
