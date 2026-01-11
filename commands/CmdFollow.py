"""
Follow Command

Allows players to follow other characters. When a player follows someone,
they will automatically move to the same room when the leader moves.
"""

from evennia import Command
from evennia.utils.search import search_object


class CmdFollow(Command):
    """
    Follow another character.
    
    Usage:
        follow <character>
        
    This will make you follow the target character. You will automatically
    move to the same room when they move. Use "unfollow" to stop following.
    """
    
    key = "follow"
    aliases = ["fol"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Follow whom?")
            return
        
        # Find the target character
        target = self._find_target(caller, self.args)
        if not target:
            return
        
        # Can't follow yourself
        if target == caller:
            caller.msg("You can't follow yourself.")
            return
        
        # Can't follow something already being followed by you
        if hasattr(caller.ndb, 'following') and caller.ndb.following == target:
            caller.msg(f"You are already following {target.get_display_name(caller)}.")
            return
        
        # Set up following relationship
        caller.ndb.following = target
        
        # Notify caller
        caller.msg(f"|gYou begin following {target.get_display_name(caller)}.|n")
        
        # Notify target if they're nearby
        if target.location == caller.location:
            target.msg(f"|w{caller.key} begins following you.|n", exclude=[caller])
        
        # Notify others in the room
        caller.location.msg_contents(
            f"|w{caller.key} begins following {target.get_display_name()}.|n",
            exclude=[caller, target]
        )
    
    def _find_target(self, caller, targetname):
        """Find target character in the same location."""
        candidates = [obj for obj in caller.location.contents if obj != caller]
        
        result = caller.search(targetname, candidates=candidates, quiet=True)
        if result:
            target = result[0] if isinstance(result, list) else result
            
            # Verify it's a character
            if not hasattr(target, 'is_typeclass') or not target.is_typeclass('typeclasses.characters.Character', exact=False):
                caller.msg(f"You can only follow characters, not {target.get_display_name(caller)}.")
                return None
            
            return target
        
        caller.msg(f"You don't see '{targetname}' here.")
        return None


class CmdUnfollow(Command):
    """
    Stop following a character.
    
    Usage:
        unfollow
        
    This will stop you from following whoever you were following.
    """
    
    key = "unfollow"
    aliases = ["unfol"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        # Check if they're following anyone
        if not hasattr(caller.ndb, 'following') or not caller.ndb.following:
            caller.msg("You aren't following anyone.")
            return
        
        target = caller.ndb.following
        target_name = target.get_display_name(caller) if target else "someone"
        
        # Clear the following relationship
        delattr(caller.ndb, 'following')
        
        # Notify caller
        caller.msg(f"|yYou stop following {target_name}.|n")
        
        # Notify target if still in game
        if target and target.location:
            target.msg(f"|w{caller.key} stops following you.|n", exclude=[caller])
        
        # Notify others in room
        caller.location.msg_contents(
            f"|w{caller.key} stops following {target_name}.|n",
            exclude=[caller, target] if target else [caller]
        )


class CmdLose(Command):
    """
    Prevent someone from following you.
    
    Usage:
        lose <character>
        lose all
        
    This will prevent the target character from following you, even if they try.
    Use "lose all" to prevent everyone from following you.
    """
    
    key = "lose"
    aliases = ["shake"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Lose whom? (Use 'lose <character>' or 'lose all')")
            return
        
        args = self.args.strip().lower()
        
        # Handle "lose all"
        if args == "all":
            self._lose_all_followers(caller)
            return
        
        # Find specific character to lose
        target = self._find_target(caller, args)
        if not target:
            return
        
        # Check if they're actually following the caller
        if not hasattr(target.ndb, 'following') or target.ndb.following != caller:
            caller.msg(f"{target.get_display_name(caller)} isn't following you.")
            return
        
        # Remove the follow relationship
        delattr(target.ndb, 'following')
        
        # Notify caller
        caller.msg(f"|gYou shake off {target.get_display_name(caller)}.|n")
        
        # Notify the lost follower
        target.msg(f"|r{caller.key} shakes you off - you're no longer following them.|n")
        
        # Notify others in room
        caller.location.msg_contents(
            f"|w{caller.key} shakes off {target.get_display_name(caller)}.|n",
            exclude=[caller, target]
        )
    
    def _lose_all_followers(self, caller):
        """Make all followers stop following the caller."""
        followers_lost = []
        
        # Check all characters in the room
        for obj in caller.location.contents:
            if hasattr(obj, 'ndb') and hasattr(obj.ndb, 'following'):
                if obj.ndb.following == caller:
                    followers_lost.append(obj)
                    delattr(obj.ndb, 'following')
        
        if not followers_lost:
            caller.msg("Nobody is following you.")
            return
        
        # Notify caller
        if len(followers_lost) == 1:
            caller.msg(f"|gYou shake off {followers_lost[0].get_display_name(caller)}.|n")
        else:
            names = ", ".join([f.get_display_name(caller) for f in followers_lost])
            caller.msg(f"|gYou shake off {names}.|n")
        
        # Notify each lost follower
        for follower in followers_lost:
            follower.msg(f"|r{caller.key} shakes you off - you're no longer following them.|n")
        
        # Notify others in room
        if len(followers_lost) == 1:
            caller.location.msg_contents(
                f"|w{caller.key} shakes off {followers_lost[0].get_display_name()}.|n",
                exclude=[caller] + followers_lost
            )
        else:
            names = ", ".join([f.get_display_name() for f in followers_lost])
            caller.location.msg_contents(
                f"|w{caller.key} shakes off {names}.|n",
                exclude=[caller] + followers_lost
            )
    
    def _find_target(self, caller, targetname):
        """Find target character in the same location."""
        candidates = [obj for obj in caller.location.contents if obj != caller]
        
        result = caller.search(targetname, candidates=candidates, quiet=True)
        if result:
            target = result[0] if isinstance(result, list) else result
            
            # Verify it's a character
            if not hasattr(target, 'is_typeclass') or not target.is_typeclass('typeclasses.characters.Character', exact=False):
                caller.msg(f"You can only lose characters, not {target.get_display_name(caller)}.")
                return None
            
            return target
        
        caller.msg(f"You don't see '{targetname}' here.")
        return None
