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
        all_rooms = [obj for obj in search_object("*") if hasattr(obj, "db") and getattr(obj.db, "x", None) is not None and getattr(obj.db, "y", None) is not None]
        room_lookup = {(r.db.x, r.db.y): r for r in all_rooms}
        for dy in range(-2, 3):
            # Room row
            room_row = []
            for dx in range(-2, 3):
                rx, ry = x0 + dx, y0 + dy
                target_room = room_lookup.get((rx, ry))
                if target_room:
                    if target_room == room:
                        room_row.append('[x]')
                    else:
                        room_row.append('[ ]')
                else:
                    room_row.append('   ')
            grid.append(''.join(room_row))
            # Connector row (between this and next room row)
            if dy < 2:
                conn_row = []
                for dx in range(-2, 3):
                    rx, ry = x0 + dx, y0 + dy
                    # East/west connector
                    right_room = room_lookup.get((rx+1, ry))
                    this_room = room_lookup.get((rx, ry))
                    if this_room and right_room:
                        conn_row.append('--')
                    else:
                        conn_row.append('  ')
                    # Vertical connector
                    down_room = room_lookup.get((rx, ry+1))
                    if this_room and down_room:
                        conn_row.append('| ')
                    else:
                        conn_row.append('  ')
                grid.append(''.join(conn_row))
        map_str = "\n".join(grid)
        coord_str = f"Current coordinates: x={x0}, y={y0}"
        caller.msg(f"{map_str}\n|c{coord_str}|n")
