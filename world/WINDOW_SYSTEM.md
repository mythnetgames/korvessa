"""
Window System Documentation

A coordinate-based observation system for rooms in Kowloon/Gelatinous.
"""

# Window System Overview

The window system allows builders to create magical windows in rooms that
observe and relay activity from distant rooms specified by coordinates.

## How It Works

### Basic Concept

1. A window is placed in a room (the "observer room")
2. The window is set to observe a target room by coordinates (x, y, z)
3. When characters enter/leave the target room, the window relays messages
   to anyone in the observer room
4. The direction from which the character entered/left is included when available

### Key Components

**Window Typeclass** (`typeclasses/window.py`)
- Stores target coordinates
- Relays movement messages to its location
- Integrates with character movement hooks

**Character Integration** (`typeclasses/characters.py`)
- `at_pre_move()`: Notifies windows when character leaves a room
- `at_post_move()`: Notifies windows when character enters a room
- Automatically finds all windows observing the room coordinates
- Calculates direction based on coordinate differences

**Commands** (`commands/window.py`)
- `attachwindow`: Create a new window in current room
- `removewindow`: Delete all windows in current room
- `windowcoord <x> <y> <z>`: Set window's target coordinates
- `debugwindows`: Show all windows in current room

## Usage Examples

### Creating a Window

```
> attachwindow
Window created. Use 'windowcoord x y z' to set its target.

> windowcoord 5 10 0
Window now observes room at coordinates (5, 10, 0).

> debugwindows
|cWindows in this room:|n
  - window: targets (5, 10, 0)
```

When a character enters the room at (5, 10, 0):
```
Through the window, you see John enter from the south.
```

When they leave:
```
Through the window, you see John leave to the north.
```

### Finding Coordinates

Use the `debugroomcoords` command to see a room's coordinates:
```
> debugroomcoords
Current room coordinates: (5, 10, 0)
```

## Technical Details

### Window Observation Process

1. Character calls `move()` to change location
2. `at_pre_move()` is called on the departing character
3. `_notify_window_observers()` finds all windows observing the current room
4. For each window, `relay_movement()` is called with movement_type='leave'
5. Character moves to new location
6. `at_post_move()` is called on the arriving character
7. `_notify_window_observers()` finds all windows observing the new room
8. For each window, `relay_movement()` is called with movement_type='enter'
9. Direction is calculated based on coordinate differences

### Direction Calculation

Windows automatically determine direction from coordinate changes:
- Moving north: to_y > from_y
- Moving south: to_y < from_y
- Moving east: to_x > from_x
- Moving west: to_x < from_x

### Coordinate System

Rooms use (x, y, z) coordinates:
- x: East/West axis (positive = east)
- y: North/South axis (positive = north)
- z: Vertical axis (positive = up)

Windows observe rooms by exact coordinate match. Both observer and target
rooms must have coordinates defined for windows to function properly.

## Utility Functions

The `world/window_utils.py` module provides helper functions:

```python
from world.window_utils import (
    get_windows_for_location,      # Get windows in a room
    get_windows_observing_coords,  # Get windows watching coordinates
    get_all_windows,               # Get all windows in game
    find_window_by_key,            # Find window by name
    test_window_relay,             # Test relay manually
    clear_all_windows              # Delete all windows (admin)
)
```

## Builders' Tips

1. **Use coordinate-based mapping**: Ensure rooms have coordinates defined
2. **Test with debugwindows**: Verify window setup before placing them
3. **Multiple windows**: You can have multiple windows in the same room
   watching different locations
4. **Direction accuracy**: Ensure rooms are properly positioned in the
   coordinate system for accurate direction messages
5. **Room descriptions**: Add window descriptions to room texts:
   "A large bay window overlooks the distant marketplace."

## Troubleshooting

### Windows Not Showing Messages

1. Verify target room has coordinates: `debugroomcoords`
2. Verify window target is set correctly: `debugwindows`
3. Check character is actually moving to that room
4. Ensure observer room has the window object

### Incorrect Directions

1. Check room coordinates are accurate
2. Verify coordinate differences match expected directions
3. Use map system to verify room layout

### Performance

- Windows perform database queries when characters move
- This is optimized to only query when entering/leaving rooms with coordinates
- Performance impact should be minimal

## Configuration

Window behavior is controlled by:
- Character typeclass: `typeclasses/characters.py`
- Window typeclass: `typeclasses/window.py`
- Commands: `commands/window.py`
- Utilities: `world/window_utils.py`

No external configuration files needed.

## Future Enhancements

Potential improvements:
- Colored/tinted windows (modify message color based on window properties)
- Scrying windows (magical observation with special effects)
- Window blocking (doors/objects blocking the view)
- Message filtering (only show specific types of movement)
- Window persistence (survives server restarts)
- Window linking (create portals between windows)

## Implementation Notes

- Windows use the coordinate system from `typeclasses/rooms.py`
- Integration with character movement is via Evennia's `at_pre_move()` and
  `at_post_move()` hooks
- All window queries are cached and optimized for performance
- Messages use character `get_display_name()` for proper display
- Direction calculation uses simple coordinate comparison (no pathfinding)
