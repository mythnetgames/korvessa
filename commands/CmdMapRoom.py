from evennia import Command

class CmdMapRoom(Command):
    """
    Set the current room's map coordinates.
    Usage:
        @maproom <x> <y>
    """
    key = "@maproom"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        room = caller.location
        args = self.args.strip().split()
        if len(args) < 2 or len(args) > 3:
            caller.msg("Usage: @maproom <x> <y> [z]")
            return
        try:
            x = int(args[0])
            y = int(args[1])
            z = int(args[2]) if len(args) == 3 else 0
        except ValueError:
            caller.msg("x, y, and z must be integers.")
            return
        room.db.x = x
        room.db.y = y
        room.db.z = z
        caller.msg(f"Room '{room.key}' mapped to coordinates x={x}, y={y}, z={z}.")
