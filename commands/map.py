from evennia import Command, search_object

class CmdMap(Command):
    """Show a 5x5 grid map of rooms and exits around you."""
    key = "map"
    locks = "cmd:all()"
    help_category = "General"
    def func(self):
        caller = self.caller
        room = caller.location
        
        # CRITICAL TEST: Show zone info
        zone = getattr(room, "zone", None)
        caller.msg(f"DEBUG_ZONE_TEST: Your current room's zone is: [{zone}]")
        
        # Check for valid x, y, z coordinates
        x0 = getattr(room.db, "x", None)
        y0 = getattr(room.db, "y", None)
        z0 = getattr(room.db, "z", None)
        args = self.args.strip().split()
        if args and args[0].lstrip('-').isdigit():
            z_view = int(args[0])
        else:
            z_view = z0
        if x0 is None or y0 is None or z0 is None:
            caller.msg("This room does not have valid x/y/z coordinates. The map cannot be displayed.")
            return
        grid = []
        found_rooms = []
        try:
            from evennia.utils.search import search_object
            all_rooms = [obj for obj in search_object("typeclasses.rooms.Room")]
        except Exception:
            all_rooms = [room]
        if room not in all_rooms:
            all_rooms.append(room)
        
        # Filter rooms to only those in the same zone as current room
        current_zone = getattr(room, "zone", None)
        zone_rooms = [r for r in all_rooms if getattr(r, "zone", None) == current_zone]
        
        caller.msg(f"|yAll rooms found: {len(all_rooms)}|n")
        caller.msg(f"|yRooms matching your zone ({current_zone}): {len(zone_rooms)}|n")
        
        # Show first few matched rooms
        for i, r in enumerate(zone_rooms[:3]):
            r_zone = getattr(r, "zone", None)
            r_x = getattr(r.db, "x", None)
            r_y = getattr(r.db, "y", None)
            r_z = getattr(r.db, "z", None)
            caller.msg(f"|y  [{i}] {r.key} - zone={r_zone}, coords=({r_x},{r_y},{r_z})|n")
        
        # Room lookup key includes zone to avoid coordinate collisions between zones
        # Only include rooms with matching zone
        room_lookup = {}
        for r in zone_rooms:
            if hasattr(r, "db") and getattr(r.db, "x", None) is not None and getattr(r.db, "y", None) is not None and getattr(r.db, "z", None) is not None:
                r_zone = getattr(r, "zone", None)
                r_x = getattr(r.db, "x", None)
                r_y = getattr(r.db, "y", None)
                r_z = getattr(r.db, "z", None)
                # Only add if zone matches current zone
                if r_zone == current_zone:
                    room_lookup[(r_zone, r_x, r_y, r_z)] = r
        
        caller.msg(f"|y=== END DEBUG ===|n")
        
        caller.msg(f"DEBUG: Current zone: {current_zone}, Zone rooms: {len(zone_rooms)}, Room lookup entries: {len(room_lookup)}")
        for key in sorted(room_lookup.keys())[:5]:
            caller.msg(f"  Lookup key: {key}")
        # Build grid with connectors for the selected Z level
        for dy in range(-2, 3):
            row = []
            for dx in range(-2, 3):
                rx, ry, rz = x0 + dx, y0 + dy, z_view
                target_room = room_lookup.get((current_zone, rx, ry, rz))
                if target_room:
                    found_rooms.append(f"Found room: {target_room.key} at ({rx},{ry},{rz})")
                    if target_room == room:
                        row.append('[x]')
                    else:
                        row.append('[ ]')
                else:
                    row.append('   ')
                # Add horizontal connector to the right
                if dx < 2:
                    east_room = room_lookup.get((current_zone, rx+1, ry, rz))
                    connector = '   '
                    if target_room and east_room:
                        if hasattr(target_room, 'exits'):
                            for ex in target_room.exits:
                                if getattr(ex, 'destination', None) == east_room:
                                    connector = '--'
                                    break
                    row.append(connector)
            grid.append(''.join(row))
            # Add vertical connector row below
            if dy < 2:
                conn_row = []
                for dx in range(-2, 3):
                    rx, ry, rz = x0 + dx, y0 + dy, z_view
                    target_room = room_lookup.get((current_zone, rx, ry, rz))
                    south_room = room_lookup.get((current_zone, rx, ry+1, rz))
                    connector = '   '
                    if target_room and south_room:
                        if hasattr(target_room, 'exits'):
                            for ex in target_room.exits:
                                if getattr(ex, 'destination', None) == south_room:
                                    connector = ' | '
                                    break
                    conn_row.append(connector)
                    # Add space for horizontal connector
                    if dx < 2:
                        conn_row.append('   ')
                grid.append(''.join(conn_row))
        # Up/down connectors for current room
        up_room = room_lookup.get((current_zone, x0, y0, z_view+1))
        down_room = room_lookup.get((current_zone, x0, y0, z_view-1))
        up_conn = ''
        down_conn = ''
        if up_room and hasattr(room, 'exits'):
            for ex in room.exits:
                if getattr(ex, 'destination', None) == up_room:
                    up_conn = '^ Up exit to z={}'.format(z_view+1)
                    break
        if down_room and hasattr(room, 'exits'):
            for ex in room.exits:
                if getattr(ex, 'destination', None) == down_room:
                    down_conn = 'v Down exit to z={}'.format(z_view-1)
                    break
        if not found_rooms:
            caller.msg("No rooms found in this area. Check room typeclass and coordinates.")
        else:
            caller.msg("\n".join(found_rooms))
        map_str = "\n".join(grid)
        coord_str = f"x={x0}, y={y0}, z={z_view}"
        z_conn_str = ''
        if up_conn:
            z_conn_str += up_conn + " "
        if down_conn:
            z_conn_str += down_conn + " "
        
        debug_info = f"\n[DEBUG] Zone: {current_zone}, Rooms in zone: {len(zone_rooms)}, Room lookup entries: {len(room_lookup)}"
        if up_conn:
            z_conn_str += f'|c{up_conn}|n\n'
        if down_conn:
            z_conn_str += f'|c{down_conn}|n'
        caller.msg(f"{map_str}\n|c{coord_str}|n{debug_info}\n{z_conn_str}")
