"""
Stamina System Admin Commands
"""

from evennia import Command


class CmdStaminaStart(Command):
    """
    Start the stamina ticker script.
    
    Usage:
        stamina_start
    
    This command creates and starts the global stamina ticker that
    updates character stamina every second.
    """
    key = "stamina_start"
    locks = "cmd:superuser()"
    help_category = "Admin"
    
    def func(self):
        from evennia.scripts.models import ScriptDB
        from world.stamina_ticker import StaminaTicker
        
        # Always remove existing ticker and create fresh one
        existing = ScriptDB.objects.filter(db_key="stamina_ticker").first()
        if existing:
            existing.stop()
            existing.delete()
            self.caller.msg("Stopped old stamina ticker.")
        
        # Create new ticker
        ticker = StaminaTicker.create(key="stamina_ticker")
        ticker.start()
        
        self.caller.msg(f"Stamina ticker started: {ticker.key}")


class CmdStaminaStatus(Command):
    """
    Check stamina system status.
    
    Usage:
        stamina_status
    
    Shows if the stamina ticker is running and details about all
    characters' stamina components.
    """
    key = "stamina_status"
    locks = "cmd:superuser()"
    help_category = "Admin"
    
    def func(self):
        from evennia.scripts.models import ScriptDB
        from evennia.accounts.models import AccountDB
        
        # Check ticker
        ticker = ScriptDB.objects.filter(db_key="stamina_ticker").first()
        self.caller.msg(f"Stamina Ticker: {'RUNNING' if ticker and ticker.is_active else 'NOT RUNNING'}")
        
        # Check connected characters
        connected = AccountDB.objects.filter(db_is_connected=True)
        self.caller.msg(f"\nConnected Accounts: {connected.count()}")
        
        for account in connected:
            char = account.db_puppet_character
            if not char:
                self.caller.msg(f"  {account.name}: No puppet character")
                continue
            
            stamina = getattr(char.ndb, "stamina", None)
            if stamina:
                self.caller.msg(f"  {char.key}: Stamina {stamina.stamina_current:.0f}/{stamina.stamina_max} - Tier: {stamina.current_tier}")
            else:
                self.caller.msg(f"  {char.key}: No stamina component")
