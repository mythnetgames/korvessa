"""
Economy Constants

Central configuration for the economy system.
All monetary values and timing constants should be defined here.
"""

# Starting money for new characters
STARTING_CASH = 1000

# Payday system
PAYDAY_PAYOUT = 1000  # Base payout (Street Rat level)
PAYDAY_PERIOD_SECONDS = 7 * 24 * 3600  # 7 days in seconds

# Cube housing (referenced from cube_housing.py)
CUBE_RENT_PER_DAY = 100

# Pad housing (larger multi-room housing)
PAD_CODE_LENGTH = 6
PAD_DEFAULT_WEEKLY_RENT = 1  # Default weekly rent in dollars (can be changed via SETRENT)
RENT_PERIOD_SECONDS = 7 * 24 * 3600  # 7 days in seconds (used for rent calculations)

# Money pile settings
MONEY_PILE_KEY = "cash"
MONEY_PILE_ALIASES = ["money", "dollars", "pile of cash", "money pile"]

# Currency formatting
CURRENCY_SYMBOL = "$"
CURRENCY_NAME = "dollars"
CURRENCY_NAME_SINGULAR = "dollar"
