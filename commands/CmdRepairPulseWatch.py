"""
Repair/reattach a severed pulse watch command.

This allows characters to reattach a cut pulse watch if they have sufficient Electronics skill.
The skill check is moderate (target ~25) to allow most deckers and tech-savvy characters to succeed.
"""

from evennia import Command
from evennia.utils import evmenu


class CmdRepairPulseWatch(Command):
    """
    Repair and reattach a severed pulse watch.
    
    Usage:
        repair <watch>
        
    Reattaches a municipal pulse watch that has been cut. This requires an Electronics
    skill check. Most characters with decent electronics skills should be able to do
    this, though it carries some risk of permanently damaging the watch.
    """
    
    key = "repair"
    aliases = ["reattach", "fix"]
    locks = "cmd:all()"
    help_category = "Items"
    
    def func(self):
        """Execute repair command."""
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: repair <watch>")
            return
        
        # Get the watch object by searching inventory
        watch = caller.search(self.args.strip(), candidates=caller.contents)
        
        if not watch:
            return
        
        # Verify it's a pulse watch
        if not (hasattr(watch.db, 'is_municipal_wristpad') and watch.db.is_municipal_wristpad):
            caller.msg(f"{watch.name} is not a municipal pulse watch.")
            return
        
        # Verify it's actually cut
        if not getattr(watch.db, 'is_cut', False):
            caller.msg(f"The {watch.name} doesn't appear to be damaged.")
            return
        
        # Get electronics skill
        electronics = getattr(caller.db, 'electronics', 0) or 0
        
        # Difficulty check (25 is moderate, should usually pass)
        difficulty = 25
        
        # Simple dice roll for success
        import random
        roll = random.randint(1, 100)
        
        # Calculate effective roll with skill bonus
        effective_roll = roll + (electronics * 2)  # Electronics * 2 as bonus
        
        caller.msg(f"|y[Electronics Check: {effective_roll} vs Difficulty {difficulty}]|n")
        
        if effective_roll >= difficulty:
            # Success - reattach the watch
            self._repair_success(caller, watch)
        else:
            # Failure - damage the watch further
            self._repair_failure(caller, watch)
    
    def _repair_success(self, caller, watch):
        """Handle successful repair."""
        # Restore watch to original state
        watch.key = watch.key.replace("cut ", "")
        watch.db.is_cut = False
        watch.db.desc = "A compact wristpad with a flexible display screen. The device wraps around the forearm, its matte surface dotted with status LEDs and a small speaker grille. When activated, holographic displays project interface elements just above the screen."
        
        caller.msg("*beep* You carefully repair the Pulse watch, reattaching the severed needle and restoring its circuitry.")
        caller.location.msg_contents(
            f"*beep* {caller.key} carefully repairs their pulse watch.",
            exclude=[caller]
        )
    
    def _repair_failure(self, caller, watch):
        """Handle failed repair."""
        caller.msg(f"|r*fzzzt* Your repair attempt fails! The delicate circuitry of the {watch.name} is now beyond recovery. The device is permanently damaged.|n")
        caller.location.msg_contents(
            f"|r*fzzzt* {caller.key}'s repair attempt fails - the {watch.name} is now beyond recovery.|n",
            exclude=[caller]
        )
        
        # Destroy the watch permanently (or mark as destroyed)
        watch.db.is_broken = True
        watch.key = "broken pulse watch"
        watch.db.desc = "A destroyed municipal wristpad, its circuits fried beyond all repair. A smoking scent rises from its shattered components."
        watch.locks.add("get:false()")  # Can't even pick it up anymore
