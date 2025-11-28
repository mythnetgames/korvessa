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
        # Only consider rooms in the 5x5 grid
        found_rooms = []
        for dy in range(-2, 3):
            row = []
            for dx in range(-2, 3):
                rx, ry = x0 + dx, y0 + dy
                # Search for a room at (rx, ry)
                target_room = None
                for obj in search_object("*"):
                    if hasattr(obj, "db") and getattr(obj.db, "x", None) == rx and getattr(obj.db, "y", None) == ry:
                        target_room = obj
                        found_rooms.append(f"Found room: {obj.key} at ({rx},{ry})")
                        break
                if target_room:
                    if target_room == room:
                        row.append('[x]')
                    else:
                        row.append('[ ]')
                else:
                    row.append('   ')
            grid.append(''.join(row))
        # Debug output for found rooms
        caller.msg("\n".join(found_rooms))
        map_str = "\n".join(grid)
        coord_str = f"Current coordinates: x={x0}, y={y0}"
        caller.msg(f"{map_str}\n|c{coord_str}|n")
