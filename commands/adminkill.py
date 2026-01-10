from evennia import Command
from typeclasses.characters import Character

class CmdAdminKill(Command):
    """
    Instantly kill a character (admin only, for testing).
    Usage: adminkill <character>
    """
    key = "adminkill"
    locks = "cmd:perm(Admin)"
    help_category = "Admin"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: adminkill <character>")
            return
        target = caller.search(self.args, typeclass=Character)
        if not target:
            caller.msg("No such character found.")
            return
        if hasattr(target, "at_death"):
            target.at_death(killer=caller)
            caller.msg(f"|r{target.key} has been killed instantly.|n")
        else:
            caller.msg("Target does not support death.")
