"""
Custom email-based login commands for gelatinous
Adapted from evennia.contrib.base_systems.email_login
"""

from django.conf import settings
from evennia.accounts.models import AccountDB
from evennia.commands.default.muxcommand import MuxCommand
from evennia.utils import class_from_module, utils
from evennia.server.models import ServerConfig
from django.db import utils as db_utils


class CmdEmailConnect(MuxCommand):
    """
    Connect to the game using your account name.

    Usage (at login screen):
        connect <account_name> <password>

    Use your account name (public identifier) to connect.
    Your email address is kept private for password resets only.
    """

    key = "connect"
    aliases = ["conn", "con", "co"]
    locks = "cmd:all()"

    def func(self):
        """Account name-based connection logic"""
        session = self.caller
        address = session.address
        arglist = self.arglist

        if not arglist or len(arglist) < 2:
            session.msg("\n\r Usage: connect <account_name> <password>")
            return
            
        username = arglist[0].lower().strip()
        password = arglist[1]

        # Look up account by username (case-insensitive)
        try:
            account = AccountDB.objects.filter(username__iexact=username).first()
        except AccountDB.DoesNotExist:
            account = None
        
        if not account:
            session.msg(f"No account found with name '{username}'.")
            session.msg("Use 'create' to make a new account.")
            return
            
        # Verify password
        if not account.check_password(password):
            session.msg("Incorrect password.")
            return

        # Check IP and/or name bans
        bans = ServerConfig.objects.conf("server_bans")
        if bans and (
            any(tup[0] == account.username for tup in bans)
            or any(tup[2].match(address[0]) for tup in bans if tup[2])
        ):
            session.msg("|rYou have been banned and cannot continue.|n")
            session.execute_cmd("quit")
            return

        # Login successful
        try:
            session.sessionhandler.login(session, account)
        except db_utils.OperationalError as e:
            # Likely a filesystem permission problem with the database (e.g. readonly).
            session.msg("|rLogin failed due to database write error. Please contact an administrator.|n")
            # Log details to server stdout for admins
            print("Database OperationalError during login:", e)
            return


class CmdEmailCreate(MuxCommand):
    """
    Create a new account with account name and email.

    Usage (at login screen):
        create <account_name> <password> <email@address.com>

    Your account name is public (shown on channels and in-game).
    Your email address is private and used for password resets only.
    Character creation happens after login.
    """

    key = "create"
    aliases = ["cre", "cr"]
    locks = "cmd:all()"

    def func(self):
        """Account creation with name and email"""
        session = self.caller
        address = session.address
        arglist = self.arglist

        # Check if account registration is enabled
        if not settings.NEW_ACCOUNT_REGISTRATION_ENABLED:
            session.msg("|rAccount creation is currently disabled.|n")
            session.msg("Contact an administrator if you need an account.")
            return

        if not arglist or len(arglist) < 3:
            session.msg("\n\r Usage: create <account_name> <password> <email@address.com>")
            return
            
        username = arglist[0].lower().strip()
        password = arglist[1]
        email = arglist[2].lower().strip()
        
        # Validate account name (no spaces, letters/numbers/underscores)
        import re
        if not re.match(r"^[a-z0-9_]{3,20}$", username):
            session.msg("Account name must be 3-20 characters (letters, numbers, underscores only).")
            return
        
        # Validate email format
        if not utils.validate_email_address(email):
            session.msg(f"'{email}' is not a valid email address.")
            return

        # Check if username already exists
        existing_username = AccountDB.objects.filter(username__iexact=username).first()
        if existing_username:
            session.msg(f"Account name '{username}' is already taken.")
            session.msg("Please choose a different account name.")
            return

        # Check if email already exists
        existing_email = AccountDB.objects.filter(email__iexact=email).first()
        if existing_email:
            session.msg(f"An account with email '{email}' already exists.")
            session.msg("Use 'connect' to log in to your existing account.")
            return

        # Create account
        Account = class_from_module(settings.BASE_ACCOUNT_TYPECLASS)
        account, errors = Account.create(
            username=username,  # Public account name
            email=email,        # Private email
            password=password, 
            ip=address
        )
        
        if account:
            session.msg(f"|gAccount created successfully!|n")
            session.msg(f"You can now connect with: |wconnect {username} <password>|n")
            session.msg("Character creation will happen after you log in.")
        else:
            session.msg(f"|rAccount creation failed:|n {'; '.join(errors)}")


# Command set to replace the default unloggedin commands
from evennia.commands.cmdset import CmdSet

class UnloggedinEmailCmdSet(CmdSet):
    """
    Command set for unloggedin users with email-based authentication.
    """
    key = "UnloggedinEmail"
    priority = 0

    def at_cmdset_creation(self):
        """Populate the command set."""
        self.add(CmdEmailConnect())
        self.add(CmdEmailCreate())
        
        # Keep other default unloggedin commands
        from evennia.commands.default.unloggedin import (
            CmdUnconnectedQuit, CmdUnconnectedLook, CmdUnconnectedHelp
        )
        self.add(CmdUnconnectedQuit())
        self.add(CmdUnconnectedLook())
        self.add(CmdUnconnectedHelp())