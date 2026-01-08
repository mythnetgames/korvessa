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
        # Find the highest zone number
        from evennia import search_object
        rooms = [obj for obj in search_object() if obj.is_typeclass(Room, exact=False) and obj.zone is not None]
        zone_numbers = []
        for room in rooms:
            try:
                zone_num = int(room.zone)
                zone_numbers.append(zone_num)
            except (ValueError, TypeError):
                continue
        next_zone = max(zone_numbers) + 1 if zone_numbers else 0
        zonename = str(next_zone)
        # Create the new zone's first room
        room = create.create_object(Room, key=f"Zone {zonename} Room (0,0,0)")
        room.db.x = 0
        room.db.y = 0
        room.db.z = 0
        room.zone = zonename
        room.db.zone = zonename
        room.db.desc = f"This is the starting room of zone {zonename}."
        caller.msg(f"Zone {zonename} created with first room at (0,0,0). Room dbref: {room.dbref}")
        # Optionally, you could link this room to the caller's current room in the given direction
        # or store the zone's origin for further expansion.
        return
