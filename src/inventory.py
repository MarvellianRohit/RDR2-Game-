class WeaponNode:
    """A node in the circular linked list representing a weapon."""
    def __init__(self, name, damage, ammo_capacity, fire_rate, sprite_ref=None):
        self.name = name
        self.damage = damage
        self.ammo_capacity = ammo_capacity
        self.current_ammo = ammo_capacity  # Initialize with full clip
        self.fire_rate = fire_rate
        self.sprite_ref = sprite_ref
        self.next = None
        self.prev = None

class WeaponWheel:
    """A Circular Linked List for weapon cycling."""
    def __init__(self):
        self.head = None
        self.current_weapon = None
        self.size = 0

    def add_weapon(self, name, damage, ammo_capacity, fire_rate, sprite_ref=None):
        """Adds a weapon to the wheel, maintaining circularity."""
        new_node = WeaponNode(name, damage, ammo_capacity, fire_rate, sprite_ref)
        
        if not self.head:
            self.head = new_node
            new_node.next = new_node
            new_node.prev = new_node
            self.current_weapon = new_node
        else:
            tail = self.head.prev
            tail.next = new_node
            new_node.prev = tail
            new_node.next = self.head
            self.head.prev = new_node
            
        self.size += 1
        print(f"[Inventory] Added {name} to weapon wheel.")

    def next_weapon(self):
        """Cycles to the next weapon."""
        if self.current_weapon:
            self.current_weapon = self.current_weapon.next
            return self.current_weapon
        return None

    def previous_weapon(self):
        """Cycles to the previous weapon."""
        if self.current_weapon:
            self.current_weapon = self.current_weapon.prev
            return self.current_weapon
        return None

    def get_current(self):
        """Returns the currently equipped weapon."""
        return self.current_weapon
