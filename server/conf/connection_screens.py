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
    """
    # Build the create command line based on registration setting
    if settings.NEW_ACCOUNT_REGISTRATION_ENABLED:
        create_line = "__ Create  : |wcreate <email@address.com> <password>|n\n\nUse your email address to connect or create a new account."
    else:
        create_line = "__ Create  : |rAccount creation disabled|n\n\nUse your email address to connect to your existing account."
    
    return f"""

|g{settings.SERVERNAME} SYSTEM |n :::: SIGNAL {utils.get_evennia_version("short")}

__ Connect : |wconnect <email@address.com> <password>|n
{create_line}
Character creation happens after login.
Enter |whelp|n for more info. |wlook|n will re-show this screen.

"""


# Keep the old static version as fallback (though the function above will take precedence)
CONNECTION_SCREEN = """

|g{} the Walled City |n Enter your ID {} |

YEAR: 1980
LOCATION: Kowloon Walled City, Hong Kong
 


__ Connect : |wconnect <email@address.com> <password>|n
__ Create  : |wcreate <email@address.com> <password>|n

Use your email address to connect or create a new account.
Character creation happens after login.
Enter |whelp|n for more info. |wlook|n will re-show this screen.

""".format(
    settings.SERVERNAME, utils.get_evennia_version("short")
)
