from evennia import Command, search_object

class CmdWipeCoords(Command):
    """
    Wipe all room coordinates in the game.
    Usage: @wipecoords
    """
    key = "@wipecoords"
    locks = "cmd:perm(Admin)"
    help_category = "Admin"

    def func(self):
        from evennia.objects.models import ObjectDB
        rooms = ObjectDB.objects.filter(db_typeclass_path="typeclasses.rooms.Room")
        count = 0
        for room in rooms:
            room.db.x = None
            room.db.y = None
            room.db.z = None
            count += 1
        # Check for any rooms that still have coordinates
        still_set = []
        for room in rooms:
            if room.db.x is not None or room.db.y is not None or room.db.z is not None:
                still_set.append(f"{room.key}({room.id}): x={room.db.x}, y={room.db.y}, z={room.db.z}")
        msg = f"Wiped coordinates for {count} rooms."
        if still_set:
            msg += f"\nWARNING: {len(still_set)} rooms still have coordinates set:\n" + "\n".join(still_set[:5])
            if len(still_set) > 5:
                msg += "\n...and more."
        else:
            msg += "\nAll room coordinates are now None."
        self.caller.msg(msg)
