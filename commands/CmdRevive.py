"""
Admin Command: Revive

Allows admins to revive dead characters, fully healing them and restoring them to life.
"""

from evennia import Command
from evennia.utils.search import search_object


class CmdRevive(Command):
    """
    Revive a dead character, fully healing them.
    
    Usage:
        @revive <character>
        @revive here          - Revive all dead characters in the room
    
    This command fully heals the target, clears all medical conditions,
    restores all organs, and removes death/unconscious states.
    
    Examples:
        @revive bob           - Revive bob
        @revive here          - Revive everyone dead in this room
    """
    key = "@revive"
    aliases = ["revive"]
    locks = "cmd:perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        """Execute the revive command."""
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: @revive <character> or @revive here")
            return
        
        target_name = self.args.strip()
        
        # Handle 'here' keyword - revive all dead in the room
        if target_name.lower() == "here":
            if not caller.location:
                caller.msg("|rYou have no location.|n")
                return
            
            from typeclasses.characters import Character
            dead_chars = [
                obj for obj in caller.location.contents 
                if isinstance(obj, Character) and self._is_dead_or_needs_revive(obj)
            ]
            
            if not dead_chars:
                caller.msg("|yNo dead characters found in this location.|n")
                return
            
            for char in dead_chars:
                self._revive_character(char)
            
            caller.msg(f"|gRevived {len(dead_chars)} character(s) in {caller.location.key}.|n")
            return
        
        # Find the target character
        target = caller.search(target_name, global_search=True)
        if not target:
            return
        
        # Check if target is a character
        from typeclasses.characters import Character
        if not isinstance(target, Character):
            caller.msg(f"|r{target.key} is not a character.|n")
            return
        
        # Check if target is actually dead or needs revival
        if not self._is_dead_or_needs_revive(target):
            caller.msg(f"|y{target.key} is not dead.|n")
            # Offer to heal them anyway
            caller.msg(f"|yUse |w@heal {target.key}|y to heal them if injured.|n")
            return
        
        # Revive the character
        self._revive_character(target)
        caller.msg(f"|g✓ {target.key} has been revived and fully healed.|n")
    
    def _is_dead_or_needs_revive(self, target):
        """
        Check if a character is dead or has death-related flags that need clearing.
        
        More robust than just is_dead() - catches edge cases where death flags
        are set but medical state might not reflect it.
        """
        # Check standard is_dead()
        if target.is_dead():
            return True
        
        # Check for death_processed flag
        if getattr(target.db, 'death_processed', False):
            return True
        
        if hasattr(target, 'ndb') and getattr(target.ndb, 'death_processed', False):
            return True
        
        # Check for death-related override_place
        if hasattr(target, 'override_place') and target.override_place:
            place_str = str(target.override_place).lower()
            if 'deceased' in place_str or 'dead' in place_str or 'motionless' in place_str:
                return True
        
        # Check for death curtain pending
        if hasattr(target, 'ndb') and getattr(target.ndb, 'death_curtain_pending', False):
            return True
        
        return False
    
    def _revive_character(self, target):
        """
        Revive a dead character.
        
        Args:
            target: The character to revive
        """
        from world.medical.utils import full_heal
        
        # Full heal restores everything and clears death flags
        full_heal(target)
        
        # Additional cleanup for edge cases
        
        # Clear death-related db flags
        if hasattr(target.db, 'death_processed'):
            del target.db.death_processed
        
        # Clear any death curtain pending flags
        if hasattr(target.ndb, 'death_curtain_pending'):
            del target.ndb.death_curtain_pending
        
        # Clear override place if it mentions death
        if hasattr(target, 'override_place') and target.override_place:
            if 'deceased' in str(target.override_place).lower() or 'dead' in str(target.override_place).lower():
                target.override_place = None
        
        # Stop any death progression scripts
        try:
            from evennia.scripts.models import ScriptDB
            death_scripts = ScriptDB.objects.filter(
                db_key__icontains="death_progression",
                db_obj=target
            )
            for script in death_scripts:
                script.stop()
        except Exception:
            pass
        
        # Notify the revived character
        target.msg("|g[REVIVED] You have been brought back from the dead by an admin.|n")
        
        # Notify the room
        if target.location:
            target.location.msg_contents(
                f"|g{target.key} has been revived!|n",
                exclude=[target]
            )
