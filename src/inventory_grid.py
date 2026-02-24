class Item:
    """Represents an item that can be stored in the inventory."""
    def __init__(self, name, stack_size=1, max_stack=1, icon_reference=None):
        self.name = name
        self.stack_size = stack_size
        self.max_stack = max_stack
        self.icon_reference = icon_reference

    def __repr__(self):
        return f"Item(name='{self.name}', stack={self.stack_size}/{self.max_stack})"

class InventoryGrid:
    """Manages a 4x6 grid of inventory slots with stacking logic."""
    def __init__(self, rows=4, cols=6):
        self.rows = rows
        self.cols = cols
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]
        print(f"[Inventory] Grid initialized ({rows}x{cols} slots).")

    def add_item(self, item):
        """Adds an item to the inventory, stacking if possible."""
        # Pass 1: Try to add to an existing stack
        for r in range(self.rows):
            for c in range(self.cols):
                slot_item = self.grid[r][c]
                if slot_item and slot_item.name == item.name:
                    space_left = slot_item.max_stack - slot_item.stack_size
                    if space_left > 0:
                        add_amount = min(space_left, item.stack_size)
                        slot_item.stack_size += add_amount
                        item.stack_size -= add_amount
                        if item.stack_size <= 0:
                            return True

        # Pass 2: Find first empty slot
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] is None:
                    self.grid[r][c] = item
                    return True

        return False # Inventory full

    def get_item_at(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]
        return None
