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
    # Build the create command line based on registration setting
    if settings.NEW_ACCOUNT_REGISTRATION_ENABLED:
      create_line = "__ Create  : |wcreate <email@address.com> <password>|n"
      instructions = "\nStep into Korvessa. Begin your story, or reclaim a lost one."
    else:
      create_line = "__ Connect : |wconnect <email@address.com> <password>|n"
      instructions = "\nReturn to Korvessa. The city remembers."

    return f"""
  |#d75f00Year 160 After Herding|n
  |#d75f00The world outside is ruin—storms, famine, and the memory of exile. Five cities endure, sealed by fate and faith.|n
  |#d75f00You stand at the edge of Korvessa, where the Watcher’s eye is ever open.|n

  |#d75f00Here, the air is heavy with incense and old grudges. The walls remember the Herding, the Corralling, the Sprinklings—each a scar, each a lesson.|n
  |#d75f00No one leaves the city’s bounds but once in a decade, and not all return whole.|n

  |#d75f00Three great factions vie beneath the Watcher’s gaze:|n
  |#d7af5f  Velorans|n   |#d75f00— order, sacrifice, duty|n
  |#afd7ff  Feyliksians|n |#d75f00— chance, art, freedom|n
  |#af5fff  Regalists|n   |#d75f00— ambition, strength, control|n
  |#d75f00All claim the Watcher’s balance, all hunger for the city’s soul.|n

  |#d70000Justice is a coin toss, a prayer, a blade in the dark. The Sprinkling draws near. Rumors whisper of a new Scholar’s Passage—one more chance to cross the unseen boundary.|n

  |#d75f00Will you serve, rebel, or vanish into the city’s shadowed heart?|n

  {create_line}
  __ Connect : |wconnect <email@address.com> <password>|n
  |g{instructions}|n
  Character creation happens after login.
  |whelp|n for more info. |wlook|n to see this again.
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
