"""
Pathfinding Utilities

Provides pathfinding functions for both NPC wandering and player auto-walk.
Uses BFS to find shortest paths across the entire room graph, supporting
cross-zone travel.
"""

from collections import deque
from evennia.objects.models import ObjectDB


def get_all_rooms():
    """
    Get all room objects in the game.
    
    Returns:
        list: All Room objects
    """
    rooms = []
    for obj in ObjectDB.objects.filter(db_typeclass_path__contains="rooms.Room"):
        if hasattr(obj, 'exits'):
            rooms.append(obj)
    return rooms


def is_exit_passable_for_player(exit_obj, character, debug_channel=None):
    """
    Check if an exit is passable for a player character.
    
    Args:
        exit_obj: The exit to check
        character: The character trying to pass
        debug_channel: Optional channel for debug output
        
    Returns:
        bool: True if passable, False if blocked
    """
    def debug_msg(msg):
        if debug_channel:
            try:
                debug_channel.msg(f"PASSABLE: {msg}")
            except Exception:
                pass
    
    if not exit_obj:
        debug_msg("exit_obj is None")
        return False
    
    # Check if character is locked by someone aiming at them
    if character:
        aimer = getattr(character.ndb, "aimed_at_by", None)
        if aimer:
            # Check if the aimer is still valid and in the same location
            if aimer.location and aimer.location == character.location:
                debug_msg(f"{exit_obj.key}: blocked - character locked by {aimer.key}'s aim")
                return False  # Character is locked by aim
    
    # Check for edge/gap exits - players need special handling
    if getattr(exit_obj.db, "is_edge", False) or getattr(exit_obj.db, "is_gap", False):
        debug_msg(f"{exit_obj.key}: blocked - edge/gap exit")
        return False
    
    # Check for sky rooms - only allow if character can fly
    if hasattr(exit_obj, 'destination') and exit_obj.destination:
        target_is_sky = getattr(exit_obj.destination.db, "is_sky_room", False)
        if target_is_sky:
            # Check if character can fly
            can_fly = getattr(character.db, "can_fly", False) if character else False
            if not can_fly:
                return False
    
    # Check for housing doors (CubeDoor or PadDoor)
    # These can be passed if the door is open/unlocked OR if character is the renter
    try:
        is_cube_door = exit_obj.is_typeclass("typeclasses.cube_housing.CubeDoor")
    except Exception:
        is_cube_door = False
    
    if is_cube_door:
        # Check if door is open (not closed)
        is_closed = getattr(exit_obj, 'is_closed', True)
        # Check paired door state too
        paired_door_id = getattr(exit_obj.db, 'paired_door_id', None)
        if not is_closed and paired_door_id:
            from evennia.objects.models import ObjectDB
            try:
                paired = ObjectDB.objects.get(id=paired_door_id)
                if paired and hasattr(paired, 'is_closed'):
                    is_closed = paired.is_closed
            except ObjectDB.DoesNotExist:
                pass
        
        if is_closed:
            # Check if character is the renter (they can pass their own door)
            renter_id = getattr(exit_obj, 'current_renter_id', None)
            if character and renter_id and character.id == renter_id:
                return True  # Renter can always pass their own door
            return False  # Door is locked
        return True  # Door is open
    
    try:
        is_pad_door = exit_obj.is_typeclass("typeclasses.pad_housing.PadDoor")
    except Exception:
        is_pad_door = False
    
    if is_pad_door:
        # Check if door is unlocked
        is_unlocked = getattr(exit_obj, 'is_unlocked', False)
        # Check paired door state too
        paired_door_id = getattr(exit_obj.db, 'paired_door_id', None)
        if not is_unlocked and paired_door_id:
            from evennia.objects.models import ObjectDB
            try:
                paired = ObjectDB.objects.get(id=paired_door_id)
                if paired and hasattr(paired, 'is_unlocked'):
                    is_unlocked = paired.is_unlocked
            except ObjectDB.DoesNotExist:
                pass
        
        if not is_unlocked:
            # Check if character is the renter (they can pass their own door)
            renter_id = getattr(exit_obj, 'current_renter_id', None)
            if character and renter_id and character.id == renter_id:
                return True  # Renter can always pass their own door
            return False  # Door is locked
        return True  # Door is unlocked
    
    # Check for regular door blocking
    direction = exit_obj.key.lower()
    room = exit_obj.location
    
    try:
        from commands.door import find_door
        door = find_door(room, direction) if find_door else None
        if door and not getattr(door.db, "is_open", True):
            return False  # Door is closed
    except (ImportError, Exception):
        pass
    
    return True


def find_path(start_room, end_room, character=None, max_depth=100):
    """
    Find the shortest path between two rooms using BFS.
    Works across zones.
    
    Args:
        start_room: Starting room object
        end_room: Destination room object
        character: Character traveling (for passability checks)
        max_depth: Maximum path length to search
        
    Returns:
        list: List of (exit_obj, destination_room) tuples representing the path,
              or None if no path found
    """
    # Get debug channel
    debug_channel = None
    try:
        from evennia.comms.models import ChannelDB
        debug_channel = ChannelDB.objects.get_channel("Pathing")
    except Exception:
        pass
    
    def debug_msg(msg):
        if debug_channel:
            try:
                debug_channel.msg(f"PATHFIND: {msg}")
            except Exception:
                pass
    
    if not start_room or not end_room:
        debug_msg(f"Invalid rooms: start={start_room}, end={end_room}")
        return None
    
    # Get dbrefs safely
    try:
        start_dbref = start_room.dbref
        end_dbref = end_room.dbref
    except Exception as e:
        debug_msg(f"Failed to get dbrefs: {e}")
        return None
    
    if start_dbref == end_dbref:
        return []  # Already there
    
    debug_msg(f"START: {start_room.key}({start_dbref}) -> {end_room.key}({end_dbref})")
    
    # BFS queue: (current_room, path_so_far)
    queue = deque([(start_room, [])])
    visited = {start_dbref}
    
    rooms_checked = 0
    exits_blocked = 0
    
    while queue:
        current_room, path = queue.popleft()
        rooms_checked += 1
        
        # Check depth limit
        if len(path) >= max_depth:
            continue
        
        # Explore exits
        try:
            room_exits = current_room.exits
        except Exception:
            continue
        
        if not room_exits:
            continue
            
        for exit_obj in room_exits:
            if not exit_obj:
                continue
            
            try:
                dest_room = exit_obj.destination
            except Exception:
                continue
                
            if not dest_room:
                continue
            
            # Get dest dbref safely
            try:
                dest_dbref = dest_room.dbref
            except Exception:
                continue
            
            # Skip already visited rooms
            if dest_dbref in visited:
                continue
            
            # Check passability
            if character:
                try:
                    passable = is_exit_passable_for_player(exit_obj, character, debug_channel)
                except Exception as e:
                    debug_msg(f"Passability check error: {e}")
                    passable = True  # Default to passable on error
                
                if not passable:
                    exits_blocked += 1
                    debug_msg(f"EXIT BLOCKED: {exit_obj.key} to {dest_room.key}")
                    continue
            
            # Build new path
            new_path = path + [(exit_obj, dest_room)]
            
            # Check if we reached destination (compare by dbref for reliability)
            if dest_dbref == end_dbref:
                debug_msg(f"FOUND: {len(new_path)} steps, {rooms_checked} rooms checked, {exits_blocked} exits blocked")
                return new_path
            
            # Add to queue
            visited.add(dest_dbref)
            queue.append((dest_room, new_path))
    
    debug_msg(f"NOT FOUND: {rooms_checked} rooms checked, {exits_blocked} blocked, {len(visited)} visited")
    return None  # No path found


def find_path_by_dbref(start_dbref, end_dbref, character=None, max_depth=100):
    """
    Find path using room dbrefs instead of objects.
    
    Args:
        start_dbref: Starting room dbref (e.g., "#123")
        end_dbref: Destination room dbref
        character: Character traveling (for passability checks)
        max_depth: Maximum path length
        
    Returns:
        list: Path as list of (exit_obj, destination_room) tuples, or None
    """
    from evennia import search_object
    
    # Resolve dbrefs to room objects
    start_results = search_object(start_dbref)
    end_results = search_object(end_dbref)
    
    if not start_results or not end_results:
        return None
    
    return find_path(start_results[0], end_results[0], character, max_depth)


def get_path_directions(path):
    """
    Convert a path to a list of direction strings.
    
    Args:
        path: List of (exit_obj, destination_room) tuples
        
    Returns:
        list: List of direction strings (exit keys)
    """
    return [exit_obj.key for exit_obj, _ in path]


def estimate_path_stamina_cost(path, movement_mode="walk"):
    """
    Estimate stamina cost for a path based on movement mode.
    
    Args:
        path: List of (exit_obj, destination_room) tuples
        movement_mode: "walk", "jog", "run", or "sprint"
        
    Returns:
        float: Estimated stamina cost
    """
    # Base costs per step by movement mode
    costs = {
        "walk": 0.5,
        "jog": 2.0,
        "run": 4.0,
        "sprint": 8.0
    }
    
    cost_per_step = costs.get(movement_mode, 0.5)
    return len(path) * cost_per_step


def validate_saved_location(character, alias):
    """
    Validate that a saved location alias still points to a valid room.
    
    Args:
        character: The character with saved locations
        alias: The alias to validate
        
    Returns:
        tuple: (is_valid, room_obj_or_error_msg)
    """
    saved_locations = getattr(character.db, 'path_locations', {}) or {}
    
    if alias not in saved_locations:
        return (False, f"No location saved with alias '{alias}'.")
    
    room_dbref = saved_locations[alias]
    
    from evennia import search_object
    results = search_object(room_dbref)
    
    if not results:
        return (False, f"Saved location '{alias}' no longer exists (room deleted).")
    
    room = results[0]
    
    # Verify it's still a room
    if not hasattr(room, 'exits'):
        return (False, f"Saved location '{alias}' is no longer a valid room.")
    
    return (True, room)
