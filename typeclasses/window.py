from evennia import DefaultObject

class Window(DefaultObject):
    """A window object that shows movements in another room based on coordinates."""
    def at_object_creation(self):
        self.db.target_coords = None  # (x, y, z) tuple
        self.db.desc = "A window looking into another space."
        self.locks.add("view:perm(Builder);setcoord:perm(Builder)")

    def set_target_coords(self, x, y, z, caller):
        if not caller.check_permstring("Builder"):
            caller.msg("You lack permission to set window coordinates.")
            return False
        self.db.target_coords = (x, y, z)
        caller.msg(f"Window now shows movements in room at ({x}, {y}, {z}).")
        return True

    def echo_movement(self, msg):
        # Called by movement event in target room
        if self.location:
            self.location.msg_contents(f"Through the window: {msg}")
