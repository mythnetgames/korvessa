from evennia import Command
from typeclasses.rooms import Room

class CmdSetZone(Command):
    """
    setzone <zone>
    
    Manually assign the current room to a zone (by number or name).
    """
    key = "setzone"
    locks = "cmd:perm(Builders)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        if not self.args.strip():
            caller.msg("Usage: setzone <zone>")
            return
        zone = self.args.strip()
        room = caller.location
        if not room or not room.is_typeclass(Room, exact=False):
            caller.msg("You must be in a room to set its zone.")
            return
        room.zone = zone
        room.db.zone = zone
        # Update coordinates to match new zone
        room.update_zone_and_coordinates()
        caller.msg(f"Room {room.key} (dbref {room.dbref}) assigned to zone '{zone}' and coordinates updated to ({room.db.x}, {room.db.y}, {room.db.z}).")
