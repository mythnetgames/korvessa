"""
Follow System Handler

This script manages the follow system by:
1. Detecting when characters move
2. Moving their followers to the same location
3. Cleaning up stale follow relationships
"""

from evennia.scripts.scripts import DefaultScript


class FollowScript(DefaultScript):
    """
    Global follow system script that handles follower tracking and movement.
    This is a persistent script that coordinates all following relationships.
    """
    
    def at_script_creation(self):
        """Initialize the follow script."""
        self.db.followers = {}  # Format: {leader_dbref: [follower_dbrefs]}
    
    def register_follow(self, leader, follower):
        """Register a follower relationship."""
        leader_ref = leader.dbref
        if leader_ref not in self.db.followers:
            self.db.followers[leader_ref] = []
        
        follower_ref = follower.dbref
        if follower_ref not in self.db.followers[leader_ref]:
            self.db.followers[leader_ref].append(follower_ref)
    
    def unregister_follow(self, leader, follower):
        """Unregister a follower relationship."""
        leader_ref = leader.dbref
        follower_ref = follower.dbref
        
        if leader_ref in self.db.followers:
            if follower_ref in self.db.followers[leader_ref]:
                self.db.followers[leader_ref].remove(follower_ref)
            
            # Clean up empty lists
            if not self.db.followers[leader_ref]:
                del self.db.followers[leader_ref]


def get_follow_script():
    """Get or create the global follow script."""
    from evennia.scripts.models import ScriptDB
    from evennia import create_script
    
    # Try to find existing script
    script = ScriptDB.objects.filter(db_key="follow_system").first()
    if script:
        return script
    
    # Create new script
    script = create_script(
        FollowScript,
        key="follow_system",
        persistent=True,
        desc="Global follow system handler"
    )
    return script


def handle_character_move(character, new_location, original_location=None):
    """
    Called when a character moves to handle follower logic.
    
    Args:
        character: The character moving
        new_location: The location they're moving to
        original_location: The location they're moving from (if None, uses character's current location)
    """
    # Determine the location to check for followers
    check_location = original_location if original_location else character.location
    
    # Get all followers from NDB
    followers_to_move = []
    
    # Check all characters in the original location for followers
    if check_location:
        for obj in check_location.contents:
            if hasattr(obj, 'ndb') and hasattr(obj.ndb, 'following'):
                if obj.ndb.following == character:
                    followers_to_move.append(obj)
    
    # Move each follower to the new location
    for follower in followers_to_move:
        # Don't move if they can't move
        if not follower.location:
            continue
        
        # Attempt to move the follower
        try:
            follower.move_to(new_location, quiet=True)
            # Silent follow - no message spam
        except Exception as e:
            # Log but don't break
            pass
