"""
Zone-aware dig command that ensures new rooms inherit the parent zone.
"""

from evennia import Command
from evennia.utils import create


class CmdZoneDig(Command):
    """
    Dig a new room in a direction, inheriting the current room's zone.
    
    Usage:
        zdig <direction> = <room name>
        
    Examples:
        zdig north = Dark Alley
        zdig east = Marketplace
        zdig up = Rooftop
    
    This command creates a new room connected to your current location,
    automatically inheriting the zone and assigning proper coordinates.
    """
    key = "zdig"
    aliases = ["zonedig"]
    locks = "cmd:perm(Builders)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        
        if "=" not in self.args:
            caller.msg("Usage: zdig <direction> = <room name>")
            return
        
        direction, room_name = self.args.split("=", 1)
        direction = direction.strip().lower()
        room_name = room_name.strip()
        
        if not direction or not room_name:
            caller.msg("Usage: zdig <direction> = <room name>")
            return
        
        current_room = caller.location
        if not current_room:
            caller.msg("You must be in a room to dig.")
            return
        
        # Get current room's zone and coordinates
        src_zone = getattr(current_room, 'zone', None)
        src_x = getattr(current_room.db, 'x', 0) or 0
        src_y = getattr(current_room.db, 'y', 0) or 0
        src_z = getattr(current_room.db, 'z', 0) or 0
        
        # Calculate new coordinates based on direction
        direction_offsets = {
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
        
        offset = direction_offsets.get(direction)
        if not offset:
            caller.msg(f"Unknown direction: {direction}")
            return
        
        new_x = src_x + offset[0]
        new_y = src_y + offset[1]
        new_z = src_z + offset[2]
        
        # Create the new room
        new_room = create.create_object(
            typeclass="typeclasses.rooms.Room",
            key=room_name
        )
        
        # Set zone and coordinates EXPLICITLY
        if src_zone:
            new_room.zone = src_zone
        new_room.db.x = new_x
        new_room.db.y = new_y
        new_room.db.z = new_z
        new_room.db.desc = "This is a room."
        
        # Create exit from current room to new room
        exit_name = direction
        # Normalize to full direction name
        direction_names = {
            "n": "north", "s": "south", "e": "east", "w": "west",
            "ne": "northeast", "nw": "northwest", "se": "southeast", "sw": "southwest",
            "u": "up", "d": "down"
        }
        exit_name = direction_names.get(direction, direction)
        
        create.create_object(
            typeclass="typeclasses.exits.Exit",
            key=exit_name,
            location=current_room,
            destination=new_room
        )
        
        # Create reverse exit
        reverse_directions = {
            "north": "south", "south": "north",
            "east": "west", "west": "east",
            "northeast": "southwest", "southwest": "northeast",
            "northwest": "southeast", "southeast": "northwest",
            "up": "down", "down": "up"
        }
        reverse_exit_name = reverse_directions.get(exit_name, None)
        if reverse_exit_name:
            create.create_object(
                typeclass="typeclasses.exits.Exit",
                key=reverse_exit_name,
                location=new_room,
                destination=current_room
            )
        
        zone_info = f" in zone '{src_zone}'" if src_zone else ""
        caller.msg(f"Created '{room_name}' ({new_room.dbref}) at ({new_x}, {new_y}, {new_z}){zone_info}.")
        caller.msg(f"Created exit '{exit_name}' to {room_name}.")
        if reverse_exit_name:
            caller.msg(f"Created return exit '{reverse_exit_name}'.")
