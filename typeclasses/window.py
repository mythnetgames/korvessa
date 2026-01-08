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

    def get_display_desc(self, looker, **kwargs):
        """
        Return the description of the target room as seen through the window.
        
        Args:
            looker: The character looking at the window
            
        Returns:
            String with the target room's description and contents
        """
        # Get target coordinates
        target_x = getattr(self.db, 'target_x', None)
        target_y = getattr(self.db, 'target_y', None)
        target_z = getattr(self.db, 'target_z', None)
        
        # If window has no target coordinates set, show base description
        base_desc = self.db.desc or "A window looking into another space."
        if target_x is None or target_y is None or target_z is None:
            return base_desc
        
        try:
            from typeclasses.rooms import Room
            
            # Search for room with matching coordinates
            target_room = None
            for room in Room.objects.all():
                room_x = getattr(room.db, 'x', None)
                room_y = getattr(room.db, 'y', None)
                room_z = getattr(room.db, 'z', None)
                
                if room_x == target_x and room_y == target_y and room_z == target_z:
                    target_room = room
                    break
            
            if not target_room:
                return base_desc
            
            # Get the target room's description
            room_desc = target_room.db.desc or "A featureless room."
            
            # Get display of what's in the target room
            room_display = target_room.get_display_characters(looker) if hasattr(target_room, 'get_display_characters') else None
            
            # Combine room description with character display
            result = room_desc
            if room_display:
                result += f"\n\n{room_display}"
            
            return result
                
        except Exception as e:
            # If anything goes wrong, return base description
            return base_desc

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

        OPPOSITE_DIRECTIONS = {
            'north': 'south', 'south': 'north',
            'east': 'west', 'west': 'east',
            'northeast': 'southwest', 'southwest': 'northeast',
            'northwest': 'southeast', 'southeast': 'northwest',
            'up': 'down', 'down': 'up',
            'in': 'out', 'out': 'in',
            'n': 's', 's': 'n', 'e': 'w', 'w': 'e',
            'ne': 'sw', 'sw': 'ne', 'nw': 'se', 'se': 'nw',
            'u': 'd', 'd': 'u'
        }
        if movement_type == 'enter':
            if direction:
                entry_dir = OPPOSITE_DIRECTIONS.get(direction.lower(), direction)
                msg = f"Through the window, you see {char.get_display_name()} enter from the {entry_dir}."
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
