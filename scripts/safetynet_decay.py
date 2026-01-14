"""
SafetyNet Decay Script

Periodically cleans up expired posts from the SafetyNet system.
Posts older than 72 hours are automatically removed.
"""

from evennia import DefaultScript
from world.safetynet.constants import POST_DECAY_SECONDS


class SafetyNetDecayScript(DefaultScript):
    """
    A global script that periodically cleans up expired SafetyNet posts.
    
    Runs every hour to remove posts older than POST_DECAY_SECONDS (72 hours).
    """
    
    def at_script_creation(self):
        """Initialize the decay script."""
        self.key = "safetynet_decay"
        self.desc = "Cleans up expired SafetyNet posts"
        self.persistent = True
        
        # Run every hour (3600 seconds)
        self.interval = 3600
        self.start_delay = True  # Don't run immediately on creation
    
    def at_repeat(self):
        """Clean up expired posts."""
        from world.safetynet.core import get_safetynet_manager
        
        try:
            manager = get_safetynet_manager()
            if manager:
                # The cleanup happens automatically in get_posts, but we can
                # trigger it explicitly here for maintenance
                manager._cleanup_expired_posts()
        except Exception as e:
            # Log error but don't crash the script
            pass


def start_decay_script():
    """
    Ensure the decay script is running.
    Call this from server start or when setting up the system.
    
    Returns:
        The decay script instance
    """
    from evennia.scripts.models import ScriptDB
    from evennia import create_script
    
    # Check if script already exists
    existing = ScriptDB.objects.filter(db_key="safetynet_decay")
    if existing.exists():
        script = existing.first()
        if not script.is_active:
            script.start()
        return script
    
    # Create new script
    script = create_script(
        SafetyNetDecayScript,
        key="safetynet_decay",
        persistent=True,
    )
    return script
