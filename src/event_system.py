from collections import deque

class Event:
    """Represents a game event with a type and optional data."""
    def __init__(self, event_type, data=None):
        self.type = event_type
        self.data = data

    def __repr__(self):
        return f"Event(type='{self.type}', data={self.data})"

class EventManager:
    """Manages an event queue for non-blocking frame-by-frame processing."""
    def __init__(self):
        self._queue = deque()
        print("[Events] Event Manager initialized.")

    def post(self, event_type, data=None):
        """Adds a new event to the queue."""
        event = Event(event_type, data)
        self._queue.append(event)

    def update(self):
        """Processes all events currently in the queue."""
        while self._queue:
            event = self._queue.popleft()
            self._handle_event(event)

    def _handle_event(self, event):
        """The internal dispatcher/processor for events."""
        # For now, we just print the event to the console as requested.
        # In a more advanced system, this would trigger callbacks or state changes.
        print(f"[Events] Processed: {event.type}")
        
        if event.type == 'PLAYER_SHOOT':
            # Specific handling for shooting (triggering C ballistics in the future)
            pass
