"""
Test Dummy NPC - Training target for combat testing.

A specialized NPC that:
- Has adjustable skills via commands
- Auto-revives and heals when killed
- Stops attacking once dead
- Useful for testing and training combat mechanics
"""

from typeclasses.npcs import NPC
from evennia.utils.utils import delay
from evennia.comms.models import ChannelDB
from world.combat.constants import SPLATTERCAST_CHANNEL, NDB_COMBAT_HANDLER


class TestDummy(NPC):
    """
    A training dummy NPC designed for combat testing and training.
    
    Features:
    - Adjustable combat stats (body, dexterity, reflexes, technique)
    - Auto-revives 5 seconds after death with full healing
    - Stops attacking/defending when dead
    - Shows statistics
    """
    
    def at_object_creation(self):
        """Initialize test dummy attributes."""
        super().at_object_creation()
        
        # Mark as test dummy
        self.db.is_test_dummy = True
        
        # Default combat stats (can be adjusted)
        self.db.body = 3
        self.db.dexterity = 3
        self.db.reflexes = 3
        self.db.technique = 3
        
        # Medical/health stats
        self.db.smarts = 1
        self.db.willpower = 1
        self.db.edge = 1
        self.db.empathy = 1
        
        # Test dummy specific
        self.db.is_active = True  # Whether dummy is actively fighting
        
        # Set appearance
        self.db.desc = """
This is a combat training dummy - a humanoid figure designed to withstand
physical punishment. It has articulated joints and weighted limbs for realistic
combat practice. When struck, it shows no pain or fatigue, simply resetting
to its neutral stance between attacks.
        """.strip()
    
    def at_init(self):
        """Called when dummy is loaded."""
        super().at_init()
        self.db.is_active = True
    
    def at_death(self):
        """
        Handle dummy death - auto-revive after 5 seconds instead of normal death.
        """
        # Mark as inactive (stops attacking)
        self.db.is_active = False
        
        # Remove from combat immediately
        if hasattr(self.ndb, NDB_COMBAT_HANDLER):
            handler = getattr(self.ndb, NDB_COMBAT_HANDLER, None)
            if handler:
                try:
                    handler.remove_combatant(self)
                except:
                    pass
            try:
                delattr(self.ndb, NDB_COMBAT_HANDLER)
            except:
                pass
        
        # Show death message
        if self.location:
            self.location.msg_contents(f"|y{self.key} slumps to the ground, mechanisms whirring down.|n")
        
        try:
            splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
            splattercast.msg(f"TEST_DUMMY_DEATH: {self.key} has been defeated - auto-revive in 5 seconds")
        except:
            pass
        
        # Schedule auto-revive
        delay(5.0, self._auto_revive)
    
    def _auto_revive(self):
        """Auto-revive and heal the test dummy."""
        from evennia.comms.models import ChannelDB
        
        if not self.location:
            return  # Dummy has been deleted
        
        try:
            splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
            splattercast.msg(f"TEST_DUMMY_REVIVE: {self.key} is reviving")
        except:
            pass
        
        # Mark as active again
        self.db.is_active = True
        
        # Reset placement
        self.override_place = None
        
        # Full heal - reset all organ HP
        if hasattr(self, 'medical_state') and self.medical_state:
            for organ in self.medical_state.organs.values():
                organ.current_hp = organ.max_hp
                organ.conditions.clear()
        
        # Clear death state
        self.remove_death_state()
        
        # Clear override placement (was showing as dead)
        self.override_place = None
        
        # Show revive message
        self.location.msg_contents(f"|g{self.key} hums back to life, mechanisms clicking and whirring into motion.|n")
    
    def is_dead(self):
        """Check if dummy is dead (not active)."""
        return not self.db.is_active
    
    def get_combat_stats(self):
        """Get all combat stats as a dict."""
        return {
            "body": self.db.body or 3,
            "dexterity": self.db.dexterity or 3,
            "reflexes": self.db.reflexes or 3,
            "technique": self.db.technique or 3,
        }
    
    def get_dummy_status(self):
        """Get status string for examination."""
        status = f"\n|wCombat Stats:|n\n"
        stats = self.get_combat_stats()
        for stat, value in stats.items():
            status += f"  {stat.capitalize()}: |w{value}|n\n"
        
        status += f"\n|wStatus:|n "
        if self.db.is_active:
            status += "|gActive|n - Ready for combat"
        else:
            status += "|rInactive|n - Preparing to revive"
        
        return status
    
    def return_appearance(self, looker, **kwargs):
        """Custom appearance showing test dummy info."""
        appearance = super().return_appearance(looker, **kwargs)
        appearance += self.get_dummy_status()
        return appearance
