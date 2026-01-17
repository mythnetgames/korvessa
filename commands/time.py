"""
Custom in-character time command that displays Korvessan calendar time.
Shows date in Common Field Reckoning format with the six-day Turning.
Uses custom color palette for lore-appropriate theming.
"""

from evennia import Command
from world.calendar import (
    get_korvessan_date, 
    format_date_full, 
    format_time,
    get_time_period_name,
    get_colloquial_date,
    is_birthday_today,
    get_holiday_today
)
import random

# Color palette (hex codes)
COLORS = {
    'dark_blue': '|#0b0d47',
    'light_purple': '|#a85fd7',
    'blue': '|#0b37d7',
    'cyan': '|#0ba5d7',
    'dark_green': '|#0d7d07',
    'bright_green': '|#0bff07',
    'light_green': '|#5fff47',
    'green': '|#5fd747',
    'yellow_green': '|#5ffd47',
    'reset': '|n'
}


class CmdTime(Command):
    """
    Check the time on a nearby clock display.
    
    Usage:
        time
    
    Shows you the current date and time as displayed on a nearby
    chronometer or sundial. The clock may be slightly imprecise.
    
    Dates are shown in Common Field Reckoning, the agrarian calendar
    used throughout Korvessa. Years are counted in AH (After Herding).
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
        
        # Check for birthday
        is_bday = is_birthday_today(caller)
        
        # Check for holiday
        holiday = get_holiday_today(date)
        
        # Format the display
        full_date = format_date_full(date)
        time_str = format_time(date)
        time_period = get_time_period_name(date['hour'])
        colloquial = get_colloquial_date(date)
        
        # Build the display
        caller.msg(f"\n{COLORS['dark_blue']}{'-' * 60}{COLORS['reset']}")
        
        if is_bday:
            # Rainbow birthday message with color palette
            rainbow_colors = [
                COLORS['dark_blue'],
                COLORS['light_purple'],
                COLORS['blue'],
                COLORS['cyan'],
                COLORS['dark_green'],
                COLORS['bright_green'],
                COLORS['light_green'],
                COLORS['green'],
                COLORS['yellow_green']
            ]
            name = caller.db.real_full_name if hasattr(caller.db, 'real_full_name') else caller.key
            bday_msg = f"Happy Birthday, {name}!"
            
            # Cycle through colors for each character
            colored_msg = ""
            for i, char in enumerate(bday_msg):
                if char != " ":
                    colored_msg += f"{rainbow_colors[i % len(rainbow_colors)]}{char}{COLORS['reset']}"
                else:
                    colored_msg += " "
            
            caller.msg(colored_msg)
            caller.msg(f"{COLORS['cyan']}{' * ' * 20}{COLORS['reset']}")
        elif holiday:
            # Holiday message
            caller.msg(f"{COLORS['light_green']}It is the holiday of {COLORS['cyan']}{holiday['name']}{COLORS['light_green']}.{COLORS['reset']}")
            caller.msg(f"{COLORS['light_green']}({holiday['tradition']}){COLORS['reset']}")
        else:
            caller.msg(f"{COLORS['bright_green']}A nearby sundial and calendar mark:{COLORS['reset']}")
        
        caller.msg(f"{COLORS['dark_blue']}{'-' * 60}{COLORS['reset']}")
        caller.msg(f"{COLORS['yellow_green']}  Date:{COLORS['reset']} {COLORS['cyan']}{full_date}{COLORS['reset']}")
        caller.msg(f"{COLORS['yellow_green']}  Time:{COLORS['reset']} {COLORS['cyan']}{time_str}{COLORS['reset']}")
        caller.msg(f"{COLORS['dark_blue']}{'-' * 60}{COLORS['reset']}")
        caller.msg(f"{COLORS['light_green']}It is {time_period}, {colloquial}.{COLORS['reset']}")
        
        # Show weekday significance if relevant
        if date['weekday_dedication']:
            caller.msg(f"{COLORS['light_green']}{date['weekday_name']} is dedicated to {date['weekday_dedication']}.{COLORS['reset']}")
        
        # Show holiday explanation if present
        if holiday:
            caller.msg(f"{COLORS['dark_blue']}{'-' * 60}{COLORS['reset']}")
            caller.msg(f"{COLORS['light_green']}{holiday['desc']}{COLORS['reset']}")
        
        caller.msg(f"{COLORS['dark_blue']}{'-' * 60}{COLORS['reset']}\n")
