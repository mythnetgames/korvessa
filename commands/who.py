"""
Custom WHO command with invisibility, location hiding, and staff admin views.
"""

from evennia import Command, default_cmds
from evennia.accounts.models import AccountDB
from evennia.objects.models import ObjectDB


class CmdWho(default_cmds.CmdWho):
    """
    Shows a list of online players.
    
    Usage:
        who              - Show all visible players
        invisible        - Toggle your invisibility (admin only)
        who_location     - Toggle your location visibility (for RP)
    
    Features:
        - Invisible players cannot be seen by regular players
        - You can hide your location for RP purposes
        - Staff see more info: account names, character names, locations
        - Staff see invisible players marked as (invisible)
    """
    key = "who"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        """Execute the WHO command."""
        caller = self.caller
        
        # If staff, show admin version
        if caller.check_permstring("builders"):
            self.show_admin_who(caller)
        else:
            self.show_player_who(caller)

    def show_player_who(self, caller):
        """Show WHO list for regular players - hidden locations and no invisible players."""
        # Get all online accounts
        accounts = AccountDB.objects.filter(db_is_connected=True)
        
        # Build player list
        visible_players = []
        for account in accounts:
            # Get character(s) for this account
            characters = account.characters
            if not characters:
                continue
            
            for character in characters:
                # Skip invisible characters
                if self.is_invisible(character):
                    continue
                
                # Get location - check if player hid it
                location_name = "Hidden"
                if not self.has_hidden_location(character):
                    loc = character.location
                    if loc:
                        location_name = loc.get_display_name(caller)
                
                visible_players.append({
                    'name': character.get_display_name(caller),
                    'location': location_name
                })
        
        # Format output
        output = f"|C{'='*70}|n\n"
        output += f"|CPlayers Online ({len(visible_players)}):|n\n"
        output += f"|C{'='*70}|n\n"
        
        if not visible_players:
            output += "|YNo players are currently online.|n\n"
        else:
            for player in visible_players:
                output += f"  |G{player['name']:<30}|n {player['location']}\n"
        
        output += f"|C{'='*70}|n"
        caller.msg(output)

    def show_admin_who(self, caller):
        """Show WHO list for staff - shows all players, accounts, and locations."""
        # Get all online accounts
        accounts = AccountDB.objects.filter(db_is_connected=True)
        
        # Build player list
        all_players = []
        invisible_count = 0
        
        for account in accounts:
            # Get character(s) for this account
            characters = account.characters
            if not characters:
                continue
            
            for character in characters:
                is_invis = self.is_invisible(character)
                if is_invis:
                    invisible_count += 1
                
                # Get location
                loc = character.location
                location_name = f"{loc.get_display_name(caller)} #{loc.dbref}" if loc else "None"
                
                # Build entry
                invis_marker = " (invisible)" if is_invis else ""
                hidden_marker = " (hidden location)" if self.has_hidden_location(character) else ""
                
                all_players.append({
                    'account': account.name,
                    'character': character.get_display_name(caller),
                    'location': location_name,
                    'invisible': is_invis,
                    'markers': invis_marker + hidden_marker
                })
        
        # Format output
        output = f"|C{'='*80}|n\n"
        output += f"|CPlayers Online ({len(all_players)}, {invisible_count} invisible):|n\n"
        output += f"|C{'='*80}|n\n"
        
        if not all_players:
            output += "|YNo players are currently online.|n\n"
        else:
            output += "|C(1 invisible to regular players)|n\n"
            for player in all_players:
                invis_marker = ""
                if player['invisible']:
                    invis_marker = " |R(invisible)|n"
                else:
                    invis_marker = " "
                
                output += f"  |G{player['account']:<20}|n {player['character']:<20} {player['location']}{invis_marker}\n"
        
        output += f"|C{'='*80}|n"
        caller.msg(output)

    @staticmethod
    def is_invisible(character):
        """Check if character is invisible to players."""
        return getattr(character.db, 'invisible', False)

    @staticmethod
    def has_hidden_location(character):
        """Check if character has hidden their location."""
        return getattr(character.db, 'who_location_hidden', False)


class CmdInvisible(Command):
    """
    Toggle your visibility on the WHO list.
    
    Usage:
        invisible       - Toggle invisible mode
    
    When invisible, regular players cannot see you on the WHO list.
    Staff will still see you marked as (invisible).
    This is useful for avoiding unwanted contact while still being online.
    """
    key = "invisible"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        
        # Toggle invisibility
        current = getattr(caller.db, 'invisible', False)
        caller.db.invisible = not current
        
        if caller.db.invisible:
            caller.msg("|Yinvisible on|n")
            caller.msg("|CYou are now invisible on the 'who' list.|n")
        else:
            caller.msg("|Yinvisible off|n")
            caller.msg("|CYou are now visible on the 'who' list.|n")


class CmdWhoLocation(Command):
    """
    Toggle your location visibility on WHO.
    
    Usage:
        who_location    - Toggle location hiding (for RP purposes)
    
    When hidden, your location will show as "Hidden" on the WHO list,
    allowing you to maintain mystery while still appearing online.
    """
    key = "who_location"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        
        # Toggle location hiding
        current = getattr(caller.db, 'who_location_hidden', False)
        caller.db.who_location_hidden = not current
        
        if caller.db.who_location_hidden:
            caller.msg("|Yyour location is now hidden on WHO|n")
            caller.msg("|CPlayers will see you as being in a 'Hidden' location.|n")
        else:
            caller.msg("|Yyour location is now visible on WHO|n")
            caller.msg("|CPlayers will see your actual location on the who list.|n")
