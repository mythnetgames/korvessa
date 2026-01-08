"""
Look Place (@lp) and Temp Place (@tp) commands for character ambient descriptions.

These commands allow players to set persistent or temporary messages about their
character's location/pose that appears when others look at the room.
"""

from evennia import Command


class CmdLookPlace(Command):
    """
    Set a persistent message about your character's location/pose in a room.
    
    Usage:
        @look_place me is <description>
        @lp me is <description>
        @look_place                      (check current setting)
        @lp                              (check current setting)
        @look_place me is/clear          (clear the setting)
        @lp me is/clear                  (clear the setting)
    
    This command sets a persistent message that will show up when people look at
    the room, replacing the default "{name} is standing here." message. It will
    persist until you change or clear it, even when moving between rooms.
    
    Examples:
        @lp me is leaning against the bar, nursing a drink.
        @lp me is sitting on a crate, arms crossed.
        @lp me is standing in the shadows, watching everyone.
    
    Tips:
        - Write in third person (he/she/they, not I/my)
        - Use |ctpemote|n to toggle auto-emote when setting @temp_place
    """
    key = "look_place"
    aliases = ["lp"]
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        caller = self.caller
        
        # No arguments - show current look_place
        if not self.args:
            current = caller.look_place
            if current:
                caller.msg(f"|GYour @look_place:|n {current}")
            else:
                caller.msg("|YYou have no @look_place set.|n")
            return
        
        args = self.args.strip()
        
        # Check for /clear suffix
        if args.lower() == "me is/clear":
            self.clear_look_place(caller)
            return
        
        # Set look_place - must have 'me is' separator
        if not args.lower().startswith("me is "):
            caller.msg("|RUsage: @lp me is <description>|n")
            return
        
        description = args[6:].strip()  # Skip "me is "
        
        # Remove quotes if present
        if (description.startswith('"') and description.endswith('"')) or \
           (description.startswith("'") and description.endswith("'")):
            description = description[1:-1].strip()
        
        if not description:
            caller.msg("|RYou must provide a description.|n")
            return
        
        self.set_look_place(caller, description)

    def set_look_place(self, caller, description):
        """Set the persistent look_place message."""
        caller.look_place = description
        caller.msg(f"|GSet @look_place:|n {description}")

    def clear_look_place(self, caller):
        """Clear the look_place message."""
        caller.look_place = None
        caller.msg("|GCleared @look_place.|n")


class CmdTempPlace(Command):
    """
    Set a temporary message about your character's location/pose.
    
    Usage:
        @temp_place me is <description>
        @tp me is <description>
        @temp_place                      (check current setting)
        @tp                              (check current setting)
        @temp_place me is/clear          (clear the setting)
        @tp me is/clear                  (clear the setting)
    
    This command sets a temporary message that overrides your @look_place while you
    are in a room. The temporary message will be automatically cleared when you move
    to a different room, allowing you to set one-off poses without having to remember
    to change them back.
    
    Examples:
        @tp me is leaning against the bar, nursing a drink.
        @tp me is sitting on a crate, arms crossed.
        @tp me is standing in the shadows, watching everyone.
    
    Tips:
        - Write in third person (he/she/they, not I/my)
        - Temp place clears automatically when you change rooms
        - Use |ctpemote|n to toggle auto-emote when setting @temp_place
    """
    key = "temp_place"
    aliases = ["tp"]
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        caller = self.caller
        
        # No arguments - show current temp_place
        if not self.args:
            current = getattr(caller.ndb, 'temp_place', None)
            if current:
                caller.msg(f"|GYour @temp_place:|n {current}")
            else:
                caller.msg("|YYou have no @temp_place set.|n")
            return
        
        args = self.args.strip()
        
        # Check for /clear suffix
        if args.lower() == "me is/clear":
            self.clear_temp_place(caller)
            return
        
        # Set temp_place - must have 'me is' separator
        if not args.lower().startswith("me is "):
            caller.msg("|RUsage: @tp me is <description>|n")
            return
        
        description = args[6:].strip()  # Skip "me is "
        
        # Remove quotes if present
        if (description.startswith('"') and description.endswith('"')) or \
           (description.startswith("'") and description.endswith("'")):
            description = description[1:-1].strip()
        
        if not description:
            caller.msg("|RYou must provide a description.|n")
            return
        
        self.set_temp_place(caller, description)

    def set_temp_place(self, caller, description):
        """Set the temporary temp_place message."""
        caller.ndb.temp_place = description
        caller.msg(f"|GSet @temp_place:|n {description}")
        
        # Auto-emote if enabled
        if getattr(caller.db, 'tpemote_enabled', False):
            caller.msg(f"|Y{caller.get_display_name(caller)}: {description}|n")
            caller.location.msg_contents(f"|Y{caller.get_display_name(caller)}: {description}|n", exclude=[caller])

    def clear_temp_place(self, caller):
        """Clear the temp_place message."""
        if hasattr(caller.ndb, 'temp_place'):
            delattr(caller.ndb, 'temp_place')
        caller.msg("|GCleared @temp_place.|n")


class CmdTPEmote(Command):
    """
    Toggle auto-emote when setting @temp_place.
    
    Usage:
        tpemote
    
    When enabled, setting your @temp_place will automatically emote the change
    to everyone in the room. This allows you to set a pose and announce it at
    the same time.
    
    Examples:
        tpemote                    (toggles the setting on/off)
        @tp me is standing up.     (if tpemote is on, will announce to room)
    """
    key = "tpemote"
    locks = "cmd:all()"
    help_category = "Character"
    
    def func(self):
        caller = self.caller
        
        # Toggle the setting
        current = getattr(caller.db, 'tpemote_enabled', False)
        caller.db.tpemote_enabled = not current
        
        if caller.db.tpemote_enabled:
            caller.msg("|GEnabled:|n Auto-emote is now |gON|n. Setting @temp_place will announce to the room.")
        else:
            caller.msg("|GDisabled:|n Auto-emote is now |rOFF|n. Setting @temp_place will be private.")
