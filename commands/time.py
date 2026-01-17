"""
Custom in-character time command that displays Korvessan calendar time.
Shows date in Common Field Reckoning format with the six-day Turning.
"""

from evennia import Command
from world.calendar import (
    get_korvessan_date, 
    format_date_full, 
    format_time,
    get_time_period_name,
    get_colloquial_date
)
import random


class CmdTime(Command):
    """
    Check the time on a nearby clock display.
    
    Usage:
        time
    
    Shows you the current date and time as displayed on a nearby
    chronometer or sundial. The clock may be slightly imprecise.
    
    Dates are shown in Common Field Reckoning, the agrarian calendar
    used throughout Korvessa. Years are counted in AH (After Harboring).
    """
    
    key = "time"
    aliases = ["clock", "date"]
    locks = "cmd:all()"
    help_category = "General"
    
    def func(self):
        """Display the current game time in Korvessan calendar format."""
        caller = self.caller
        
        # Get current Korvessan date
        date = get_korvessan_date()
        
        # Add slight variation to minutes for flavor (imprecise timekeeping)
        variation = random.randint(-5, 5)
        adjusted_minute = max(0, min(59, date['minute'] + variation))
        date['minute'] = adjusted_minute
        
        # Format the display
        full_date = format_date_full(date)
        time_str = format_time(date)
        time_period = get_time_period_name(date['hour'])
        colloquial = get_colloquial_date(date)
        
        # Build the display
        caller.msg(f"\n|w{'-' * 60}|n")
        caller.msg(f"|bA nearby sundial and calendar mark:|n")
        caller.msg(f"|w{'-' * 60}|n")
        caller.msg(f"|y  Date:|n |c{full_date}|n")
        caller.msg(f"|y  Time:|n |c{time_str}|n")
        caller.msg(f"|w{'-' * 60}|n")
        caller.msg(f"|xIt is {time_period}, {colloquial}.|n")
        
        # Show weekday significance if relevant
        if date['weekday_dedication']:
            caller.msg(f"|x{date['weekday_name']} is dedicated to {date['weekday_dedication']}.|n")
        
        caller.msg(f"|w{'-' * 60}|n\n")
