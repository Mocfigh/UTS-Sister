import logging
import asyncio
import os
import signal
from contextlib import asynccontextmanager
from typing import Optional, Union

from fastapi import FastAPI, HTTPException

from .config import Config
from .dedup_store import DedupStore
from .event_processor import EventProcessor
from .stats import Stats
from .models import Event, EventBatch, EventResponse, StatsResponse

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("EventAggregator")
logger = logging.getLogger("uvicorn.error")

# 🎯 Target event count untuk auto-shutdown
TARGET_EVENT_COUNT = 5000

# =========================
# Factory function
# =========================
def create_app(db_path: Optional[str] = None) -> FastAPI:
    """Create FastAPI app with optional DB path for testing"""

    # Pilih db_path default dari config
    db_path = db_path or getattr(Config, "DATABASE_PATH", None)

    # Inisialisasi komponen
    dedup_store = DedupStore(db_path=db_path)
    stats = Stats()
    event_processor = EventProcessor(dedup_store, stats, queue_size=getattr(Config, "QUEUE_SIZE", 100))

    # Lifespan context
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("🚀 Starting Event Aggregator Service...")
        await event_processor.start()
        logger.info(f"✅ Service started on {getattr(Config, 'HOST', '127.0.0.1')}:{getattr(Config, 'PORT', 8080)}")

        async def monitor_and_shutdown():
            while True:
                await asyncio.sleep(5)
                current = stats.get_stats()["received"]
                if current >= TARGET_EVENT_COUNT:
                    logger.info(f"\n🎯 Target {TARGET_EVENT_COUNT} events reached!")
                    final_stats = stats.get_stats()
                    topics = dedup_store.get_all_topics()
                    logger.info("=== 📊 Final Statistics ===")
                    logger.info(f"Total Events Received : {final_stats['received']}")
                    logger.info(f"Unique Processed       : {final_stats['unique_processed']}")
                    logger.info(f"Duplicate Dropped      : {final_stats['duplicate_dropped']}")
                    logger.info(f"Topics                 : {topics}")
                    logger.info("==============================")
                    await event_processor.stop()
                    logger.info("🟢 EventProcessor stopped. Shutting down service...")
                    await asyncio.sleep(2)
                    os.kill(os.getpid(), signal.SIGTERM)
                    break

        asyncio.create_task(monitor_and_shutdown())
        yield
        logger.info("🛑 Shutting down Event Aggregator Service...")
        await event_processor.stop()
        logger.info("Service stopped gracefully.")

    # Create FastAPI app
    app = FastAPI(
        title="Event Aggregator Service",
        description="A distributed event aggregator with idempotency and deduplication",
        version="1.0.0",
        lifespan=lifespan
    )

    # =========================
    # Endpoints
    # =========================
    @app.get("/")
    async def root():
        return {"service": "Event Aggregator", "status": "running", "version": "1.0.0"}

    @app.post("/publish", response_model=EventResponse)
    async def publish_events(data: Union[Event, EventBatch]):
        try:
            events = [data] if isinstance(data, Event) else data.events or []

            if not events:
                raise HTTPException(status_code=400, detail="No events provided")

            processed = 0
            duplicates = 0

            for event in events:
                result = await event_processor.publish(event)
                if result["status"] == "processed":
                    processed += 1
                elif result["status"] == "duplicate":
                    duplicates += 1

            return EventResponse(
                message="Events processed",
                received=len(events),
                processed=processed,
                duplicates=duplicates
            )
        except Exception as e:
            logger.error(f"Error in publish endpoint: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/events")
    async def get_events(topic: Optional[str] = None):
        try:
            events = dedup_store.get_events(topic)
            import json
            return {
                "count": len(events),
                "events": [
                    {
                        "topic": row[0],
                        "event_id": row[1],
                        "timestamp": row[2],
                        "source": row[3],
                        "payload": json.loads(row[4])
                    }
                    for row in events
                ]
            }
        except Exception as e:
            logger.error(f"Error in get_events endpoint: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/stats", response_model=StatsResponse)
    async def get_stats():
        try:
            stat_data = stats.get_stats()
            topics = dedup_store.get_all_topics()
            return StatsResponse(
                received=stat_data["received"],
                unique_processed=stat_data["unique_processed"],
                duplicate_dropped=stat_data["duplicate_dropped"],
                topics=topics,
                uptime=stat_data["uptime"]
            )
        except Exception as e:
            logger.error(f"Error in stats endpoint: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    return app

# =========================
# Production app
# =========================
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=getattr(Config, "HOST", "127.0.0.1"),
        port=getattr(Config, "PORT", 8080),
        reload=True
    )
