"""
Survival System Script

Handles periodic processing for the survival system:
- Sobering over time
- Hunger/thirst ambient messages
- Login day tracking for starvation
"""

from evennia import DefaultScript
from evennia.utils import logger
import random


class SurvivalTickerScript(DefaultScript):
    """
    A global script that processes survival effects for all online characters.
    
    Runs every 5 minutes to:
    - Process sobering for intoxicated characters
    - Send hunger/thirst ambient messages
    - Apply liver damage for heavily intoxicated characters
    """
    
    def at_script_creation(self):
        """Initialize the script."""
        self.key = "survival_ticker"
        self.desc = "Processes survival effects for online characters"
        self.interval = 300  # 5 minutes
        self.persistent = True
        self.start_delay = True
    
    def at_repeat(self):
        """Called every interval. Process all online characters."""
        try:
            from evennia import SESSION_HANDLER
            from world.survival.core import (
                process_sobering, is_hungry, is_thirsty, is_starving, is_dehydrated,
                get_random_hunger_message, get_random_thirst_message,
                get_intoxication_level, get_intoxication_tier, INTOXICATION_TIERS
            )
            
            # Get all online characters
            for session in SESSION_HANDLER.all_connected_sessions():
                if not session.puppet:
                    continue
                
                character = session.puppet
                
                # Skip NPCs and non-characters
                if not hasattr(character, 'db'):
                    continue
                
                # Process sobering
                intox_level = get_intoxication_level(character)
                if intox_level > 0:
                    result = process_sobering(character)
                    
                    # Notify on tier change
                    if result.get("tier_changed"):
                        new_tier = result.get("new_tier", "sober")
                        if new_tier == "sober":
                            character.msg("|gYou feel clear-headed again. You are sober.|n")
                        else:
                            tier_data = INTOXICATION_TIERS.get(new_tier, {})
                            desc = tier_data.get("description", new_tier)
                            character.msg(f"|yYou feel a bit less intoxicated. You are now {desc}.|n")
                    
                    # Notify on liver damage
                    if result.get("liver_damage"):
                        damage_info = result["liver_damage"]
                        if damage_info.get("damage_dealt"):
                            character.msg("|r[WARNING] Your liver aches from the alcohol abuse.|n")
                            if damage_info.get("liver_destroyed"):
                                character.msg("|R[CRITICAL] Your liver has failed!|n")
                
                # Hunger/thirst ambient messages (20% chance per tick when affected)
                if is_starving(character) and random.random() < 0.3:
                    character.msg(f"|y{get_random_hunger_message()}|n")
                elif is_hungry(character) and random.random() < 0.15:
                    character.msg(f"|y{get_random_hunger_message()}|n")
                
                if is_dehydrated(character) and random.random() < 0.3:
                    character.msg(f"|y{get_random_thirst_message()}|n")
                elif is_thirsty(character) and random.random() < 0.15:
                    character.msg(f"|y{get_random_thirst_message()}|n")
                    
        except Exception as e:
            logger.log_err(f"SurvivalTickerScript error: {e}")


def start_survival_ticker():
    """Start the survival ticker script if not already running."""
    from evennia.scripts.models import ScriptDB
    
    # Check if already running
    existing = ScriptDB.objects.filter(db_key="survival_ticker")
    if existing.exists():
        return existing.first()
    
    # Create and start the script
    from evennia import create_script
    script = create_script(
        SurvivalTickerScript,
        key="survival_ticker",
        persistent=True,
        autostart=True
    )
    return script


def stop_survival_ticker():
    """Stop the survival ticker script."""
    from evennia.scripts.models import ScriptDB
    
    scripts = ScriptDB.objects.filter(db_key="survival_ticker")
    for script in scripts:
        script.stop()
        script.delete()
