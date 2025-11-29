from evennia import Command

class CmdDebugRoomCoords(Command):
    """Show the coordinates of the current room."""
    key = "debugroomcoords"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        room = caller.location
        x = getattr(room.db, "x", None)
        y = getattr(room.db, "y", None)
        z = getattr(room.db, "z", None)
        caller.msg(f"Room '{room.key}' coordinates: x={x}, y={y}, z={z}")
