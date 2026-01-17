# Pad Housing System - Quick Reference

## Overview

Pads are larger rented living spaces than cubes. Each pad creates its own ZONE and can contain multiple rooms. Entry uses code-based access similar to cubes, but with different behavior:

- **Cubes**: Auto-traverse on correct code entry
- **Pads**: Door unlocks and swings open, player must walk through manually

## Door Status Indicators

When you look in a room, housing doors display with status indicators:

- **+north** = Door is closed and locked (cannot pass without correct code)
- **-north** = Door is open and unlocked (can be traversed freely)

This helps players quickly see:
1. Where doors are located
2. Whether they are secure or someone left them open
3. Security at a glance

For cubes: + = closed, - = open (via OPEN DOOR command)
For pads: + = locked, - = unlocked (via ENTER <code> command)

## Constants

Located in `world/economy/constants.py`:

- `PAD_CODE_LENGTH = 6` - Access codes are 6 characters
- `PAD_DEFAULT_WEEKLY_RENT = 1` - Default weekly rent (changeable via SETRENT)
- `RENT_PERIOD_SECONDS = 7 * 24 * 3600` - 7 days in seconds

## Player Commands

### ENTER <code> <direction>
Enter a pad or cube using the door code.

```
enter ABC123 north
enter XY7Z9K n
```

- **For pads**: Door unlocks and swings open. Walk through to enter.
- **For cubes**: Auto-enters on correct code.

### CHECK <direction>
Check a door's rental status.

```
check north
check e
```

Shows weekly/nightly rate and rental status.

### PAY RENT <direction> [= <amount>]
Pay rent for a pad or cube.

```
pay rent north
pay rent n = 50
```

- Uses cash_on_hand
- Partial payments accepted
- First payment on unclaimed unit claims it and generates a code
- Pads: weekly_rent dollars = 7 days
- Cubes: 100 dollars = 1 day

### CLOSE DOOR [<direction>]
Close and lock the door from inside.

```
close door
close door north
```

- For pads: "You pull the door shut. The lock clicks."
- For cubes: "You pull the door shut. The keypad beeps once..."

### OPEN DOOR [<direction>]
Open a closed cube door (cubes only).

```
open door
open door north
```

Note: Pad doors require ENTER <code> to unlock.

## Admin Commands

### CREATEPAD <direction> <name>
Create a new pad housing unit with its own zone.

```
createpad north Luxury Pad 1A
createpad e Riverside Suite
```

Creates:
- New zone (numbered automatically) named "Pad: <name>"
- Pad entry room at (0,0,0) in that zone
- PadDoor from current room to pad entry
- Return PadDoor from pad back to hallway

Output includes:
- Direction, pad name, zone created, room created
- Current weekly rent ($1 default)
- State (unassigned)

### SETRENT <direction> <amount>
Set weekly rent for a pad.

```
setrent north 50
setrent e 100
```

Must be > 0. Applies to both entry and exit doors.

### SETPADRENTER <direction> = <character>
Assign a renter to a pad.

```
setpadrenter north = Bob
setpadrenter e = Alice
```

- Generates new unique 6-char code
- Sets character housing attributes (housing_tier, pad_id, pad_code)
- Gives 1 hour grace period for rent
- Messages the renter their code

### PADINFO <direction>
View pad door information.

```
padinfo north
padinfo e
```

Shows: renter, code, weekly rent, rent status, zone ID, destination.

### CLEARPADRENTER <direction>
Remove renter from a pad.

```
clearpadrenter north
```

Clears renter, code, and rent data. Returns pad to unassigned state.

## Data Storage

### PadDoor Attributes (category="housing")
- `current_door_code` - 6-char A-Z0-9 code
- `rent_paid_until_ts` - Unix timestamp when rent expires
- `current_renter_id` - Character dbref of current renter
- `weekly_rent` - Weekly rent amount in dollars
- `zone_id` - Zone this pad belongs to
- `hallway_room_id` - Hallway room this door connects from
- `is_entry_door` - True if this is the door INTO the pad
- `is_unlocked` - Temporary unlock state
- `paired_door_id` - ID of the paired door (entry<->exit)

### Character Housing Attributes
When assigned as renter:
- `db.housing_tier = "pad"`
- `db.pad_id` - PadDoor dbref
- `db.pad_code` - Current access code
- `db.rent_paid_until_ts` - Rent expiration

## Access Rules

1. Entry requires correct code AND rent current
2. Anyone with correct code can enter (not just renter)
3. If rent overdue: always deny entry
4. If unassigned (no active code): deny entry

## Error Messages (Plain Text Only)

- Unassigned: "The keypad is dark. This unit is unassigned."
- Rent expired: "The keypad buzzes. Payment required. A red indicator flashes."
- Wrong code: "The keypad beeps angrily. A red indicator flashes."
- Door locked: "The door is locked. A red indicator light glows steadily."

## Success Messages (Plain Text Only)

- Correct code: "The keypad chirps once. The door swings open."
- Room message: "<name> pushes a code on the <direction> and the door swings open."
- Close door (pad): "You pull the door shut. The lock clicks."

## Files

- `typeclasses/pad_housing.py` - PadDoor, PadRoom typeclasses
- `commands/pad_housing.py` - All pad (and unified housing) commands
- `world/economy/constants.py` - PAD_* constants

## Integration Notes

The PadHousingCmdSet now handles player commands for BOTH cubes and pads:
- `enter` - Works for both cube and pad doors
- `check` - Works for both cube and pad doors
- `close door` - Works for both cube and pad doors
- `open door` - Works for cubes only (pads use enter)
- `pay rent` - Works for both cube and pad doors

CubeHousingCmdSet now only contains cube-specific admin commands:
- `createcube`
- `setcuberenter`
- `cubeinfo`
- `clearcuberenter`
