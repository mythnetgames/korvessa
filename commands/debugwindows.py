from evennia import Command
from evennia.objects.models import ObjectDB

class CmdDebugWindows(Command):
    """Show all window objects and their target coordinates."""
    key = "debugwindows"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        windows = ObjectDB.objects.filter(db_typeclass_path="typeclasses.window.Window")
        if not windows:
            caller.msg("No window objects found.")
            return
        for win in windows:
            loc = win.location.key if win.location else "None"
            coords = win.db.target_coords if hasattr(win.db, "target_coords") else "None"
            caller.msg(f"Window #{win.id} in '{loc}' targets {coords}")
