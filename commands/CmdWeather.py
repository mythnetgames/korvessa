"""
CmdWeatherRoom - Toggle weather_room flag on the current room
"""

from evennia import Command


class CmdWeatherRoom(Command):
    """
    Toggle weather_room flag on current room
    
    Usage:
      weatherroom                - Check current weather room status
      weatherroom on             - Enable weather for this room
      weatherroom off            - Disable weather for this room
      weatherroom toggle         - Toggle weather on/off
    """
    
    key = "weatherroom"
    aliases = ["wroom", "weatherrm"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        """Execute the weather command"""
        caller = self.caller
        room = caller.location
        
        if not room:
            caller.msg("You are not in a room.")
            return
        
        if not self.args:
            # Check current status
            status = room.weather_room
            caller.msg(f"Weather room status: {'ENABLED' if status else 'DISABLED'}")
            return
        
        arg = self.args.strip().lower()
        
        if arg in ("on", "enable", "1", "true", "yes"):
            room.weather_room = True
            caller.msg(f"Weather enabled for {room.key}")
        elif arg in ("off", "disable", "0", "false", "no"):
            room.weather_room = False
            caller.msg(f"Weather disabled for {room.key}")
        elif arg in ("toggle", "switch"):
            room.weather_room = not room.weather_room
            status = "ENABLED" if room.weather_room else "DISABLED"
            caller.msg(f"Weather {status} for {room.key}")
        else:
            caller.msg("Usage: weather [on|off|toggle]")
