"""
Furniture Commands

Commands for interacting with furniture - sitting, lying, standing.
"""

from evennia import Command, CmdSet


class CmdSit(Command):
    """
    Sit down on a piece of furniture.
    
    Usage:
        sit <furniture>
        sit on <furniture>
        
    Examples:
        sit bed
        sit on couch
        sit chair
    """
    
    key = "sit"
    aliases = ["sit on", "sit down on"]
    locks = "cmd:all()"
    help_category = "General"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Sit on what?")
            return
        
        # Clean up args - remove "on" if present
        target_name = self.args.strip().lower()
        if target_name.startswith("on "):
            target_name = target_name[3:].strip()
        
        # Check if already sitting/lying
        if caller.db.sitting_on or caller.db.lying_on:
            current = caller.db.sitting_on or caller.db.lying_on
            caller.msg(f"You are already on {current.get_display_name(caller)}. Stand up first.")
            return
        
        # Find the furniture in the room
        furniture = None
        for obj in caller.location.contents:
            if obj == caller:
                continue
            if target_name in obj.key.lower() or any(target_name in alias.lower() for alias in obj.aliases.all()):
                furniture = obj
                break
        
        if not furniture:
            caller.msg(f"You don't see '{target_name}' here.")
            return
        
        # Check if furniture can be sat on
        can_sit = getattr(furniture.db, "can_sit", None)
        can_lie = getattr(furniture.db, "can_lie_down", None)
        max_seats = getattr(furniture.db, "max_seats", None)
        
        # If no explicit can_sit, check for common furniture keywords
        furniture_keywords = ["bed", "chair", "couch", "sofa", "bench", "stool", "seat", "throne", "mattress"]
        is_furniture = any(kw in furniture.key.lower() for kw in furniture_keywords)
        
        if not can_sit and not can_lie and not is_furniture and max_seats is None:
            caller.msg(f"You can't sit on {furniture.get_display_name(caller)}.")
            return
        
        # Check seat capacity if defined
        if max_seats is not None and max_seats > 0:
            # Count current occupants
            occupants = [c for c in caller.location.contents 
                        if hasattr(c, 'db') and (c.db.sitting_on == furniture or c.db.lying_on == furniture)]
            if len(occupants) >= max_seats:
                caller.msg(f"The {furniture.key} is full.")
                return
        
        # Sit down
        caller.db.sitting_on = furniture
        caller.db.lying_on = None
        
        # Get custom message or use default
        sit_msg_first = getattr(furniture.db, "sit_msg_first", None)
        sit_msg_third = getattr(furniture.db, "sit_msg_third", None)
        
        if sit_msg_first:
            caller.msg(sit_msg_first.format(furniture=furniture.key, name=caller.key))
        else:
            caller.msg(f"You sit down on the {furniture.key}.")
        
        if sit_msg_third:
            caller.location.msg_contents(
                sit_msg_third.format(furniture=furniture.key, name=caller.key),
                exclude=[caller]
            )
        else:
            caller.location.msg_contents(
                f"{caller.key} sits down on the {furniture.key}.",
                exclude=[caller]
            )


class CmdLie(Command):
    """
    Lie down on a piece of furniture.
    
    Usage:
        lie <furniture>
        lie on <furniture>
        lie down on <furniture>
        
    Examples:
        lie bed
        lie on couch
        lie down on mattress
    """
    
    key = "lie"
    aliases = ["lie on", "lie down", "lie down on", "lay", "lay on", "lay down", "lay down on"]
    locks = "cmd:all()"
    help_category = "General"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Lie on what?")
            return
        
        # Clean up args - remove "on" and "down" if present
        target_name = self.args.strip().lower()
        for prefix in ["down on ", "on ", "down "]:
            if target_name.startswith(prefix):
                target_name = target_name[len(prefix):].strip()
                break
        
        # Check if already sitting/lying
        if caller.db.sitting_on or caller.db.lying_on:
            current = caller.db.sitting_on or caller.db.lying_on
            caller.msg(f"You are already on {current.get_display_name(caller)}. Stand up first.")
            return
        
        # Find the furniture in the room
        furniture = None
        for obj in caller.location.contents:
            if obj == caller:
                continue
            if target_name in obj.key.lower() or any(target_name in alias.lower() for alias in obj.aliases.all()):
                furniture = obj
                break
        
        if not furniture:
            caller.msg(f"You don't see '{target_name}' here.")
            return
        
        # Check if furniture can be lain on
        can_lie = getattr(furniture.db, "can_lie_down", None)
        
        # If no explicit can_lie, check for common furniture keywords
        lie_keywords = ["bed", "couch", "sofa", "mattress", "futon", "cot", "hammock"]
        is_lie_furniture = any(kw in furniture.key.lower() for kw in lie_keywords)
        
        if not can_lie and not is_lie_furniture:
            caller.msg(f"You can't lie down on {furniture.get_display_name(caller)}.")
            return
        
        # Check seat capacity if defined (lying takes same space as sitting)
        max_seats = getattr(furniture.db, "max_seats", None)
        if max_seats is not None and max_seats > 0:
            # Count current occupants
            occupants = [c for c in caller.location.contents 
                        if hasattr(c, 'db') and (c.db.sitting_on == furniture or c.db.lying_on == furniture)]
            if len(occupants) >= max_seats:
                caller.msg(f"There's not enough room on the {furniture.key}.")
                return
        
        # Lie down
        caller.db.lying_on = furniture
        caller.db.sitting_on = None
        
        # Get custom message or use default
        lie_msg_first = getattr(furniture.db, "lie_msg_first", None)
        lie_msg_third = getattr(furniture.db, "lie_msg_third", None)
        
        if lie_msg_first:
            caller.msg(lie_msg_first.format(furniture=furniture.key, name=caller.key))
        else:
            caller.msg(f"You lie down on the {furniture.key}.")
        
        if lie_msg_third:
            caller.location.msg_contents(
                lie_msg_third.format(furniture=furniture.key, name=caller.key),
                exclude=[caller]
            )
        else:
            caller.location.msg_contents(
                f"{caller.key} lies down on the {furniture.key}.",
                exclude=[caller]
            )


class CmdStand(Command):
    """
    Stand up from furniture you are sitting or lying on.
    
    Usage:
        stand
        stand up
        get up
    """
    
    key = "stand"
    aliases = ["stand up", "get up"]
    locks = "cmd:all()"
    help_category = "General"
    
    def func(self):
        caller = self.caller
        
        sitting_on = caller.db.sitting_on
        lying_on = caller.db.lying_on
        
        if not sitting_on and not lying_on:
            caller.msg("You are already standing.")
            return
        
        furniture = sitting_on or lying_on
        was_lying = lying_on is not None
        
        # Clear the state
        caller.db.sitting_on = None
        caller.db.lying_on = None
        
        # Messages
        if was_lying:
            caller.msg(f"You get up from the {furniture.key}.")
            caller.location.msg_contents(
                f"{caller.key} gets up from the {furniture.key}.",
                exclude=[caller]
            )
        else:
            caller.msg(f"You stand up from the {furniture.key}.")
            caller.location.msg_contents(
                f"{caller.key} stands up from the {furniture.key}.",
                exclude=[caller]
            )


class FurnitureCmdSet(CmdSet):
    """Command set for furniture interaction commands."""
    
    key = "furniture"
    
    def at_cmdset_creation(self):
        self.add(CmdSit())
        self.add(CmdLie())
        self.add(CmdStand())
