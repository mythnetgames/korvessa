"""
Gamebud Constants

All constants for the Okama Gamebud communication system.
"""

# =============================================================================
# SYSTEM LIMITS
# =============================================================================

# Maximum alias length
MAX_ALIAS_LENGTH = 10

# Maximum message length that fits in the display (40 chars to fit with name)
MAX_MESSAGE_LENGTH = 40

# Number of messages shown at a time
MESSAGES_PER_PAGE = 3

# Maximum messages stored (24 hours worth of messages)
MAX_MESSAGES_STORED = 24

# Default port and IP (static values)
GAMEBUD_PORT = "80"
GAMEBUD_IP = "67.420.69.kwc"

# =============================================================================
# COLOR DEFINITIONS
# =============================================================================

# Default shell color - always bright white
DEFAULT_SHELL_COLOR = "W"

# Friendly names for alias colors (IC)
ALIAS_COLOR_NAMES = {
    "red": "r",
    "green": "g",
    "yellow": "y",
    "blue": "b",
    "purple": "m",
    "cyan": "c",
    "white": "w",
    "bright red": "R",
    "bright green": "G",
    "bright yellow": "Y",
    "bright blue": "B",
    "bright purple": "M",
    "bright cyan": "C",
    "bright white": "W",
}

# Reverse lookup for displaying current color
ALIAS_COLOR_DISPLAY = {v: k for k, v in ALIAS_COLOR_NAMES.items()}

# Default alias color
DEFAULT_ALIAS_COLOR = "w"

# =============================================================================
# DISPLAY STRINGS
# =============================================================================

# UI Template - the main display
# Note: || is escaped pipe character in Evennia ANSI
UI_TEMPLATE = """,_________________________________________________________________,
( |#5faf00OKAMA|W(c)|n 1969 .'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'. )
( .'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'. )
(                         |COKAMA GAMEBUD|n                           )
()====PORT:|Y{port}|n====CPU:|Y{cpu}%|n====PROXY:  |rNULL|n====IP:|Y{ip}|n=====()
( Alias: |Y{alias:<10}|n ||>|#0087ffLobbies|| GameBuds(|Y{msg_count}|n Messages)|| Settings     )
(      ,-------------------------------------------------------,  )
(      ||________________Recent Lobbies_________________________||  )
{messages}(      '-------------------------------------------------------'  )
(                    [Q W E R T Y U I O P]                        )
(       /\\           [A S D F G H J K L .]                        )
(     <-|#ffffdf()|N->         [Z X C V B N M , : ;]                        )
(       \\/           [1 2 3 4 5 6 7 8 9 0]                        )
\\_________________________________________________________________/|n"""

# Message line template - name (10 chars) : message (40 chars max)
# Note: || is escaped pipe character in Evennia ANSI
# {alias_color} is user's chosen alias color
MESSAGE_LINE_TEMPLATE = "(      ||C||{alias_color}{name}|n: {message}||  )\n"

# Empty message line (matches message line width)
EMPTY_MESSAGE_LINE = "(      ||                                                     || )\n"

# =============================================================================
# MESSAGES
# =============================================================================

# Error messages
MSG_NO_DEVICE = "|rYou need an Okama Gamebud to do that.|n"
MSG_ALIAS_TOO_LONG = f"|rAlias must be {MAX_ALIAS_LENGTH} characters or less.|n"
MSG_ALIAS_INVALID = "|rAlias can only contain letters, numbers, and underscores.|n"
MSG_MESSAGE_TOO_LONG = f"|rMessage must be {MAX_MESSAGE_LENGTH} characters or less.|n"
MSG_NO_MESSAGE = "|rYou need to provide a message. Use: gamebud post=<message>|n"
MSG_NO_MESSAGES = "|yNo messages in the lobby yet.|n"
MSG_END_OF_MESSAGES = "|yNo more messages to display.|n"

# Success messages
MSG_ALIAS_SET = "|gAlias set to: {alias}|n"
MSG_POST_SUCCESS = "|gMessage posted to the lobby.|n"
MSG_MUTED = "|yGamebud notifications muted.|n"
MSG_UNMUTED = "|gGamebud notifications unmuted.|n"
MSG_ALREADY_MUTED = "|yGamebud is already muted.|n"
MSG_ALREADY_UNMUTED = "|yGamebud is already unmuted.|n"
MSG_COLOR_SET = "|gAlias color set to: |{color}{color_name}|n"
MSG_INVALID_COLOR = "|rInvalid color. Choose from: {colors}|n"
MSG_COLOR_SET = "|gAlias color set to: |{color}{color_name}|n"
MSG_INVALID_COLOR = "|rInvalid color. Choose from: {colors}|n"

# Notification message (beep)
MSG_NEW_MESSAGE = "|c*beep*|n Your Gamebud chirps - new message from |w{sender}|n!"

# =============================================================================
# HELP TEXT
# =============================================================================

GAMEBUD_HELP = """
|wOkama Gamebud Commands:|n

  |wgamebud|n              - View the Gamebud display
  |wgamebud view|n         - View recent messages
  |wgamebud next|n         - View next page of messages
  |wgamebud post=|n<msg>   - Post a message to the lobby
  |wgamebud alias=|n<name> - Set your display alias (max 10 chars)
  |wgamebud color=|n<col>  - Set your alias color (red, blue, cyan, etc.)
  |wgamebud mute|n         - Turn off new message notifications
  |wgamebud unmute|n       - Turn on new message notifications
"""
