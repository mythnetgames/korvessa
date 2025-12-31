"""
Admin Application Queue Command

Allows staff to view, sort, and read all pending character applications.
"""
from evennia.commands.command import Command as BaseCommand
from evennia.utils.evtable import EvTable

class CmdAppQueue(BaseCommand):
    """
    View and manage the character application queue.

    Usage:
        appqueue
        appqueue <#>
    """
    key = "appqueue"
    locks = "cmd:perm(Builder)"
    help_category = "Admin"

    def func(self):
        """Show all pending applications, or details for a specific one."""
        from evennia.objects.models import ObjectDB
        args = self.args.strip()
        # List all pending applications
        if not args:
            # Get all player objects and filter by application_status attribute
            all_chars = ObjectDB.objects.filter(db_is_player=True).order_by('db_date_created')
            apps = [obj for obj in all_chars if getattr(obj.db, 'application_status', None) == 'pending']
            if not apps:
                self.caller.msg("|y[INFO]|n No pending character applications.")
                return
            table = EvTable("#", "Char Name", "Account", "Created", "Status")
            for idx, char in enumerate(apps, 1):
                acct = char.db_account.key if hasattr(char, 'db_account') and char.db_account else "?"
                table.add_row(str(idx), char.key, acct, str(char.db_date_created)[:19], char.db.application_status)
            self.caller.msg("|wPending Character Applications:|n\n" + str(table) + "\n(Type |cappqueue <#>|n to read details.)")
        else:
            # Show details for a specific application
            try:
                idx = int(args)
            except ValueError:
                self.caller.msg("|r[ERROR]|n Usage: appqueue <#>")
                return
            all_chars = ObjectDB.objects.filter(db_is_player=True).order_by('db_date_created')
            apps = [obj for obj in all_chars if getattr(obj.db, 'application_status', None) == 'pending']
            if idx < 1 or idx > len(apps):
                self.caller.msg("|r[ERROR]|n Invalid application number.")
                return
            char = apps[idx-1]
            acct = char.db_account.key if hasattr(char, 'db_account') and char.db_account else "?"
            details = f"|wApplication #{idx}|n\n|cCharacter:|n {char.key}\n|cAccount:|n {acct}\n|cCreated:|n {char.db_date_created}\n|cStatus:|n {char.db.application_status}\n"
            # Show chargen data if available
            chargen = getattr(char.db, 'chargen_data', None)
            if chargen:
                details += "|cChargen Data:|n\n"
                for k, v in chargen.items():
                    details += f"  |w{k}:|n {v}\n"
            self.caller.msg(details)
