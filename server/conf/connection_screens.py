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
    Thematic to Kowloon Walled City.
    """
    # Color palette from image: #5f005f, #5f0087, #5f00af, #5f00d7, #5f00ff, #af00ff, #af00d7, #af00af, #af0087, #af005f
    # Short, unsettling, and atmospheric
    if settings.NEW_ACCOUNT_REGISTRATION_ENABLED:
      prompt_line = "|#af00ffCreate|n: |wcreate <email@address.com> <password>|n"
    else:
      prompt_line = "|#5f00ffConnect|n: |wconnect <email@address.com> <password>|n"

    return f"""
  |#5f005fKorvessa|n |#af00ffYear 160 AH|n
  |#5f00afThe city is sealed. The Watcher sees all. The walls whisper. You are not alone.|n
  |#af0087Factions hunger. Faith divides. The Sprinkling is near. Doors close behind you.|n

  {prompt_line}
  |#af00afAfter login, you will create your character.|n
  |#af005fType |whelp|#af005f for info. |wlook|#af005f to see this again.|n
  """


# Keep the old static version as fallback (though the function above will take precedence)
CONNECTION_SCREEN = """

|g{} the Walled City |n Enter your ID {} |

YEAR: 198?
LOCATION: Kowloon Walled City
 


__ Connect : |wconnect <email@address.com> <password>|n
__ Create  : |wcreate <email@address.com> <password>|n

Use your email address to connect or create a new account.
Character creation happens after login.
Enter |whelp|n for more info. |wlook|n will re-show this screen.

""".format(
    settings.SERVERNAME, utils.get_evennia_version("short")
)
