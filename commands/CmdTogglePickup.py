"""
Admin command to toggle whether an object can be picked up.

Usage:
    togglepickup <object>           - Toggle pickup ability on/off
    togglepickup <object> on/off    - Set to specific state
"""

from evennia.commands.command import Command


class CmdTogglePickup(Command):
    """
    Toggle whether an object can be picked up.
    
    Usage:
        togglepickup <object>          - Toggle pickup ability on/off
        togglepickup <object> on       - Allow pickup
        togglepickup <object> off      - Prevent pickup
    
    This command toggles the 'no_pick' attribute on objects, preventing
    them from being picked up by players. Useful for:
    - NPCs (so they can't be carried)
    - Decorations and scenery
    - Shop display items
    - Quest objects that shouldn't be moved
    
    Examples:
        togglepickup self              - Toggle if you can be picked up
        togglepickup painting off      - Make painting permanent
        togglepickup #123 on           - Allow pickup on object #123
    """
    key = "togglepickup"
    aliases = ["tpick", "nopick"]
    locks = "cmd:perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: togglepickup <object> [on|off]")
            caller.msg("Example: togglepickup painting off")
            return
        
        # Parse arguments
        args = self.args.split()
        target_str = args[0]
        state = args[1].lower() if len(args) > 1 else None
        
        # Get the target object
        if target_str == "self":
            target = caller
        else:
            matches = caller.search(target_str)
            if not matches:
                return
            target = matches
        
        # Check if object supports this
        if not hasattr(target, 'db'):
            caller.msg(f"|r{target.name} does not support pickup toggling.|n")
            return
        
        # Get current state
        current_no_pick = target.db.no_pick if hasattr(target.db, 'no_pick') else False
        
        # Determine new state
        if state is None:
            # Toggle
            new_state = not current_no_pick
        elif state in ('on', 'yes', 'true', '1'):
            new_state = False  # "on" means allow pickup (no_pick = False)
        elif state in ('off', 'no', 'false', '0'):
            new_state = True   # "off" means prevent pickup (no_pick = True)
        else:
            caller.msg("|rState must be 'on' or 'off'.|n")
            return
        
        # Apply the state
        target.db.no_pick = new_state
        
        # Feedback
        pickup_state = "cannot" if new_state else "can"
        action = "enabled" if new_state else "disabled"
        
        caller.msg(f"|g[PICKUP TOGGLED]|n")
        caller.msg(f"|wObject:|n {target.name} (#{target.dbref})")
        caller.msg(f"|wState:|n {target.name} {pickup_state} be picked up ({action})")
        
        # Room message
        caller.location.msg_contents(
            f"{caller.key} adjusts {target.name}.",
            exclude=[caller]
        )
