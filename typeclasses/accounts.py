"""
Account

The Account represents the game "account" and each login has only one
Account object. An Account is what chats on default channels but has no
other in-game-world existence. Rather the Account puppets Objects (such
as Characters) in order to actually participate in the game world.


Guest

Guest accounts are simple low-level accounts that are created/deleted
on the fly and allows users to test the game without the commitment
of a full registration. Guest accounts are deactivated by default; to
activate them, add the following line to your settings file:

    GUEST_ENABLED = True

You will also need to modify the connection screen to reflect the
possibility to connect with a guest account. The setting file accepts
several more options for customizing the Guest account system.

"""

from evennia.accounts.accounts import DefaultAccount, DefaultGuest


class Account(DefaultAccount):
    """
    An Account is the actual OOC player entity. It doesn't exist in the game,
    but puppets characters.

    Account Enhancements for Korvessa:
     - db.email - Account email address
     - db.ansi_color - Toggle ANSI color support (default: True)
     - db.created_chars - List of created character keys
     - db.retired_chars - List of retired character keys
     - db.pending_apps - List of pending character applications
     - db.discord_id - Linked Discord user ID
    """

    def at_account_creation(self):
        """Initialize new account attributes."""
        self.db.email = ""
        self.db.created_chars = []
        self.db.retired_chars = []
        self.db.pending_apps = []


class Guest(DefaultGuest):
    """
    This class is used for guest logins. Unlike Accounts, Guests and their
    characters are deleted after disconnection.
    """

    pass
