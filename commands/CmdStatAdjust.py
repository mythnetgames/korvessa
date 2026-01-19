"""
Admin Command: Adjust Character Stats and Skills

Allows admins to modify character D&D 5e stats on the fly.
"""

from evennia import Command
from world.combat.constants import (
    STAT_STR, STAT_DEX, STAT_CON, STAT_INT, STAT_WIS, STAT_CHA
)


class CmdStatAdjust(Command):
    """
    Adjust a character's D&D 5e stats or skills.
    
    Usage:
        statadj <character> <stat> <value>        - Set a stat to an exact value
        statadj <character> <stat> +<value>       - Increase a stat
        statadj <character> <stat> -<value>       - Decrease a stat
        statadj <character> <stat|skill> ?        - Show current value
        statadj/list <character>                  - List all stats and skills
        statadj/help                              - Show available stats
    
    Available stats: str, dex, con, int, wis, cha (D&D 5e 8-16 range, average 10)
    
    Examples:
        statadj dalao con 14          - Set constitution to 14
        statadj dalao dex +1          - Increase dexterity by 1
        statadj dalao wis -1          - Decrease wisdom by 1
        statadj/list dalao            - Show all stats
    """
    key = "statadj"
    aliases = ["stat", "statsadj"]
    locks = "cmd:perm(Builder)"
    help_category = "Admin"
    
    VALID_STATS = {
        "str": STAT_STR,
        "dex": STAT_DEX,
        "con": STAT_CON,
        "int": STAT_INT,
        "wis": STAT_WIS,
        "cha": STAT_CHA,
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
                current = getattr(target, stat_name, 10)
                new_value = current + adjustment
                op_desc = f"increased by {adjustment}"
            elif value_str.startswith("-"):
                adjustment = int(value_str[1:])
                current = getattr(target, stat_name, 10)
                new_value = current - adjustment
                op_desc = f"decreased by {adjustment}"
            else:
                new_value = int(value_str)
                op_desc = f"set to {new_value}"
        except ValueError:
            self.caller.msg("Value must be a number, +number, or -number.")
            return
        
        # Clamp D&D 5e stats to 8-16 range
        if new_value < 8:
            new_value = 8
            self.caller.msg(f"Value clamped to 8 (D&D 5e minimum).")
        elif new_value > 16:
            new_value = 16
            self.caller.msg(f"Value clamped to 16 (D&D 5e maximum).")
        
        # Set the stat (using AttributeProperty on character)
        setattr(target, stat_name, new_value)
        
        # Force save to ensure persistence
        if hasattr(target, 'save'):
            target.save()
        
        self.caller.msg(f"|g✓ {target.key}'s {stat_name.upper()} {op_desc} (now {new_value}).|n")
        target.msg(f"|yAn admin has adjusted your {stat_name.upper()} to {new_value}.|n")
    
    def _show_stat(self, target, stat_name):
        """Show a single stat value."""
        current_value = getattr(target, stat_name, 10)
        self.caller.msg(f"{target.key}'s {stat_name.upper()}: {current_value}")
    
    def _list_stats(self, target_name):
        """List all stats for a character."""
        target = self.caller.search(target_name)
        if not target:
            self.caller.msg(f"Character '{target_name}' not found.")
            return
        
        self.caller.msg(f"|y=== D&D 5e Stats for {target.key} ===|n")
        for stat_name in self.VALID_STATS.keys():
            value = getattr(target, stat_name, 10)
            mod = (value - 10) // 2
            self.caller.msg(f"  {stat_name.upper():6} : {value} (modifier: {mod:+d})")
    
    def _show_help(self):
        """Show help information."""
        self.caller.msg("""
|yAvailable D&D 5e Stats (8-16 range, average 10):|n
  str      - Strength: Physical power and melee damage
  dex      - Dexterity: Agility, reflexes, ranged attacks
  con      - Constitution: Health, stamina, endurance
  int      - Intelligence: Reasoning, technical knowledge
  wis      - Wisdom: Perception, intuition, willpower
  cha      - Charisma: Personality, social influence

|yExamples:|n
  statadj dalao con 14       - Set constitution to 14
  statadj dalao dex +1       - Increase dexterity by 1
  statadj dalao wis -1       - Decrease wisdom by 1
  statadj/list dalao         - Show all stats
  statadj dalao str ?        - Show current strength value
        """)
