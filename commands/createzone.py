from evennia import Command
from evennia.utils import create
from typeclasses.rooms import Room

class CmdCreateZone(Command):
    """
    createzone <direction> <zonename>
    
    Creates a new zone in the specified direction, with its own grid and map. The new zone's first room is at (0,0,0).
    """
    key = "createzone"
    locks = "cmd:perm(Builders)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        args = self.args.strip().split()
        if len(args) < 2:
            caller.msg("Usage: createzone <direction> <zonename>")
            return
        direction, zonename = args[0], " ".join(args[1:])
        # Create the new zone's first room
        room = create.create_object(Room, key=f"{zonename} Room (0,0,0)")
        room.db.x = 0
        room.db.y = 0
        room.db.z = 0
        room.zone = zonename
        room.db.zone = zonename
        room.db.desc = f"This is the starting room of zone '{zonename}'."
        caller.msg(f"Zone '{zonename}' created with first room at (0,0,0). Room dbref: {room.dbref}")
        # Optionally, you could link this room to the caller's current room in the given direction
        # or store the zone's origin for further expansion.
