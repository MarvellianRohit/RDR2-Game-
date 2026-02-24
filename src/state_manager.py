import pygame

class GameState:
    """Base class for all game states."""
    def __init__(self, manager):
        self.manager = manager

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, screen):
        pass

class StateManager:
    """Manages game states using a LIFO stack."""
    def __init__(self):
        self._stack = []
        print("[State] State Manager initialized.")

    def push(self, state):
        """Pushes a new state onto the stack."""
        self._stack.append(state)
        print(f"[State] Pushed: {type(state).__name__}")

    def pop(self):
        """Removes the top state from the stack."""
        if self._stack:
            state = self._stack.pop()
            print(f"[State] Popped: {type(state).__name__}")
            return state
        return None

    def peek(self):
        """Returns the top state without removing it."""
        return self._stack[-1] if self._stack else None

    def handle_event(self, event):
        """Passes events to the active state."""
        state = self.peek()
        if state:
            state.handle_event(event)

    def update(self, dt):
        """Updates the active state."""
        state = self.peek()
        if state:
            state.update(dt)

    def draw(self, screen):
        """Renders the active state."""
        # Optional: You could draw all states in the stack if you want transparency
        # but for now we only draw the top state.
        state = self.peek()
        if state:
            state.draw(screen)
