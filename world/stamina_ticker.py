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
        from evennia.accounts.models import AccountDB
        
        # Get all connected accounts and their characters
        connected_accounts = AccountDB.objects.filter(db_is_connected=True)
        
        for account in connected_accounts:
            char = account.db_puppet_character
            if not char:
                continue
            
            # Create stamina component if needed
            if not hasattr(char.ndb, "stamina"):
                from commands.movement import _get_or_create_stamina
                stamina = _get_or_create_stamina(char)
            else:
                stamina = char.ndb.stamina
            
            # Update stamina
            stamina.update(self.interval)
