"""
Stamina Ticker Script

A global ticker that updates all character stamina every tick.
"""

from evennia import DefaultScript


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
        from evennia import SESSION_HANDLER
        
        # Get all active sessions and their puppets
        for session in SESSION_HANDLER.get_sessions():
            char = session.get_puppet()
            if not char:
                continue
            
            # Get or create stamina component
            stamina = getattr(char.ndb, "stamina", None)
            if stamina is None:
                from commands.movement import _get_or_create_stamina
                stamina = _get_or_create_stamina(char)
            
            if stamina:
                # Update stamina
                stamina.update(self.interval)
