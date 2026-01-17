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
# HOLIDAYS - Religious and Superstitious Observances
# =============================================================================

HOLIDAYS = [
    # PLOWBREAK
    {'month': 0, 'day': 3, 'name': 'Turning Oath', 'tradition': 'Velora', 'desc': 'Followers of Velora reaffirm discipline before the year begins in earnest. Tools are cleaned and checked. Sloppy labor after this day is seen as moral failure, not accident.'},
    {'month': 0, 'day': 12, 'name': 'The Watched Furrow', 'tradition': 'Watcher', 'desc': 'Fields are worked in silence where possible. It is believed the Watcher sees what is hidden in soil and in intent. Lies spoken this day are said to surface later in the year.'},
    {'month': 0, 'day': 21, 'name': 'The Uneven Line', 'tradition': 'Superstitious', 'desc': 'One furrow is deliberately plowed crooked to confuse ill fate. Those who insist on perfection invite misfortune, according to folk belief.'},
    
    # SEEDWAKE
    {'month': 1, 'day': 2, 'name': 'Casting of Hands', 'tradition': 'Three Children', 'desc': 'The young and inexperienced are set to sow seed. Errors are expected and forgiven. Effort matters more than result.'},
    {'month': 1, 'day': 11, 'name': 'Held Seed', 'tradition': 'Watcher', 'desc': 'No planting is done. Frost or blight following this day is blamed on those who ignored the warning.'},
    {'month': 1, 'day': 23, 'name': 'Open Palm', 'tradition': 'Feyliks', 'desc': 'Seed is shared freely, gambled, or traded. Hoarding on this day is believed to sour fortune later.'},
    
    # SPROUTMERE
    {'month': 2, 'day': 5, 'name': 'Green Oath', 'tradition': 'Velora', 'desc': 'Commitments are renewed. Contracts sworn this day are expected to endure hardship.'},
    {'month': 2, 'day': 14, 'name': 'Small Feet', 'tradition': 'Three Children', 'desc': 'Children and apprentices walk the fields. Damage caused is forgiven, but negligence by elders is not.'},
    {'month': 2, 'day': 26, 'name': 'Watching Leaves', 'tradition': 'Watcher', 'desc': 'Fields are inspected closely. Signs of blight discovered after this day are blamed on willful blindness.'},
    
    # TALLGROW
    {'month': 3, 'day': 4, 'name': 'Bound Work', 'tradition': 'Velora', 'desc': 'Crops are tied and corrected. Neglect here is remembered at harvest.'},
    {'month': 3, 'day': 13, 'name': 'Foolstep', 'tradition': 'Feyliks', 'desc': 'A day associated with accidents and daring. Risky labor is undertaken deliberately. Failure is blamed on luck, not skill.'},
    {'month': 3, 'day': 22, 'name': 'The Quiet Mark', 'tradition': 'Superstitious', 'desc': 'Midday labor pauses briefly. Ignoring the pause is said to invite injury before the month ends.'},
    
    # SUNPRESS
    {'month': 4, 'day': 6, 'name': 'Thirstcount', 'tradition': 'Watcher', 'desc': 'Water stores are measured honestly. Lying about supply is believed to draw drought.'},
    {'month': 4, 'day': 15, 'name': 'Heat Mercy', 'tradition': 'Velora', 'desc': 'Excessive punishment and labor are avoided. Cruelty shown this day is remembered by the faithful.'},
    {'month': 4, 'day': 27, 'name': 'Flygift', 'tradition': 'Superstitious', 'desc': 'Food is left out for vermin spirits to keep them from livestock. Refusal is blamed if sickness spreads.'},
    
    # FIRSTREAP
    {'month': 5, 'day': 1, 'name': 'First Sheaf', 'tradition': 'Velora', 'desc': 'The earliest harvest is cut carefully. Waste on this day is deeply frowned upon.'},
    {'month': 5, 'day': 10, 'name': 'Bread of Chance', 'tradition': 'Feyliks', 'desc': 'First loaves from new grain are eaten. Ill fortune blamed on luck, not milling.'},
    {'month': 5, 'day': 19, 'name': 'Counted Silence', 'tradition': 'Watcher', 'desc': 'Harvest totals are tallied quietly. Boasting invites suspicion.'},
    
    # FULLREAP
    {'month': 6, 'day': 3, 'name': 'Open Field', 'tradition': 'Regalus', 'desc': 'Harvest begins under authority. Theft during this period carries harsh consequence.'},
    {'month': 6, 'day': 16, 'name': 'Measure True', 'tradition': 'Velora', 'desc': 'Weights and measures are checked. False accounting after this day is treated as deliberate crime.'},
    {'month': 6, 'day': 28, 'name': 'Feast of Plenty', 'tradition': 'Feyliks', 'desc': 'Excess is permitted briefly. Those who abstain are assumed fearful or hiding loss.'},
    
    # STUBBLEWAKE
    {'month': 7, 'day': 7, 'name': 'Gleaning Right', 'tradition': 'Three Children', 'desc': 'The landless may gather remains. Denial is seen as cruelty.'},
    {'month': 7, 'day': 18, 'name': 'Herd Turn', 'tradition': 'Superstitious', 'desc': 'Livestock are moved. Injuries are blamed on poor fortune rather than skill.'},
    {'month': 7, 'day': 25, 'name': 'The Last Look', 'tradition': 'Watcher', 'desc': 'Fields are inspected one final time. Missed harvest after this day is blamed on neglect.'},
    
    # TURNSOIL
    {'month': 8, 'day': 4, 'name': 'Second Claim', 'tradition': 'Regalus', 'desc': 'Land boundaries are reaffirmed or seized. Authority asserted now is expected to hold.'},
    {'month': 8, 'day': 14, 'name': 'Ashmark', 'tradition': 'Superstitious', 'desc': 'Controlled burning is permitted. Fire afterward is unforgivable.'},
    {'month': 8, 'day': 26, 'name': 'Broken Spade', 'tradition': 'Velora', 'desc': 'Tools that fail are repaired or discarded. Using broken tools later is seen as stubborn pride.'},
    
    # COLDROOT
    {'month': 9, 'day': 5, 'name': 'Rootpull', 'tradition': 'Velora', 'desc': 'Root crops are harvested carefully. Delay beyond this day is blamed for rot.'},
    {'month': 9, 'day': 17, 'name': 'Cellar Seal', 'tradition': 'Watcher', 'desc': 'Stores are closed and counted. Missing goods spark accusations.'},
    {'month': 9, 'day': 24, 'name': 'Mistwalk', 'tradition': 'Superstitious', 'desc': 'Travel avoided where possible. Loss on this day is attributed to fate.'},
    
    # STORETHIN
    {'month': 10, 'day': 6, 'name': 'Short Measure', 'tradition': 'Regalus', 'desc': 'Rations are reduced by decree. Failure to comply is treated as defiance.'},
    {'month': 10, 'day': 15, 'name': 'Quiet Hearth', 'tradition': 'Watcher', 'desc': 'Social visits decline. Secrets shared are believed remembered.'},
    {'month': 10, 'day': 27, 'name': 'Coin Turn', 'tradition': 'Feyliks', 'desc': 'Last risky trades before scarcity bites. Loss is blamed on chance, not judgment.'},
    
    # LASTSEED
    {'month': 11, 'day': 3, 'name': 'Final Count', 'tradition': 'Watcher', 'desc': 'Stores are tallied honestly. Lies now are remembered into the next year.'},
    {'month': 11, 'day': 14, 'name': 'Hard Night', 'tradition': 'Velora', 'desc': 'No excess is permitted. Discipline is observed openly.'},
    {'month': 11, 'day': 30, 'name': 'Dominion Mark', 'tradition': 'Regalus', 'desc': 'The year ends in authority. Debts are named, punishments declared, and nothing is forgiven yet.'},
]


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


def calculate_birthday_epoch(age, birthday_month, birthday_day):
    """
    Calculate when a character was born based on their age and birthday.
    
    Args:
        age (int): Character's age in years
        birthday_month (int): Month of birth (0-11, 0=Plowbreak)
        birthday_day (int): Day of birth (1-30)
        
    Returns:
        int: Game time in seconds when the character was born
    """
    # Get current date
    current_date = get_korvessan_date()
    current_year = current_date['year']
    current_month = current_date['month_index']
    current_day = current_date['day']
    
    # Calculate birth year
    birth_year = current_year - age
    
    # If birthday hasn't happened yet this year, they were born a year earlier
    if birthday_month > current_month or (birthday_month == current_month and birthday_day > current_day):
        birth_year -= 1
    
    # Calculate total days since calendar epoch to birth date
    days_to_birth = (birth_year - CALENDAR_EPOCH_YEAR) * DAYS_PER_YEAR
    days_to_birth += birthday_month * DAYS_PER_MONTH
    days_to_birth += birthday_day - 1  # Days are 1-indexed, but we need 0-indexed for calculation
    
    # Convert to seconds
    return days_to_birth * SECONDS_PER_DAY


def is_birthday_today(character=None, birthday_month=None, birthday_day=None):
    """
    Check if today is a character's birthday.
    
    Args:
        character: Character object (optional, if not provided use birthday_month/day)
        birthday_month (int): Month of birth (0-11) if character not provided
        birthday_day (int): Day of birth (1-30) if character not provided
        
    Returns:
        bool: True if today is the birthday
    """
    current_date = get_korvessan_date()
    
    if character:
        # Get birthday from character database
        if not hasattr(character.db, 'birthday_month') or not hasattr(character.db, 'birthday_day'):
            return False
        birthday_month = character.db.birthday_month
        birthday_day = character.db.birthday_day
    
    if birthday_month is None or birthday_day is None:
        return False
    
    return current_date['month_index'] == birthday_month and current_date['day'] == birthday_day


def get_character_age(character=None, birthday_month=None, birthday_day=None):
    """
    Calculate a character's current age.
    
    Args:
        character: Character object (optional)
        birthday_month (int): Month of birth (0-11) if character not provided
        birthday_day (int): Day of birth (1-30) if character not provided
        
    Returns:
        int: Age in years
    """
    if character:
        if not hasattr(character.db, 'birthday_month') or not hasattr(character.db, 'birthday_day'):
            return None
        birthday_month = character.db.birthday_month
        birthday_day = character.db.birthday_day
    
    if birthday_month is None or birthday_day is None:
        return None
    
    current_date = get_korvessan_date()
    current_year = current_date['year']
    current_month = current_date['month_index']
    current_day = current_date['day']
    
    # Start with year difference
    age = current_year - (current_year - CALENDAR_EPOCH_YEAR)  # This is overly complex, simplify:
    
    # Actually, we need to know birth year. Let's recalculate properly.
    # If we have birthday_month and birthday_day, we can work backwards from now
    # But we don't have the birth year directly. This function assumes we know birth year somehow.
    # For now, we'll assume age was stored separately.
    
    return None  # This needs more info to work


def format_birthday(birthday_month, birthday_day):
    """
    Format a birthday as a string.
    
    Args:
        birthday_month (int): Month (0-11)
        birthday_day (int): Day (1-30)
        
    Returns:
        str: Formatted birthday like "the 15th of Fullreap"
    """
    suffix = get_ordinal_suffix(birthday_day)
    return f"the {birthday_day}{suffix} of {MONTHS[birthday_month]['name']}"


def get_holiday_today(date=None):
    """
    Check if today is a holiday and return its information.
    
    Args:
        date: Date dict from get_korvessan_date(), or None for current
        
    Returns:
        dict: Holiday info with 'name', 'tradition', 'desc', or None if not a holiday
    """
    if date is None:
        date = get_korvessan_date()
    
    current_month = date['month_index']
    current_day = date['day']
    
    for holiday in HOLIDAYS:
        if holiday['month'] == current_month and holiday['day'] == current_day:
            return holiday
    
    return None
