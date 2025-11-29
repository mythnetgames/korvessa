from evennia import DefaultObject

class Window(DefaultObject):
    """
    A window object that watches a target room by coordinates (x, y, z).
    When someone enters or leaves the watched room, this window relays a message
    to its own location (the source room).
    """

    def get_display_name(self, looker=None):
        """Return a plain string name for display in room items."""
        return str(self.key)

    def at_object_creation(self):
        self.db.target_x = None
        self.db.target_y = None
        self.db.target_z = None
        self.db.desc = "A window looking into another space."
        self.locks.add("view:all();setcoord:perm(Builder)")

    def set_target_coords(self, x, y, z):
        self.db.target_x = x
        self.db.target_y = y
        self.db.target_z = z
        self.location.msg(f"Window now watches room at ({x}, {y}, {z}).")

    def relay_movement(self, char, movement_type, direction=None):
        # movement_type: 'enter' or 'leave'
        debug_msg = f"[DEBUG] Window {self.key} relay_movement called: char={char.key}, movement_type={movement_type}, direction={direction}, window_loc={self.location}, target=({self.db.target_x},{self.db.target_y},{self.db.target_z})"
        print(debug_msg)
        if movement_type == 'enter':
            msg = f"Through the window, you see {char.key} enter the room."
            if direction:
                msg = f"Through the window, you see {char.key} enter the room to the {direction}."
        else:
            msg = f"Through the window, you see {char.key} leave the room."
        if self.location:
            self.location.msg_contents(msg)
        else:
            print(f"[DEBUG] Window {self.key} has no location!")
