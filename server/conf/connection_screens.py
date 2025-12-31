# -*- coding: utf-8 -*-
"""
Connection screen

This is the text to show the user when they first connect to the game (before
they log in).

To change the login screen in this module, do one of the following:

  called first and must return the full string to act as the connection screen.
  This can be used to produce more dynamic screens.
  with the connection string that should be displayed. If more than one such
  variable is given, Evennia will pick one of them at random.

The commands available to the user when the connection screen is shown
are defined in evennia.default_cmds.UnloggedinCmdSet. The parsing and display
of the screen is done by the unlogged-in "look" command.

"""

from django.conf import settings
from evennia import utils

CONNECTION_SCREEN = f"""
|#ff00ff============================================================|n
|#00ffff  Welcome to |#ffaf00{settings.SERVERNAME}|n
|#ff00ff============================================================|n


|#ffaf00------------------------------------------------------------|n
 |#00ff00C|n) |#ffffffCreate a new game account. (NOTE: Not your character name)|n
 |#00ff00C|n) |wcreate <username> <password>
 |#00afff------------------------------------------------------------|n 
 |#00afffL|n) |#ffffffLogin to an existing account with:|n
 |#00afffL|n) |wlogin <username> <password>
 |#ffaf00------------------------------------------------------------|n

|#ff87ffYour choice:|n
"""

