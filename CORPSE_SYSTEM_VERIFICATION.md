# Corpse System - Verification Scenarios

## Scenario 1: Player Chooses LIVE

**Sequence of events:**
1. Character dies → `start_death_progression()` called
2. 90 seconds of death messages play
3. `_complete_death()` called:
   - Stores `death_location = character.location`
   - Stores `account.ndb._death_location = death_location`
4. Player sees death choice menu
5. Player types: `live`
6. `_process_death_choice(account, "live")` called:
   - Deletes `account.ndb._death_location` (no longer needed)
   - Calls `_handle_live_path()`
7. `_handle_live_path()`:
   - NO corpse creation
   - Teleports character to room #5
   - Account receives messages about being in admin room

**Result:** ✓ Character survives with no corpse left behind

---

## Scenario 2: Player Chooses DIE

**Sequence of events:**
1. Character dies → `start_death_progression()` called
2. 90 seconds of death messages play
3. `_complete_death()` called:
   - Stores `death_location = character.location` (e.g., room #23)
   - Stores `account.ndb._death_location = death_location`
4. Player sees death choice menu
5. Player types: `die`
6. `_process_death_choice(account, "die")` called:
   - Retrieves `death_location` from `account.ndb._death_location`
   - Deletes `account.ndb._death_location` after retrieval
   - Calls `_handle_permanent_death_path(account, character, session, death_location)`
7. `_handle_permanent_death_path()`:
   - **Corpse creation happens NOW:**
     - `_create_corpse(character, death_location)` called with room #23
     - Corpse object created in room #23
     - All items transferred to corpse
     - Logging confirms: "Corpse created in room #23 for PlayerName"
   - Character moved to limbo
   - Account unpuppeted
   - Character removed from account's character list
8. `_play_permanent_death()`:
   - Plays dissolution sequence
   - Shows Watcher's final monologue
   - Calls character creation after ~80 seconds

**Result:** ✓ Corpse appears in death room with all inventory and items

---

## Error Handling

**If death_location is None:**
- Try/except catches the error
- Log: "PERMANENT_DEATH: Error creating corpse: [error details]"
- Death sequence continues (not blocked)
- Character eventually deleted
- Corpse simply doesn't exist (acceptable fallback)

**If corpse creation fails:**
- Exception caught and logged
- Traceback included in logs for debugging
- Death sequence completes normally
- No AttributeError thrown to player

---

## Key Implementation Details

### Death Location Storage
```python
# In _complete_death():
death_location = character.location
account.ndb._death_location = death_location
```
- NDB fields are **temporary** (not persistent)
- Survives account unpuppeting
- Automatically cleaned up when choice is made

### Corpse Creation Timing
```python
# In _handle_permanent_death_path():
if death_location and character:
    try:
        corpse = _create_corpse(character, death_location)
    except Exception as e:
        _log(f"PERMANENT_DEATH: Error creating corpse: {e}")
```
- Corpse created **BEFORE** character moves to limbo
- Character still has original location reference
- Corpse placed in actual death room

### _create_corpse() Signature Change
```python
def _create_corpse(character, location=None):
    """location: Optional specific location for corpse."""
    corpse_location = location or character.location
```
- Backwards compatible (default uses character.location)
- New code passes explicit death_location
- Never creates corpse with None location

---

## Database State After Death

### When choosing LIVE:
- No corpse created
- Character in room #5 (or limbo as fallback)
- Character can be manipulated by staff
- No permanent death recorded yet

### When choosing DIE:
- Corpse in original death room
- Character in limbo (temporary)
- Character eventually deleted
- Name added to account.db.deceased_character_names
- Corpse contains all death-state items

---

## Staff Admin Considerations

**Room with corpse after DIE:**
- Corpse object contains character's inventory
- Corpse displays as "fresh corpse"
- Items can be looted from corpse
- Room description shows corpse presence
- Corpse can be cleaned up manually if needed

**Room where LIVE player was:**
- No corpse left behind
- Clean room state
- Character has been teleported away
- Can be managed by staff as needed
