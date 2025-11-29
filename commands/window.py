class CmdDebugWindows(Command):
    """Show all windows in this room and their target coordinates."""
    key = "debugwindows"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        windows = [obj for obj in caller.location.contents if obj.is_typeclass("typeclasses.window.Window", exact=True)]
        if not windows:
            coords = (win.db.target_x, win.db.target_y, win.db.target_z)
            from evennia import Command
            from evennia.utils import create
            caller.msg(f"Window '{win.key}' targets room at {coords}.")
from evennia import Command
from evennia.utils import create

## All imports must be at the top before any class definitions
class CmdAttachWindow(Command):
    """Attach a new window to this room, watching a target room by coordinates."""
    key = "attachwindow"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        args = self.args.strip().split()
        if len(args) != 3:
            caller.msg("Usage: attachwindow <x> <y> <z>")
            return
        try:
            x, y, z = map(int, args)
        except ValueError:
            caller.msg("Coordinates must be integers.")
            return
        window = create.create_object("typeclasses.window.Window", key="window", location=caller.location)
        window.set_target_coords(x, y, z)
        caller.msg(f"Window attached in this room, watching ({x}, {y}, {z}).")

class CmdRemoveWindow(Command):
    """Remove all windows from this room."""
    key = "removewindow"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        count = 0
        for obj in caller.location.contents:
            if obj.is_typeclass("typeclasses.window.Window", exact=True):
                obj.delete()
                count += 1
        if count:
            caller.msg(f"Removed {count} window(s) from this room.")
        else:
            caller.msg("No windows found in this room.")

class CmdWindowCoord(Command):
    """Set the coordinates for a window in this room to watch another room."""
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
            if obj.is_typeclass("typeclasses.window.Window", exact=True):
                window = obj
                break
        if not window:
            caller.msg("No window found in this room.")
            return
        window.set_target_coords(x, y, z)
        caller.msg(f"Window now watches room at ({x}, {y}, {z}).")
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
            caller.msg("No window functionality is available.")
