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

CONNECTION_SCREEN = """
|#ffffff════════════════════════════════════════════════════════|n
                       Welcome to |#5f005f{}|n
                    |#ffff00May He Watch over you...|n
|#ffffff════════════════════════════════════════════════════════|n

By logging into our game you affirm you have reached the 
age of majority/consent in your jurisdiction or country.
When in game refer to "help information consent"

|b────────────────────────────────────────────────────────────|n
 |wC|n) Create a new game account. (NOTE: Not your character name)
 |wL|n) Login to an existing account
 |wG|n) Guest Gladiator
 |wX|n) Disconnect from the server
|b────────────────────────────────────────────────────────────|n

Your account name: |n""".format(
    settings.SERVERNAME
)
