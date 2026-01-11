"""
Set a stat value for a target character.
Usage:
    setstat <target> <stat> <value>
Admins only. Sets the specified stat on the target character.
"""
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
    
    # Map stat names to their database attribute names
    STAT_MAP = {
        'smrt': 'smrt',
        'will': 'will',
        'edge': 'edge',
        'ref': 'ref',
        'body': 'body',
        'dex': 'dex',
        'emp': '_emp',
        'tech': 'tech',
    }

    def func(self):
        if not self.args:
            self.caller.msg("Usage: setstat \"<target>\" <stat> <value>")
            return
        
        import shlex
        try:
            args = shlex.split(self.args.strip())
        except ValueError:
            self.caller.msg("Invalid quoting in arguments.")
            return
        
        if len(args) != 3:
            self.caller.msg("Usage: setstat \"<target>\" <stat> <value>")
            return
        target_name, stat, value = args
        target = self.caller.search(target_name)
        if not target:
            self.caller.msg(f"Target '{target_name}' not found.")
            return
        
        stat_lower = stat.lower()
        if stat_lower not in self.STAT_MAP:
            self.caller.msg(f"Unknown stat '{stat}'. Valid stats: {', '.join(self.STAT_MAP.keys())}")
            return
        
        try:
            value = int(value)
        except ValueError:
            self.caller.msg("Value must be an integer.")
            return
        
        # Set the stat via db attributes to ensure persistence
        db_attr = self.STAT_MAP[stat_lower]
        setattr(target, db_attr, value)
        
        # Force save
        if hasattr(target, 'save'):
            target.save()
        
        self.caller.msg(f"Set {stat.upper()} for {target.key} to {value}.")
        target.msg(f"Your {stat.upper()} has been set to {value} by an admin.")
