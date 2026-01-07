"""Window management commands for builders."""

from evennia import Command
from evennia.utils import create
from typeclasses.window import Window


class CmdAttachWindow(Command):
    """Attach a new window to this room.

    Usage:
        attachwindow

    This creates a window object in your current room. After creating it,
    use 'windowcoord x y z' to set which room it observes.
    """

    key = "attachwindow"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        location = caller.location

        if not location:
            caller.msg("You must be in a room to attach a window.")
            return

        # Check for existing windows to prevent spam
        windows = [obj for obj in location.contents
                   if obj.is_typeclass("typeclasses.window.Window", exact=True)]

        if windows:
            caller.msg(f"There {('is' if len(windows) == 1 else 'are')} already "
                       f"{len(windows)} window(s) in this room.")
            return

        # Create the window
        window = create.create_object(
            "typeclasses.window.Window",
            key="window",
            location=location
        )

        caller.msg(f"Window created. Use 'windowcoord x y z' to set its target.")
        location.msg_contents(f"{caller.get_display_name()} creates a window.",
                              exclude=[caller])


class CmdRemoveWindow(Command):
    """Remove all windows from this room.

    Usage:
        removewindow

    This destroys all window objects in your current room.
    """

    key = "removewindow"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        location = caller.location

        if not location:
            caller.msg("You must be in a room.")
            return

        windows = [obj for obj in location.contents
                   if obj.is_typeclass("typeclasses.window.Window", exact=True)]

        if not windows:
            caller.msg("No windows found in this room.")
            return

        count = len(windows)
        for window in windows:
            window.delete()

        caller.msg(f"Removed {count} window(s).")
        location.msg_contents(f"{caller.get_display_name()} removes some windows.",
                              exclude=[caller])


class CmdWindowCoord(Command):
    """Set a window's target coordinates.

    Usage:
        windowcoord <x> <y> <z>

    Sets the target room coordinates for the window in this room.
    The window will observe the room at those coordinates.

    Example:
        windowcoord 5 10 0
    """

    key = "windowcoord"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        location = caller.location

        if not location:
            caller.msg("You must be in a room.")
            return

        # Parse coordinates
        args = self.args.strip().split()
        if len(args) != 3:
            caller.msg("Usage: windowcoord <x> <y> <z>")
            return

        try:
            x, y, z = int(args[0]), int(args[1]), int(args[2])
        except ValueError:
            caller.msg("Coordinates must be integers.")
            return

        # Find the window
        windows = [obj for obj in location.contents
                   if obj.is_typeclass("typeclasses.window.Window", exact=True)]

        if not windows:
            caller.msg("No window found in this room. Use 'attachwindow' first.")
            return

        window = windows[0]  # Use the first window if multiple exist
        window.set_target_coords(x, y, z)
        caller.msg(f"Window now observes room at coordinates ({x}, {y}, {z}).")
        location.msg_contents(f"{caller.get_display_name()} adjusts a window.",
                              exclude=[caller])


class CmdDebugWindows(Command):
    """Show all windows in this room and their target coordinates.

    Usage:
        debugwindows

    This command is for debugging and shows information about all windows
    in your current room.
    """

    key = "debugwindows"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        location = caller.location

        if not location:
            caller.msg("You must be in a room.")
            return

        windows = [obj for obj in location.contents
                   if obj.is_typeclass("typeclasses.window.Window", exact=True)]

        if not windows:
            caller.msg("No windows found in this room.")
            return

        caller.msg("|cWindows in this room:|n")
        for window in windows:
            x, y, z = window.get_target_coords()
            caller.msg(f"  - {window.get_display_name()}: targets ({x}, {y}, {z})")

