# Connect Command Implementation Summary

## What Was Created

A new `connect` command that allows players to use a digging tool to create bidirectional connections between rooms by their coordinates.

## Files Modified

1. **`commands/connect.py`** (NEW)
   - Full implementation of the CmdConnect class
   - Direction mapping and coordinate calculations
   - Digging tool detection
   - Room lookup by coordinates
   - Exit creation with bidirectional support

2. **`commands/default_cmdsets.py`** (MODIFIED)
   - Added import and registration of CmdConnect in CharacterCmdSet.at_cmdset_creation()

## Files Created for Documentation

1. **`commands/CONNECT_COMMAND.md`**
   - Comprehensive documentation
   - All supported directions
   - Examples and use cases
   - Error messages reference
   - Technical details

2. **`commands/CONNECT_QUICKSTART.md`**
   - Quick start guide
   - Step-by-step instructions
   - Troubleshooting tips

## Command Details

### Command Key
- `connect`
- Alias: `dig`

### Usage
```
connect <direction>
```

### Supported Directions
- Cardinal: north, south, east, west (n, s, e, w)
- Diagonal: northeast, northwest, southeast, southwest (ne, nw, se, sw)
- Vertical: up, down (u, d)

### Requirements
1. Must be holding a digging tool (wielded or equipped)
2. Current room must have coordinates (x, y, z)
3. Target room must exist at the calculated coordinates
4. Both rooms should be in the same zone

### Features
- **Coordinate-based**: Calculates target room coordinates from direction
- **Zone-aware**: Respects zone boundaries
- **Bidirectional**: Automatically creates both forward and return exits
- **Tool flexible**: Detects digging tools by keywords or attributes
- **Safe**: Validates all prerequisites before creating exits
- **Informative**: Provides clear feedback and error messages

### How It Works

1. Validates player has a digging tool equipped
2. Gets current room coordinates (x, y, z)
3. Calculates target coordinates based on direction offset
4. Searches database for room at target coordinates in same zone
5. If found:
   - Creates forward exit in specified direction
   - Creates reverse exit in opposite direction
   - Notifies all parties
6. If not found:
   - Informs player that no room exists there

## Digging Tool Detection

The command recognizes digging tools in multiple ways:

### By Item Key/Name Keywords
Items with keywords: dig, shovel, pickaxe, pick, axe, spade, excavator, tool

### By Database Attribute
Items with `db.tool_type` containing "dig"

### By Hand Equipment
Items currently wielded via the wield command

### By Inventory Tags
Items in inventory with 'equipped' tag in 'combat' category

## Coordinate System

Uses the existing room coordinate system:
- **X**: East/West axis (positive = east)
- **Y**: North/South axis (positive = north)
- **Z**: Vertical axis (positive = up)

### Direction Offsets

```
North:        (0, +1, 0)
South:        (0, -1, 0)
East:         (+1, 0, 0)
West:         (-1, 0, 0)
Northeast:    (+1, +1, 0)
Northwest:    (-1, +1, 0)
Southeast:    (+1, -1, 0)
Southwest:    (-1, -1, 0)
Up:           (0, 0, +1)
Down:         (0, 0, -1)
```

## Integration with Existing Systems

- **Rooms**: Uses standard Room.db.x, Room.db.y, Room.db.z coordinates
- **Exits**: Creates standard Exit objects with proper destinations
- **Items**: Works with any item that contains digging keywords
- **Wield System**: Integrates with existing wield command for equipped item detection
- **Zones**: Respects zone boundaries like other commands

## Error Handling

Comprehensive error checking:
- No digging tool: "You need to be holding a digging tool..."
- Invalid direction: "Unknown direction..."
- No target room: "No room exists at coordinates..."
- Exit exists: "An exit to the... already exists."
- Not in room: "You must be in a room..."

## Example Usage

```
# Player in Room A (0,0,0) with shovel equipped
> connect north

# Creates:
# - Exit "north" from Room A to Room B (0,1,0)
# - Exit "south" from Room B to Room A

# Now player can:
> north    # Move to Room B
> south    # Return to Room A
```

## Related Commands

- `@maproom x y z` - Set room coordinates
- `setcoord x y z` - Alternative coordinate setting
- `zdig <dir> = <name>` - Create new rooms with coordinates
- `wield <item>` - Equip items/tools
- `look` - View room and exits

## Testing Recommendations

1. Create test rooms with known coordinates
2. Create a digging tool item
3. Equip the tool
4. Test each direction (n, s, e, w, ne, nw, se, sw, u, d)
5. Verify bidirectional exits are created
6. Verify without tool equipped, command fails
7. Verify connecting non-existent rooms fails with clear message

## Future Enhancement Possibilities

- Animation/emote during digging
- Stamina cost for using digging tool
- Delay before exit creation (simulating digging time)
- Different tool speeds
- Damage degradation on tools
- Skill checks for success/failure
- Noise/disturbance alerts
- Permission-based access (zones, areas)
