"""
Godhood command: Grants or removes the 'Immortal' race for admin/staff use only.
"""
from evennia.commands.command import Command

class CmdGodhood(Command):
    """
    Grant or remove godhood (Immortal race) to a character.
    Usage:
        godhood <character> [on|off]
    Only available to Admins.
    """
    key = "godhood"
    locks = "cmd:perm(Immortal) or perm(Admin)"
    help_category = "Admin"

    def func(self):
        if not self.args:
            self.caller.msg("|rUsage: godhood <character> [on|off]|n")
            return
        parts = self.args.strip().split()
        charname = parts[0]
        mode = parts[1].lower() if len(parts) > 1 else "on"
        from evennia.objects.models import ObjectDB
        try:
            char = ObjectDB.objects.get(db_key__iexact=charname)
        except ObjectDB.DoesNotExist:
            self.caller.msg(f"|rCharacter '{charname}' not found.|n")
            return
        if mode == "on":
            char.db.race = "Immortal"
            self.caller.msg(f"|g{char.key} is now Immortal!|n")
            char.msg("|yYou have been granted godhood (Immortal race) by an admin.|n")
        elif mode == "off":
            char.db.race = None
            self.caller.msg(f"|yGodhood removed from {char.key}.|n")
            char.msg("|rYour godhood (Immortal race) has been removed by an admin.|n")
        else:
            self.caller.msg("|rUsage: godhood <character> [on|off]|n")
