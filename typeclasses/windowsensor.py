from evennia import DefaultObject

class WindowSensor(DefaultObject):
    """Invisible sensor object placed in the target room to relay movement events to the installed window."""
    def at_object_creation(self):
        self.db.installed_window_dbref = None  # dbref of the window to notify
        self.locks.add("view:perm(Builder)")
        self.db.desc = "An invisible window sensor."
        self.tags.add("window_sensor")
        self.db.is_invisible = True

    def at_object_receive(self, moved_obj, source_location, **kwargs):
        # Relay entry event to installed window
        win_dbref = self.db.installed_window_dbref
        if win_dbref:
            from evennia.objects.models import ObjectDB
            win_obj = ObjectDB.objects.get(dbref=win_dbref)
            if win_obj:
                win_obj.echo_movement(f"{moved_obj.key} enters the room at ({getattr(self.location.db, 'x', None)}, {getattr(self.location.db, 'y', None)}, {getattr(self.location.db, 'z', None)}).")

    def at_object_leave(self, moved_obj, target_location, **kwargs):
        # Relay exit event to installed window
        win_dbref = self.db.installed_window_dbref
        if win_dbref:
            from evennia.objects.models import ObjectDB
            win_obj = ObjectDB.objects.get(dbref=win_dbref)
            if win_obj:
                win_obj.echo_movement(f"{moved_obj.key} leaves the room at ({getattr(self.location.db, 'x', None)}, {getattr(self.location.db, 'y', None)}, {getattr(self.location.db, 'z', None)}).")
