from typing import Callable, Dict, List
import logging

class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}

    def subscribe(self, event: str, listener: Callable):
        self._listeners.setdefault(event, []).append(listener)

    def publish(self, event: str, *args, **kwargs):
        for listener in self._listeners.get(event, []):
            try:
                listener(*args, **kwargs)
            except Exception as e:
                logging.error(f"Error in event listener '{event}': {e}")

# Global event bus instance
event_bus = EventBus()