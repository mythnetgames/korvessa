"""
Commands for the sdesc/shortdesc system.

- name: Assign a name to someone's sdesc (recog system)
- names: List all people you've named
- setsdesc: Admin command to set someone's sdesc

Players cannot change their own sdesc - admins can set it if needed.
Use the 'tp' command for posing, not a separate pose command.
"""

from evennia import Command
from world.sdesc_system import (
    get_sdesc, set_sdesc,
    get_recog, set_recog, clear_recog,
    find_character_by_sdesc, validate_sdesc,
    format_sdesc_for_room
)


class CmdName(Command):
    """
    Assign a personal name to someone's sdesc.
    
    Usage:
        name <sdesc> = <name>
        name <sdesc>
        name clear <sdesc>
        names
        
    When you 'name' someone, you'll see that name instead of their sdesc
    in emotes and room descriptions. This is personal to you - others
    won't see the name you've assigned.
    
    Examples:
        name tall = Tom
            You'll now see "Tom" instead of "a tall man"
            
        name scarred elven = Lady Vex
            You'll now see "Lady Vex" instead of "a scarred elven woman"
            
        name clear tall
            Forget Tom's name, see his sdesc again
            
        name tall
            Show what name you know for "a tall man"
            
        names
            List all people you've named
            
    Note: Names respect disguises. If someone puts on a disguise,
    you'll need to name their new appearance separately.
    """
    
    key = "name"
    aliases = ["recog", "recognize", "remember"]
    locks = "cmd:all()"
    help_category = "Character"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            # Show all recognized names
            self.list_names()
            return
        
        args = self.args.strip()
        
        # Check for 'names' to list all
        if args.lower() == 'names':
            self.list_names()
            return
        
        # Check for 'clear' command
        if args.lower().startswith('clear '):
            search_term = args[6:].strip()
            self.clear_name(search_term)
            return
        
        # Check if assigning a name (contains =)
        if '=' in args:
            sdesc_part, name_part = args.split('=', 1)
            sdesc_part = sdesc_part.strip()
            name_part = name_part.strip()
            
            if not sdesc_part or not name_part:
                caller.msg("|rUsage: name <sdesc> = <name>|n")
                return
            
            self.assign_name(sdesc_part, name_part)
        else:
            # Just looking up a name
            self.lookup_name(args)
    
    def list_names(self):
        """List all recognized characters."""
        caller = self.caller
        recog_dict = caller.db.recog or {}
        
        if not recog_dict:
            caller.msg("|yYou haven't named anyone yet.|n")
            caller.msg("|wUse |yname <sdesc> = <name>|w to remember someone.|n")
            return
        
        caller.msg("|w=== People You've Named ===|n")
        for key, name in recog_dict.items():
            # Try to find the character to show their sdesc
            if key.startswith('disguise_'):
                caller.msg(f"  |c{name}|n (disguised identity)")
            else:
                try:
                    from evennia.objects.models import ObjectDB
                    char = ObjectDB.objects.get(id=int(key))
                    sdesc = char.db.sdesc or char.key
                    caller.msg(f"  |c{name}|n - {sdesc}")
                except:
                    caller.msg(f"  |c{name}|n (character no longer exists)")
    
    def assign_name(self, search_term, name):
        """Assign a name to a character found by sdesc."""
        caller = self.caller
        
        # Find the target
        matches = find_character_by_sdesc(caller.location, search_term, caller)
        
        if not matches:
            caller.msg(f"|rNo one matching '{search_term}' found here.|n")
            return
        
        if len(matches) > 1:
            caller.msg(f"|yMultiple matches for '{search_term}':|n")
            for m in matches:
                caller.msg(f"  - {get_sdesc(m, caller)}")
            caller.msg("|yBe more specific.|n")
            return
        
        target = matches[0]
        
        if target == caller:
            caller.msg("|yYou can't name yourself.|n")
            return
        
        # Validate name
        if len(name) > 40:
            caller.msg("|rName cannot exceed 40 characters.|n")
            return
        
        if len(name) < 2:
            caller.msg("|rName must be at least 2 characters.|n")
            return
        
        # Set the recognition
        old_sdesc = get_sdesc(target, None)  # Get without recog
        set_recog(caller, target, name)
        
        caller.msg(f"|gYou will now know '|w{old_sdesc}|g' as '|c{name}|g'.|n")
    
    def lookup_name(self, search_term):
        """Look up what name we know for someone."""
        caller = self.caller
        
        matches = find_character_by_sdesc(caller.location, search_term, caller)
        
        if not matches:
            caller.msg(f"|rNo one matching '{search_term}' found here.|n")
            return
        
        for target in matches:
            sdesc = target.db.sdesc or target.key
            recog = get_recog(caller, target)
            
            if recog:
                caller.msg(f"|wYou know '|y{sdesc}|w' as '|c{recog}|w'.|n")
            else:
                caller.msg(f"|wYou don't have a name for '|y{sdesc}|w'.|n")
    
    def clear_name(self, search_term):
        """Clear recognition of someone."""
        caller = self.caller
        
        matches = find_character_by_sdesc(caller.location, search_term, caller)
        
        if not matches:
            caller.msg(f"|rNo one matching '{search_term}' found here.|n")
            return
        
        for target in matches:
            recog = get_recog(caller, target)
            if recog:
                sdesc = target.db.sdesc or target.key
                clear_recog(caller, target)
                caller.msg(f"|gYou no longer know '|w{sdesc}|g' as '|c{recog}|g'.|n")
            else:
                caller.msg(f"|yYou didn't have a name for that person.|n")


class CmdNames(Command):
    """
    List all people you've named.
    
    Usage:
        names
        
    Shows everyone you've assigned a personal name to via the 'name' command.
    """
    
    key = "names"
    aliases = ["recogs", "remembered"]
    locks = "cmd:all()"
    help_category = "Character"
    
    def func(self):
        caller = self.caller
        recog_dict = caller.db.recog or {}
        
        if not recog_dict:
            caller.msg("|yYou haven't named anyone yet.|n")
            caller.msg("|wUse |yname <sdesc> = <name>|w to remember someone.|n")
            return
        
        caller.msg("|w=== People You've Named ===|n")
        for key, name in recog_dict.items():
            if key.startswith('disguise_'):
                caller.msg(f"  |c{name}|n (disguised identity)")
            else:
                try:
                    from evennia.objects.models import ObjectDB
                    char = ObjectDB.objects.get(id=int(key))
                    sdesc = char.db.sdesc or char.key
                    caller.msg(f"  |c{name}|n - {sdesc}")
                except:
                    caller.msg(f"  |c{name}|n (character no longer exists)")


class CmdSetSdesc(Command):
    """
    Staff command to set another character's sdesc.
    
    Usage:
        setsdesc <character> = <sdesc>
    """
    
    key = "setsdesc"
    locks = "cmd:perm(Admin) or perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        
        if not self.args or '=' not in self.args:
            caller.msg("|rUsage: setsdesc <character> = <sdesc>|n")
            return
        
        char_name, sdesc = self.args.split('=', 1)
        char_name = char_name.strip()
        sdesc = sdesc.strip()
        
        # Find character
        from evennia.objects.models import ObjectDB
        targets = ObjectDB.objects.filter(db_key__iexact=char_name)
        if not targets:
            caller.msg(f"|rCharacter '{char_name}' not found.|n")
            return
        
        target = targets[0]
        
        # Validate (pass target to exclude from duplicate check)
        is_valid, error = validate_sdesc(sdesc, exclude_character=target)
        if not is_valid:
            caller.msg(f"|r{error}|n")
            return
        
        # Set sdesc (now returns success/error tuple)
        success, error = set_sdesc(target, sdesc)
        if not success:
            caller.msg(f"|r{error}|n")
            return
        
        caller.msg(f"|gSet {target.key}'s sdesc to:|n {sdesc}")
