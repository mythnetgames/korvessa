from evennia import Command
from evennia.objects.models import ObjectDB

class CmdFixRoomTypeclass(Command):
    """
    Fix all rooms to use the correct typeclass.
    Usage: @fixroomtypeclass
    """
    key = "@fixroomtypeclass"
    locks = "cmd:perm(Admin)"
    help_category = "Admin"

    def func(self):
        correct_typeclass = "typeclasses.rooms.Room"
        rooms = ObjectDB.objects.filter(db_location=None, db_typeclass_path__contains="room")
        updated = 0
        for room in rooms:
            if room.db_typeclass_path != correct_typeclass:
                room.swap_typeclass(correct_typeclass, clean_attributes=False)
                updated += 1
        self.caller.msg(f"Checked {len(rooms)} rooms. Updated {updated} to {correct_typeclass}.")
