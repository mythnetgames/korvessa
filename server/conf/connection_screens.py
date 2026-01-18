# -*- coding: utf-8 -*-
"""
Connection screen

This is the text to show the user when they first connect to the game (before
they log in).

To change the login screen in this module, do one of the following:

- Define a function `connection_screen()`, taking no arguments. This will be
  called first and must return the full string to act as the connection screen.
  This can be used to produce more dynamic screens.
- Alternatively, define a string variable in the outermost scope of this module
  with the connection string that should be displayed. If more than one such
  variable is given, Evennia will pick one of them at random.

The commands available to the user when the connection screen is shown
are defined in evennia.default_cmds.UnloggedinCmdSet. The parsing and display
of the screen is done by the unlogged-in "look" command.

"""

from django.conf import settings
from evennia import utils


def connection_screen():
    """
    Dynamic connection screen that adjusts based on settings.
    Explains the two-identifier account system: account name (public) and email (private).
    """
    if settings.NEW_ACCOUNT_REGISTRATION_ENABLED:
      prompt_line = "|#af00ffCreate|n: |wcreate <account_name> <password> <email@address.com>|n"
      create_info = "|#af00afYour account name is public (shown on channels and in-game).|n\n  |#af00afYour email is private and used for password resets only.|n"
    else:
      prompt_line = "|#5f00ffConnect|n: |wconnect <account_name> <password>|n"
      create_info = ""

    return f"""
  |#5f005fKorvessa|n |#af00ffYear 160 AH|n
  |#5f00afThe city is sealed. The Watcher sees all. The walls whisper. You are not alone.|n
  |#af0087Factions hunger. Faith divides. The Sprinkling is near. Doors close behind you.|n

  {prompt_line}
  {create_info}
  |#af00afAfter login, you will create your character.|n
  |#af005fType |whelp|#af005f for info. |wlook|#af005f to see this again.|n
  """


# Keep the old static version as fallback (though the function above will take precedence)
CONNECTION_SCREEN = """

|g{} the Walled City |n Enter your ID {} |

YEAR: 160 AH
LOCATION: Korvessa
 

__ Connect : |wconnect <account_name> <password>|n
__ Create  : |wcreate <account_name> <password> <email@address.com>|n

Your account name is public (shown on channels and in-game).
Your email address is private and used for password resets only.
Character creation happens after login.
Enter |whelp|n for more info. |wlook|n will re-show this screen.

""".format(
    settings.SERVERNAME, utils.get_evennia_version("short")
)
