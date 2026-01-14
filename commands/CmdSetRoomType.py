"""
Command to set room tags/attributes.
"""

from evennia import Command
from world.room_tags import set_tags, ALL_TAGS, ACTIVE_TAGS, PASSIVE_TAGS


class CmdSetRoomType(Command):
    """
    Set room tags/attributes that affect gameplay and environment.
    
    Usage:
        setroomtype <tag1>, <tag2>, ...
        setroomtype --clear
        setroomtype --list
        setroomtype --help
        
    Examples:
        setroomtype ON FIRE
        setroomtype MEDICAL, STERILE
        setroomtype OUTDOORS, OUTSIDE
        setroomtype --clear
        
    Valid tags are listed with 'setroomtype --list'.
    Active tags (x) have gameplay effects.
    Passive tags (o) are informational/bonus.
    """
    
    key = "setroomtype"
    aliases = ["roomtag", "roomtype"]
    locks = "cmd:perm(Admin)"
    help_category = "Building"
    
    def func(self):
        """Execute command"""
        caller = self.caller
        room = caller.location
        
        if not room:
            caller.msg("You must be in a room to set its tags.")
            return
        
        args = self.args.strip()
        
        if not args or args == "--help":
            self._show_help(caller)
            return
        
        if args == "--list":
            self._show_tag_list(caller)
            return
        
        if args == "--clear":
            room.tags = []
            caller.msg(f"Cleared all tags from {room.key}.")
            return
        
        # Parse tag list
        tag_list = [t.strip() for t in args.split(",")]
        success, msg, applied = set_tags(room, tag_list)
        
        caller.msg(msg)
        if applied:
            caller.msg(f"\n|gRoom tags updated: {', '.join(applied)}|n")
            
            # Attach effect handler if there are active tags
            from world.room_tag_effects import attach_effect_handler
            has_active = any(tag in ACTIVE_TAGS for tag in applied)
            if has_active:
                handler = attach_effect_handler(room)
    
    def _show_help(self, caller):
        """Show help text"""
        help_text = """
|wRoom Tag System|n

Room tags are attributes that affect gameplay and create dynamic environments.

|wActive Tags (x) - Have ongoing effects:|n"""
        
        for tag, info in sorted(ACTIVE_TAGS.items()):
            help_text += f"\n  |y{tag}|n - {info['desc']}"
        
        help_text += "\n\n|wPassive Tags (o) - Informational/bonus:|n"
        
        for tag, info in sorted(PASSIVE_TAGS.items()):
            help_text += f"\n  |y{tag}|n - {info['desc']}"
        
        help_text += "\n\n|wUsage:|n\n  setroomtype <tag1>, <tag2>, ...\n  setroomtype --clear"
        
        caller.msg(help_text)
    
    def _show_tag_list(self, caller):
        """Show list of all available tags"""
        output = "|wAvailable Room Tags:|n\n"
        
        output += "|wActive Tags (x - have gameplay effects):|n\n"
        for tag, info in sorted(ACTIVE_TAGS.items()):
            output += f"  |y{tag:<20}|n {info['desc']}\n"
        
        output += "\n|wPassive Tags (o - informational/bonus):|n\n"
        for tag, info in sorted(PASSIVE_TAGS.items()):
            output += f"  |g{tag:<20}|n {info['desc']}\n"
        
        caller.msg(output)
