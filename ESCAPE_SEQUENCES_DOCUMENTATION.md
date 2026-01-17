# Escape Sequence Processing in Room Descriptions

## Overview

Admin staff can now use escape sequences (like `\n`) in room descriptions to create multi-line flavor text. This feature applies to:

- Room descriptions (set via `@desc` command)
- Door/exit descriptions (set via builder tools)

**Note:** This is an admin-only feature for atmospheric flavor text. Player-controlled descriptions like `@longdesc` and `@nakeds` are not affected.

## Usage Examples

### Room Description with Line Breaks

```
@desc here = "This is the first line of the description.\nThis is the second line.\nAnd here's the third."
```

When a player looks at the room, they will see:
```
This is the first line of the description.
This is the second line.
And here's the third.
```

### Door/Exit Description with Line Breaks

```
setdoordesc north = "A heavy wooden door blocks your path.\nIt appears to be locked.\nMaybe someone has the key."
```

The door description will display with proper line breaks when examined.

## Supported Escape Sequences

The following standard Python escape sequences are supported:

| Sequence | Character |
|----------|-----------|
| `\n` | Newline (line break) |
| `\t` | Tab (indentation) |
| `\\` | Backslash |
| `\"` | Double quote |
| `\'` | Single quote |
| `\r` | Carriage return |

## Technical Implementation

### Files Modified

1. **world/utils/text_processing.py** (NEW)
   - Contains `process_escape_sequences()` function
   - Handles escape sequence conversion using Python's `codecs.decode()`
   - Gracefully handles invalid sequences by returning original text

2. **typeclasses/rooms.py** (MODIFIED)
   - Modified `return_appearance()` method
   - Processes room.db.desc after super() call
   - Replaces processed description in appearance string

3. **typeclasses/exits.py** (MODIFIED)
   - Modified `get_display_desc()` method
   - Processes self.db.desc for custom door/exit descriptions
   - Applied before strip() to preserve formatting

### How It Works

When a player looks at a room or door:

1. The description is retrieved from the database (e.g., `self.db.desc`)
2. The `process_escape_sequences()` function converts escape sequences to actual characters
3. The processed description is inserted into the display output
4. Players see the formatted multi-line text

### Edge Cases

- **Empty descriptions:** Handled gracefully (returns empty string)
- **None values:** Returns None unchanged
- **Invalid sequences:** Original text returned on decode failure
- **Multiple occurrences:** Only first occurrence is replaced in room appearance

## Scope & Limitations

### What This Applies To

- ✅ Room descriptions (`@desc` command)
- ✅ Door/exit descriptions (builder commands)
- ✅ Any admin-set description fields using `db.desc`

### What This Does NOT Apply To

- ❌ Player `@longdesc` descriptions (player-controlled)
- ❌ Player `@nakeds` body descriptions (player-controlled)
- ❌ NPC descriptions (use separate system)
- ❌ Item descriptions (unless explicitly set via admin tools)

## Future Enhancements

Potential improvements:

1. Add support for color codes alongside escape sequences
2. Create admin command for testing escape sequences
3. Add escape sequence validation to description commands
4. Support additional formatting options (bold, italic via MUD conventions)

## Testing

To test the feature manually:

1. Create a test room or use an existing one
2. Set a description with `\n`:
   ```
   @desc <room> = "First line\nSecond line"
   ```
3. Look at the room
4. Verify that the description displays with actual line breaks

To test the utility function directly:
```python
from world.utils import process_escape_sequences
result = process_escape_sequences("Line 1\nLine 2")
# Result: "Line 1\nLine 2" (with actual newline character)
```

## Admin Guidelines

- **When to use:** Adding atmospheric, multi-line flavor to rooms and descriptions
- **Keep it brief:** Multi-line descriptions should still be readable
- **Test in-game:** Always verify the output looks right before saving
- **Consistency:** Follow existing description style guidelines
- **Not for players:** This feature is admin-only; players use standard single-line descriptions

## Implementation Notes

- Processing happens at **display time**, not storage time
- Descriptions are stored with literal `\n` sequences in the database
- This allows safe modification and doesn't affect backwards compatibility
- The process_escape_sequences() function is safe against malformed input
