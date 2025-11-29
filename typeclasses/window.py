from evennia import DefaultObject

class Window(DefaultObject):
        def get_display_name(self, looker=None):
            """Return a plain string name for display, avoiding ANSIString issues."""
            return str(self.key)
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
        # Find the target room by coordinates
        from evennia.objects.models import ObjectDB
        target_room = None
        for obj in ObjectDB.objects.filter(db_typeclass_path__endswith="Room"):
            rx = getattr(obj.db, "x", None)
            ry = getattr(obj.db, "y", None)
            rz = getattr(obj.db, "z", None)
            if rx == x and ry == y and rz == z:
                target_room = obj
                break
        if not target_room:
            caller.msg(f"No room found at ({x}, {y}, {z}). Window will not show movement until a room exists at those coordinates.")
            self.db.target_room_dbref = None
        else:
            self.db.target_room_dbref = target_room.dbref
            # Create or update WindowSensor in target room
            from evennia.objects.models import ObjectDB
            sensor = None
            for obj in target_room.contents:
                if obj.is_typeclass("typeclasses.windowsensor.WindowSensor", exact=True):
                    sensor = obj
                    break
            if not sensor:
                from typeclasses.windowsensor import WindowSensor
                sensor_obj, errors = WindowSensor.create(key="window_sensor", location=target_room)
                sensor = sensor_obj
                sensor.db.installed_window_dbref = self.dbref
                caller.msg(f"|gDEBUG|n: Created new WindowSensor in '{target_room.key}' for window {self.dbref}.")
            else:
                sensor.db.installed_window_dbref = self.dbref
                caller.msg(f"|yDEBUG|n: Updated existing WindowSensor in '{target_room.key}' for window {self.dbref}.")
        caller.msg(f"Window now shows movements in room at ({x}, {y}, {z}).")
        return True

    def echo_movement(self, msg):
        # Called by movement event in target room
        debug_msg = f"|cWINDOW DEBUG|n: {msg}"
        # Always send to room
        if self.location:
            self.location.msg_contents(debug_msg)
            # Directly notify all builders in the room
            for obj in self.location.contents:
                if hasattr(obj, "check_permstring") and obj.check_permstring("Builder"):
                    obj.msg(debug_msg)
        # Also print to console for server-side debugging
        print(debug_msg)
        # Fallback: try Splattercast
        try:
            from evennia.comms.models import ChannelDB
            splattercast = ChannelDB.objects.get_channel("Splattercast")
            if splattercast:
                splattercast.msg(debug_msg)
        except Exception:
            pass
