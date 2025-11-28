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
        if len(args) != 2:
            caller.msg("Usage: @maproom <x> <y>")
            return
        try:
            x = int(args[0])
            y = int(args[1])
        except ValueError:
            caller.msg("Both x and y must be integers.")
            return
        room.db.x = x
        room.db.y = y
        caller.msg(f"Room '{room.key}' mapped to coordinates x={x}, y={y}.")
