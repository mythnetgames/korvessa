"""
Wipe all mapping and coordinate attributes from all rooms in the database.
Run with: py evennia shell scripts/wipe_coordinates.py
"""
from evennia.objects.models import ObjectDB

def wipe_coords():
    rooms = ObjectDB.objects.filter(db_typeclass_path__endswith="typeclasses.rooms.Room")
    for room in rooms:
        for attr in ["x", "y", "z", "map_color"]:
            if hasattr(room.db, attr):
                delattr(room.db, attr)
        print(f"Wiped coordinates for {room.key}")

if __name__ == "__main__":
    wipe_coords()
    print("All room coordinates and map colors wiped.")
