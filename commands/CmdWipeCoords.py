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
        self.caller.msg(f"Wiped coordinates for {count} rooms.")
