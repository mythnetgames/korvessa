"""
Stamina Ticker Script

A global ticker that updates all character stamina every second.
Simple and robust - just calls stamina.update() for each character.
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
        self.start_delay = False  # Start immediately on first tick
    
    def at_repeat(self):
        """Called every interval (1 second)."""
        from evennia import SESSION_HANDLER
        from world.stamina import get_or_create_stamina
        
        try:
            # Get all active sessions and their puppets
            sessions = SESSION_HANDLER.get_sessions()
            
            for session in sessions:
                char = session.get_puppet()
                if not char:
                    continue
                
                try:
                    # Get or create stamina component
                    stamina = get_or_create_stamina(char)
                    if not stamina:
                        continue
                    
                    # Check if in combat - combat handles its own stamina
                    in_combat = hasattr(char.ndb, "combat_handler") and char.ndb.combat_handler
                    
                    if not in_combat:
                        # Update stamina (handles regen/drain based on movement tier)
                        stamina.update(self.interval)
                
                except Exception as e:
                    # Log errors but don't crash the ticker
                    import traceback
                    error_msg = f"[STAMINA_ERROR] {char.key if char else 'unknown'}: {str(e)}\n{traceback.format_exc()}"
                    try:
                        from evennia.comms.models import ChannelDB
                        splattercast = ChannelDB.objects.get_channel("Splattercast")
                        if splattercast:
                            splattercast.msg(error_msg)
                    except:
                        print(error_msg)
        
        except Exception as e:
            # Critical error - log it
            import traceback
            error_msg = f"[STAMINA_TICKER] CRITICAL ERROR: {str(e)}\n{traceback.format_exc()}"
            try:
                from evennia.comms.models import ChannelDB
                splattercast = ChannelDB.objects.get_channel("Splattercast")
                if splattercast:
                    splattercast.msg(error_msg)
            except:
                print(error_msg)


def start_stamina_ticker():
    """
    Ensure the stamina ticker is running.
    Call this from at_server_start() or manually.
    """
    from evennia.scripts.models import ScriptDB
    
    ticker = ScriptDB.objects.filter(db_key="stamina_ticker").first()
    if not ticker:
        ticker = StaminaTicker.create(key="stamina_ticker")
        if ticker and not ticker.is_active:
            ticker.start()
        return ticker
    elif not ticker.is_active:
        ticker.start()
    return ticker
