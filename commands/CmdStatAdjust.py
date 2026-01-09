"""
Admin Command: Adjust Character Stats and Skills

Allows admins to modify character stats and skills on the fly.
"""

from evennia import Command
from world.combat.constants import (
    STAT_BODY, STAT_REF, STAT_DEX, STAT_TECH, STAT_SMRT, STAT_WILL, STAT_EDGE, STAT_EMP
)


class CmdStatAdjust(Command):
    """
    Adjust a character's stats or skills.
    
    Usage:
        statadj <character> <stat> <value>        - Set a stat to an exact value
        statadj <character> <stat> +<value>       - Increase a stat
        statadj <character> <stat> -<value>       - Decrease a stat
        statadj <character> <stat|skill> ?        - Show current value
        statadj/list <character>                  - List all stats and skills
        statadj/help                              - Show available stats
    
    Available stats: body, ref, dex, tech, smrt, will, edge, emp
    
    Examples:
        statadj dalao body 5          - Set body to 5
        statadj dalao smrt +2         - Increase smrt by 2
        statadj dalao dex -1          - Decrease dex by 1
        statadj/list dalao            - Show all stats
    """
    key = "statadj"
    aliases = ["stat", "statsadj"]
    locks = "cmd:perm(Builder)"
    help_category = "Admin"
    
    VALID_STATS = {
        "body": STAT_BODY,
        "ref": STAT_REF,
        "dex": STAT_DEX,
        "tech": STAT_TECH,
        "smrt": STAT_SMRT,
        "will": STAT_WILL,
        "edge": STAT_EDGE,
        "emp": STAT_EMP,
    }
    
    def func(self):
        """Execute the stat adjustment command."""
        if not self.args:
            self.caller.msg("Usage: statadj <character> <stat> <value>")
            return
        
        if "help" in self.switches:
            self._show_help()
            return
        
        args = self.args.strip().split()
        
        if "list" in self.switches:
            if not args:
                self.caller.msg("Usage: statadj/list <character>")
                return
            self._list_stats(args[0])
            return
        
        if len(args) < 3:
            self.caller.msg("Usage: statadj <character> <stat> <value>")
            return
        
        target_name = args[0]
        stat_name = args[1].lower()
        value_str = args[2]
        
        # Find the target
        target = self.caller.search(target_name)
        if not target:
            self.caller.msg(f"Character '{target_name}' not found.")
            return
        
        # Validate stat name
        if stat_name not in self.VALID_STATS:
            self.caller.msg(f"Invalid stat '{stat_name}'. Valid stats: {', '.join(self.VALID_STATS.keys())}")
            return
        
        # Handle query
        if value_str == "?":
            self._show_stat(target, stat_name)
            return
        
        # Parse the value
        try:
            if value_str.startswith("+"):
                adjustment = int(value_str[1:])
                current = getattr(target.db, stat_name, 1)
                new_value = current + adjustment
                op_desc = f"increased by {adjustment}"
            elif value_str.startswith("-"):
                adjustment = int(value_str[1:])
                current = getattr(target.db, stat_name, 1)
                new_value = current - adjustment
                op_desc = f"decreased by {adjustment}"
            else:
                new_value = int(value_str)
                op_desc = f"set to {new_value}"
        except ValueError:
            self.caller.msg("Value must be a number, +number, or -number.")
            return
        
        # Ensure non-negative
        if new_value < 0:
            new_value = 0
            self.caller.msg(f"Value clamped to 0 (cannot be negative).")
        
        # Set the stat
        setattr(target.db, stat_name, new_value)
        
        self.caller.msg(f"|g✓ {target.key}'s {stat_name.upper()} {op_desc} (now {new_value}).|n")
        target.msg(f"|yAn admin has adjusted your {stat_name.upper()} to {new_value}.|n")
    
    def _show_stat(self, target, stat_name):
        """Show a single stat value."""
        current_value = getattr(target.db, stat_name, 1)
        self.caller.msg(f"{target.key}'s {stat_name.upper()}: {current_value}")
    
    def _list_stats(self, target_name):
        """List all stats for a character."""
        target = self.caller.search(target_name)
        if not target:
            self.caller.msg(f"Character '{target_name}' not found.")
            return
        
        self.caller.msg(f"|y=== Stats for {target.key} ===|n")
        for stat_name in self.VALID_STATS.keys():
            value = getattr(target.db, stat_name, 1)
            self.caller.msg(f"  {stat_name.upper():6} : {value}")
    
    def _show_help(self):
        """Show help information."""
        self.caller.msg("""
|yAvailable Stats:|n
  body     - Physical durability and health
  ref      - Reflexes and reaction time
  dex      - Dexterity and hand-eye coordination
  tech     - Technical knowledge and crafting
  smrt     - Intelligence and reasoning
  will     - Willpower and mental fortitude
  edge     - Luck and chance
  emp      - Empathy and social skills

|yExamples:|n
  statadj dalao body 5       - Set body to 5
  statadj dalao smrt +2      - Increase smrt by 2
  statadj dalao dex -1       - Decrease dex by 1
  statadj/list dalao         - Show all stats
  statadj dalao body ?       - Show current body value
        """)
