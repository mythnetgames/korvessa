# Gamebud Color System Implementation

## Overview

The Okama Gamebud now features a dual-color system:
1. **Shell Color**: Random ANSI color assigned to each device on creation (the `()` parentheses)
2. **Alias Color**: User-selectable color for their alias/messages visible to all users

## Features

### Shell Color
- Randomly generated when device is spawned
- Uses any ANSI color except black (14 colors total)
- Stored in `gamebud.db.shell_color`
- Visible only on that specific device's UI
- Cannot be changed by user (device hardware characteristic)

### Alias Color
- User-selectable via `gamebud color=<colorname>` command
- Defaults to white if not set
- Stored in `gamebud.db.alias_color`
- Shows on ALL devices when your messages appear
- IC-friendly color names for immersion

### UI Enhancement
- Labels, borders, and UI elements use xterm-256 colors for rich display
- Cyan highlights for labels (PORT, CPU, IP, etc.)
- Yellow highlights for values
- Consistent color scheme across entire UI

## Available Alias Colors

```
red, green, yellow, blue, magenta, cyan, white
bright red, bright green, bright yellow, bright blue, bright purple, bright cyan, bright white
```

## Usage

### Viewing Messages
```
gamebud view
```
Shows the Gamebud UI with:
- Shell color applied to `()` throughout the display
- Alias colors applied to sender names in messages

### Setting Alias Color
```
gamebud color=bright purple
```
Changes your alias color to bright purple. All future messages will display in this color on everyone's Gamebud.

### Posting Messages
```
gamebud post=Hello Kowloon!
```
Posts a message with your current alias color attached to it.

## Technical Details

### Files Modified

1. **world/gamebud/constants.py**
   - Added `SHELL_COLORS` list (14 ANSI colors)
   - Added `ALIAS_COLOR_NAMES` dict mapping IC names to ANSI codes
   - Added `ALIAS_COLOR_DISPLAY` reverse lookup
   - Added `DEFAULT_ALIAS_COLOR = "w"`
   - Updated `UI_TEMPLATE` with xterm-256 color codes
   - Updated `MESSAGE_LINE_TEMPLATE` with `{shell}` and `{alias_color}` placeholders
   - Added `MSG_COLOR_SET` and `MSG_INVALID_COLOR` messages

2. **world/gamebud/core.py**
   - Added `generate_random_shell_color()` function
   - Updated `add_message()` to accept `alias_color` parameter
   - Updated message data structure to include `alias_color` field
   - Updated `format_gamebud_display()` to apply shell and alias colors to UI

3. **typeclasses/items.py (OkamaGamebud)**
   - Added `shell_color` attribute (random on creation)
   - Added `alias_color` attribute (defaults to white)
   - Imports color generation functions

4. **commands/CmdGamebud.py**
   - Added `color=` command routing
   - Added `do_color()` method to set alias color
   - Updated `do_post()` to pass alias_color to manager
   - Added color-related constant imports

### Color Format

- ANSI codes: `r`, `g`, `y`, `b`, `m`, `c`, `w` (normal), `R`, `G`, `Y`, `B`, `M`, `C`, `W` (bright)
- Applied with `|{color_code}` prefix in Evennia
- Reset with `|n`
- xterm-256: `|[38;5;NNN` where NNN is color number (0-255)

### Message Structure

```python
{
    "alias": str,           # Sender's alias
    "message": str,         # Message content
    "sender_dbref": int,    # Sender's database ID
    "timestamp": float,     # Unix timestamp
    "alias_color": str      # ANSI color code (e.g. "M" for bright purple)
}
```

### Device Attributes

```python
gamebud.db.shell_color = "c"      # Cyan shell color
gamebud.db.alias_color = "M"      # Bright purple alias
gamebud.db.alias = "R4Z0RB0Y"     # User's alias
gamebud.db.muted = False          # Notification state
gamebud.db.current_page = 0       # Viewing page
```

## Examples

### Device Spawn
```python
# Device created with:
shell_color = "R"  # Random bright red
alias_color = "w"  # Default white
alias = "X7K2P9M1"  # Random 8-char
```

### Changing Alias Color
```
> gamebud color=bright cyan
Gamebud alias color set to bright cyan.
```

### Viewing Messages
```
> gamebud view
[Shows UI with bright red () shell and messages in their respective colors]
```

### Message Display
- User A (bright purple alias): Name shows in bright purple
- User B (yellow alias): Name shows in yellow
- Your device (red shell): All `()` shown in red
- Another user's device (cyan shell): All `()` shown in cyan

## Design Philosophy

### Immersion
- IC-friendly color names (no "xterm-256 color 51")
- Shell color represents physical device hardware
- Alias color represents user software customization

### Visual Clarity
- 14 shell colors provide device distinction
- Alias colors help identify regular posters
- xterm-256 UI elements create retro-tech aesthetic

### Theft Mechanics
- Shell color moves with device if stolen
- Alias color moves with device if stolen
- Thief can post using victim's color/alias combo
- Reinforces "aliases stored on device" security model

## Future Enhancements

Potential additions:
- `gamebud info` - Show your current shell/alias colors
- Color preview in `gamebud view` header
- Color codes in help text
- Shell color trading/swapping (hardware mod RP)
