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
    
    def return_appearance(self, looker):
        """
        Return the appearance of the window, including contents of the room it observes.
        
        Args:
            looker: The character looking at the window
            
        Returns:
            String describing the window and what's visible through it
        """
        # Get the base description
        base_desc = self.db.desc or "A window looking into another space."
        
        # Try to find the target room by coordinates
        from typeclasses.rooms import Room
        coords = self.get_target_coords()
        
        try:
            target_room = Room.objects.get(
                db_attributes__db_key="zone",
                db_attributes__db_value=str(getattr(self.location, 'db', type('obj', (object,), {'zone': '0'})).zone or '0'))
            
            # Look for room with matching coordinates in the same zone
            for room in Room.objects.filter(db_location=None):  # Rooms with no parent (world rooms)
                room_x = getattr(room.db, 'x', None)
                room_y = getattr(room.db, 'y', None)
                room_z = getattr(room.db, 'z', None)
                
                if room_x == coords[0] and room_y == coords[1] and room_z == coords[2]:
                    target_room = room
                    break
            else:
                # Room not found, return just the base description
                return base_desc
                
        except Exception:
            # If anything goes wrong, just return base description
            return base_desc
        
        # Get characters and objects in the target room
        contents = []
        for obj in target_room.contents:
            if hasattr(obj, 'get_display_name'):
                contents.append(obj.get_display_name(looker))
        
        # Format the description with contents
        if contents:
            contents_str = ", ".join(contents)
            return f"{base_desc}\n\n|cThrough the window:|n {contents_str}"
        else:
            return f"{base_desc}\n\n|cThrough the window:|n The room appears empty."

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
