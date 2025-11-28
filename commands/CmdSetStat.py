from evennia import Command

class CmdSetStat(Command):
    """
    Set a stat value for a target character.
    Usage:
        setstat <target> <stat> <value>
    Admins only. Sets the specified stat on the target character.
    """
    key = "setstat"
    locks = "cmd:perm(Builder)"
    help_category = "Admin"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: setstat <target> <stat> <value>")
            return
        args = self.args.strip().split()
        if len(args) != 3:
            self.caller.msg("Usage: setstat <target> <stat> <value>")
            return
        target_name, stat, value = args
        target = self.caller.search(target_name)
        if not target:
            self.caller.msg(f"Target '{target_name}' not found.")
            return
        try:
            value = int(value)
        except ValueError:
            self.caller.msg("Value must be an integer.")
            return
        # Set the stat
        setattr(target, stat.lower(), value)
        self.caller.msg(f"Set {stat.upper()} for {target.key} to {value}.")
        target.msg(f"Your {stat.upper()} has been set to {value} by an admin.")
