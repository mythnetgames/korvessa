"""
Gamebud Commands

All commands for the Okama Gamebud communication device.
"""

import re
from evennia import Command, CmdSet
from world.gamebud.core import (
    get_gamebud_manager,
    check_gamebud_device,
    format_gamebud_display,
)
from world.gamebud.constants import (
    MAX_ALIAS_LENGTH,
    MAX_MESSAGE_LENGTH,
    MSG_NO_DEVICE,
    MSG_ALIAS_TOO_LONG,
    MSG_ALIAS_INVALID,
    MSG_MESSAGE_TOO_LONG,
    MSG_NO_MESSAGE,
    MSG_NO_MESSAGES,
    MSG_END_OF_MESSAGES,
    MSG_ALIAS_SET,
    MSG_POST_SUCCESS,
    MSG_MUTED,
    MSG_UNMUTED,
    MSG_ALREADY_MUTED,
    MSG_ALREADY_UNMUTED,
    MSG_COLOR_SET,
    MSG_INVALID_COLOR,
    ALIAS_COLOR_NAMES,
    DEFAULT_ALIAS_COLOR,
    GAMEBUD_HELP,
)


class CmdGamebud(Command):
    """
    Use your Okama Gamebud communication device.
    
    Usage:
        gamebud              - View the Gamebud display
        gamebud view         - View recent messages
        gamebud next         - View next page of messages
        gamebud post=<msg>   - Post a message to the lobby
        gamebud alias=<name> - Set your display alias (max 10 chars)
        gamebud mute         - Turn off new message notifications
        gamebud unmute       - Turn on new message notifications
    
    The Okama Gamebud is a handheld communication device from 1969 that
    allows peer-to-peer messaging within Kowloon Walled City. Set an
    alias and start chatting with other Gamebud users!
    """
    
    key = "gamebud"
    aliases = ["gb", "okama"]
    locks = "cmd:all()"
    help_category = "Communication"
    
    def func(self):
        caller = self.caller
        
        # Check for Gamebud device
        gamebud = check_gamebud_device(caller)
        if not gamebud:
            caller.msg(MSG_NO_DEVICE)
            return
        
        # Parse args
        args = self.args.strip() if self.args else ""
        
        if not args:
            # No subcommand, show display
            self.do_view(gamebud)
            return
        
        # Check for = sign (post=msg or alias=name or color=colorname)
        if "=" in args:
            cmd_part, value_part = args.split("=", 1)
            cmd_part = cmd_part.strip().lower()
            value_part = value_part.strip()
            
            if cmd_part == "post":
                self.do_post(gamebud, value_part)
            elif cmd_part == "alias":
                self.do_alias(gamebud, value_part)
            elif cmd_part == "color":
                self.do_color(gamebud, value_part)
            else:
                caller.msg(f"|rUnknown Gamebud command: {cmd_part}|n")
                caller.msg(GAMEBUD_HELP)
            return
        
        # Single word commands
        primary_cmd = args.lower()
        
        if primary_cmd == "view":
            self.do_view(gamebud)
        elif primary_cmd == "next":
            self.do_next(gamebud)
        elif primary_cmd == "mute":
            self.do_mute(gamebud)
        elif primary_cmd == "unmute":
            self.do_unmute(gamebud)
        elif primary_cmd == "help":
            self.caller.msg(GAMEBUD_HELP)
        else:
            caller.msg(f"|rUnknown Gamebud command: {primary_cmd}|n")
            caller.msg(GAMEBUD_HELP)
    
    def do_view(self, gamebud):
        """Show the Gamebud display with messages."""
        caller = self.caller
        
        # Reset page to 0 when viewing
        gamebud.db.current_page = 0
        
        # Format and display
        display = format_gamebud_display(gamebud, page=0)
        caller.msg(display)
        
        # Show page info
        manager = get_gamebud_manager()
        total_pages = manager.get_total_pages()
        if total_pages > 1:
            caller.msg(f"|wPage 1 of {total_pages} - use 'gamebud next' for more|n")
    
    def do_next(self, gamebud):
        """View next page of messages."""
        caller = self.caller
        manager = get_gamebud_manager()
        
        # Get current page
        current_page = gamebud.db.current_page or 0
        total_pages = manager.get_total_pages()
        
        if total_pages == 0:
            caller.msg(MSG_NO_MESSAGES)
            return
        
        # Increment page
        next_page = current_page + 1
        
        if next_page >= total_pages:
            caller.msg(MSG_END_OF_MESSAGES)
            # Reset to first page
            gamebud.db.current_page = 0
            return
        
        # Update page and display
        gamebud.db.current_page = next_page
        display = format_gamebud_display(gamebud, page=next_page)
        caller.msg(display)
        caller.msg(f"|wPage {next_page + 1} of {total_pages} - use 'gamebud next' for more|n")
    
    def do_post(self, gamebud, message):
        """Post a message to the lobby."""
        caller = self.caller
        
        # Get alias from device (always has one, either set or random)
        from world.gamebud.core import generate_random_alias
        alias = gamebud.db.alias or generate_random_alias()
        
        # Get alias color from device (defaults to white)
        alias_color = gamebud.db.alias_color or DEFAULT_ALIAS_COLOR
        
        # Validate message
        if not message:
            caller.msg(MSG_NO_MESSAGE)
            return
        
        if len(message) > MAX_MESSAGE_LENGTH:
            caller.msg(MSG_MESSAGE_TOO_LONG)
            caller.msg(f"|yYour message is {len(message)} characters. Max is {MAX_MESSAGE_LENGTH}.|n")
            return
        
        # Post message with alias color
        manager = get_gamebud_manager()
        manager.add_message(alias, message, caller, alias_color)
        
        caller.msg(MSG_POST_SUCCESS)
    
    def do_alias(self, gamebud, alias):
        """Set the display alias."""
        caller = self.caller
        
        # Validate length
        if len(alias) > MAX_ALIAS_LENGTH:
            caller.msg(MSG_ALIAS_TOO_LONG)
            return
        
        # Validate characters (alphanumeric and underscore only)
        if not re.match(r'^[a-zA-Z0-9_]+$', alias):
            caller.msg(MSG_ALIAS_INVALID)
            return
        
        # Set alias and reset color to white (sockpuppeting anonymity)
        gamebud.db.alias = alias
        gamebud.db.alias_color = DEFAULT_ALIAS_COLOR
        caller.msg(MSG_ALIAS_SET.format(alias=alias))
    
    def do_mute(self, gamebud):
        """Mute new message notifications."""
        caller = self.caller
        
        if gamebud.db.muted:
            caller.msg(MSG_ALREADY_MUTED)
            return
        
        gamebud.db.muted = True
        caller.msg(MSG_MUTED)
    
    def do_unmute(self, gamebud):
        """Unmute new message notifications."""
        caller = self.caller
        
        if not gamebud.db.muted:
            caller.msg(MSG_ALREADY_UNMUTED)
            return
        
        gamebud.db.muted = False
        caller.msg(MSG_UNMUTED)
    
    def do_color(self, gamebud, color_name):
        """Set the color of your alias on the Gamebud."""
        caller = self.caller
        
        if not color_name:
            caller.msg(MSG_INVALID_COLOR)
            return
        
        # Check if color name is valid
        color_key = color_name.lower()
        if color_key not in ALIAS_COLOR_NAMES:
            caller.msg(MSG_INVALID_COLOR)
            # Show available colors
            color_list = ", ".join(sorted(ALIAS_COLOR_NAMES.keys()))
            caller.msg(f"|yAvailable colors: {color_list}|n")
            return
        
        # Set the alias color
        alias_color = ALIAS_COLOR_NAMES[color_key]
        gamebud.db.alias_color = alias_color
        
        # Show confirmation with the color applied to the color name display
        colored_name = f"|{alias_color}{color_name}|n"
        caller.msg(MSG_COLOR_SET.format(color=colored_name))


class GamebudCmdSet(CmdSet):
    """Command set for Gamebud commands."""
    
    key = "gamebud_cmdset"
    
    def at_cmdset_creation(self):
        self.add(CmdGamebud())
