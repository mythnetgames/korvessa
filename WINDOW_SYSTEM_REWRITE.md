"""
Window System Rewrite - Complete Implementation Summary
"""

# CHANGES MADE

This document summarizes the complete rewrite of the window system to make it
fully functional.

## Files Modified

### 1. typeclasses/window.py (REWRITTEN)
**Changes:**
- Complete cleanup of Window typeclass
- Added proper `get_target_coords()` method
- Fixed `relay_movement()` to use proper display names
- Removed debug print statements
- Added comprehensive docstrings
- Now properly integrates with character movement

**Key Methods:**
- `set_target_coords(x, y, z)` - Set observation target
- `get_target_coords()` - Retrieve observation target
- `relay_movement(char, movement_type, direction)` - Relay messages

### 2. commands/window.py (REWRITTEN)
**Changes:**
- Completely rewrote all four command classes
- Removed duplicate code and conflicting implementations
- Consolidated from three separate files into one organized module
- Added proper error handling
- Added comprehensive docstrings and usage examples
- Fixed command logic

**Commands:**
- `CmdAttachWindow` - Create a new window (refined)
- `CmdRemoveWindow` - Delete windows (refined)
- `CmdWindowCoord` - Set target coordinates (refined)
- `CmdDebugWindows` - Show window status (refined)

### 3. typeclasses/characters.py (ENHANCED)
**Changes:**
- Added `at_pre_move()` hook to notify windows of departure
- Enhanced `at_post_move()` to notify windows of arrival
- Added `_notify_window_observers()` method - finds and notifies relevant windows
- Added `_get_direction_from_rooms()` method - calculates direction from coordinates
- Windows now properly integrated into character movement

**New Methods:**
- `_notify_window_observers(movement_type, previous_location)` - Main notification handler
- `_get_direction_from_rooms(from_room, to_room)` - Direction calculation

### 4. commands/default_cmdsets.py (UPDATED)
**Changes:**
- Fixed broken imports at top of file
- Consolidated window command imports from scattered locations
- Added all four window commands to CharacterCmdSet
- Proper import: `from commands.window import CmdAttachWindow, CmdRemoveWindow, CmdWindowCoord, CmdDebugWindows`

### 5. commands/attachwindow.py (DEPRECATED)
**Changes:**
- Marked as deprecated
- Replaced by consolidated commands/window.py
- Old functionality moved to main window.py

### 6. commands/removewindow.py (DEPRECATED)
**Changes:**
- Marked as deprecated
- Replaced by consolidated commands/window.py
- Old functionality moved to main window.py

### 7. commands/debugwindows.py (DEPRECATED)
**Changes:**
- Removed from imports in default_cmdsets.py
- Replaced by consolidated commands/window.py

## New Files Created

### 1. world/window_utils.py (NEW)
**Purpose:** Utility functions for window operations
**Functions:**
- `get_windows_for_location(location)` - Get windows in a room
- `get_windows_observing_coords(x, y, z)` - Get windows watching coordinates
- `get_all_windows()` - Get all windows in game
- `find_window_by_key(key)` - Find window by name
- `test_window_relay(window, char, movement_type, direction)` - Manual relay testing
- `clear_all_windows()` - Delete all windows (admin)

### 2. commands/window_test.py (NEW)
**Purpose:** Testing and debugging commands for builders
**Commands:**
- `windowtest [show | coords]` - Display window information
- `windowdebugmove [on | off]` - Enable movement debugging
- `listwindowsobs <x> <y> <z>` - List windows observing coordinates

### 3. world/WINDOW_SYSTEM.md (NEW)
**Purpose:** Comprehensive documentation for builders
**Contents:**
- System overview and how it works
- Basic usage examples
- Technical details
- Utility functions reference
- Troubleshooting guide
- Future enhancement ideas

## How the System Now Works

### Movement Flow

1. **Character moves:**
   ```
   character.move(destination)
   ```

2. **at_pre_move() called:**
   ```
   - Current location coordinates checked
   - All windows observing current location found
   - relay_movement() called for each with movement_type='leave'
   ```

3. **Character relocates**

4. **at_post_move() called:**
   ```
   - New location coordinates checked
   - All windows observing new location found
   - Direction calculated from coordinate difference
   - relay_movement() called for each with movement_type='enter', direction
   ```

5. **Window relays message:**
   ```
   "Through the window, you see John enter from the south."
   ```

### Coordinate System

- Rooms have (x, y, z) coordinates in `db.x`, `db.y`, `db.z`
- Windows observe rooms by exact coordinate match
- Direction calculated automatically from coordinate differences:
  - North: to_y > from_y
  - South: to_y < from_y
  - East: to_x > from_x
  - West: to_x < from_x

## Setup Requirements

For windows to work properly:

1. **Rooms must have coordinates:**
   - Use `debugroomcoords` to check
   - Coordinates should be set via the mapping system
   - x, y coordinates are required; z defaults to 0

2. **Windows must be attached to rooms:**
   - Use `attachwindow` to create
   - Use `windowcoord x y z` to set target
   - Use `debugwindows` to verify

3. **Characters must move between rooms:**
   - Movement triggers the observation system
   - Only works when characters move to different rooms
   - Requires coordinate system to be in place

## Testing

### Quick Test

1. Create two rooms with coordinates (5, 10, 0) and (5, 11, 0)
2. In first room: `attachwindow`
3. In first room: `windowcoord 5 11 0`
4. Have character move to second room
5. Should see: "Through the window, you see [Character] enter from the south."

### Debug Test

1. Enable debugging: `windowdebugmove on`
2. Move to another room
3. Check console for debug output
4. Use `windowtest show` to see all windows
5. Use `listwindowsobs x y z` to see who's watching

## Performance Considerations

- Window queries run only when characters move
- Database query limited to Window typeclasses
- Optimized to skip if location has no coordinates
- Direction calculation is simple coordinate comparison
- Message sending uses Evennia's efficient msg_contents()
- No persistent polling or timers

## Backward Compatibility

- Old window.py, attachwindow.py, removewindow.py still exist (deprecated)
- New system completely replaces old functionality
- No data migration needed
- Old windows can be deleted with `removewindow` command

## Known Limitations

1. Windows work only when rooms have coordinates defined
2. Direction calculation is based on simple coordinate math (no diagonal directions)
3. Windows show ALL character movement (no filtering)
4. Messages are generic (no customization per window)
5. No permission system (all builders can create windows)

## Future Enhancements

- Colored/tinted messages based on window type
- Scrying/magic observation with special effects
- Message filtering (only show specific actions)
- Window permissions system
- Persistent window configuration
- Portal linking between windows
- Animated movements through windows

## Testing Checklist

- [x] Window creation works
- [x] Window coordinate setting works
- [x] Window debugging commands work
- [x] Character entry triggers messages
- [x] Character exit triggers messages
- [x] Direction calculation works
- [x] Multiple windows in same location work
- [x] Windows observing same location work
- [x] No syntax errors
- [x] Proper error handling
- [x] Documentation complete

## Troubleshooting Common Issues

### Windows not showing messages
- Verify rooms have coordinates: `debugroomcoords`
- Verify window target matches room coordinates: `debugwindows`
- Check character actually moves to that room
- Verify window object exists in observer room

### Wrong directions shown
- Check room coordinates are accurate
- Verify coordinate system matches game layout
- Use map system to verify positions

### Performance issues
- Check how many windows exist: `windowtest show`
- Monitor server load during movement
- Consider reducing number of windows if needed

---

**Window System Status: FULLY FUNCTIONAL**

All components are now integrated and working together. The system
automatically notifies windows when characters move, calculates proper
directions, and relays messages to observers.
