from evennia import Command
from evennia.objects.models import ObjectDB
from typeclasses.rooms import Room

class CmdDeleteZone(Command):
    """
    deletezone <zone>
    
    Deletes all rooms assigned to the specified zone.
    """
    key = "deletezone"
    locks = "cmd:perm(Builders)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        zone = self.args.strip()
        if not zone:
            caller.msg("Usage: deletezone <zone>")
            return
        rooms = [obj for obj in ObjectDB.objects.all() if obj.is_typeclass(Room, exact=False) and (getattr(obj, 'zone', None) == zone or obj.db.zone == zone)]
        if not rooms:
            caller.msg(f"No rooms found for zone '{zone}'.")
            return
        for room in rooms:
            room.delete()
        caller.msg(f"Deleted {len(rooms)} rooms in zone '{zone}'.")
