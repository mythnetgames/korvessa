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
        from evennia.objects.models import ObjectDB
        rooms = [obj for obj in ObjectDB.objects.all() if obj.is_typeclass(Room, exact=False) and getattr(obj, 'zone', None) is not None]
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
        room.zone = zonename
        room.db.x = 0
        room.db.y = 0
        room.db.z = 0
        room.db.desc = f"This is the starting room of zone {zonename}."
        room.update_zone_and_coordinates()
        caller.msg(f"Zone {zonename} created with first room at (0,0,0). Room dbref: {room.dbref}")
        # Link the new zone's room to the caller's current room in the specified direction
        current_room = caller.location
        if current_room and direction:
            # Create exit from current room to new zone room
            exit_obj = create.create_object(
                typeclass="typeclasses.exits.Exit",
                key=direction,
                location=current_room,
                destination=room
            )
            caller.msg(f"Created exit '{direction}' from {current_room.key} to new zone room {room.key}.")
        # Optionally, you could store the zone's origin for further expansion.
        return
