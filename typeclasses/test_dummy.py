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

# All stats that can be set on the test dummy
DUMMY_STATS = [
    "body", "ref", "dex", "tech", "smrt", "will", "edge", "emp"
]

# All skills that can be set on the test dummy
DUMMY_SKILLS = [
    "chemical", "modern_medicine", "holistic_medicine", "surgery", "science",
    "dodge", "blades", "pistols", "rifles", "melee", "brawling", "martial_arts",
    "grappling", "snooping", "stealing", "hiding", "sneaking", "disguise",
    "tailoring", "tinkering", "manufacturing", "cooking", "forensics",
    "decking", "electronics", "mercantile", "streetwise", "paint_draw_sculpt",
    "instrument", "athletics"
]


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
        
        # Default stats (can be adjusted)
        self.body = 3
        self.ref = 3
        self.dex = 3
        self.tech = 3
        self.smrt = 1
        self.will = 1
        self.edge = 1
        self.emp = 2  # Auto-calculated as edge + will, but set explicitly
        
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
    
    def at_object_delete(self):
        """Clean up when test dummy is deleted."""
        try:
            # Cancel any pending auto-revive callbacks
            if hasattr(self.ndb, '_revive_callback'):
                try:
                    callback = self.ndb._revive_callback
                    # Try different methods to cancel depending on callback type
                    if hasattr(callback, 'remove'):
                        callback.remove()
                    elif hasattr(callback, 'cancel'):
                        callback.cancel()
                    # Clear the reference
                    delattr(self.ndb, '_revive_callback')
                except Exception:
                    pass  # Callback may have already fired or be in an invalid state
            
            # Clear any held items from hands to break circular references
            if hasattr(self, 'hands'):
                try:
                    hands = self.hands
                    for hand in hands:
                        if hands[hand]:
                            hands[hand] = None
                    self.hands = hands
                except Exception:
                    pass
            
            # Clear medical state reference if it exists
            if hasattr(self, 'medical_state'):
                try:
                    self.medical_state = None
                except Exception:
                    pass
        except Exception:
            pass  # Don't let cleanup errors prevent deletion
        
        # Call parent's at_object_delete for normal cleanup (handles NPC registry)
        try:
            super().at_object_delete()
        except Exception:
            pass  # Don't let parent cleanup errors prevent deletion
    
    def delete(self):
        """Override delete to ensure cleanup happens and deletion succeeds."""
        # First, remove ourselves from any holder's hands
        if hasattr(self, 'location') and self.location:
            holder = self.location
            if hasattr(holder, 'hands'):
                try:
                    hands = holder.hands
                    for hand, item in hands.items():
                        if item == self:
                            hands[hand] = None
                    holder.hands = hands
                except Exception:
                    pass
        
        try:
            # Remove death state if applied (prevents deletion issues)
            self.remove_death_state()
        except Exception:
            pass
        
        try:
            # Clear all cmdsets that might interfere
            self.cmdset.clear()
        except Exception:
            pass
        
        try:
            # Perform at_object_delete cleanup explicitly
            self.at_object_delete()
        except Exception:
            pass
        
        try:
            # Reset to active state to clear any death-related flags
            self.db.is_active = True
            self.db.is_dead = False
            self.db.is_unconscious = False
        except Exception:
            pass
        
        try:
            # Force location to None first
            self.location = None
        except Exception:
            pass
        
        try:
            # Call the parent delete
            result = super().delete()
            if result:
                return True
        except Exception:
            pass
        
        # If parent delete fails, try to force it anyway
        try:
            from evennia.objects.models import ObjectDB
            ObjectDB.objects.filter(pk=self.pk).delete()
            return True
        except Exception:
            return False
    
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
        # Store the callback handle so we can cancel it if the dummy is deleted
        callback = delay(5.0, self._auto_revive)
        self.ndb._revive_callback = callback
    
    def _auto_revive(self):
        """Auto-revive and heal the test dummy using full_heal."""
        from evennia.comms.models import ChannelDB
        from world.medical.utils import full_heal
        from world.medical.script import stop_medical_script
        
        if not self.location:
            return  # Dummy has been deleted
        
        try:
            splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
            splattercast.msg(f"TEST_DUMMY_REVIVE: {self.key} is reviving")
        except:
            splattercast = None
        
        # Stop any running medical script first
        try:
            stop_medical_script(self)
        except:
            pass
        
        # Use full_heal to properly reset everything
        try:
            full_heal(self)
            if splattercast:
                splattercast.msg(f"TEST_DUMMY_HEALED: {self.key} fully healed")
        except Exception as e:
            if splattercast:
                splattercast.msg(f"TEST_DUMMY_HEAL_ERROR: {e}")
            # Manual fallback healing
            if hasattr(self, 'medical_state') and self.medical_state:
                self.medical_state.conditions.clear()
                self.medical_state.blood_level = 100.0
                self.medical_state.pain_level = 0.0
                self.medical_state.consciousness = 1.0
                for organ in self.medical_state.organs.values():
                    organ.current_hp = organ.max_hp
                    organ.conditions.clear()
                self.save_medical_state()
        
        # Mark as active again
        self.db.is_active = True
        
        # Clear death state flags
        if hasattr(self.ndb, 'death_processed'):
            self.ndb.death_processed = False
        if hasattr(self.db, 'death_processed'):
            del self.db.death_processed
        
        # Reset placement
        self.override_place = None
        
        # Remove death cmdset and restore normal one
        try:
            self.remove_death_state()
        except:
            pass
        
        # Show revive message
        self.location.msg_contents(f"|g{self.key} hums back to life, mechanisms clicking and whirring into motion.|n")
    
    def is_dead(self):
        """Check if dummy is dead (not active)."""
        return not self.db.is_active
    
    def get_combat_stats(self):
        """Get all combat stats as a dict."""
        stats = {}
        for stat in DUMMY_STATS:
            value = getattr(self.db, stat, None)
            if value is not None and value > 0:
                stats[stat] = value
        return stats
    
    def get_skills(self):
        """Get all skills above 0 as a dict."""
        skills = {}
        for skill in DUMMY_SKILLS:
            value = getattr(self.db, skill, None)
            if value is not None and value > 0:
                skills[skill] = value
        return skills
    
    def get_dummy_status(self):
        """Get status string for examination."""
        status = ""
        
        # Combat stats
        stats = self.get_combat_stats()
        if stats:
            status += f"\n|wCombat Stats:|n\n"
            for stat, value in sorted(stats.items()):
                status += f"  {stat.capitalize()}: |w{value}|n\n"
        
        # Skills
        skills = self.get_skills()
        if skills:
            status += f"\n|wSkills:|n\n"
            for skill, value in sorted(skills.items()):
                # Format skill name nicely
                display_name = skill.replace("_", " ").title()
                status += f"  {display_name}: |c{value}|n\n"
        
        # Activity status
        status += f"\n|wStatus:|n "
        if self.db.is_active:
            status += "|gActive|n - Ready for combat"
        else:
            status += "|rInactive|n - Preparing to revive"
        
        # Health info if available
        if hasattr(self, 'medical_state') and self.medical_state:
            blood = getattr(self.medical_state, 'blood_level', 100)
            pain = getattr(self.medical_state, 'pain_level', 0)
            conditions = len(getattr(self.medical_state, 'conditions', []))
            status += f"\n|wHealth:|n Blood: |r{blood:.0f}%|n | Pain: |y{pain:.0f}|n | Conditions: {conditions}"
        
        return status
    
    def return_appearance(self, looker, **kwargs):
        """Custom appearance showing test dummy info."""
        appearance = super().return_appearance(looker, **kwargs)
        appearance += self.get_dummy_status()
        return appearance

    def msg(self, text=None, from_obj=None, session=None, **kwargs):
        """
        Override msg to bypass death filtering and always allow at_msg_receive to be called.
        Test dummies need to hear 'reset' even when dead.
        """
        # Skip the Character death filtering, go straight to DefaultObject.msg
        from evennia.objects.objects import DefaultObject
        return DefaultObject.msg(self, text=text, from_obj=from_obj, session=session, **kwargs)

    def at_msg_receive(self, msg, from_obj=None, **kwargs):
        """React to messages in the room. Heal and reset on 'reset', robust to accents and Evennia Msg objects."""
        import unicodedata
        import re
        
        # Log ALL messages to see if this is being called
        try:
            from evennia.comms.models import ChannelDB
            splattercast = ChannelDB.objects.get_channel('Splattercast')
            if splattercast:
                splattercast.msg(f"[DUMMY at_msg_receive] Called with msg={repr(msg)[:100]}, from_obj={from_obj}")
        except Exception:
            pass

        if not msg:
            return
        
        # Always convert to string, handle Evennia Msg objects and raw text
        try:
            if hasattr(msg, 'message'):
                msg_str = str(msg.message)
            elif hasattr(msg, 'text'):
                msg_str = str(msg.text)
            elif isinstance(msg, str):
                msg_str = msg
            else:
                msg_str = str(msg)
        except Exception:
            msg_str = str(msg)
        
        # Strip Evennia color codes properly (|r, |g, |n, etc.) - NOT individual letters!
        msg_str = re.sub(r'\|[a-zA-Z0-9/=_]', '', msg_str)
        msg_str = msg_str.strip().lower()
        
        # Normalize to NFC then NFD, then strip accents
        msg_str = unicodedata.normalize('NFC', msg_str)
        msg_nfd = unicodedata.normalize('NFD', msg_str)
        msg_normalized = ''.join(c for c in msg_nfd if unicodedata.category(c) != 'Mn')

        # Debug: show what the dummy is receiving
        try:
            from evennia.comms.models import ChannelDB
            splattercast = ChannelDB.objects.get_channel('Splattercast')
            if splattercast:
                splattercast.msg(f"[DUMMY DEBUG] msg_str='{msg_str}' | normalized='{msg_normalized}' | contains 'reset'={('reset' in msg_normalized)}")
        except Exception:
            pass

        if "reset" in msg_normalized:
            # Remove from combat if needed
            handler = getattr(self.ndb, NDB_COMBAT_HANDLER, None)
            if handler:
                try:
                    handler.remove_combatant(self)
                except Exception:
                    pass
                try:
                    delattr(self.ndb, NDB_COMBAT_HANDLER)
                except Exception:
                    pass
            # Revive if dead or unconscious
            if self.db.is_dead or self.db.is_unconscious:
                self.db.is_dead = False
                self.db.is_unconscious = False
                self.db.health = self.db.max_health if hasattr(self.db, 'max_health') else 100
                self.location.msg_contents(f"|g{self.key} is revived!|n")
            # Heal fully
            try:
                from world.medical.utils import full_heal
                full_heal(self)
            except Exception:
                pass
            self.db.is_active = True
            # Announce and update appearance
            if self.location:
                self.location.msg_contents(f"|g{self.key} resets and returns to pristine condition.|n")
            # Force update of status/appearance for all lookers
            for obj in self.location.contents:
                if hasattr(obj, 'msg'):
                    obj.msg(self.return_appearance(obj))
        super().at_msg_receive(msg, from_obj=from_obj, **kwargs)
    
    def at_object_receive(self, moved_object, source):
        """When the dummy receives an item, immediately free its hands (not full heal), but keep the item."""
        result = super().at_object_receive(moved_object, source)
        # Free all hands (set to None)
        if hasattr(self, 'hands'):
            hands = self.hands
            for hand in hands:
                hands[hand] = None
            self.hands = hands
        return result
    
    def at_pre_move(self, destination, **kwargs):
        """
        Called before the dummy moves.
        Always remove death state to allow movement regardless of destination.
        """
        # Always remove death state before any move to bypass cmdset movement restrictions
        if hasattr(self, 'is_dead') and self.is_dead():
            try:
                self.remove_death_state()
            except Exception:
                pass
        
        return True  # Always allow movement for test dummies
    
    def move_to(self, destination, quiet=False, emit_to_obj=None, use_destination=True, to_none=False, move_type="move", **kwargs):
        """
        Override move_to to force movement even if cmdset restrictions normally prevent it.
        This ensures test dummies can always be dropped/moved even when in death state.
        """
        # Remove death state and cmdset restrictions before moving
        if hasattr(self, 'is_dead') and self.is_dead():
            try:
                self.remove_death_state()
            except Exception:
                pass
        
        # Clear any cmdset that might block movement
        try:
            self.cmdset.remove_default()
        except Exception:
            pass
        
        # Also clear the holder's reference to this in hands if being dropped
        if hasattr(self, 'location') and self.location:
            holder = self.location
            if hasattr(holder, 'hands'):
                try:
                    hands = holder.hands
                    for hand, item in hands.items():
                        if item == self:
                            hands[hand] = None
                    holder.hands = hands
                except Exception:
                    pass
        
        # Perform the move - bypass normal restrictions by setting location directly
        try:
            old_location = self.location
            self.location = destination
            
            # Emit arrival/departure messages if not quiet
            if not quiet:
                if old_location and hasattr(old_location, 'msg_contents'):
                    old_location.msg_contents(f"{self.key} is moved away.", exclude=[self])
                if destination and hasattr(destination, 'msg_contents'):
                    destination.msg_contents(f"{self.key} arrives.", exclude=[self])
            
            return True
        except Exception:
            return False
