"""
fix_room_coordinates.py

Automated coordinate assignment for all rooms in the database.
Recursively propagates coordinates from mapped rooms to all reachable rooms using exits and direction names.

Usage:
    py evennia shell scripts/fix_room_coordinates.py
"""

from evennia.objects.models import ObjectDB

DIRECTIONS = {
    "north": (0, 1, 0),
    "south": (0, -1, 0),
    "east": (1, 0, 0),
    "west": (-1, 0, 0),
    "up": (0, 0, 1),
    "down": (0, 0, -1)
}

def get_room_exits(room):
    return [ex for ex in room.exits if hasattr(ex, "destination") and ex.destination]

def propagate_coordinates(start_room):
    from collections import deque
    visited = set()
    queue = deque()
    queue.append(start_room)
    visited.add(start_room.id)

    while queue:
        room = queue.popleft()
        x, y, z = room.db.x, room.db.y, room.db.z
        for exit_obj in get_room_exits(room):
            dest = exit_obj.destination
            if dest.id in visited:
                continue
            dx, dy, dz = DIRECTIONS.get(exit_obj.key.lower(), (0, 0, 0))
            # Only assign if dest has missing coordinates
            if getattr(dest.db, "x", None) is None or getattr(dest.db, "y", None) is None or getattr(dest.db, "z", None) is None:
                dest.db.x = x + dx
                dest.db.y = y + dy
                dest.db.z = z + dz
                print(f"Set coordinates for {dest.key}: x={dest.db.x}, y={dest.db.y}, z={dest.db.z}")
            queue.append(dest)
            visited.add(dest.id)

def fix_all_room_coordinates():
    # Find all rooms with valid coordinates
    rooms = ObjectDB.objects.filter(db_typeclass_path__endswith="typeclasses.rooms.Room")
    mapped_rooms = [room for room in rooms if getattr(room.db, "x", None) is not None and getattr(room.db, "y", None) is not None and getattr(room.db, "z", None) is not None]
    if not mapped_rooms:
        print("No mapped rooms found. Use @maproom in at least one room to set initial coordinates.")
        return
    for start_room in mapped_rooms:
        propagate_coordinates(start_room)

if __name__ == "__main__":
    fix_all_room_coordinates()
    print("Automated room coordinate propagation complete.")
