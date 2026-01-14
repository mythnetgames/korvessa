"""
Stamina Ticker Script

A global ticker that updates all character stamina every tick.
"""

from evennia import DefaultScript, search_object


class StaminaTicker(DefaultScript):
    """
    Global ticker that updates stamina for all connected characters.
    Runs every 1 second.
    """
    
    def at_script_creation(self):
        """Called when script is first created."""
        self.key = "stamina_ticker"
        self.desc = "Updates character stamina every tick"
        self.interval = 1  # Run every 1 second
        self.persistent = True  # Survive server restart
        self.start_delay = True  # Wait one interval before first tick
    
    def at_repeat(self):
        """Called every interval (1 second)."""
        # Get all connected characters
        from typeclasses.characters import Character
        characters = search_object(typeclass=Character)
        
        for char in characters:
            # Only update characters with accounts and stamina
            if char.has_account and hasattr(char.ndb, "stamina"):
                stamina = char.ndb.stamina
                stamina.update(self.interval)
