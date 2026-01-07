"""
Window System Utilities

Provides utility functions for the window observation system.
"""

from evennia.objects.models import ObjectDB


def get_windows_for_location(location):
    """
    Get all windows in a specific location.

    Args:
        location: Room object

    Returns:
        List of Window objects in that location
    """
    if not location:
        return []

    return [obj for obj in location.contents
            if obj.is_typeclass("typeclasses.window.Window", exact=True)]


def get_windows_observing_coords(x, y, z):
    """
    Get all windows that observe a specific room coordinate.

    Args:
        x, y, z: Room coordinates

    Returns:
        List of Window objects observing those coordinates
    """
    all_windows = ObjectDB.objects.filter(db_typeclass_path='typeclasses.window.Window')
    observing_windows = []

    for window in all_windows:
        try:
            if (window.db.target_x == x and
                window.db.target_y == y and
                window.db.target_z == z):
                observing_windows.append(window)
        except (AttributeError, TypeError):
            pass

    return observing_windows


def get_all_windows():
    """
    Get all window objects in the game.

    Returns:
        List of all Window objects
    """
    return ObjectDB.objects.filter(db_typeclass_path='typeclasses.window.Window')


def find_window_by_key(key):
    """
    Find a window by its key/name.

    Args:
        key: Window key/name

    Returns:
        Window object or None
    """
    try:
        return ObjectDB.objects.get(db_typeclass_path='typeclasses.window.Window', db_key=key)
    except (ObjectDB.DoesNotExist, ObjectDB.MultipleObjectsReturned):
        return None


def test_window_relay(window, char, movement_type, direction=None):
    """
    Test window relay manually (for debugging).

    Args:
        window: Window object
        char: Character moving
        movement_type: 'enter' or 'leave'
        direction: Optional direction string
    """
    window.relay_movement(char, movement_type, direction)


def clear_all_windows():
    """
    Delete all windows in the game (DESTRUCTIVE - for admin use only).

    Returns:
        Number of windows deleted
    """
    windows = get_all_windows()
    count = len(windows)

    for window in windows:
        window.delete()

    return count
