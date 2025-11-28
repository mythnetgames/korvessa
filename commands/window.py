from evennia import Command
from typeclasses.window import Window

class CmdWindowCoord(Command):
    """Set the coordinates for a window to observe another room (builder+ only)."""
    key = "windowcoord"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        args = self.args.strip().split()
        if len(args) != 3:
            caller.msg("Usage: windowcoord <x> <y> <z>")
            return
        try:
            x, y, z = map(int, args)
        except ValueError:
            caller.msg("Coordinates must be integers.")
            return
        # Find window in room
        window = None
        for obj in caller.location.contents:
            if obj.is_typeclass("typeclasses.window.Window"):
                window = obj
                break
        if not window:
            caller.msg("No window found in this room.")
            return
        window.set_target_coords(x, y, z, caller)
