from evennia import Command

class CmdDebugSensors(Command):
    """Show all window sensors in the current room and their linked window dbrefs."""
    key = "debugsensors"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        room = caller.location
        sensors = [obj for obj in room.contents if obj.is_typeclass("typeclasses.windowsensor.WindowSensor", exact=True)]
        if not sensors:
            caller.msg("No window sensors found in this room.")
            return
        for sensor in sensors:
            win_dbref = getattr(sensor.db, "installed_window_dbref", None)
            caller.msg(f"Sensor #{sensor.id} linked to window dbref: {win_dbref}")
