"""
Slotting System Commands

Allows items to be slotted into compatible devices (wristpads, computers, etc.)
"""

from evennia import Command


class CmdSlot(Command):
    """
    Slot an item into a compatible device.
    
    Usage:
        slot <item> in <device>
    
    This installs a module (like a proxy module) into a compatible device.
    The device must have slot capability.
    
    Examples:
        slot proxy in wristpad
        slot module in computer
    """
    key = "slot"
    locks = "cmd:all()"
    help_category = "SafetyNet"
    
    def func(self):
        caller = self.caller
        
        if not self.args or " in " not in self.args:
            caller.msg("|rUsage: slot <item> in <device>|n")
            return
        
        # Parse arguments
        parts = self.args.split(" in ", 1)
        item_name = parts[0].strip()
        device_name = parts[1].strip()
        
        # Find item in inventory
        item = caller.search(item_name, location=caller, quiet=True)
        if not item:
            caller.msg(f"|rYou don't have '{item_name}'.|n")
            return
        
        # Check if item is a proxy module
        if not getattr(item.db, "is_proxy", False):
            caller.msg(f"|r{item.name} is not a slottable module.|n")
            return
        
        # Find device
        device = caller.search(device_name, location=caller, quiet=True)
        if not device:
            caller.msg(f"|rYou don't have '{device_name}'.|n")
            return
        
        # Check if device can accept modules
        if not (getattr(device.db, "is_wristpad", False) or 
                getattr(device.db, "is_computer", False) or
                getattr(device.db, "can_slot_modules", False)):
            caller.msg(f"|r{device.name} cannot accept modules.|n")
            return
        
        # Slot the item
        device.db.slotted_proxy = item
        caller.msg(f"|g[SafetyNet] |yYou slot {item.name}|g into {device.name}.|n")
        caller.location.msg_contents(
            f"|g[SafetyNet] |y{caller.name}|g slots {item.name} into {device.name}.|n",
            exclude=[caller]
        )


class CmdUnslot(Command):
    """
    Remove a slotted item from a device.
    
    Usage:
        unslot <device>
    
    This removes any slotted module from a device and returns it to your inventory.
    
    Examples:
        unslot wristpad
        unslot computer
    """
    key = "unslot"
    locks = "cmd:all()"
    help_category = "SafetyNet"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("|rUsage: unslot <device>|n")
            return
        
        # Find device
        device = caller.search(self.args.strip(), location=caller, quiet=True)
        if not device:
            caller.msg(f"|rYou don't have '{self.args.strip()}'.|n")
            return
        
        # Get slotted item
        slotted = getattr(device.db, "slotted_proxy", None)
        if not slotted:
            caller.msg(f"|r{device.name} has nothing slotted in it.|n")
            return
        
        # Move item back to inventory
        device.db.slotted_proxy = None
        slotted.move_to(caller, quiet=True)
        
        caller.msg(f"|g[SafetyNet] |yYou remove {slotted.name}|g from {device.name}.|n")
        caller.location.msg_contents(
            f"|g[SafetyNet] |y{caller.name}|g removes {slotted.name} from {device.name}.|n",
            exclude=[caller]
        )
