"""
Repair Command

Allows players to repair weapons and armor.
"""

from evennia import Command
from world.repair_system import start_repair, cancel_repair, get_repair_status


class CmdRepair(Command):
    """
    Repair a weapon or piece of armor.
    
    Usage:
        repair <item>
        repair status
        repair cancel
    
    Repairs restore durability to damaged equipment.
    Artificer personality repairs 50% faster.
    
    Base repair times:
      - Weapons: 5 minutes
      - Armor: 10 minutes
    """
    
    key = "repair"
    aliases = ["fix", "mend"]
    locks = "cmd:all()"
    help_category = "Crafting"
    
    def func(self):
        caller = self.caller
        
        if not self.args or not self.args.strip():
            caller.msg("Usage: repair <item>, repair status, or repair cancel")
            return
        
        args = self.args.strip().lower()
        
        # Check status
        if args == "status":
            status = get_repair_status(caller)
            if not status:
                caller.msg("|yYou are not currently repairing anything.|n")
                return
            
            item = status['item']
            progress = status['progress']
            remaining = status['remaining']
            
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            
            caller.msg(f"|yRepairing:|n {item.get_display_name(caller)}")
            caller.msg(f"|yProgress:|n {progress:.1f}%")
            caller.msg(f"|yTime remaining:|n {minutes}m {seconds}s")
            return
        
        # Cancel repair
        if args == "cancel":
            if cancel_repair(caller):
                caller.msg("|yRepair canceled.|n")
            else:
                caller.msg("|yYou are not currently repairing anything.|n")
            return
        
        # Start repair
        # Find the item
        item = caller.search(
            self.args,
            candidates=caller.contents,
            quiet=True
        )
        
        if not item:
            caller.msg(f"You don't have '{self.args}'.")
            return
        
        if len(item) > 1:
            caller.msg("Which item do you mean?")
            return
        
        item = item[0]
        
        start_repair(caller, item)


class CmdCraftingSet(Command):
    """
    Crafting commands collection.
    """
    
    key = "crafting"
    help_category = "Crafting"
    
    def func(self):
        caller = self.caller
        caller.msg("|wCrafting Commands:|n")
        caller.msg("  |wrepair <item>|n - Repair damaged equipment")
        caller.msg("  |wrepair status|n - Check repair progress")
        caller.msg("  |wrepair cancel|n - Cancel current repair")
