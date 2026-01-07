# Description/Naked System Overview

## How It Works

The Kowloon description system integrates character descriptions with clothing/armor to show what's visible based on what the character is wearing.

## Key Components

### 1. **Character Description Layers**

When someone looks at a character, the appearance is built in this order:

```
1. Character Name (Display Name)
   ↓
2. Short Description (char.db.desc)
   - Initial description, shown once
   ↓
3. Body Part Descriptions (char.longdesc)
   - Organized by body location
   - Shows clothing OR naked body based on coverage
   ↓
4. Wielded Items
   - What character is holding in hands
   ↓
5. Admin Inventory (for builders only)
   - Full contents list with dbrefs
```

### 2. **Clothing Coverage System**

The system tracks what body locations are covered:

**Coverage Map Building** (`_build_clothing_coverage_map`):
- Scans `char.worn_items` dictionary (organized by body location)
- Maps each location to the **outermost** clothing item
- Works by layer: if location has items, first item is outermost

**Worn Items Structure**:
```python
char.worn_items = {
    'chest': [shirt, undershirt],    # First item visible
    'legs': [pants],
    'feet': [boots],
    'hands': [gloves],
}
```

### 3. **Visible Body Descriptions** (`_get_visible_body_descriptions`)

For each body location in anatomical order:

```python
if location is covered by clothing:
    → Show clothing item's worn description
else:
    → Show character's longdesc for that location
    → If no longdesc, check for wounds
    → If no wounds, location is "naked"
```

**Example**:
- Chest: Wearing shirt → Show shirt description
- Chest: No shirt → Show `longdesc['chest']` (e.g., "muscular torso")
- Chest: No shirt, no longdesc → Naked/default

### 4. **Description Variables & Template Processing**

Descriptions support template variables for perspective-aware text:

```python
# In character descriptions or clothing:
"{They} are muscular and well-toned."
"{Their} skin shows signs of scarring."
```

**Template Variables Available**:
- Pronouns: `{they}`, `{them}`, `{their}`, `{theirs}`, `{themselves}`
- Capitalized: `{They}`, `{Them}`, `{Their}`, etc.
- Character-specific: `{name}`, `{name's}`

**Processing (`_process_description_variables`)**:
- Replaces variables based on looker's perspective
- If looker is self: uses second person ("you", "your")
- If looker is someone else: uses third person pronouns (he/she/they)
- Applies skintone coloring to body part descriptions only

### 5. **Skintone Integration**

When displaying naked body parts (longdesc):
- Applies skintone color from `char.db.skintone`
- Maps skintone to color code from `SKINTONE_PALETTE`
- Makes visible body descriptions color-coordinated with character appearance

## The "Naked" System

There's no explicit "naked" attribute. Instead:

1. **Naked Detection**: A body location is "naked" if:
   - Not covered by clothing (`location` not in coverage_map)
   - AND has no `longdesc` for that location

2. **Naked Display**: When a location is naked:
   - Shows character's `longdesc` if available
   - Shows wounds if any exist
   - Otherwise defaults to nothing (implicitly naked)

3. **Example Scenarios**:
   ```
   Chest covered by shirt → Shows shirt worn_desc
   Chest naked + has longdesc → Shows "muscular torso"
   Chest naked + no longdesc → Naked (nothing shown)
   ```

## Anatomical Display Order

Descriptions are shown in consistent anatomical order (top to bottom):
- Head/Hair
- Face/Eyes
- Torso/Chest
- Arms
- Hands
- Legs
- Feet
- Custom/Extended locations

## Command Integration

**`look <character>`** calls `return_appearance()` which:
1. Gets display name
2. Processes short description
3. Calls `_get_visible_body_descriptions()` for clothing+body parts
4. Shows wielded items
5. Shows admin inventory (if looker is builder)
6. Joins all parts with blank lines between sections

**Example Output**:
```
Dalao

Dalao is a mysterious figure with sharp features.

Dalao is wearing a long black coat that seems to absorb light.
Beneath it, muscular arms ripple with intricate tattoos.

Dalao is holding a katana.
```

## Clothing Integration

Each clothing item has:
- `worn_desc`: Description when worn (supports template variables)
- Coverage locations: Which body parts it covers
- Layers: Order in worn_items array (first = outermost, visible)

When displaying:
- Uses outermost clothing item for covered locations
- Calls `get_current_worn_desc_with_perspective()` for template processing
- Skips wounds for covered locations

## How to Use

**Setting character descriptions**:
```python
char.db.desc = "A tall figure with sharp features."

char.longdesc = {
    'chest': 'muscular torso with faded scars',
    'arms': 'strong arms marked with old tattoos', 
    'legs': 'sturdy legs in well-worn pants',
}

char.db.skintone = 'fair'  # Applies color to body descriptions
```

**Creating clothing**:
```python
shirt.db.worn_desc = "a black t-shirt with {their} personal insignia"
shirt.db.coverage = ['chest', 'arms']
char.wear(shirt)  # Adds to worn_items
```

**Looking at character**:
- `look <character>` triggers `return_appearance()`
- Shows all visible parts: clothing + naked body parts
- Wounds appear on uncovered locations

## Key Files

- `typeclasses/characters.py` - Main implementation
  - `return_appearance()` - Main display method
  - `_get_visible_body_descriptions()` - Builds clothing+body map
  - `_build_clothing_coverage_map()` - Maps coverage
  - `_process_description_variables()` - Template processing
  - `_format_longdescs_with_paragraphs()` - Formatting

- `typeclasses/clothing.py` - Clothing item system
  - Manages worn_desc, coverage, layers

- `world/combat/constants.py` - Constants
  - `ANATOMICAL_DISPLAY_ORDER` - Display sequence
  - `SKINTONE_PALETTE` - Color mappings

## Summary

**Naked Detection**: Automatic - a body location shows naked if no clothing covers it AND no longdesc describes it.

**Clothing Priority**: Outermost clothing item in each location is always shown first, hiding any body parts beneath.

**Template Variables**: Descriptions dynamically adjust based on who's looking (second person for self-look, third person for looking at others).

**Skintone Integration**: Colors naked body descriptions to match character appearance.

The system creates a seamless, immersive character appearance that adapts based on clothing coverage while maintaining narrative description for uncovered areas.
