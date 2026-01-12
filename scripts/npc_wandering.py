"""
NPC Wandering Script

This script handles NPC wandering behavior within restricted zones.
NPCs will randomly move between rooms in their assigned zone, never leaving the zone.
"""

from random import randint, choice
from evennia.scripts.scripts import DefaultScript
from evennia.objects.models import ObjectDB


def get_or_create_channel(channel_name):
    """Get or create a channel by name."""
    try:
        from evennia.comms.models import ChannelDB
        channel = ChannelDB.objects.get_channel(channel_name)
        if not channel:
            # Channel doesn't exist, try to create it
            channel = ChannelDB.objects.channel_create(
                key=channel_name,
                description=f"Channel for {channel_name} messages",
                locks="listen:all();send:all();edit:false()"
            )
        return channel
    except Exception as e:
        return None


class NPCWanderingScript(DefaultScript):
    """
    Script that manages NPC wandering within a zone.
    
    Assigned to individual NPCs via their db.npc_can_wander flag.
    """
    
    def at_script_creation(self):
        """Initialize the wandering script."""
        self.key = "npc_wandering"
        self.desc = "Handles NPC wandering behavior"
        # Update interval in seconds - 10-30 seconds between movements
        self.interval = 15  # Fixed interval
        self.persistent = True
    
    def at_repeat(self):
        """Called at each interval - handles the wandering logic."""
        obj = self.obj  # The NPC this script is attached to
        
        if not obj:
            # If NPC is deleted, stop the script
            self.stop()
            return
        
        # Check if NPC can wander
        if not getattr(obj.db, "npc_can_wander", False):
            return
        
        # Get the zone the NPC should wander in
        zone = getattr(obj.db, "npc_zone", None)
        if not zone:
            return
        
        # Check blocking conditions FIRST
        is_puppeted = bool(getattr(obj.db, "puppeted_by", None))
        
        # Get channel early for cleanup logging
        channel = get_or_create_channel("wanderers")
        
        # Check combat status - verify handler is actually active and NPC is in it
        is_in_combat = False
        if hasattr(obj.ndb, "combat_handler"):
            handler = obj.ndb.combat_handler
            # Verify handler exists and is active
            if handler and hasattr(handler, 'is_active') and handler.is_active:
                # Verify NPC is actually in the handler's combatants list
                combatants = getattr(handler.db, 'combatants', [])
                is_in_combat = any(entry.get('char') == obj for entry in combatants)
                
                # If handler reference is stale, clean it up
                if not is_in_combat:
                    delattr(obj.ndb, "combat_handler")
                    if channel:
                        channel.msg(f"CLEANUP: Removed stale combat_handler reference from {obj.name}")
            else:
                # Handler is dead/inactive, clean up the reference
                delattr(obj.ndb, "combat_handler")
                if channel:
                    channel.msg(f"CLEANUP: Removed dead combat_handler reference from {obj.name}")
        
        # If blocked by puppeting or combat, report it and return
        if is_puppeted or is_in_combat:
            location = obj.location.key if obj.location else "unknown"
            puppeted = "PUPPETED" if is_puppeted else "free"
            in_combat = "COMBAT" if is_in_combat else "safe"
            blocked_by = "PUPPETED" if is_puppeted else "COMBAT"
            if channel:
                channel.msg(f"TICK: {obj.name} in {location} ({zone}) - {puppeted}, {in_combat} - BLOCKED BY {blocked_by}")
            return
        
        # Now do the roll
        if channel:
            # Show NPC status
            location = obj.location.key if obj.location else "unknown"
            puppeted = "PUPPETED" if is_puppeted else "free"
            in_combat = "COMBAT" if is_in_combat else "safe"
            roll = randint(1, 10)
            will_move = "YES" if roll <= 3 else "NO"
            channel.msg(f"TICK: {obj.name} in {location} ({zone}) - {puppeted}, {in_combat} - ROLL({roll}) -> {will_move}")
            
            # Random chance to wander (30% chance each interval)
            if roll <= 3:
                # Attempt to move to a random room in the zone
                self._wander_to_zone_room(obj, zone)
        else:
            # No channel, still do the roll and movement
            roll = randint(1, 10)
            if roll <= 3:
                self._wander_to_zone_room(obj, zone)
    
    def _wander_to_zone_room(self, npc, zone):
        """
        Move NPC to a random adjacent room within its zone via real exits.
        Uses actual exit connections instead of teleporting.
        
        Args:
            npc: The NPC character object
            zone: The zone identifier string
        """
        channel = get_or_create_channel("wanderers")
        
        # Get current room
        current_room = npc.location
        if not current_room:
            if channel:
                channel.msg(f"WANDER_FAIL: {npc.name} - No current location")
            return
        
        # Find all exits from current room that lead to rooms in the same zone
        adjacent_zone_rooms = []
        
        # Check all exits from current location
        if hasattr(current_room, 'exits'):
            for exit_obj in current_room.exits:
                if not exit_obj or not hasattr(exit_obj, 'destination'):
                    continue
                    
                dest_room = exit_obj.destination
                if not dest_room:
                    continue
                
                # Check if destination is in the same zone
                dest_zone = getattr(dest_room, 'zone', None)
                if dest_zone == zone:
                    adjacent_zone_rooms.append((exit_obj, dest_room))
        
        if not adjacent_zone_rooms:
            if channel:
                channel.msg(f"WANDER_FAIL: {npc.name} - No exits to rooms in zone '{zone}'")
            return
        
        if channel:
            channel.msg(f"WANDER_ATTEMPT: {npc.name} - Found {len(adjacent_zone_rooms)} adjacent rooms in zone '{zone}'")
        
        # Pick a random exit and traverse it
        exit_obj, destination = choice(adjacent_zone_rooms)
        
        if channel:
            channel.msg(f"WANDER_ATTEMPT: {npc.name} - Traversing exit '{exit_obj.key}' from '{current_room.key}' to '{destination.key}'")
        
        # Use the exit traversal to properly move through the game world
        try:
            # Call at_traverse to properly move the NPC through the exit
            exit_obj.at_traverse(npc, destination)
            if channel:
                channel.msg(f"WANDER_SUCCESS: {npc.name} traversed '{exit_obj.key}' and arrived at '{destination.key}'")
        except Exception as e:
            if channel:
                channel.msg(f"WANDER_ERROR: {npc.name} - Failed to traverse '{exit_obj.key}': {e}")
    
    def _get_zone_rooms(self, zone):
        """
        Get all rooms that belong to a specific zone.
        
        Args:
            zone (str): The zone identifier
            
        Returns:
            list: List of room objects in that zone
        """
        from typeclasses.rooms import Room
        
        channel = get_or_create_channel("wanderers")
        
        try:
            # Query all rooms and filter by zone
            rooms = []
            total_checked = 0
            for room in ObjectDB.objects.filter(db_typeclass_path__icontains="rooms.Room"):
                total_checked += 1
                room_zone = getattr(room, "zone", None)
                if room_zone == zone:
                    rooms.append(room)
            
            if channel:
                channel.msg(f"ZONE_LOOKUP: Checking zone '{zone}' - Checked {total_checked} rooms, found {len(rooms)} in zone")
            
            return rooms
        except Exception as e:
            if channel:
                channel.msg(f"ZONE_LOOKUP_ERROR: {zone} - Exception: {e}")
            # Fallback: return empty list on error
            return []


class NPCZoneWandererManager(DefaultScript):
    """
    Global script that manages zone-based wandering for all NPCs.
    
    This is an alternative to attaching a script to each NPC.
    It periodically checks for NPCs that should wander and moves them.
    """
    
    def at_script_creation(self):
        """Initialize the zone wanderer manager."""
        self.key = "npc_zone_wanderer_manager"
        self.desc = "Manages all NPC zone wandering"
        self.interval = 15  # Check every 15 seconds
        self.persistent = True
    
    def at_repeat(self):
        """Called at each interval - manages all NPC wandering."""
        try:
            # Get all NPCs that should wander
            npcs_to_manage = self._get_wandering_npcs()
            
            for npc in npcs_to_manage:
                # Don't move if puppeted
                if getattr(npc.db, "puppeted_by", None):
                    continue
                
                # Don't move if in combat
                if hasattr(npc.ndb, "combat_handler"):
                    continue
                
                # Get zone
                zone = getattr(npc.db, "npc_zone", None)
                if not zone:
                    continue
                
                # Random chance to wander (don't move every interval)
                if randint(1, 10) <= 3:  # 30% chance each interval
                    self._attempt_wander(npc, zone)
        
        except Exception as e:
            # Log error but don't crash
            pass
    
    def _get_wandering_npcs(self):
        """Get all NPCs that have wandering enabled."""
        try:
            npcs = []
            # Query for objects that have wandering enabled
            for obj in ObjectDB.objects.all():
                if (hasattr(obj, "db") and 
                    getattr(obj.db, "is_npc", False) and 
                    getattr(obj.db, "npc_can_wander", False)):
                    npcs.append(obj)
            return npcs
        except:
            return []
    
    def _attempt_wander(self, npc, zone):
        """Attempt to move an NPC within its zone."""
        try:
            zone_rooms = self._get_zone_rooms(zone)
            
            if not zone_rooms:
                return
            
            # Don't move if only one room in zone
            if len(zone_rooms) <= 1:
                return
            
            # Get available destination rooms (not current location)
            available = [r for r in zone_rooms if r != npc.location]
            if not available:
                return
            
            # Choose random destination
            destination = choice(available)
            
            # Verify zone match and move
            if getattr(destination, "zone", None) == zone:
                old_loc = npc.location
                try:
                    npc.location = destination
                    
                    # Send messages
                    if old_loc and hasattr(old_loc, "msg_contents"):
                        old_loc.msg_contents(f"|r{npc.name} wanders away.|n")
                    if hasattr(destination, "msg_contents"):
                        destination.msg_contents(f"|r{npc.name} wanders in.|n")
                except:
                    # Restore location on failure
                    npc.location = old_loc
        
        except Exception as e:
            # Silently fail
            pass
    
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
