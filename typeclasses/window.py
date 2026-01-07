"""Window - A coordinate-based observation system for rooms."""

from evennia import DefaultObject


class Window(DefaultObject):
    """
    A window object that observes a target room by coordinates (x, y, z).

    When characters enter or leave the target room, this window relays
    messages to its own location about that activity.
    """

    def get_display_name(self, looker=None):
        """Return a plain string name for display."""
        return self.key if isinstance(self.key, str) else str(self.key)

    def at_object_creation(self):
        """Initialize window with target coordinates and description."""
        self.db.target_x = None
        self.db.target_y = None
        self.db.target_z = None
        self.db.desc = "A window looking into another space."
        self.locks.add("view:all();setcoord:perm(Builder)")

    def set_target_coords(self, x, y, z):
        """Set the coordinates of the room this window observes."""
        self.db.target_x = x
        self.db.target_y = y
        self.db.target_z = z

    def get_target_coords(self):
        """Get the coordinates this window is observing."""
        return (self.db.target_x, self.db.target_y, self.db.target_z)

    def relay_movement(self, char, movement_type, direction=None):
        """
        Relay a character's movement to observers in this window's location.

        Args:
            char: The character who moved
            movement_type: 'enter' or 'leave'
            direction: Optional direction string (e.g., 'north', 'south')
        """
        if not self.location:
            return

        if movement_type == 'enter':
            if direction:
                msg = f"Through the window, you see {char.get_display_name()} enter from the {direction}."
            else:
                msg = f"Through the window, you see {char.get_display_name()} enter the room."
        elif movement_type == 'leave':
            if direction:
                msg = f"Through the window, you see {char.get_display_name()} leave to the {direction}."
            else:
                msg = f"Through the window, you see {char.get_display_name()} leave the room."
        else:
            return

        self.location.msg_contents(msg)
