# Corpse System Changes - Summary

## Overview
Modified the death system so that:
1. **Corpses are only created when a player chooses DIE**, not when they choose LIVE
2. Corpses spawn in the actual **room where death occurred**, not in limbo
3. The death location is **safely stored internally** to avoid errors

## Changes Made

### 1. Modified `_complete_death()` function
- **Added:** Store the character's death location before any movements
- **Change:** Added `account.ndb._death_location = death_location` to preserve room reference
- **Impact:** Ensures we know WHERE the death occurred for later corpse spawning

### 2. Modified `_process_death_choice()` function
- **Changed:** Added `death_location` parameter extraction from stored account data
- **Changed:** Pass `death_location` to `_handle_permanent_death_path()`
- **Impact:** Routes the death location through the DIE path when needed

### 3. Modified `_handle_permanent_death_path()` function
- **Changed:** Now accepts `death_location` parameter
- **Added:** Corpse creation NOW happens BEFORE character moves to limbo
- **Added:** Uses the stored `death_location` instead of character's current location
- **Added:** Try/except wrapping around corpse creation with logging
- **Impact:** Corpses appear in correct location and won't throw errors

### 4. Modified `_create_corpse()` function
- **Changed:** Now accepts optional `location` parameter
- **Changed:** Uses provided location OR falls back to `character.location`
- **Added:** Better error handling with traceback logging
- **Added:** Validation that location exists before corpse creation
- **Impact:** Function is more flexible and safer

## Behavior Flow

### When Player Chooses LIVE:
1. Character's death location is discarded
2. NO corpse is created
3. Character is teleported to room #5 for admin review
4. No reference to death location is needed

### When Player Chooses DIE:
1. Death location is extracted from `account.ndb._death_location`
2. Corpse is created **in the death room** with all items
3. Character is then moved to limbo
4. Permanent death sequence plays out
5. Character is eventually deleted

## Error Handling

- All `_create_corpse()` calls are wrapped in try/except
- Traceback logging provides debugging information
- Location validation prevents None-pointer errors
- Corpse creation failure doesn't crash the death sequence

## Database Impact

### Temporary NDB Fields (cleaned up):
- `account.ndb._death_location` - Removed after choice is made
- `account.ndb._character_to_delete` - Removed after deletion
- `account.ndb._corpse_location` - Used then removed

### Persistent Corpse Data:
- `corpse.db.original_character_name` - Who died
- `corpse.db.original_character_dbref` - Character reference
- `corpse.db.death_time` - When they died
- `corpse.db.physical_description` - Body description
- `corpse.db.worn_items_data` - Items worn (for display)
- `corpse.db.hands_data` - Wielded items

## Testing Checklist

- [ ] Player dies and chooses LIVE - no corpse created
- [ ] Player dies and chooses DIE - corpse appears in death room
- [ ] Corpse contains all inventory items
- [ ] Corpse shows worn items correctly
- [ ] Corpse shows wielded items correctly
- [ ] No "NoneType" errors when creating corpse
- [ ] Death location is properly cleaned up from account NDB
