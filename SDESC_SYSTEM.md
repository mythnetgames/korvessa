# Sdesc System - Short Description Implementation

## Overview

The sdesc (short description) system replaces traditional display names with descriptive phrases like "a tall man" or "a scarred elven woman". This creates more immersive roleplay as characters are identified by their appearance rather than names.

## Features

### 1. Sdescs (Short Descriptions)
- Replace character names in room descriptions and emotes
- Stored in `character.db.sdesc`
- Set during chargen or via `sdesc` command
- Example: "a tall man", "a hooded figure", "a scarred elven woman"

### 2. Static Poses
- Appended to sdescs when viewing rooms
- Stored in `character.db.pose`
- Set via `pose` command
- Example: "is standing by the bar", "sits alone in the corner"

Room display example:
```
Tavern
A tall man is standing by the bar. A hooded figure sits alone in the corner.
```

### 3. Recognition System (Recog)
- Players can personally name other characters
- Stored in `viewer.db.recog` as dict mapping character ID to name
- Set via `name <sdesc> = <name>` command
- Names are viewer-specific and respect disguises

Example:
```
> name tall = Tom
You will now know 'a tall man' as 'Tom'.

> look
Tavern
Tom is standing by the bar.
```

### 4. Emote Target Parsing
- Use `/word` syntax to target characters by partial sdesc match
- Targets are personalized per-viewer
- Example: `emote smiles at /tall` becomes "A short woman smiles at a tall man" (or "Tom" if viewer knows them)

### 5. Language Prefix for Speech
- Use `language"speech"` format to speak in specific language
- Example: `say dwarven"Greetings, friend."`
- Requires minimum 10% proficiency in the language

### 6. Disguise Integration
- Disguises can override sdescs with disguise-specific descriptions
- Recog names can be set for disguised identities separately
- When disguise is removed, original sdesc and recog names return

## Commands

### Player Commands

| Command | Description |
|---------|-------------|
| `sdesc <description>` | Set your short description |
| `sdesc` | View your current sdesc |
| `pose <text>` | Set a static pose |
| `pose` | View your current pose |
| `pose clear` | Clear your static pose |
| `name <sdesc> = <name>` | Name someone you recognize |
| `name <target> =` | Forget a name (clear recog) |
| `names` | List all people you have named |

### Staff Commands

| Command | Description |
|---------|-------------|
| `setsdesc <character> = <sdesc>` | Set another character's sdesc |

## Technical Details

### Storage

```python
character.db.sdesc = "a tall man"           # Short description
character.db.pose = "is standing by bar"    # Static pose
viewer.db.recog = {                          # Recognition dictionary
    "123": "Tom",                            # Character ID -> name
    "disguise_456": "Mystery Man"            # Disguised identity
}
```

### Key Functions (world/sdesc_system.py)

| Function | Purpose |
|----------|---------|
| `get_sdesc(character, viewer)` | Get appropriate sdesc/recog name |
| `get_sdesc_with_pose(character, viewer)` | Include static pose |
| `set_sdesc(character, sdesc)` | Set sdesc |
| `set_pose(character, pose)` | Set static pose |
| `get_recog(viewer, target)` | Get recog name |
| `set_recog(viewer, target, name)` | Set recog name |
| `find_target_by_sdesc(location, term, searcher)` | Find character by partial match |
| `parse_targets_in_string(text, location, speaker)` | Parse /target references |
| `personalize_text(text, targets, viewer)` | Replace placeholders per-viewer |
| `parse_language_speech(text)` | Parse language"speech" format |
| `format_sdesc_for_room(character, viewer)` | Format for room display |
| `validate_sdesc(sdesc)` | Validate sdesc format |

### Character Display Flow

1. Room description requested
2. For each character in room:
   - `format_sdesc_for_room(char, viewer)` called
   - Checks disguise status
   - Checks viewer's recog for this character
   - Falls back to sdesc or key
   - Appends pose if set
   - Capitalizes and adds period

### Emote Processing Flow

1. Player types: `emote smiles at /tall and waves`
2. `parse_targets_in_string()` finds /tall, matches "a tall man"
3. Creates placeholder: `smiles at {target_0} and waves`
4. For each viewer:
   - `personalize_text()` replaces {target_0} with:
     - "you" if viewer is the target
     - Viewer's recog name for target
     - Target's sdesc as seen by viewer
5. Each viewer sees personalized message

## Chargen Integration

During character creation:
1. After name entry, player sets sdesc
2. Sdesc stored in `charcreate_data['sdesc']`
3. On finalize:
   - Character key = real name
   - `character.db.sdesc` = chosen sdesc
   - First name, last name stored separately

## Validation Rules

Sdescs must:
- Be 3-80 characters
- Not contain newlines
- Only use letters, numbers, spaces, and basic punctuation (- ' , .)
- Typically start with "a" or "an" (encouraged but not enforced)

## Migration Notes

For existing characters without sdescs:
- `get_sdesc()` falls back to `character.key` if no sdesc set
- Staff can use `setsdesc` to assign sdescs
- Players can use `sdesc` command to set their own
