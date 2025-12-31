"""
Unlogged command to capture email after account creation.
"""
from evennia.commands.command import Command as BaseCommand
import re

class CmdSetEmail(BaseCommand):
    """
    Set your email address after account creation.
    Usage:
        <email>
    """
    key = "setemail"
    locks = "cmd:all()"
    help_category = "Account"

    def parse(self):
        self.email = self.args.strip()

    def func(self):
        if not hasattr(self.caller, 'ndb') or not getattr(self.caller.ndb, 'awaiting_email', None):
            return  # Only trigger if awaiting_email is set
        email = self.email or self.raw_string.strip()
        # Basic email validation
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            self.caller.msg("|r[ERROR]|n Please enter a valid email address:")
            return
        account = self.caller.ndb.awaiting_email
        account.db.email = email
        account.save()
        self.caller.msg(f"|g[SUCCESS]|n Email '{email}' saved. You may now log in with your new account.")
        del self.caller.ndb.awaiting_email
