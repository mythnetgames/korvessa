"""
Wield/Hold Command

Allows characters to equip and unequip weapons and items in their hands.

Usage:
    wield <item>     - Equip item in right hand (or only hand if item is one-handed)
    hold <item>      - Alias for wield
    unwield <item>   - Unequip item from hand
    unwield          - Unequip all items
    wield/left <item> - Equip item in left hand
    wield/both <item> - Equip item as two-handed weapon
"""

from evennia import Command
from evennia.utils.utils import inherits_from


class CmdWield(Command):
    """
    Wield or hold an item in your hands.
    
    Usage:
        wield <item>          - Equip item (right hand by default)
        hold <item>           - Alias for wield
        wield/left <item>     - Equip in left hand
        wield/both <item>     - Equip as two-handed weapon
        unwield [item]        - Unequip item or all items
    """
    key = "wield"
    aliases = ["hold", "unwield"]
    locks = "cmd:all()"
    help_category = "General"
    
    def func(self):
        """Implement the wield/hold command."""
        caller = self.caller
        
        # Check if this is an unwield command
        if self.cmdname == "unwield":
            self._handle_unwield()
            return
        
        if not self.args:
            caller.msg("Usage: wield <item> or unwield [item]")
            return
        
        # Get the item to wield
        item_name = self.args.strip()
        item = caller.search(item_name, location=caller)
        
        if not item:
            return
        
        # Check if item is in character's inventory
        if item.location != caller:
            caller.msg(f"You don't have {item.key}.")
            return
        
        # Determine which hand to use
        hand = "right"
        if "left" in self.switches:
            hand = "left"
        elif "both" in self.switches:
            hand = "both"
        
        self._wield_item(item, hand)
    
    def _wield_item(self, item, hand="right"):
        """Wield an item in the specified hand."""
        caller = self.caller
        
        # Initialize hands if needed
        if not hasattr(caller, "hands"):
            caller.hands = {}
        
        # Check if hand is already occupied
        current_item = caller.hands.get(hand)
        if current_item:
            caller.msg(f"Your {hand} hand is already holding {current_item.key}. Unwield it first.")
            return
        
        # If two-handed, check both hands
        if hand == "both":
            if caller.hands.get("left") or caller.hands.get("right"):
                caller.msg("Both your hands are already holding something. Unwield first.")
                return
            caller.hands["left"] = item
            caller.hands["right"] = item
            caller.location.msg_contents(f"{caller.key} wields {item.key} with both hands.", exclude=[caller])
            caller.msg(f"You wield {item.key} with both hands.")
        else:
            caller.hands[hand] = item
            caller.location.msg_contents(f"{caller.key} wields {item.key} in their {hand} hand.", exclude=[caller])
            caller.msg(f"You wield {item.key} in your {hand} hand.")
        
        # Set equipped tag on the item
        item.tags.add("equipped", category="combat")
    
    def _handle_unwield(self):
        """Handle unwielding items."""
        caller = self.caller
        
        if not hasattr(caller, "hands"):
            caller.hands = {}
        
        if not self.args:
            # Unwield everything
            if not caller.hands or not any(caller.hands.values()):
                caller.msg("You're not holding anything.")
                return
            
            held_items = []
            for hand, item in caller.hands.items():
                if item:
                    held_items.append(item)
                    caller.hands[hand] = None
                    item.tags.remove("equipped", category="combat")
            
            if held_items:
                item_names = ", ".join([item.key for item in held_items])
                caller.msg(f"You stop holding {item_names}.")
                caller.location.msg_contents(
                    f"{caller.key} stops holding {item_names}.",
                    exclude=[caller]
                )
        else:
            # Unwield specific item
            item_name = self.args.strip()
            item = caller.search(item_name, location=caller)
            
            if not item:
                return
            
            # Find which hand is holding it
            unwielded = False
            for hand, held_item in caller.hands.items():
                if held_item == item:
                    caller.hands[hand] = None
                    item.tags.remove("equipped", category="combat")
                    unwielded = True
                    
                    # If it was two-handed, clear both hands
                    if caller.hands.get("left") == item and caller.hands.get("right") == item:
                        caller.hands["left"] = None
                        caller.hands["right"] = None
            
            if unwielded:
                caller.msg(f"You stop holding {item.key}.")
                caller.location.msg_contents(
                    f"{caller.key} stops holding {item.key}.",
                    exclude=[caller]
                )
            else:
                caller.msg(f"You're not holding {item.key}.")
