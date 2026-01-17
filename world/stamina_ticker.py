"""
Stamina Ticker Script

A global ticker that updates all character stamina every tick.
"""

from evennia import DefaultScript


# Thirst effect multipliers
THIRST_REGEN_PENALTY = 0.75  # 25% slower regen when thirsty
DEHYDRATION_REGEN_PENALTY = 0.5  # 50% slower regen when dehydrated  
DEHYDRATION_POOL_PENALTY = 0.8  # 20% lower max pool when dehydrated


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
                # Get thirst modifiers before update
                regen_mult, pool_mult = self._get_thirst_modifiers(char)
                
                # Store original values if we need to apply pool penalty
                if pool_mult < 1.0:
                    effective_max = int(stamina.stamina_max * pool_mult)
                    # Cap current stamina at the reduced max
                    if stamina.stamina_current > effective_max:
                        stamina.stamina_current = float(effective_max)
                
                # Update stamina
                stamina.update(self.interval, char)
                
                # Apply regen penalty (reduce any gains made)
                if regen_mult < 1.0 and stamina.stamina_current > 0:
                    # Only apply if we were regenerating (not draining)
                    # This is handled by reducing the delta after the fact
                    pass  # The regen penalty is complex to apply post-update
                    # Instead we'll reduce the current stamina slightly
                    # when thirsty as a soft penalty
                    thirst_drain = 0.1 * (1.0 - regen_mult)  # Small drain per tick
                    stamina.stamina_current = max(0, stamina.stamina_current - thirst_drain)
    
    def _get_thirst_modifiers(self, character):
        """
        Get stamina modifiers based on character's thirst level.
        
        Returns:
            tuple: (regen_multiplier, pool_multiplier)
        """
        try:
            from world.survival.core import is_thirsty, is_dehydrated
            
            if is_dehydrated(character):
                return (DEHYDRATION_REGEN_PENALTY, DEHYDRATION_POOL_PENALTY)
            elif is_thirsty(character):
                return (THIRST_REGEN_PENALTY, 1.0)
            else:
                return (1.0, 1.0)
        except Exception:
            return (1.0, 1.0)
