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
# DISPLAY STRINGS
# =============================================================================

# UI Template - the main display
# Note: || is escaped pipe character in Evennia ANSI
UI_TEMPLATE = """,_________________________________________________________________,
( OKAMA(c) 1969 .'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'. )
( .'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'.'. )
(                         OKAMA GAMEBUD                           )
())====PORT:{port}====CPU:{cpu}%====PROXY:  NULL====IP:{ip}===(()
( Alias: {alias:<10} ||>Lobbies|| GameBuds({msg_count} Messages)|| Settings     )
(      ,-------------------------------------------------------,  )
(      ||________________Recent Lobbies_________________________||  )
{messages}(     '-------------------------------------------------------'   )
(                    [Q W E R T Y U I O P]                        )
(       /\\           [A S D F G H J K L .]                        )
(     <-()->         [Z X C V B N M , : ;]                        )
(       \\/           [1 2 3 4 5 6 7 8 9 0]                        )
\\_________________________________________________________________/"""

# Message line template - name (10 chars) : message (40 chars max)
# Note: || is escaped pipe character in Evennia ANSI
MESSAGE_LINE_TEMPLATE = "(      ||C||{name}: {message}||   )\n"

# Empty message line (matches message line width)
EMPTY_MESSAGE_LINE = "(      ||                                                    ||   )\n"

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
  |wgamebud mute|n         - Turn off new message notifications
  |wgamebud unmute|n       - Turn on new message notifications
"""
