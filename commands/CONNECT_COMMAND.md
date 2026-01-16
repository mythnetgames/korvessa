# Connect Command Documentation

## Overview

The `connect` command allows you to use a digging tool to connect two rooms together by their coordinates. This is useful for creating exits between rooms that already exist at calculated coordinate positions.

## Prerequisites

1. **You must be holding a digging tool** - The command will check for items with keywords like:
   - "dig", "shovel", "pickaxe", "pick", "axe", "spade", "excavator", "tool"
   - Or items with a `tool_type` database attribute containing "dig"

2. **Source room must have coordinates** - The room you are in must have x, y, z coordinates set

3. **Target room must exist** - A room must already exist at the calculated coordinates

## Usage

```
connect <direction>
```

### Supported Directions

**Cardinal Directions:**
- `north` (or `n`)
- `south` (or `s`)
- `east` (or `e`)
- `west` (or `w`)

**Diagonal Directions:**
- `northeast` (or `ne`)
- `northwest` (or `nw`)
- `southeast` (or `se`)
- `southwest` (or `sw`)

**Vertical Directions:**
- `up` (or `u`)
- `down` (or `d`)

## Examples

```
connect north      - Connect to room north of current location
connect e          - Connect to room east of current location
connect up         - Connect to room above current location
connect southeast  - Connect to room southeast of current location
```

## How It Works

1. **Calculates target coordinates** based on the direction and your current room's coordinates
2. **Searches for a room** at those exact coordinates in the same zone
3. **If found**: Creates bidirectional exits between the current room and target room
   - Exit from current room -> target room (in the specified direction)
   - Return exit from target room -> current room (opposite direction)
4. **If not found**: The command fails and reports that no room exists at those coordinates

## Coordinate System

The coordinate system uses:
- **X axis**: East/West (positive = east)
- **Y axis**: North/South (positive = north)
- **Z axis**: Vertical (positive = up)

### Direction Offsets

- North: (0, +1, 0)
- South: (0, -1, 0)
- East: (+1, 0, 0)
- West: (-1, 0, 0)
- Northeast: (+1, +1, 0)
- Northwest: (-1, +1, 0)
- Southeast: (+1, -1, 0)
- Southwest: (-1, -1, 0)
- Up: (0, 0, +1)
- Down: (0, 0, -1)

## Error Messages

| Message | Meaning |
|---------|---------|
| "You need to be holding a digging tool to use this command." | No digging tool found in inventory or equipped |
| "Unknown direction: {direction}" | Invalid direction specified |
| "No room exists at coordinates (x, y, z)." | No room found at target coordinates |
| "An exit to the {direction} already exists." | Exit already connects these rooms |
| "You must be in a room to use this command." | You're not in a valid location |

## Creating a Digging Tool

To create an item that works as a digging tool:

```
@create Tool Name:typeclasses.items.Item
@set tool_name/key = shovel
@set tool_name/worn_desc = is holding a shovel
```

Or with a tool_type attribute:

```
@create Excavator:typeclasses.items.Item
@set excavator/db.tool_type = digging_tool
```

## Example Workflow

1. Create two separate rooms at known coordinates:
   ```
   Room A at (0, 0, 0)
   Room B at (1, 0, 0)
   ```

2. Move to Room A and equip your digging tool:
   ```
   wield shovel
   ```

3. Connect to Room B to the east:
   ```
   connect east
   ```

4. The system will:
   - Create an exit "east" from Room A to Room B
   - Create an exit "west" from Room B to Room A
   - Notify you and the room of the successful connection

5. You can now travel between the rooms:
   ```
   east    - Move from Room A to Room B
   west    - Move from Room B to Room A
   ```

## Technical Details

- **Tool Detection**: Checks item keys and names for digging keywords, or looks for `db.tool_type` containing "dig"
- **Zone Awareness**: Rooms must be in the same zone (or both have no zone) to connect
- **Coordinate Matching**: Searches for exact coordinate matches
- **Bidirectional Exits**: Both forward and reverse exits are created automatically
- **Exit Prevention**: Won't create exits if one already exists in that direction

## Related Commands

- `@maproom` - Set coordinates for current room
- `setcoord` - Set coordinates manually
- `zdig` - Create new rooms (dig) while creating coordinates
- `@tunnel` - Traditional Evennia tunnel command
- `look` - Display room information and exits

## Tips

- Coordinates can be set with `@maproom x y z` or `setcoord x y z`
- You can view current room coordinates with `@inspect` or custom coordinate debug commands
- Both rooms must have valid coordinates for connection to work
- The command works within zone boundaries - rooms in different zones won't connect
