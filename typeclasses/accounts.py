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
     - db.created_chars - List of created character keys
     - db.retired_chars - List of retired character keys
     - db.pending_apps - List of pending character applications
    """

    def at_account_creation(self):
        """Initialize new account attributes and standing."""
        self.db.email = ""
        self.db.created_chars = []
        self.db.retired_chars = []
        self.db.pending_apps = []
        self.db.standing = {
            'Civic_Order': 0,
            'Laborers': 0,
            'Merchants': 0,
            'Nobility': 0,
            'Underbelly': 0,
            'Watcher_Cult': 0,
            'Scholars': 0,
            'Feyliks_Freefolk': 0,
        }
        # --- Staff/Admin Scaffolding ---
        self.db.is_staff = False
        self.db.is_admin = False

    def set_staff(self, value=True):
        self.db.is_staff = value

    def set_admin(self, value=True):
        self.db.is_admin = value

    def is_staff(self):
        return bool(self.db.is_staff)

    def is_admin(self):
        return bool(self.db.is_admin)

    def get_standing(self, group):
        """Get social standing for a faction group (account-wide)."""
        return self.db.standing.get(group, 0)

    def set_standing(self, group, value):
        """Set social standing for a faction group (account-wide)."""
        self.db.standing[group] = value
    
    def at_post_login(self, session=None, **kwargs):
        """
        Called after a successful login.
        Assign default AccountCmdSet so basic commands are available.
        """
        from evennia.commands.default.account import AccountCmdSet
        self.cmdset.add(AccountCmdSet, permanent=True)
        # Optionally show character menu:
        # self.show_character_menu()
    
    def show_character_menu(self):
        """Display character selection menu."""
        menu_text = """
|#ffff00════════════════════════════════════════════════════════════|n
|#ffff00CHARACTER MANAGEMENT|n
|#ffff00════════════════════════════════════════════════════════════|n

  1. Login a character.
  2. Submit a character application.
                (Approval required)
  3. Delete a pending application.
  4. Retire your current character.
  5. View your characters.
  6. Update your e-mail address.
  7. Change your account password.
  8. Send/Check OOC Mail.

 11. Log Out.

|#ffff00Your Selection:|n """
        self.msg(menu_text)


class Guest(DefaultGuest):
    """
    This class is used for guest logins. Unlike Accounts, Guests and their
    characters are deleted after disconnection.
    """

    pass
