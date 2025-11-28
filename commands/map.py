from evennia import Command, search_object

class CmdMap(Command):
    """Show a 5x5 grid map of rooms and exits around you."""
    key = "map"
    locks = "cmd:all()"
    help_category = "General"
    def func(self):
        caller = self.caller
        room = caller.location
        # Check for valid x and y coordinates
        x0 = getattr(room.db, "x", None)
        y0 = getattr(room.db, "y", None)
        if x0 is None or y0 is None:
            caller.msg("This room does not have valid x/y coordinates. The map cannot be displayed.")
            return
        grid = []
        found_rooms = []
        # Try to get all rooms by typeclass (if available)
        try:
            from evennia.utils.search import search_object
            all_rooms = [obj for obj in search_object("typeclasses.rooms.Room")]
        except Exception:
            all_rooms = [room]  # fallback: only current room
        # Always include current room
        if room not in all_rooms:
            all_rooms.append(room)
        room_lookup = {(r.db.x, r.db.y): r for r in all_rooms if hasattr(r, "db") and getattr(r.db, "x", None) is not None and getattr(r.db, "y", None) is not None}
        for dy in range(-2, 3):
            row = []
            for dx in range(-2, 3):
                rx, ry = x0 + dx, y0 + dy
                target_room = room_lookup.get((rx, ry))
                if target_room:
                    found_rooms.append(f"Found room: {target_room.key} at ({rx},{ry})")
                    if target_room == room:
                        row.append('[x]')
                    else:
                        row.append('[ ]')
                else:
                    row.append('   ')
            grid.append(''.join(row))
        if not found_rooms:
            caller.msg("No rooms found in this area. Check room typeclass and coordinates.")
        else:
            caller.msg("\n".join(found_rooms))
        map_str = "\n".join(grid)
        coord_str = f"Current coordinates: x={x0}, y={y0}"
        caller.msg(f"{map_str}\n|c{coord_str}|n")
