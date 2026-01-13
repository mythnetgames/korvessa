"""
Custom in-character time command that displays time from a nearby clock display.
The clock can vary by up to 3 minutes (random seconds and minutes).
"""

from evennia import Command
from evennia.utils import gametime
import time as real_time
import random


class CmdTime(Command):
    """
    Check the time on a nearby clock display.
    
    Usage:
        time
    
    Shows you the current date and time as displayed on a nearby
    chronometer or digital clock. The clock may be slightly fast or slow.
    """
    
    key = "time"
    aliases = ["clock", "date"]
    locks = "cmd:all()"
    help_category = "General"
    
    def func(self):
        """Display the current game time from a nearby clock."""
        caller = self.caller
        
        # Get current game time in seconds
        game_time_seconds = gametime.get_gametime()
        
        # Add random variation: -180 to +180 seconds (3 minutes range)
        variation = random.randint(-180, 180)
        display_time = game_time_seconds + variation
        
        # Convert to time struct for formatting
        time_struct = real_time.gmtime(display_time)
        
        # Format the display
        date_str = real_time.strftime("%A, %B %d, %Y", time_struct)
        time_str = real_time.strftime("%H:%M:%S", time_struct)
        
        # Display as a nearby clock reading
        caller.msg(f"\n|w{'-' * 60}|n")
        caller.msg(f"|bA nearby chronometer display reads:|n")
        caller.msg(f"|w{'-' * 60}|n")
        caller.msg(f"|yDate: |c{date_str}|n")
        caller.msg(f"|yTime: |c{time_str}|n")
        caller.msg(f"|w{'-' * 60}|n\n")
