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
            # Register window with target room
            if not hasattr(target_room.db, "window_list") or target_room.db.window_list is None:
                target_room.db.window_list = []
            if self.dbref not in target_room.db.window_list:
                target_room.db.window_list.append(self.dbref)
                caller.msg(f"|gDEBUG|n: Registered window {self.dbref} with room '{target_room.key}' window_list: {target_room.db.window_list}")
            else:
                caller.msg(f"|yDEBUG|n: Window {self.dbref} already registered with room '{target_room.key}' window_list: {target_room.db.window_list}")
        caller.msg(f"Window now shows movements in room at ({x}, {y}, {z}).")
        return True

    def echo_movement(self, msg):
        # Called by movement event in target room
        if self.location:
            self.location.msg_contents(f"|cWINDOW DEBUG|n: {msg}")
        # Fallback debug: also print to Splattercast and to all builders in the room
        try:
            from evennia.comms.models import ChannelDB
            splattercast = ChannelDB.objects.get_channel("Splattercast")
            if splattercast:
                splattercast.msg(f"|cWINDOW DEBUG|n: {msg}")
        except Exception as e:
            pass
        # Directly notify all builders in the room
        if self.location:
            for obj in self.location.contents:
                if hasattr(obj, "check_permstring") and obj.check_permstring("Builder"):
                    obj.msg(f"|cWINDOW DEBUG|n: {msg}")
