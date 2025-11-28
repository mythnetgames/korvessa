from evennia import Command
from typeclasses.window import Window

class CmdAttachWindow(Command):
    """Attach a window to this room (builder+ only)."""
    key = "attachwindow"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        if not caller.location:
            caller.msg("You must be in a room to attach a window.")
            return
        # Create and place window in this room
        window = Window()
        window.save()
        window.location = caller.location
        caller.msg("Window attached to this room. Use 'windowcoord x y z' to set its target.")
