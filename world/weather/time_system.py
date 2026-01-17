"""
Time System

Manages game time and provides current time period for weather system.
Integrates with the Korvessan calendar (Common Field Reckoning).
"""

from world.calendar import (
    get_korvessan_date,
    get_time_period,
    get_time_period_name,
    get_season,
    TIME_PERIODS
)


# Re-export time periods for backward compatibility
TIME_PERIOD_LIST = [
    'dawn',           # 5-6 AM
    'early_morning',  # 6-8 AM  
    'late_morning',   # 8-11 AM
    'midday',         # 11 AM-1 PM
    'early_afternoon',# 1-4 PM
    'late_afternoon', # 4-6 PM
    'dusk',           # 6-7 PM
    'early_evening',  # 7-9 PM
    'late_evening',   # 9-11 PM
    'night',          # 11 PM-1 AM
    'late_night',     # 1-3 AM
    'pre_dawn'        # 3-5 AM
]

# Hour ranges for each time period (24-hour format) - for backward compatibility
TIME_RANGES = {
    'dawn': (5, 6),
    'early_morning': (6, 8),
    'late_morning': (8, 11),
    'midday': (11, 13),
    'early_afternoon': (13, 16),
    'late_afternoon': (16, 18),
    'dusk': (18, 19),
    'early_evening': (19, 21),
    'late_evening': (21, 23),
    'night': (23, 1),
    'late_night': (1, 3),
    'pre_dawn': (3, 5)
}


class TimeSystem:
    """
    Manages game time and time-based calculations.
    
    Integrates with the Korvessan calendar for weather and
    other time-dependent game mechanics.
    """
    
    def __init__(self):
        """Initialize time system."""
        pass
        
    def get_current_hour(self):
        """
        Get current game hour (0-23).
        
        Returns:
            int: Current hour in 24-hour format
        """
        date = get_korvessan_date()
        return date['hour']
        
    def get_current_time_period(self):
        """
        Get current time period for weather system.
        
        Returns:
            str: Current time period (e.g., 'dawn', 'midday', 'night')
        """
        return get_time_period()
    
    def get_current_season(self):
        """
        Get current season based on Korvessan calendar month.
        
        Returns:
            str: Season name ('spring', 'summer', 'autumn', 'winter')
        """
        return get_season()
    
    def get_time_period_description(self):
        """
        Get a descriptive name for the current time period.
        
        Returns:
            str: Descriptive time (e.g., 'the dead of night', 'early morning')
        """
        return get_time_period_name()


# Singleton instance for easy access
_time_system = None

def get_time_system():
    """Get or create the time system singleton."""
    global _time_system
    if _time_system is None:
        _time_system = TimeSystem()
    return _time_system



# Global convenience function
def get_current_time_period():
    """
    Convenience function to get current time period.
    
    Returns:
        str: Current time period
    """
    # For now, direct calculation - later will use global time system instance
    current_time = time.localtime()
    hour = current_time.tm_hour
    
    for period, (start, end) in TIME_RANGES.items():
        if start <= end:
            if start <= hour < end:
                return period
        else:
            if hour >= start or hour < end:
                return period
                
    return 'midday'
