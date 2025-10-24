import asyncio
import logging
import json  # ← Tambahkan ini
from typing import Optional

from .dedup_store import DedupStore
from .stats import Stats
from .models import Event

logger = logging.getLogger("EventAggregator")

class EventProcessor:
    def __init__(self, dedup_store: DedupStore, stats: Stats, queue_size: int = 100):
        self.dedup_store = dedup_store
        self.stats = stats
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=queue_size)
        self._worker_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        if not self._running:
            self._running = True
            self._worker_task = asyncio.create_task(self._worker_loop())
            logger.info("EventProcessor started.")

    async def stop(self):
        if self._running:
            self._running = False
            if self._worker_task:
                await self._worker_task
                logger.info("EventProcessor stopped.")

    async def publish(self, event: Event) -> dict:
        """
        Publish event to queue after dedup check.
        Returns dict with status: 'processed' or 'duplicate'
        """
        self.stats.increment_received()

        # Check duplicate
        if self.dedup_store.is_duplicate(event.topic, event.event_id):
            self.stats.increment_duplicates()
            return {"status": "duplicate"}

        # store event (in-memory + SQLite if ada)
        self.dedup_store.store_event(
            topic=event.topic,
            event_id=event.event_id,
            timestamp=event.timestamp,
            source=event.source,
            payload=json.dumps(event.payload)  # ✅ Convert dict ke JSON string
        )

        # increment unique count
        self.stats.increment_unique()

        # enqueue for async processing
        await self.queue.put(event)
        return {"status": "processed"}

    async def _worker_loop(self):
        while self._running:
            try:
                event: Event = await self.queue.get()
                # Simulate processing delay if needed
                # await asyncio.sleep(0.01)
                logger.info(f"Processed event: topic={event.topic}, id={event.event_id}")
            except Exception as e:
                logger.error(f"Error in worker loop: {e}")
            finally:
                self.queue.task_done()