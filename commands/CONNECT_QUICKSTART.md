# Quick Start: Using the Connect Command

## What You Need

A digging tool item in your inventory, equipped/wielded.

## Basic Steps

### Step 1: Create a Digging Tool (Admin)

If you don't have a digging tool, create one:

```
@create Shovel:typeclasses.items.Item
@set Shovel/key = shovel
@set Shovel/desc = A sturdy shovel for digging.
```

### Step 2: Set Room Coordinates

Both rooms need coordinates. Set them with:

```
@maproom x y z
```

Example - Set Room A to (0,0,0):
```
@maproom 0 0 0
```

Example - Set Room B to (1,0,0):
```
@maproom 1 0 0
```

### Step 3: Equip the Digging Tool

```
wield shovel
```

### Step 4: Use the Connect Command

Move to Room A and use:

```
connect east
```

This will:
- Find Room B at coordinates (1, 0, 0) 
- Create an "east" exit from Room A to Room B
- Create a "west" exit from Room B to Room A

## Success!

You can now travel between the rooms:

```
east    # Move from Room A to Room B
west    # Move from Room B to Room A
```

## Troubleshooting

**"You need to be holding a digging tool"**
- Make sure you've equipped the digging tool: `wield shovel`

**"No room exists at coordinates (x, y, z)"**
- The target room doesn't have coordinates set
- Set them with: `@maproom x y z`
- Verify the calculated coordinates are correct

**"An exit to the {direction} already exists"**
- An exit already connects these rooms in that direction
- Either delete the old exit or use a different connection

**"Unknown direction: {direction}"**
- Check spelling: north, south, east, west, northeast, northwest, southeast, southwest, up, down
- Can also use short forms: n, s, e, w, ne, nw, se, sw, u, d

## Tips

- Use `@inspect here` or custom coordinate commands to see room coordinates
- The command works within zone boundaries
- Exits are bidirectional (both directions auto-created)
- The tool type is detected by keywords: "dig", "shovel", "pickaxe", "pick", "axe", "spade", "excavator", "tool"
