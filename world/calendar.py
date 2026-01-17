"""
Korvessan Calendar System - Common Field Reckoning

The year is divided into twelve months of thirty days each (360 days total).
The week is a six-day cycle called the Turning.
Years are counted in AH (After Herding).

This module converts Evennia gametime to Korvessan calendar dates.
"""

from evennia.utils import gametime
from evennia import settings

# =============================================================================
# CALENDAR CONSTANTS
# =============================================================================

# Months of the year (Common Field Reckoning)
MONTHS = [
    {
        'name': 'Plowbreak',
        'desc': 'The ground softens enough to be worked. Plows break, animals strain, and labor resumes after scarcity.'
    },
    {
        'name': 'Seedwake',
        'desc': 'Seed is sown while frost still threatens. Too early risks loss, too late risks hunger.'
    },
    {
        'name': 'Sproutmere',
        'desc': 'First green shoots appear. Growth begins, but so do weeds, pests, and theft.'
    },
    {
        'name': 'Tallgrow',
        'desc': 'Crops stretch high and require constant tending. Days are long, rest is scarce.'
    },
    {
        'name': 'Sunpress',
        'desc': 'Heat bears down on fields and people alike. Water grows precious. Illness spreads.'
    },
    {
        'name': 'Firstreap',
        'desc': 'Early harvests begin. Barley and greens offer relief, but success here does not guarantee survival.'
    },
    {
        'name': 'Fullreap',
        'desc': 'The primary harvest month. The outcome of the entire year is decided. Plenty or famine is set here.'
    },
    {
        'name': 'Stubblewake',
        'desc': 'Fields are cut bare. Leftovers are gathered. Livestock graze the remains.'
    },
    {
        'name': 'Turnsoil',
        'desc': 'Fields are worked again or abandoned. Long-term decisions are made. Regret often begins here.'
    },
    {
        'name': 'Coldroot',
        'desc': 'Root crops are pulled and cellars filled. Mistakes become visible. What was not stored will be missed.'
    },
    {
        'name': 'Storethin',
        'desc': 'Supplies begin to run low. Rations quietly shrink. Tempers shorten. Fear grows communal.'
    },
    {
        'name': 'Lastseed',
        'desc': 'Nothing remains to plant. Survival depends entirely on preparation. The year ends in endurance.'
    }
]

# Weekdays of the Six-Day Turning
WEEKDAYS = [
    {
        'name': 'Eveday',
        'desc': 'The opening of the week. Plans are laid, journeys begun, and intentions revealed.',
        'dedication': None
    },
    {
        'name': 'Watchday',
        'desc': 'Dedicated to the Watcher. Favored for oaths, inspections, testimony, and judgment.',
        'dedication': 'the Watcher'
    },
    {
        'name': 'Trialday',
        'desc': 'Dedicated to the Three Children. A day of learning, first attempts, and forgivable failure.',
        'dedication': 'the Three Children'
    },
    {
        'name': 'Velorday',
        'desc': 'Dedicated to Velora, the Path of Order. A day for disciplined labor, repair, and service.',
        'dedication': 'Velora'
    },
    {
        'name': 'Feyday',
        'desc': 'Dedicated to Feyliks, the Path of Chance. Markets swell, games are played, and risks are taken.',
        'dedication': 'Feyliks'
    },
    {
        'name': 'Regaldy',
        'desc': 'Dedicated to Regalus, the Path of Dominion. Accounts are settled and authority enforced.',
        'dedication': 'Regalus'
    }
]

# Calendar structure
DAYS_PER_WEEK = 6
DAYS_PER_MONTH = 30
MONTHS_PER_YEAR = 12
DAYS_PER_YEAR = DAYS_PER_MONTH * MONTHS_PER_YEAR  # 360

# Seconds per game unit (standard 24-hour day)
SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 3600
SECONDS_PER_DAY = 86400

# Starting year for the AH (After Herding) calendar
# Set so that the current year is 160 AH
now = gametime.gametime()
total_days = int(now // SECONDS_PER_DAY)
elapsed_years = total_days // DAYS_PER_YEAR
CALENDAR_EPOCH_YEAR = 160 - elapsed_years


# =============================================================================
# TIME PERIOD MAPPINGS (for weather/atmosphere)
# =============================================================================

TIME_PERIODS = {
    (0, 1): 'night',
    (1, 3): 'late_night',
    (3, 5): 'pre_dawn',
    (5, 6): 'dawn',
    (6, 8): 'early_morning',
    (8, 11): 'late_morning',
    (11, 13): 'midday',
    (13, 16): 'early_afternoon',
    (16, 18): 'late_afternoon',
    (18, 19): 'dusk',
    (19, 21): 'early_evening',
    (21, 23): 'late_evening',
    (23, 24): 'night'
}

TIME_PERIOD_NAMES = {
    'night': 'the dead of night',
    'late_night': 'the late night hours',
    'pre_dawn': 'the hours before dawn',
    'dawn': 'dawn',
    'early_morning': 'early morning',
    'late_morning': 'late morning',
    'midday': 'midday',
    'early_afternoon': 'early afternoon',
    'late_afternoon': 'late afternoon',
    'dusk': 'dusk',
    'early_evening': 'early evening',
    'late_evening': 'late evening'
}


# =============================================================================
# CALENDAR FUNCTIONS
# =============================================================================

def get_game_time():
    """
    Get the current game time in seconds since epoch.
    
    Returns:
        int: Game time in seconds
    """
    return gametime.gametime()


def get_korvessan_date(game_seconds=None):
    """
    Convert game time to Korvessan calendar date.
    
    Args:
        game_seconds: Game time in seconds (defaults to current time)
        
    Returns:
        dict: Calendar date with year, month, day, weekday, hour, minute
    """
    if game_seconds is None:
        game_seconds = get_game_time()
    
    # Ensure positive time
    game_seconds = max(0, game_seconds)
    
    # Calculate total days elapsed
    total_days = int(game_seconds // SECONDS_PER_DAY)
    remaining_seconds = int(game_seconds % SECONDS_PER_DAY)
    
    # Calculate year (0-indexed, then add epoch)
    year = (total_days // DAYS_PER_YEAR) + CALENDAR_EPOCH_YEAR
    day_of_year = total_days % DAYS_PER_YEAR
    
    # Calculate month (0-indexed) and day of month (1-indexed)
    month_index = day_of_year // DAYS_PER_MONTH
    day_of_month = (day_of_year % DAYS_PER_MONTH) + 1
    
    # Calculate weekday (0-indexed)
    weekday_index = total_days % DAYS_PER_WEEK
    
    # Calculate hour and minute
    hour = remaining_seconds // SECONDS_PER_HOUR
    minute = (remaining_seconds % SECONDS_PER_HOUR) // SECONDS_PER_MINUTE
    
    return {
        'year': year,
        'month_index': month_index,
        'month_name': MONTHS[month_index]['name'],
        'month_desc': MONTHS[month_index]['desc'],
        'day': day_of_month,
        'weekday_index': weekday_index,
        'weekday_name': WEEKDAYS[weekday_index]['name'],
        'weekday_desc': WEEKDAYS[weekday_index]['desc'],
        'weekday_dedication': WEEKDAYS[weekday_index]['dedication'],
        'hour': hour,
        'minute': minute,
        'day_of_year': day_of_year + 1,
        'total_days': total_days
    }


def get_time_period(hour=None):
    """
    Get the current time period name based on hour.
    
    Args:
        hour: Hour (0-23), defaults to current game hour
        
    Returns:
        str: Time period key (e.g., 'dawn', 'midday', 'night')
    """
    if hour is None:
        date = get_korvessan_date()
        hour = date['hour']
    
    for (start, end), period in TIME_PERIODS.items():
        if start <= hour < end:
            return period
    
    return 'night'


def get_time_period_name(hour=None):
    """
    Get a descriptive name for the current time period.
    
    Args:
        hour: Hour (0-23), defaults to current game hour
        
    Returns:
        str: Descriptive time period (e.g., 'the dead of night', 'early morning')
    """
    period = get_time_period(hour)
    return TIME_PERIOD_NAMES.get(period, 'an unknown hour')


def format_date_short(date=None):
    """
    Format date in short form: "15th of Fullreap, Year 3 AH"
    
    Args:
        date: Date dict from get_korvessan_date(), or None for current
        
    Returns:
        str: Formatted date string
    """
    if date is None:
        date = get_korvessan_date()
    
    day = date['day']
    suffix = get_ordinal_suffix(day)
    
    return f"the {day}{suffix} of {date['month_name']}, Year {date['year']} AH (After Herding)"


def format_date_full(date=None):
    """
    Format date with weekday: "Watchday, the 15th of Fullreap, Year 3 AH"
    
    Args:
        date: Date dict from get_korvessan_date(), or None for current
        
    Returns:
        str: Formatted date string with weekday
    """
    if date is None:
        date = get_korvessan_date()
    
    day = date['day']
    suffix = get_ordinal_suffix(day)
    
    return f"{date['weekday_name']}, the {day}{suffix} of {date['month_name']}, Year {date['year']} AH (After Herding)"


def format_time(date=None):
    """
    Format time in 12-hour format with period description.
    
    Args:
        date: Date dict from get_korvessan_date(), or None for current
        
    Returns:
        str: Formatted time string
    """
    if date is None:
        date = get_korvessan_date()
    
    hour = date['hour']
    minute = date['minute']
    
    # Convert to 12-hour format
    if hour == 0:
        hour_12 = 12
        period = 'in the night'
    elif hour < 12:
        hour_12 = hour
        if hour < 6:
            period = 'in the pre-dawn hours'
        else:
            period = 'in the morning'
    elif hour == 12:
        hour_12 = 12
        period = 'at midday'
    else:
        hour_12 = hour - 12
        if hour < 18:
            period = 'in the afternoon'
        elif hour < 21:
            period = 'in the evening'
        else:
            period = 'in the night'
    
    return f"{hour_12}:{minute:02d} {period}"


def get_ordinal_suffix(n):
    """
    Get ordinal suffix for a number (1st, 2nd, 3rd, 4th, etc.)
    
    Args:
        n: Number
        
    Returns:
        str: Ordinal suffix
    """
    if 11 <= n <= 13:
        return 'th'
    remainder = n % 10
    if remainder == 1:
        return 'st'
    elif remainder == 2:
        return 'nd'
    elif remainder == 3:
        return 'rd'
    else:
        return 'th'


def get_month_position(date=None):
    """
    Get descriptive position within the month.
    
    Args:
        date: Date dict from get_korvessan_date(), or None for current
        
    Returns:
        str: Position description ('early', 'mid', 'late', 'deep into')
    """
    if date is None:
        date = get_korvessan_date()
    
    day = date['day']
    
    if day <= 7:
        return 'early'
    elif day <= 15:
        return 'mid'
    elif day <= 23:
        return 'late'
    else:
        return 'deep into'


def get_season(date=None):
    """
    Get approximate season based on month.
    
    Args:
        date: Date dict from get_korvessan_date(), or None for current
        
    Returns:
        str: Season name
    """
    if date is None:
        date = get_korvessan_date()
    
    month = date['month_index']
    
    # Spring: Plowbreak, Seedwake, Sproutmere (0-2)
    # Summer: Tallgrow, Sunpress, Firstreap (3-5)
    # Autumn: Fullreap, Stubblewake, Turnsoil (6-8)
    # Winter: Coldroot, Storethin, Lastseed (9-11)
    
    if month < 3:
        return 'spring'
    elif month < 6:
        return 'summer'
    elif month < 9:
        return 'autumn'
    else:
        return 'winter'


def get_colloquial_date(date=None):
    """
    Get a colloquial date reference as common folk might say it.
    
    Args:
        date: Date dict from get_korvessan_date(), or None for current
        
    Returns:
        str: Colloquial reference like "late Fullreap" or "deep into Storethin"
    """
    if date is None:
        date = get_korvessan_date()
    
    position = get_month_position(date)
    return f"{position} {date['month_name']}"
