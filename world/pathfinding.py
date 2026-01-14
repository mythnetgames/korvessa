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


def is_exit_passable_for_player(exit_obj, character):
    """
    Check if an exit is passable for a player character.
    
    Args:
        exit_obj: The exit to check
        character: The character trying to pass
        
    Returns:
        bool: True if passable, False if blocked
    """
    if not exit_obj:
        return False
    
    # Check for edge/gap exits - players need special handling
    if getattr(exit_obj.db, "is_edge", False) or getattr(exit_obj.db, "is_gap", False):
        return False
    
    # Check for sky rooms - only allow if character can fly
    if hasattr(exit_obj, 'destination') and exit_obj.destination:
        target_is_sky = getattr(exit_obj.destination.db, "is_sky_room", False)
        if target_is_sky:
            # Check if character can fly
            can_fly = getattr(character.db, "can_fly", False)
            if not can_fly:
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
    if not start_room or not end_room:
        return None
    
    if start_room == end_room:
        return []  # Already there
    
    # BFS queue: (current_room, path_so_far)
    queue = deque([(start_room, [])])
    visited = {start_room.dbref}
    
    while queue:
        current_room, path = queue.popleft()
        
        # Check depth limit
        if len(path) >= max_depth:
            continue
        
        # Explore exits
        if not hasattr(current_room, 'exits'):
            continue
            
        for exit_obj in current_room.exits:
            if not exit_obj or not hasattr(exit_obj, 'destination'):
                continue
                
            dest_room = exit_obj.destination
            if not dest_room:
                continue
            
            # Skip already visited rooms
            if dest_room.dbref in visited:
                continue
            
            # Check passability
            if character and not is_exit_passable_for_player(exit_obj, character):
                continue
            
            # Build new path
            new_path = path + [(exit_obj, dest_room)]
            
            # Check if we reached destination
            if dest_room == end_room:
                return new_path
            
            # Add to queue
            visited.add(dest_room.dbref)
            queue.append((dest_room, new_path))
    
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
