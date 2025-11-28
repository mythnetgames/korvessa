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
        # Get all rooms in the game with x and y attributes
        all_rooms = [obj for obj in search_object("*") if hasattr(obj, "db") and getattr(obj.db, "x", None) is not None and getattr(obj.db, "y", None) is not None]
        for dy in range(-2, 3):
            row = []
            for dx in range(-2, 3):
                rx, ry = x0 + dx, y0 + dy
                target_room = next((r for r in all_rooms if r.db.x == rx and r.db.y == ry), None)
                if target_room:
                    if target_room == room:
                        cell = "|c@|n"  # Player's current room
                    else:
                        cell = "|wO|n"  # Other room
                else:
                    cell = "|x.|n"  # No room
                row.append(cell)
            grid.append(" ".join(row))
        map_str = "\n".join(grid)
        caller.msg("|wMap (5x5 grid):|n\n" + map_str)
