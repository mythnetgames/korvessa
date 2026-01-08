from evennia import Command
from typeclasses.rooms import Room

class CmdSetCoord(Command):
    """
    setcoord <x> <y> <z>
    
    Manually set the coordinates of the current room.
    """
    key = "setcoord"
    locks = "cmd:perm(Builders)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        args = self.args.strip().split()
        if len(args) != 3:
            caller.msg("Usage: setcoord <x> <y> <z>")
            return
        
        try:
            x, y, z = int(args[0]), int(args[1]), int(args[2])
        except ValueError:
            caller.msg("Coordinates must be integers.")
            return
        
        room = caller.location
        if not room or not room.is_typeclass(Room, exact=False):
            caller.msg("You must be in a room to set its coordinates.")
            return
        
        room.db.x = x
        room.db.y = y
        room.db.z = z
        caller.msg(f"Room {room.key} (dbref {room.dbref}) coordinates set to ({x}, {y}, {z}).")
