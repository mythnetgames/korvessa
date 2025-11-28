from evennia import Command

class CmdMap(Command):
    """
    Show a 5x5 map centered on your current room.
    Usage: map
    """
    key = "map"
    locks = "cmd:perm(Builder)"
    help_category = "Mapping"

    def func(self):
        room = self.caller.location
        x = getattr(room.db, "x", None)
        y = getattr(room.db, "y", None)
        z = getattr(room.db, "z", None)
        if x is None or y is None or z is None:
            self.caller.msg("This room does not have valid coordinates. The map cannot be displayed.")
            return
        # Find all rooms with coordinates on this z level
        from evennia.objects.models import ObjectDB
        rooms = ObjectDB.objects.filter(db_typeclass_path="typeclasses.rooms.Room")
        coords = {(r.db.x, r.db.y): r for r in rooms if r.db.x is not None and r.db.y is not None and r.db.z == z}
        # Build 5x5 grid
        grid = []
        for dy in range(2, -3, -1):
            row = []
            for dx in range(-2, 3):
                cx, cy = x + dx, y + dy
                if (cx, cy) == (x, y):
                    row.append("[x]")
                elif (cx, cy) in coords:
                    row.append("[ ]")
                else:
                    row.append("   ")
            grid.append(" ".join(row))
        self.caller.msg("\n".join(grid) + f"\nCurrent coordinates: x={x}, y={y}, z={z}")
