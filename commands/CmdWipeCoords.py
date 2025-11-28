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
        rooms = [obj for obj in search_object() if obj.is_typeclass("typeclasses.rooms.Room", exact=False)]
        count = 0
        for room in rooms:
            room.db.x = None
            room.db.y = None
            room.db.z = None
            count += 1
        self.caller.msg(f"Wiped coordinates for {count} rooms.")
