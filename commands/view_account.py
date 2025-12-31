"""
Admin command to view account details, including email and characters.
"""
from evennia.commands.command import Command as BaseCommand
from evennia.accounts.models import AccountDB
from evennia.objects.models import ObjectDB

class CmdViewAccount(BaseCommand):
    """
    View account details and character emails.
    Usage:
        viewaccount <accountname>
    """
    key = "viewaccount"
    locks = "cmd:perm(Admin)"
    help_category = "Admin"

    def func(self):
        if not self.args:
            self.caller.msg("|r[ERROR]|n Usage: viewaccount <accountname>")
            return
        name = self.args.strip()
        try:
            account = AccountDB.objects.get(username__iexact=name)
        except AccountDB.DoesNotExist:
            self.caller.msg(f"|r[ERROR]|n Account '{name}' not found.")
            return
        email = getattr(account.db, 'email', None) or account.email or "(none)"
        msg = f"|wAccount:|n {account.username}\n|wEmail:|n {email}\n|wCharacters:|n\n"
        chars = ObjectDB.objects.filter(db_account=account)
        if not chars:
            msg += "  (none)"
        else:
            for char in chars:
                char_email = getattr(char.db, 'email', None) or "(none)"
                msg += f"  |c{char.key}|n (email: {char_email})\n"
        self.caller.msg(msg)
