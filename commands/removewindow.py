from evennia import Command

class CmdRemoveWindow(Command):
    """Remove the window from this room (builder+ only)."""
    key = "removewindow"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        if not caller.location:
            caller.msg("You must be in a room to remove a window.")
            return
        window = None
        for obj in caller.location.contents:
            if obj.is_typeclass("typeclasses.window.Window"):
                window = obj
                break
        if not window:
            caller.msg("No window found in this room.")
            return
        window.delete()
        caller.msg("Window removed from this room.")