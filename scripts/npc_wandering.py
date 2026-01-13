"""
NPC Wandering Script

This script handles NPC wandering behavior within restricted zones.
NPCs will pick a destination in their zone and pathfind towards it,
using real exits and respecting doors and zone boundaries.
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


def is_exit_passable(exit_obj, npc):
    """
    Check if an exit is passable (not blocked by a closed door, edge, gap, or sky room).
    
    Args:
        exit_obj: The exit to check
        npc: The NPC trying to pass
        
    Returns:
        bool: True if passable, False if blocked
    """
    if not exit_obj:
        return False
    
    # Check for edge/gap exits - NPCs cannot use these
    if getattr(exit_obj.db, "is_edge", False) or getattr(exit_obj.db, "is_gap", False):
        return False
    
    # Check for sky rooms - NPCs cannot enter or exit sky rooms normally
    if hasattr(exit_obj, 'destination') and exit_obj.destination:
        target_is_sky = getattr(exit_obj.destination.db, "is_sky_room", False)
        if target_is_sky:
            return False
    
    current_is_sky = getattr(npc.location.db, "is_sky_room", False) if npc.location else False
    if current_is_sky:
        return False
    
    # Check for door blocking
    direction = exit_obj.key.lower()
    room = exit_obj.location
    
    try:
        from commands.door import find_door
        door = find_door(room, direction) if find_door else None
        if door and not getattr(door.db, "is_open", True):
            return False  # Door is closed
    except ImportError:
        pass  # No door system
    
    return True


class NPCWanderingScript(DefaultScript):
    """
    Script that manages NPC wandering within a zone.
    
    NPCs pick a destination coordinate and pathfind towards it.
    They respect doors, zone boundaries, and only use real exits.
    """
    
    def at_script_creation(self):
        """Initialize the wandering script."""
        self.key = "npc_wandering"
        self.desc = "Handles NPC wandering behavior"
        self.interval = 15  # Check every 15 seconds
        self.persistent = True
    
    def at_repeat(self):
        """Called at each interval - handles the wandering logic."""
        obj = self.obj  # The NPC this script is attached to
        
        if not obj:
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
            if handler and hasattr(handler, 'is_active') and handler.is_active:
                combatants = getattr(handler.db, 'combatants', [])
                is_in_combat = any(entry.get('char') == obj for entry in combatants)
                
                if not is_in_combat:
                    delattr(obj.ndb, "combat_handler")
                    if channel:
                        channel.msg(f"CLEANUP: Removed stale combat_handler reference from {obj.name}")
            else:
                delattr(obj.ndb, "combat_handler")
                if channel:
                    channel.msg(f"CLEANUP: Removed dead combat_handler reference from {obj.name}")
        
        # If blocked by puppeting or combat, report it and return
        if is_puppeted or is_in_combat:
            location = obj.location.key if obj.location else "unknown"
            blocked_by = "PUPPETED" if is_puppeted else "COMBAT"
            if channel:
                channel.msg(f"TICK: {obj.name} in {location} ({zone}) - BLOCKED BY {blocked_by}")
            return
        
        # Check if we have a destination
        dest_x = getattr(obj.ndb, 'wander_dest_x', None)
        dest_y = getattr(obj.ndb, 'wander_dest_y', None)
        
        # 1/50 chance to pick a new destination (or if we don't have one)
        roll = randint(1, 50)
        location = obj.location.key if obj.location else "unknown"
        
        if roll == 1 or dest_x is None or dest_y is None:
            # Pick new destination
            if channel:
                channel.msg(f"TICK: {obj.name} in {location} ({zone}) - ROLL({roll}/50) -> Pick new destination")
            self._pick_new_destination(obj, zone)
        
        # Always try to move toward current destination (if we have one)
        dest_x = getattr(obj.ndb, 'wander_dest_x', None)
        dest_y = getattr(obj.ndb, 'wander_dest_y', None)
        
        if dest_x is not None and dest_y is not None:
            if channel:
                channel.msg(f"TICK: {obj.name} in {location} ({zone}) - Moving toward ({dest_x},{dest_y})")
            self._pathfind_step(obj, zone)
        else:
            if channel:
                channel.msg(f"TICK: {obj.name} in {location} ({zone}) - No destination, waiting for next roll")
    
    def _pathfind_step(self, npc, zone):
        """
        Take one step towards the NPC's destination, or pick a new destination.
        
        Args:
            npc: The NPC character object
            zone: The zone identifier string
        """
        import time
        from random import uniform
        
        channel = get_or_create_channel("wanderers")
        
        current_room = npc.location
        if not current_room:
            if channel:
                channel.msg(f"PATH_FAIL: {npc.name} - No current location")
            return
        
        # Clean up stale combat handler FIRST before any other checks
        if hasattr(npc.ndb, 'combat_handler'):
            handler = npc.ndb.combat_handler
            if not handler or not getattr(handler, 'is_active', False):
                delattr(npc.ndb, 'combat_handler')
                if channel:
                    channel.msg(f"PATH_CLEANUP: {npc.name} - Cleared stale combat_handler")
        
        # Clear any movement lock that shouldn't be there
        if hasattr(npc.ndb, '_movement_locked'):
            delattr(npc.ndb, '_movement_locked')
        
        # Rate limiting: Require 1-2 seconds between moves (variable)
        last_move_time = getattr(npc.ndb, 'last_pathfind_move', None)
        if last_move_time is None:
            last_move_time = 0
        
        # Get variable rate limit (1-2 seconds) with proper defaults
        min_interval = getattr(npc.ndb, 'move_interval_min', None) or 1.0
        max_interval = getattr(npc.ndb, 'move_interval_max', None) or 2.0
        rate_limit = uniform(min_interval, max_interval)
        
        current_time = time.time()
        time_since_last = current_time - last_move_time
        
        if time_since_last < rate_limit:
            # Too soon since last move, skip this step
            if channel:
                channel.msg(f"PATH_RATE_LIMIT: {npc.name} - Only {time_since_last:.1f}s since last move (need {rate_limit:.1f}s)")
            return
        
        # Get or set destination
        dest_x = getattr(npc.ndb, 'wander_dest_x', None)
        dest_y = getattr(npc.ndb, 'wander_dest_y', None)
        dest_z = getattr(npc.ndb, 'wander_dest_z', None)
        
        # Check if we need a new destination
        current_x = getattr(current_room.db, 'x', None)
        current_y = getattr(current_room.db, 'y', None)
        current_z = getattr(current_room.db, 'z', None)
        
        if channel:
            channel.msg(f"PATH_DEST_CHECK: {npc.name} - current=({current_x},{current_y},{current_z}), dest=({dest_x},{dest_y},{dest_z})")
        
        need_new_dest = False
        if dest_x is None or dest_y is None:
            if channel:
                channel.msg(f"PATH_NO_DEST: {npc.name} - No destination set, waiting for roll to pick one")
            return
        elif current_x == dest_x and current_y == dest_y:
            # Check z coordinate if it was specified
            if dest_z is not None:
                if current_z != dest_z:
                    # Haven't reached z yet
                    if channel:
                        channel.msg(f"PATH_Z_MISMATCH: {npc.name} - At ({current_x},{current_y}) but z={current_z}, need z={dest_z}")
                else:
                    # Reached full 3D destination
                    if channel:
                        channel.msg(f"PATH_ARRIVED: {npc.name} reached destination ({dest_x},{dest_y},{dest_z})")
                    # Clear destination and stop moving - wait for next roll to pick new one
                    npc.ndb.wander_dest_x = None
                    npc.ndb.wander_dest_y = None
                    npc.ndb.wander_dest_z = None
                    return
            else:
                # No z specified, 2D destination reached
                if channel:
                    channel.msg(f"PATH_ARRIVED: {npc.name} reached destination ({dest_x},{dest_y})")
                # Clear destination and stop moving - wait for next roll to pick new one
                npc.ndb.wander_dest_x = None
                npc.ndb.wander_dest_y = None
                npc.ndb.wander_dest_z = None
                return
        
        # Find best exit towards destination
        best_exit = self._find_best_exit(npc, zone, dest_x, dest_y, dest_z)
        
        if not best_exit:
            # Can't reach destination from here, pick a new one
            if channel:
                channel.msg(f"PATH_BLOCKED: {npc.name} - No valid exits towards ({dest_x},{dest_y}), picking new destination")
            self._pick_new_destination(npc, zone)
            return
        
        exit_obj, destination = best_exit
        
        if channel:
            channel.msg(f"PATH_STEP: {npc.name} - Taking '{exit_obj.key}' towards ({dest_x},{dest_y})")
            channel.msg(f"PATH_DEST_OBJ: {npc.name} - destination object is {destination}")
        
        # Move the NPC using move_to
        try:
            # Store original location before moving
            original_location = npc.location
            
            if channel:
                channel.msg(f"PATH_BEFORE_MOVE: {npc.name} at {original_location}")
            
            # Call move_to with normal hooks enabled so at_post_move fires and sends messages
            try:
                result = npc.move_to(destination, quiet=False)
                if channel:
                    channel.msg(f"PATH_MOVE_RESULT: {npc.name} - move_to returned {result}")
            except Exception as move_err:
                if channel:
                    channel.msg(f"PATH_MOVE_ERROR: {npc.name} - move_to raised exception: {move_err}")
                result = False
            
            # Check if movement actually occurred
            if result and npc.location and npc.location != original_location:
                # Update last move timestamp only on successful move
                import time
                npc.ndb.last_pathfind_move = time.time()
                
                # Handle followers after successful move
                try:
                    from scripts.follow_system import handle_character_move
                    handle_character_move(npc, npc.location, original_location)
                except Exception as follow_err:
                    # Log follow failure but don't break NPC movement
                    if channel:
                        channel.msg(f"PATH_FOLLOW_ERROR: {npc.name} - Failed to move followers: {follow_err}")
                
                if channel:
                    channel.msg(f"PATH_SUCCESS: {npc.name} moved via '{exit_obj.key}' to '{npc.location.key}'")
            else:
                # Movement failed - don't pick a new destination, just log and return
                # The NPC will retry on the next tick with the same destination
                if channel:
                    channel.msg(f"PATH_BLOCKED: {npc.name} - move_to returned {result}, will retry next tick")
        except Exception as e:
            import traceback
            if channel:
                channel.msg(f"PATH_ERROR: {npc.name} - Failed to move: {e}")
                channel.msg(f"PATH_TRACEBACK: {traceback.format_exc()}")
    
    def _pick_new_destination(self, npc, zone):
        """
        Pick a new random destination coordinate within the zone.
        
        Args:
            npc: The NPC character object
            zone: The zone identifier string
        """
        channel = get_or_create_channel("wanderers")
        
        # Get all rooms in zone
        zone_rooms = self._get_zone_rooms(zone)
        
        if not zone_rooms:
            if channel:
                channel.msg(f"PATH_FAIL: {npc.name} - No rooms in zone '{zone}'")
            return
        
        # Filter to rooms with valid coordinates
        rooms_with_coords = []
        for room in zone_rooms:
            x = getattr(room.db, 'x', None)
            y = getattr(room.db, 'y', None)
            if x is not None and y is not None:
                rooms_with_coords.append((room, x, y))
        
        if not rooms_with_coords:
            if channel:
                channel.msg(f"PATH_FAIL: {npc.name} - No rooms with coordinates in zone '{zone}'")
            return
        
        # Pick a random room as destination (not current room if possible)
        current_room = npc.location
        other_rooms = [(r, x, y) for r, x, y in rooms_with_coords if r != current_room]
        
        if other_rooms:
            dest_room, dest_x, dest_y = choice(other_rooms)
        else:
            # Only one room in zone
            dest_room, dest_x, dest_y = rooms_with_coords[0]
        
        # Store destination
        npc.ndb.wander_dest_x = dest_x
        npc.ndb.wander_dest_y = dest_y
        
        if channel:
            channel.msg(f"PATH_NEW_DEST: {npc.name} - New destination: '{dest_room.key}' ({dest_x},{dest_y})")
    
    def _find_best_exit(self, npc, zone, dest_x, dest_y, dest_z=None):
        """
        Find the best exit to move closer to the destination.
        
        Args:
            npc: The NPC character object
            zone: The zone identifier string
            dest_x: Destination X coordinate
            dest_y: Destination Y coordinate
            dest_z: Destination Z coordinate (optional)
            
        Returns:
            Tuple of (exit_obj, destination_room) or None if no valid exit
        """
        current_room = npc.location
        if not current_room or not hasattr(current_room, 'exits'):
            return None
        
        current_x = getattr(current_room.db, 'x', None)
        current_y = getattr(current_room.db, 'y', None)
        current_z = getattr(current_room.db, 'z', None)
        
        if current_x is None or current_y is None:
            return None
        
        # Calculate current distance to destination
        current_dist = abs(dest_x - current_x) + abs(dest_y - current_y)
        if dest_z is not None and current_z is not None:
            current_dist += abs(dest_z - current_z)
        
        # Find all valid exits that get us closer
        valid_exits = []
        
        for exit_obj in current_room.exits:
            if not exit_obj or not hasattr(exit_obj, 'destination'):
                continue
            
            dest_room = exit_obj.destination
            if not dest_room:
                continue
            
            # Check zone
            room_zone = getattr(dest_room, 'zone', None)
            if room_zone != zone:
                continue
            
            # Check if exit is passable (not blocked by door)
            if not is_exit_passable(exit_obj, npc):
                continue
            
            # Get destination room coordinates
            room_x = getattr(dest_room.db, 'x', None)
            room_y = getattr(dest_room.db, 'y', None)
            room_z = getattr(dest_room.db, 'z', None)
            
            if room_x is None or room_y is None:
                continue
            
            # Calculate distance from that room to final destination
            new_dist = abs(dest_x - room_x) + abs(dest_y - room_y)
            if dest_z is not None and room_z is not None:
                new_dist += abs(dest_z - room_z)
            
            # Only consider exits that get us closer (or maintain distance with some randomness)
            if new_dist < current_dist:
                valid_exits.append((exit_obj, dest_room, new_dist))
            elif new_dist == current_dist:
                # Allow lateral movement with lower priority
                valid_exits.append((exit_obj, dest_room, new_dist + 0.5))
        
        if not valid_exits:
            return None
        
        # Sort by distance and pick the best (or random among equally good)
        valid_exits.sort(key=lambda x: x[2])
        best_dist = valid_exits[0][2]
        best_exits = [(e, r) for e, r, d in valid_exits if d == best_dist]
        
        return choice(best_exits)
    
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
