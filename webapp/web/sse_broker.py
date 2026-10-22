"""
SSE event broker — fan-out of live events to connected dashboard clients.

Two backends, selected automatically:

  - InMemoryBroker (default): per-process Queue fan-out. Perfect for a single
    Gunicorn worker / single instance. Zero dependencies.

  - RedisBroker (when REDIS_URL is set): publishes events to a Redis channel and
    every worker/instance subscribes, so an event produced on one worker reaches
    SSE clients connected to ANY worker or instance. This is what makes the
    real-time dashboard correct when scaled horizontally.

Both expose the same interface:
    broker.publish(message: dict)
    broker.subscribe() -> generator yielding message dicts (blocking with timeout)

A subscriber generator yields None on idle timeout so the caller can emit an SSE
heartbeat and keep the connection alive.
"""
import json
import logging
import os
import queue
import threading

logger = logging.getLogger(__name__)

_IDLE_TIMEOUT = 15  # seconds between heartbeats


class InMemoryBroker:
    backend = "memory"

    def __init__(self):
        self._subscribers = []
        self._lock = threading.Lock()

    def publish(self, message: dict):
        with self._lock:
            subs = list(self._subscribers)
        for q in subs:
            try:
                q.put_nowait(message)
            except queue.Full:
                pass  # drop for slow consumers rather than block the producer

    def subscribe(self):
        q = queue.Queue(maxsize=100)
        with self._lock:
            self._subscribers.append(q)
        try:
            while True:
                try:
                    yield q.get(timeout=_IDLE_TIMEOUT)
                except queue.Empty:
                    yield None  # heartbeat tick
        finally:
            with self._lock:
                if q in self._subscribers:
                    self._subscribers.remove(q)


class RedisBroker:
    backend = "redis"
    CHANNEL = "autoprocure:events"

    def __init__(self, url: str):
        import redis  # imported lazily so redis is optional
        self._redis = redis.Redis.from_url(url, decode_responses=True)
        # Fail fast if unreachable so the factory can fall back to in-memory.
        self._redis.ping()

    def publish(self, message: dict):
        try:
            self._redis.publish(self.CHANNEL, json.dumps(message, ensure_ascii=False))
        except Exception as e:  # pragma: no cover - network dependent
            logger.warning("Redis publish failed (%s).", e)

    def subscribe(self):
        pubsub = self._redis.pubsub()
        pubsub.subscribe(self.CHANNEL)
        try:
            while True:
                msg = pubsub.get_message(ignore_subscribe_messages=True, timeout=_IDLE_TIMEOUT)
                if msg is None:
                    yield None  # heartbeat tick
                    continue
                data = msg.get("data")
                if not data:
                    yield None
                    continue
                try:
                    yield json.loads(data)
                except (ValueError, TypeError):
                    yield None
        finally:
            try:
                pubsub.close()
            except Exception:
                pass


def _make_broker():
    url = os.environ.get("REDIS_URL", "").strip()
    if url:
        try:
            broker = RedisBroker(url)
            logger.info("SSE broker: Redis (%s) — multi-worker fan-out enabled.", RedisBroker.CHANNEL)
            return broker
        except Exception as e:
            logger.warning("REDIS_URL set but Redis unavailable (%s) — falling back to in-memory SSE.", e)
    return InMemoryBroker()


broker = _make_broker()
