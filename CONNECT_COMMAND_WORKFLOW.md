# Connect Command - Complete Workflow Example

## Scenario

You are a builder in a game with a coordinate-based room system. You have already created two rooms at specific coordinates and now want to connect them using the new `connect` command.

## Setup (Admin/Builder)

### Create Two Test Rooms

```
@create Room A
@set Room A/key = room_a
@set Room A/db.desc = A spacious chamber.

@create Room B  
@set Room B/key = room_b
@set Room B/db.desc = An adjoining corridor.
```

### Set Their Coordinates

Move to Room A:
```
@goto Room A
@maproom 0 0 0
```

Move to Room B:
```
@goto Room B
@maproom 1 0 0
```

### Create a Digging Tool

Create it in your inventory:
```
@create Shovel:typeclasses.items.Item
@set Shovel/key = shovel
@set Shovel/desc = A sturdy shovel with a wooden handle and metal head.
@set Shovel/db.tool_type = digging_tool
```

## Workflow (Player/Builder)

### Step 1: Move to Room A

```
> goto room_a
You are now in Room A.

> look
Room A
A spacious chamber.

Exits: (none yet)
```

### Step 2: Pick Up and Equip the Shovel

```
> get shovel
You pick up a shovel.

> wield shovel
You wield a shovel in your right hand.

> inventory
You are carrying:
  - a shovel (wielded in right hand)
```

### Step 3: Use the Connect Command

```
> connect east
You use your digging tool to connect to room_b to the east.
room_a (0, 0, 0) <-> room_b (1, 0, 0)
```

**Room A now shows:**
```
> look
Room A
A spacious chamber.

Exits: east to room_b
```

### Step 4: Verify the Connection

Move east to Room B:
```
> east
You head east.

[Room B Description...]

> look
Room B
An adjoining corridor.

Exits: west to room_a
```

### Step 5: Return to Room A

```
> west
You head west.

[Room A Description...]
```

## Success Verification

Both directions work:
- From Room A: `east` -> Room B
- From Room B: `west` -> Room A

The exits were created automatically and bidirectionally!

## Connecting More Rooms

### Create Room C at (0, 1, 0)

```
@create Room C
@set Room C/key = room_c
@set Room C/db.desc = A narrow passage.
@goto room_c
@maproom 0 1 0
```

### Connect Room A North to Room C

```
> goto room_a
> wield shovel
> connect north
You use your digging tool to connect to room_c to the north.
room_a (0, 0, 0) <-> room_c (0, 1, 0)
```

### Now Room A Has Multiple Exits

```
> look
Room A
A spacious chamber.

Exits: east to room_b, north to room_c
```

## Creating a More Complex Layout

### Set Up Rooms in a 2x2 Grid

Coordinates:
```
Room D (0, 1, 0) -- Room C (1, 1, 0)
   |                    |
Room A (0, 0, 0) -- Room B (1, 0, 0)
```

### Create All Rooms

```
@create Room A: @maproom 0 0 0
@create Room B: @maproom 1 0 0
@create Room C: @maproom 1 1 0
@create Room D: @maproom 0 1 0
```

### Connect All Rooms

From Room A:
```
> wield shovel
> connect east    # to Room B (1, 0, 0)
> connect north   # to Room D (0, 1, 0)
```

From Room B:
```
> wield shovel
> connect north   # to Room C (1, 1, 0)
```

From Room D:
```
> wield shovel
> connect east    # to Room C (1, 1, 0)
```

### Result: Fully Connected Grid

```
Room D --- Room C
 |         |
 |         |
Room A --- Room B
```

Now you can navigate the entire grid:
- From Room A: east, north, or (via north) east again
- From Room B: west, north, or (via north) west again
- From Room C: west, south, or (via south) west again
- From Room D: south, east, or (via east) south again

## Troubleshooting During Workflow

### Problem: "No room exists at coordinates (1, 0, 0)"

**Solution:** Room B doesn't have coordinates set yet.
```
> goto room_b
> @maproom 1 0 0
```

### Problem: "You need to be holding a digging tool"

**Solution:** You haven't wielded the shovel yet.
```
> wield shovel
```

### Problem: "An exit to the east already exists"

**Solution:** Room A already has an east exit. Try a different direction or check existing exits with `look`.

### Problem: "Unknown direction: eastt"

**Solution:** Check spelling. Use: north, south, east, west, northeast, northwest, southeast, southwest, up, down

## Advanced Example: Multi-Level Connection

### Create Vertical Room Stack

```
Room on Level 1: @maproom 5 5 0
Room on Level 2: @maproom 5 5 1
Room on Level 3: @maproom 5 5 2
```

### Connect Vertically

From Level 1:
```
> wield shovel
> connect up     # Creates exit to Level 2
```

From Level 2:
```
> wield shovel
> connect up     # Creates exit to Level 3
> connect down   # Creates exit back to Level 1
```

### Result: Vertical Shaft

```
[L3] ^ up
      | down
[L2] ^ up
      | down
[L1]
```

## Tips for Efficient Building

1. **Plan your layout** - Know which coordinates each room should have
2. **Batch operations** - Connect multiple rooms in sequence
3. **Use coordinates wisely** - Leave gaps for future rooms
4. **Document your zones** - Keep track of what's at which coordinates
5. **Test connections** - Walk through all connected rooms to verify
6. **Use map command** - If available, visualize your room layout

## Integration with Game Building

This command integrates smoothly with other building tools:

- Use `@maproom` or `setcoord` to set initial coordinates
- Use `zdig` to create rooms with automatic coordinates
- Use `connect` to link existing rooms by their coordinates
- Use standard exits for manual connections if needed

The coordinate system allows for:
- Automated layout mapping
- Spatial relationship visualization
- Procedural room generation
- Better building documentation
- Easier debugging of room layouts
