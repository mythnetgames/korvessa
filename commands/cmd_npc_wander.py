"""
Admin command for managing NPC zone wandering.
"""

from evennia import Command
from evennia.objects.models import ObjectDB


class CmdNPCWander(Command):
    """
    Manage NPC wandering behavior.
    
    Usage:
        npcwander <npc> = enable <zone>      # Enable wandering in zone
        npcwander <npc> = disable             # Disable wandering
        npcwander <npc> = zone <zone_name>    # Change wandering zone
        npcwander <npc> = status              # Check wandering status
        npcwander zone <zone_name>            # List all rooms in zone
    
    Examples:
        npcwander street_vendor = enable market_district
        npcwander street_vendor = disable
        npcwander street_vendor = zone fortress_entrance
        npcwander street_vendor = status
        npcwander zone market_district
    """
    
    key = "npcwander"
    aliases = ["npc_wander", "wander_npc"]
    locks = "cmd:perm(Admin)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: npcwander <npc> = <action> [zone]")
            caller.msg("  Actions: enable <zone>, disable, zone <zone>, status")
            caller.msg("Or: npcwander zone <zone_name> - list rooms in zone")
            return
        
        # Parse arguments
        args = self.args.strip()
        
        # Check for "npcwander zone <zone_name>" format
        if args.lower().startswith("zone "):
            zone_name = args[5:].strip()
            self._list_zone_rooms(caller, zone_name)
            return
        
        # Otherwise: "npcwander <npc> = <action>"
        if "=" not in args:
            caller.msg("Use format: npcwander <npc> = <action>")
            return
        
        npc_name, action_str = args.split("=", 1)
        npc_name = npc_name.strip()
        action_str = action_str.strip()
        
        # Find the NPC
        npc = caller.search(npc_name, candidates=caller.location.contents if caller.location else [])
        if not npc:
            caller.msg(f"NPC '{npc_name}' not found.")
            return
        
        # Parse action
        action_parts = action_str.split()
        if not action_parts:
            caller.msg("No action specified.")
            return
        
        action = action_parts[0].lower()
        
        # Handle actions
        if action == "enable":
            if len(action_parts) < 2:
                caller.msg("Usage: npcwander <npc> = enable <zone>")
                return
            zone = " ".join(action_parts[1:])
            self._enable_wandering(caller, npc, zone)
        
        elif action == "disable":
            self._disable_wandering(caller, npc)
        
        elif action == "zone":
            if len(action_parts) < 2:
                caller.msg("Usage: npcwander <npc> = zone <zone_name>")
                return
            zone = " ".join(action_parts[1:])
            self._set_zone(caller, npc, zone)
        
        elif action == "status":
            self._check_status(caller, npc)
        
        else:
            caller.msg(f"Unknown action: {action}")
            caller.msg("Actions: enable <zone>, disable, zone <zone>, status")
    
    def _enable_wandering(self, caller, npc, zone):
        """Enable wandering for an NPC in a specific zone."""
        if not hasattr(npc, "db"):
            caller.msg(f"{npc.name} is not a valid NPC.")
            return
        
        # Check zone exists and has rooms
        zone_rooms = self._get_zone_rooms(zone)
        if not zone_rooms:
            caller.msg(f"|rNo rooms found in zone '{zone}'.|n")
            return
        
        if len(zone_rooms) < 2:
            caller.msg(f"|yWarning: Zone '{zone}' has only {len(zone_rooms)} room. NPC won't wander.|n")
        
        # Enable wandering
        npc.db.npc_can_wander = True
        npc.db.npc_zone = zone
        
        # Initialize wandering if NPC has at_init
        if hasattr(npc, "at_init"):
            try:
                npc.at_init()
            except:
                pass
        
        caller.msg(f"|g{npc.name} will now wander in zone '{zone}' ({len(zone_rooms)} rooms).|n")
        npc.location.msg_contents(f"|g{npc.name} looks around curiously.|n", exclude=[caller, npc])
    
    def _disable_wandering(self, caller, npc):
        """Disable wandering for an NPC."""
        if not hasattr(npc, "db"):
            caller.msg(f"{npc.name} is not a valid NPC.")
            return
        
        npc.db.npc_can_wander = False
        
        # Stop wandering script if it exists
        if hasattr(npc, "_disable_wandering"):
            try:
                npc._disable_wandering()
            except:
                pass
        
        caller.msg(f"|y{npc.name} will no longer wander.|n")
        npc.location.msg_contents(f"|y{npc.name} settles in place.|n", exclude=[caller, npc])
    
    def _set_zone(self, caller, npc, zone):
        """Change an NPC's wandering zone."""
        if not hasattr(npc, "db"):
            caller.msg(f"{npc.name} is not a valid NPC.")
            return
        
        # Check zone exists
        zone_rooms = self._get_zone_rooms(zone)
        if not zone_rooms:
            caller.msg(f"|rNo rooms found in zone '{zone}'.|n")
            return
        
        # Set zone
        npc.db.npc_zone = zone
        
        # Enable wandering if not already enabled
        if not getattr(npc.db, "npc_can_wander", False):
            npc.db.npc_can_wander = True
            if hasattr(npc, "at_init"):
                try:
                    npc.at_init()
                except:
                    pass
        
        caller.msg(f"|g{npc.name}'s wandering zone changed to '{zone}' ({len(zone_rooms)} rooms).|n")
    
    def _check_status(self, caller, npc):
        """Check wandering status of an NPC."""
        if not hasattr(npc, "db"):
            caller.msg(f"{npc.name} is not a valid NPC.")
            return
        
        can_wander = getattr(npc.db, "npc_can_wander", False)
        zone = getattr(npc.db, "npc_zone", None)
        puppeted = getattr(npc.db, "puppeted_by", None)
        
        status_text = "|cWandering Status for " + npc.name + ":|n\n"
        status_text += f"  Wandering Enabled: |y{'Yes' if can_wander else 'No'}|n\n"
        status_text += f"  Wandering Zone: |y{zone if zone else 'None'}|n\n"
        status_text += f"  Currently Puppeted: |y{'Yes' if puppeted else 'No'}|n\n"
        status_text += f"  Current Location: |y{npc.location.name if npc.location else 'Unknown'}|n\n"
        
        if zone:
            zone_rooms = self._get_zone_rooms(zone)
            status_text += f"  Rooms in Zone: |y{len(zone_rooms)}|n\n"
            if len(zone_rooms) < 2:
                status_text += f"  |r⚠ Warning: Zone needs at least 2 rooms for wandering!|n\n"
        
        caller.msg(status_text)
    
    def _list_zone_rooms(self, caller, zone):
        """List all rooms in a zone."""
        zone_rooms = self._get_zone_rooms(zone)
        
        if not zone_rooms:
            caller.msg(f"|rNo rooms found in zone '{zone}'.|n")
            return
        
        msg = f"|cRooms in zone '{zone}': ({len(zone_rooms)} total)|n\n"
        msg += "-" * 60 + "\n"
        
        for idx, room in enumerate(zone_rooms, 1):
            # Count NPCs in room with same zone
            npc_count = 0
            for obj in room.contents:
                if hasattr(obj, "db") and getattr(obj.db, "npc_zone", None) == zone:
                    npc_count += 1
            
            npc_info = f" (|c{npc_count} NPC(s)|n)" if npc_count > 0 else ""
            msg += f"  {idx}. |y{room.name}|n (#{room.id}){npc_info}\n"
        
        msg += "-" * 60 + "\n"
        caller.msg(msg)
    
    def _get_zone_rooms(self, zone):
        """Get all rooms in a zone."""
        try:
            rooms = []
            for room in ObjectDB.objects.all():
                if getattr(room, "zone", None) == zone:
                    rooms.append(room)
            return rooms
        except:
            return []
