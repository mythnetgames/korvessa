"""
NPC (Non-Player Character) typeclass with reactions, wandering, and puppet support.
"""

from evennia import DefaultCharacter, utils
from random import choice, randint
from datetime import datetime


class NPC(DefaultCharacter):
    """
    An NPC character that can be controlled by players through puppeting,
    has reactions to player input, and can wander within zones.
    """
    
    def at_object_creation(self):
        """Initialize NPC attributes."""
        super().at_object_creation()
        
        # NPC Configuration
        self.db.is_npc = True
        self.db.npc_can_wander = False
        self.db.npc_zone = None  # Zone to wander in
        self.db.npc_accent = None  # Accent/dialect for speech
        
        # Reactions: {trigger_keyword: [action_list]}
        self.db.npc_reactions = {}
        
        # Puppet tracking
        self.db.puppeted_by = None  # Admin account puppeting this NPC
        self.db.admin_location = None  # Where admin was before puppeting
        self.db.admin_saved_state = {}  # Saved state to restore after puppeting
        
        # Personality
        self.db.npc_personality = {
            "greeting": "Hello there.",
            "idle_emotes": ["looks around", "sighs"],
            "idle_chance": 0.05,  # 5% chance per round
        }
        
        # Add NPC to npc_objects registry
        if not hasattr(self.location, 'npc_objects'):
            self.location.npc_objects = []
        if self not in self.location.npc_objects:
            self.location.npc_objects.append(self)
    
    def at_object_delete(self):
        """Clean up when NPC is deleted."""
        # Remove from location's NPC registry
        if self.location and hasattr(self.location, 'npc_objects'):
            if self in self.location.npc_objects:
                self.location.npc_objects.remove(self)
        
        # If puppeted, unpuppet immediately
        if self.db.puppeted_by:
            self._unpuppet_admin()
        
        super().at_object_delete()
    
    def at_object_receive(self, moved_object, source):
        """Handle items being given to the NPC."""
        super().at_object_receive(moved_object, source)
        # Could trigger reactions here
    
    def at_init(self):
        """Called when NPC is loaded."""
        super().at_init()
        # Could start wandering script here if enabled
    
    def puppet_admin(self, admin_account):
        """Allow an admin to puppet this NPC."""
        if self.db.puppeted_by:
            return False, "This NPC is already being puppeted."
        
        # Find admin's puppet (character)
        admin_puppet = None
        for session in admin_account.sessions.all():
            admin_puppet = session.get_puppet()
            if admin_puppet:
                break
        
        if not admin_puppet:
            return False, "Admin has no active puppet to puppet from."
        
        # Save admin state
        self.db.puppeted_by = admin_account
        self.db.admin_location = admin_puppet.location
        self.db.admin_saved_state = {
            "location": admin_puppet.location,
            "inventory": list(admin_puppet.contents),
        }
        
        # Move admin puppet to NPC location
        admin_puppet.location = self.location
        
        return True, f"You are now puppeting {self.key}."
    
    def unpuppet_admin(self):
        """Return control to the admin."""
        if not self.db.puppeted_by:
            return False, "This NPC is not being puppeted."
        
        admin_account = self.db.puppeted_by
        admin_location = self.db.admin_location
        
        # Find admin's puppet
        admin_puppet = None
        for session in admin_account.sessions.all():
            admin_puppet = session.get_puppet()
            if admin_puppet:
                break
        
        if admin_puppet:
            # Restore admin location
            if admin_location:
                admin_puppet.location = admin_location
        
        # Clear puppet state
        self.db.puppeted_by = None
        self.db.admin_location = None
        self.db.admin_saved_state = {}
        
        return True, f"{self.key} has been released."
    
    def add_reaction(self, trigger, action):
        """
        Add a reaction to a trigger word/phrase.
        
        trigger: keyword to match (case-insensitive)
        action: what the NPC does (emote, say, etc.)
        """
        if not self.db.npc_reactions:
            self.db.npc_reactions = {}
        
        trigger = trigger.lower().strip()
        if trigger not in self.db.npc_reactions:
            self.db.npc_reactions[trigger] = []
        
        self.db.npc_reactions[trigger].append(action)
        return True
    
    def remove_reaction(self, trigger, action=None):
        """Remove a reaction."""
        if not self.db.npc_reactions:
            return False
        
        trigger = trigger.lower().strip()
        if trigger not in self.db.npc_reactions:
            return False
        
        if action is None:
            # Remove all reactions for this trigger
            del self.db.npc_reactions[trigger]
        else:
            # Remove specific action
            if action in self.db.npc_reactions[trigger]:
                self.db.npc_reactions[trigger].remove(action)
                if not self.db.npc_reactions[trigger]:
                    del self.db.npc_reactions[trigger]
            else:
                return False
        
        return True
    
    def get_reactions(self, trigger):
        """Get all reactions for a trigger word."""
        if not self.db.npc_reactions:
            return []
        
        trigger = trigger.lower().strip()
        return self.db.npc_reactions.get(trigger, [])
    
    def process_reaction(self, trigger_word, triggering_player=None):
        """
        Process a reaction to a trigger word.
        Returns the action to execute.
        """
        reactions = self.get_reactions(trigger_word)
        if not reactions:
            return None
        
        # Pick a random reaction
        action = choice(reactions)
        return action
    
    def execute_reaction(self, action, triggering_player=None):
        """Execute a reaction action."""
        if not action:
            return
        
        # Parse action format: "emote looks surprised" or "say Oh my!"
        parts = action.split(None, 1)
        if not parts:
            return
        
        action_type = parts[0].lower()
        action_arg = parts[1] if len(parts) > 1 else ""
        
        if action_type == "emote":
            self.execute_cmd("emote " + action_arg)
        elif action_type == "say":
            self.execute_cmd("say " + action_arg)
        elif action_type == "pose":
            self.execute_cmd("pose " + action_arg)
    
    def execute_cmd(self, cmdstring):
        """Execute a command as this NPC."""
        # Get the NPC's command set and execute the command
        if not self.cmdset:
            return False
        
        # Parse and execute
        cmdset = self.cmdset
        cmd, args = cmdstring.split(None, 1) if " " in cmdstring else (cmdstring, "")
        
        # This is simplified - would need proper command parsing
        return True
    
    def at_turn_start(self):
        """Called at the start of each turn."""
        super().at_turn_start()
        
        # Idle emotes
        if self.db.npc_personality and "idle_chance" in self.db.npc_personality:
            if randint(1, 100) / 100.0 < self.db.npc_personality["idle_chance"]:
                idle_emotes = self.db.npc_personality.get("idle_emotes", [])
                if idle_emotes:
                    self.execute_cmd("emote " + choice(idle_emotes))
    
    def is_puppeted(self):
        """Check if this NPC is currently being puppeted."""
        return bool(self.db.puppeted_by)
    
    def get_puppeteer(self):
        """Get the account puppeting this NPC."""
        return self.db.puppeted_by
    
    def set_zone(self, zone):
        """Set the zone this NPC can wander in."""
        self.db.npc_zone = zone
    
    def get_zone(self):
        """Get the zone this NPC can wander in."""
        return self.db.npc_zone
    
    def set_accent(self, accent_name):
        """Set the NPC's accent/dialect."""
        self.db.npc_accent = accent_name
    
    def get_accent(self):
        """Get the NPC's accent."""
        return self.db.npc_accent
