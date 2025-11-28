from evennia import Command

class CmdMapRoom(Command):
    """
    Set coordinates for the current room.
    Usage: @maproom x y z
    """
    key = "@maproom"
    locks = "cmd:perm(Builder)"
    help_category = "Mapping"

    def func(self):
        args = self.args.strip().split()
        if len(args) != 3:
            self.caller.msg("Usage: @maproom x y z")
            return
        try:
            x, y, z = map(int, args)
        except ValueError:
            self.caller.msg("Coordinates must be integers.")
            return
        room = self.caller.location
        room.db.x = x
        room.db.y = y
        room.db.z = z
        self.caller.msg(f"Room '{room.key}' mapped to ({x},{y},{z}).")

class CmdMapOn(Command):
    """
    Turn on the mapper for this session.
    Usage: @mapon
    """
    key = "@mapon"
    locks = "cmd:perm(Builder)"
    help_category = "Mapping"

    def func(self):
        room = self.caller.location
        if not (hasattr(room.db, "x") and hasattr(room.db, "y") and hasattr(room.db, "z")):
            self.caller.msg("You must be in a coordinate-assigned room to enable the mapper.")
            return
        self.caller.ndb.mapper_enabled = True
        self.caller.msg("Mapper enabled. Move to see the map.")

class CmdMapOff(Command):
    """
    Turn off the mapper for this session.
    Usage: @mapoff
    """
    key = "@mapoff"
    locks = "cmd:perm(Builder)"
    help_category = "Mapping"

    def func(self):
        self.caller.ndb.mapper_enabled = False
        self.caller.msg("Mapper disabled.")

