"""
Window System Test/Demo Commands

Provides testing and demonstration commands for the window system.
For builder+ use only.
"""

from evennia import Command
from world.window_utils import (
    get_windows_for_location,
    get_windows_observing_coords,
    get_all_windows
)


class CmdWindowTest(Command):
    """Test window observation system.

    Usage:
        windowtest [show | relay | coords]

    show: Show all windows in game
    relay: Test relay manually (requires target)
    coords: Show current room coordinates
    """

    key = "windowtest"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        args = self.args.strip().lower()

        if not args or args == "show":
            self.show_all_windows()
        elif args == "coords":
            self.show_room_coords()
        else:
            caller.msg(f"Unknown windowtest option: {args}")
            caller.msg("Usage: windowtest [show | coords]")

    def show_all_windows(self):
        """Display all windows in the game."""
        caller = self.caller
        all_windows = get_all_windows()

        if not all_windows:
            caller.msg("No windows exist in the game.")
            return

        caller.msg("|c=== All Windows in Game ===|n")
        for window in all_windows:
            try:
                x, y, z = window.get_target_coords()
                loc = window.location.key if window.location else "nowhere"
                caller.msg(f"  [{window.id}] {window.key}: in {loc}, watching ({x}, {y}, {z})")
            except (AttributeError, TypeError) as e:
                caller.msg(f"  [{window.id}] {window.key}: ERROR - {e}")

    def show_room_coords(self):
        """Display current room's coordinates."""
        caller = self.caller
        location = caller.location

        if not location:
            caller.msg("You are not in a room.")
            return

        x = getattr(location.db, 'x', None)
        y = getattr(location.db, 'y', None)
        z = getattr(location.db, 'z', 0)

        if x is None or y is None:
            caller.msg(f"Room has no coordinates defined.")
            return

        caller.msg(f"|cCurrent room coordinates: ({x}, {y}, {z})|n")

        # Show any windows here
        windows = get_windows_for_location(location)
        if windows:
            caller.msg(f"\nWindows in this room:")
            for window in windows:
                tx, ty, tz = window.get_target_coords()
                caller.msg(f"  - {window.key}: watches ({tx}, {ty}, {tz})")

        # Show any windows observing this location
        observing = get_windows_observing_coords(x, y, z)
        if observing:
            caller.msg(f"\nWindows observing THIS location from other rooms:")
            for window in observing:
                loc = window.location.key if window.location else "nowhere"
                caller.msg(f"  - {window.key} (in {loc})")


class CmdWindowDebugMove(Command):
    """Debug character movement and window notifications.

    Usage:
        windowdebugmove [on | off]

    Enables detailed debugging output when moving between rooms
    to help diagnose window observation issues.
    """

    key = "windowdebugmove"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        args = self.args.strip().lower()

        if args == "on":
            caller.ndb.window_debug_move = True
            caller.msg("Window movement debugging enabled.")
            caller.msg("Next time you move, you'll see detailed debug output.")
        elif args == "off":
            caller.ndb.window_debug_move = False
            caller.msg("Window movement debugging disabled.")
        elif not args:
            status = "ON" if getattr(caller.ndb, 'window_debug_move', False) else "OFF"
            caller.msg(f"Window movement debugging is currently {status}.")
        else:
            caller.msg("Usage: windowdebugmove [on | off]")


class CmdListWindowsObserving(Command):
    """List all windows observing a specific room.

    Usage:
        listwindowsobs <x> <y> <z>

    Shows all windows that are watching the room at the given coordinates.
    """

    key = "listwindowsobs"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        args = self.args.strip().split()

        if len(args) != 3:
            caller.msg("Usage: listwindowsobs <x> <y> <z>")
            return

        try:
            x, y, z = int(args[0]), int(args[1]), int(args[2])
        except ValueError:
            caller.msg("Coordinates must be integers.")
            return

        windows = get_windows_observing_coords(x, y, z)

        if not windows:
            caller.msg(f"No windows are observing location ({x}, {y}, {z}).")
            return

        caller.msg(f"|c=== Windows Observing ({x}, {y}, {z}) ===|n")
        for window in windows:
            loc = window.location.key if window.location else "nowhere"
            caller.msg(f"  - {window.key} (located in {loc})")
