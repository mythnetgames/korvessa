"""
Stamina Ticker Script

A global ticker that updates all character stamina every tick.
Ensures stamina regens properly when characters are idle or walking slowly.
"""

from evennia import DefaultScript


# Thirst effect multipliers
THIRST_REGEN_PENALTY = 0.75  # 25% slower regen when thirsty
DEHYDRATION_REGEN_PENALTY = 0.5  # 50% slower regen when dehydrated  
DEHYDRATION_POOL_PENALTY = 0.8  # 20% lower max pool when dehydrated

# Base regen for idle/resting characters (stamina/sec when standing still)
IDLE_REGEN_RATE = 3.0  # Will be multiplied by stat modifiers


class StaminaTicker(DefaultScript):
    """
    Global ticker that updates stamina for all connected characters.
    Runs every 1 second.
    
    This ensures:
    - Characters out of combat regenerate stamina passively
    - Movement-based stamina system works correctly
    - Thirst penalties apply as expected
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
        from evennia.comms.models import ChannelDB
        
        splattercast = None
        try:
            splattercast = ChannelDB.objects.get_channel("Splattercast")
        except:
            pass
        
        try:
            # Get all active sessions and their puppets
            sessions = SESSION_HANDLER.get_sessions()
            
            for session in sessions:
                char = session.get_puppet()
                if not char:
                    continue
                
                try:
                    # Get or create stamina component
                    stamina = getattr(char.ndb, "stamina", None)
                    if stamina is None:
                        from commands.movement import _get_or_create_stamina
                        stamina = _get_or_create_stamina(char)
                    
                    if not stamina:
                        continue
                    
                    # Store values before update
                    stamina_before = stamina.stamina_current
                    
                    # Check if in combat - if so, skip natural regen
                    in_combat = hasattr(char.ndb, "combat_handler") and char.ndb.combat_handler
                    
                    # Apply thirst modifiers
                    regen_mult, pool_mult = self._get_thirst_modifiers(char)
                    
                    # Cap stamina at effective max if dehydrated
                    if pool_mult < 1.0:
                        effective_max = int(stamina.stamina_max * pool_mult)
                        if stamina.stamina_current > effective_max:
                            stamina.stamina_current = float(effective_max)
                    
                    # Update stamina via movement system
                    # This handles movement-based drain/regen
                    stamina.update(self.interval, char)
                    
                    # For characters NOT in combat and not moving, apply bonus idle regen
                    if not in_combat:
                        # Only apply if stamina is not already at max
                        if stamina.stamina_current < stamina.stamina_max:
                            # Apply regen based on CON
                            con_val = getattr(char, "con", 10) or 10
                            # Scale CON (8-16) to 0-100, then normalize
                            con_scaled = int((con_val - 8) * (100.0 / 7.0))
                            
                            # Base idle regen + CON bonus
                            idle_regen = IDLE_REGEN_RATE + (con_scaled * 0.015)
                            
                            # Apply thirst penalty
                            idle_regen *= regen_mult
                            
                            # Apply to stamina (this is passive regen, not movement-related)
                            stamina.stamina_current = min(
                                stamina.stamina_current + idle_regen * self.interval,
                                stamina.stamina_max
                            )
                    
                    # Track delta for debugging
                    stamina_after = stamina.stamina_current
                    delta = stamina_after - stamina_before
                    
                    # Only log if there's a significant change or if there's an issue
                    if delta != 0 or stamina.stamina_current == 0:
                        if splattercast:
                            in_combat_str = "(COMBAT)" if in_combat else ""
                            splattercast.msg(
                                f"[STAMINA] {char.key} {in_combat_str}: {stamina_before:.1f} -> {stamina_after:.1f} "
                                f"(delta={delta:+.2f}), tier={stamina.current_tier.name if hasattr(stamina.current_tier, 'name') else stamina.current_tier}, "
                                f"max={stamina.stamina_max}"
                            )
                
                except Exception as e:
                    import traceback
                    if splattercast:
                        splattercast.msg(f"[STAMINA_ERROR] {char.key}: {e}")
                        splattercast.msg(f"[STAMINA_TRACEBACK] {traceback.format_exc()}")
        
        except Exception as e:
            import traceback
            if splattercast:
                splattercast.msg(f"[STAMINA_TICKER] CRITICAL ERROR: {e}")
                splattercast.msg(f"[STAMINA_TICKER] {traceback.format_exc()}")
    
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
