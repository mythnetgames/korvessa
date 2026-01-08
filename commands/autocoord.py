from evennia import Command
from typeclasses.rooms import Room

class CmdAutoCoord(Command):
    """
    autocoord
    
    Automatically assign coordinates to the current room based on exits.
    """
    key = "autocoord"
    locks = "cmd:perm(Builders)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        room = caller.location
        if not room or not room.is_typeclass(Room, exact=False):
            caller.msg("You must be in a room to auto-assign coordinates.")
            return
        
        room._assign_coordinates_from_exits()
        caller.msg(f"Room {room.key} coordinates auto-assigned to ({room.db.x}, {room.db.y}, {room.db.z}).")
