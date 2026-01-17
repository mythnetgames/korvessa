"""
Custom Look command that handles petitions viewing and housing door status indicators.
"""

from evennia.commands.default.general import CmdLook as DefaultCmdLook


class CmdLook(DefaultCmdLook):
    """
    Look at the world and people around you with petition support.
    
    Usage:
        look
        look <object>
        look petitions     - View your petitions
        look pending       - View your pending petitions
    
    Door Status Indicators:
        +north = door exists and is closed/locked
        -north = door exists and is open/unlocked
    """
    
    aliases = ["l", "ls"]
    
    def func(self):
        """Override look to handle petitions."""
        caller = self.caller
        
        # Check if looking at petitions
        if self.args and self.args.lower() == "petitions":
            self.view_petitions(caller)
            return
        elif self.args and self.args.lower() == "pending":
            self.view_pending(caller)
            return
        
        # Otherwise use default look
        super().func()
    
    def format_room_exits(self, room):
        """
        Format exits with housing door status indicators.
        Overrides parent to show +direction for closed/locked doors, -direction for open/unlocked.
        
        Args:
            room: The room to format exits for
            
        Returns:
            str: Formatted exit string with indicators
        """
        exit_list = room.exits
        
        if not exit_list:
            return ""
        
        # Get the caller for lock checking
        caller = self.caller
        
        exit_strs = []
        for exit_obj in exit_list:
            # Check if this is a housing door (CubeDoor or PadDoor)
            if exit_obj.is_typeclass("typeclasses.cube_housing.CubeDoor"):
                # Use the door's formatted name with +/- indicator
                formatted_name = exit_obj.get_formatted_exit_name()
                exit_strs.append(formatted_name)
            elif exit_obj.is_typeclass("typeclasses.pad_housing.PadDoor"):
                # Use the door's formatted name with +/- indicator
                formatted_name = exit_obj.get_formatted_exit_name()
                exit_strs.append(formatted_name)
            elif getattr(exit_obj.db, "has_door", False):
                # Exit has a door attached directly - use its display method
                if hasattr(exit_obj, "get_door_display_name"):
                    exit_strs.append(exit_obj.get_door_display_name())
                else:
                    # Fallback: manual +/- indicator
                    if not getattr(exit_obj.db, "door_is_open", False) or getattr(exit_obj.db, "door_is_locked", False):
                        exit_strs.append(f"+{exit_obj.key}")
                    else:
                        exit_strs.append(f"-{exit_obj.key}")
            else:
                # Check if there's a legacy door object attached to this exit
                exit_name = exit_obj.key
                for obj in room.contents:
                    if (obj.is_typeclass("typeclasses.doors.Door") and 
                        getattr(obj.db, "exit_direction", None) == exit_obj.key):
                        if hasattr(obj, "get_formatted_exit_name"):
                            exit_name = obj.get_formatted_exit_name()
                        break
                exit_strs.append(exit_name)
        
        # Sort and format
        exit_strs = ", ".join(exit_strs) if exit_strs else ""
        return f"|cExits:|n {exit_strs}"
    
    def view_petitions(self, char):
        """Display active petitions for the character."""
        petitions = getattr(char.db, 'petitions', None) or []
        active_petitions = [p for p in petitions if p.get('status') == 'active']
        
        if not active_petitions:
            char.msg("|YYou have no active petitions.|n")
            return
        
        char.msg("|c=== Your Petitions ===|n")
        for p in active_petitions:
            timestamp = p.get('timestamp', '').strftime('%Y-%m-%d %H:%M') if hasattr(p.get('timestamp', ''), 'strftime') else str(p.get('timestamp', ''))
            char.msg(f"  |w[#{p.get('id', '?')}]|n [{timestamp}] to {p.get('target', '?')}: {p.get('message', '?')}")
            char.msg(f"      To erase: erase petitions {p.get('id', '?')}")
    
    def view_pending(self, char):
        """Display pending petitions for the character."""
        petitions = getattr(char.db, 'petitions', None) or []
        pending_petitions = [p for p in petitions if p.get('status') == 'pending']
        
        if not pending_petitions:
            char.msg("|YYou have no pending petitions.|n")
            return
        
        char.msg("|c=== Your Pending Petitions ===|n")
        char.msg("|yThese petitions are being reviewed by other staff members.|n")
        for p in pending_petitions:
            timestamp = p.get('timestamp', '').strftime('%Y-%m-%d %H:%M') if hasattr(p.get('timestamp', ''), 'strftime') else str(p.get('timestamp', ''))
            char.msg(f"  |w[#{p.get('id', '?')}]|n [{timestamp}] to {p.get('target', '?')}: {p.get('message', '?')}")
            char.msg(f"      To erase: erase pending {p.get('id', '?')}")
