"""
Connect command - Use a digging tool to connect two rooms via coordinates.

This command allows characters holding a digging tool to connect the current room
to another room that exists at the calculated coordinates in the specified direction.
If a room exists at those coordinates, bidirectional exits are created.
If no room exists at those coordinates, the command fails.
"""

from evennia import Command
from evennia.utils import create


class CmdConnect(Command):
    """
    Use a digging tool to connect two rooms together.
    
    Usage:
        connect <direction>
        
    Examples:
        connect north
        connect e
        connect up
    
    This command requires you to be holding a digging tool. It will:
    1. Calculate the coordinates of the room to the specified direction
    2. Look for an existing room at those coordinates
    3. If found, create bidirectional exits between the current room and that room
    4. If not found, the command fails
    
    Supported directions: north, south, east, west, northeast, northwest, southeast, southwest, up, down
    (Also accepts short forms: n, s, e, w, ne, nw, se, sw, u, d)
    """
    key = "connect"
    aliases = ["dig"]
    locks = "cmd:all()"
    help_category = "Building"
    
    # Direction to coordinate offset mapping
    DIRECTION_OFFSETS = {
        "north": (0, 1, 0), "n": (0, 1, 0),
        "south": (0, -1, 0), "s": (0, -1, 0),
        "east": (1, 0, 0), "e": (1, 0, 0),
        "west": (-1, 0, 0), "w": (-1, 0, 0),
        "northeast": (1, 1, 0), "ne": (1, 1, 0),
        "northwest": (-1, 1, 0), "nw": (-1, 1, 0),
        "southeast": (1, -1, 0), "se": (1, -1, 0),
        "southwest": (-1, -1, 0), "sw": (-1, -1, 0),
        "up": (0, 0, 1), "u": (0, 0, 1),
        "down": (0, 0, -1), "d": (0, 0, -1),
    }
    
    # Reverse direction mapping for creating return exits
    REVERSE_DIRECTIONS = {
        "north": "south", "south": "north",
        "east": "west", "west": "east",
        "northeast": "southwest", "southwest": "northeast",
        "northwest": "southeast", "southeast": "northwest",
        "up": "down", "down": "up"
    }
    
    # Full names for directions (normalize short forms)
    DIRECTION_NAMES = {
        "n": "north", "s": "south", "e": "east", "w": "west",
        "ne": "northeast", "nw": "northwest", "se": "southeast", "sw": "southwest",
        "u": "up", "d": "down"
    }
    
    def func(self):
        """Execute the connect command."""
        caller = self.caller
        
        # Validate arguments
        if not self.args:
            caller.msg("Usage: connect <direction>")
            caller.msg("Supported directions: north, south, east, west, northeast, northwest, southeast, southwest, up, down")
            return
        
        # Get current location
        current_room = caller.location
        if not current_room:
            caller.msg("You must be in a room to use this command.")
            return
        
        # Check for digging tool
        if not self._has_digging_tool(caller):
            caller.msg("You need to be holding a digging tool to use this command.")
            return
        
        # Parse direction
        direction = self.args.strip().lower()
        if direction not in self.DIRECTION_OFFSETS:
            caller.msg(f"Unknown direction: {direction}")
            caller.msg("Supported directions: north, south, east, west, northeast, northwest, southeast, southwest, up, down")
            return
        
        # Get current room coordinates
        src_x = getattr(current_room.db, 'x', 0) or 0
        src_y = getattr(current_room.db, 'y', 0) or 0
        src_z = getattr(current_room.db, 'z', 0) or 0
        
        # Calculate target coordinates
        offset = self.DIRECTION_OFFSETS[direction]
        target_x = src_x + offset[0]
        target_y = src_y + offset[1]
        target_z = src_z + offset[2]
        
        # Get the zone (both rooms must be in same zone)
        current_zone = getattr(current_room, 'zone', None)
        
        # Search for a room at the target coordinates in the same zone
        target_room = self._find_room_at_coords(target_x, target_y, target_z, current_zone)
        
        if not target_room:
            caller.msg(f"No room exists at coordinates ({target_x}, {target_y}, {target_z}).")
            return
        
        # Check if exit already exists
        if self._exit_exists(current_room, direction):
            caller.msg(f"An exit to the {direction} already exists.")
            return
        
        # Normalize direction name
        dir_name = self.DIRECTION_NAMES.get(direction, direction)
        reverse_dir_name = self.REVERSE_DIRECTIONS.get(dir_name, None)
        
        # Create forward exit
        try:
            create.create_object(
                typeclass="typeclasses.exits.Exit",
                key=dir_name,
                location=current_room,
                destination=target_room
            )
        except Exception as e:
            caller.msg(f"Error creating forward exit: {e}")
            return
        
        # Create reverse exit
        try:
            if reverse_dir_name:
                create.create_object(
                    typeclass="typeclasses.exits.Exit",
                    key=reverse_dir_name,
                    location=target_room,
                    destination=current_room
                )
        except Exception as e:
            caller.msg(f"Forward exit created, but error creating return exit: {e}")
            return
        
        # Success messages
        caller.msg(f"|gYou use your digging tool to connect to {target_room.key} to the {dir_name}.|n")
        caller.msg(f"|g{current_room.key} ({src_x}, {src_y}, {src_z}) <-> {target_room.key} ({target_x}, {target_y}, {target_z})|n")
        
        # Notify room
        current_room.msg_contents(
            f"|g{caller.key} uses a digging tool to create an exit to the {dir_name}.|n",
            exclude=[caller]
        )
    
    def _has_digging_tool(self, character):
        """Check if character is holding a digging tool."""
        # Check if character has a hands attribute with equipped items
        if hasattr(character, 'hands') and character.hands:
            for hand, item in character.hands.items():
                if item and self._is_digging_tool(item):
                    return True
        
        # Fallback: check equipped items in inventory with tags
        for item in character.contents:
            if hasattr(item, 'tags') and item.tags.has('equipped', category='combat'):
                if self._is_digging_tool(item):
                    return True
        
        # Fallback: search for digging tool in inventory by keyword
        for item in character.contents:
            if self._is_digging_tool(item):
                return True
        
        return False
    
    def _is_digging_tool(self, item):
        """Check if an item is a digging tool."""
        if not item:
            return False
        
        item_key = item.key.lower()
        item_name = getattr(item, 'name', '').lower()
        
        # Check item key and name for digging tool keywords
        digging_keywords = ['dig', 'shovel', 'pickaxe', 'pick', 'axe', 'spade', 'excavator', 'tool']
        
        for keyword in digging_keywords:
            if keyword in item_key or keyword in item_name:
                return True
        
        # Check db attributes for tool type
        if hasattr(item, 'db'):
            tool_type = getattr(item.db, 'tool_type', '')
            if tool_type and 'dig' in tool_type.lower():
                return True
        
        return False
    
    def _find_room_at_coords(self, x, y, z, zone=None):
        """Find a room at the specified coordinates in the given zone."""
        from evennia.objects.models import ObjectDB
        
        try:
            # Query for rooms at the target coordinates
            if zone:
                room = ObjectDB.objects.filter(
                    db_typeclass_path__endswith='typeclasses.rooms.Room',
                    db_zone=zone
                ).filter(
                    db_attributes__db_key='x',
                    db_attributes__db_value=str(x)
                ).filter(
                    db_attributes__db_key='y',
                    db_attributes__db_value=str(y)
                ).filter(
                    db_attributes__db_key='z',
                    db_attributes__db_value=str(z)
                ).first()
            else:
                # If no zone, search without zone filter
                room = ObjectDB.objects.filter(
                    db_typeclass_path__endswith='typeclasses.rooms.Room'
                ).filter(
                    db_attributes__db_key='x',
                    db_attributes__db_value=str(x)
                ).filter(
                    db_attributes__db_key='y',
                    db_attributes__db_value=str(y)
                ).filter(
                    db_attributes__db_key='z',
                    db_attributes__db_value=str(z)
                ).first()
            
            return room
        except Exception as e:
            # Fallback: iterate through all rooms
            return self._find_room_at_coords_fallback(x, y, z, zone)
    
    def _find_room_at_coords_fallback(self, x, y, z, zone=None):
        """Fallback method to find room by iterating through objects."""
        from evennia.objects.models import ObjectDB
        
        try:
            rooms = ObjectDB.objects.filter(
                db_typeclass_path__endswith='typeclasses.rooms.Room'
            )
            
            for room in rooms:
                room_x = getattr(room.db, 'x', None)
                room_y = getattr(room.db, 'y', None)
                room_z = getattr(room.db, 'z', None)
                room_zone = getattr(room, 'zone', None)
                
                # Match coordinates and zone if specified
                if room_x == x and room_y == y and room_z == z:
                    if zone is None or room_zone == zone:
                        return room
            
            return None
        except Exception:
            return None
    
    def _exit_exists(self, room, direction):
        """Check if an exit in the given direction already exists."""
        # Normalize direction name
        dir_name = self.DIRECTION_NAMES.get(direction, direction)
        
        if hasattr(room, 'exits'):
            for exit_obj in room.exits:
                if exit_obj.key.lower() == dir_name.lower():
                    return True
        
        return False
