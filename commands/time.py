"""
Custom time command that displays in-game time from a clock display.
"""

from evennia import Command
from evennia.utils import gametime
import time as real_time


class CmdTime(Command):
    """
    Display the current in-game time from a nearby clock display.
    
    Usage:
        time
    
    Shows you the current date and time in the game world,
    as displayed on a nearby chronometer or digital clock.
    """
    
    key = "time"
    aliases = ["clock", "date"]
    locks = "cmd:all()"
    help_category = "General"
    
    def func(self):
        """Display the current game time."""
        caller = self.caller
        
        # Get current game time in seconds
        game_time_seconds = gametime.get_gametime()
        
        # Convert to time struct for formatting
        # Since TIME_GAME_EPOCH = 0 (which is 1970-01-01), this will show 1970 dates
        time_struct = real_time.gmtime(game_time_seconds)
        
        # Format the display
        date_str = real_time.strftime("%A, %B %d, %Y", time_struct)
        time_str = real_time.strftime("%H:%M:%S", time_struct)
        
        # Display in a styled format suggesting it's from a clock display
        caller.msg(f"\n|w{'-' * 60}|n")
        caller.msg(f"|bCHRONOMETER DISPLAY|n")
        caller.msg(f"|w{'-' * 60}|n")
        caller.msg(f"|yDate: |c{date_str}|n")
        caller.msg(f"|yTime: |c{time_str}|n")
        caller.msg(f"|w{'-' * 60}|n\n")
