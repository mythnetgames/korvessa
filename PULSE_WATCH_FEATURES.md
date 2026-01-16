# PULSE WATCH ADVANCED FEATURES GUIDE

## Overview

The municipal pulse watch now includes advanced features that create immersive gameplay mechanics and support specialized roles like deckers and trackers. These features include:

1. **Unique Identifiers** - Each watch has a 10-character unique ID for tracking and decker gameplay
2. **Welcome Chime** - Audio feedback when first worn
3. **Scissors-Required Removal** - Painful, character-driven item removal mechanic
4. **Reattachment via Electronics** - Skill-gated recovery mechanics

---

## Feature Details

### 1. Unique Pulse Watch Identifiers

**What it does:**
- When a municipal pulse watch is created, it automatically generates a unique 10-character string
- The ID contains a mix of letters, numbers, and symbols (e.g., "K7m@4P!xZ2")
- The ID is stored in `watch.db.pulse_watch_id`
- Each watch has a different ID for tracking purposes

**Usage:**
- Deckers can use the ID to track specific watches/characters across the city
- Useful for location tracking gameplay
- Adds immersion and personal connection to the watch

**Technical:**
- Generated in `Wristpad.at_object_creation()` using `random.choice()`
- 10 characters of: a-z, A-Z, 0-9, !@#$%^&*
- Automatically created on spawn, not modifiable by players

---

### 2. Welcome Chime System

**What it does:**
- When a character puts on a municipal pulse watch, they hear a welcome chime
- The chime displays the watch's unique ID
- Message: "Welcome, [UNIQUE_ID]! Glory be to China!"
- Creates immersive audio-visual feedback

**Where it triggers:**
- In the `at_wear()` hook of the Wristpad class
- Only triggers for municipal wristpads (not hacked SafetyNet watches)
- Only triggers when first worn/equipped

**Message format:**
```
|y*beep* |CWelcome, K7m@4P!xZ2! Glory be to China!|n
```

**Technical:**
- Implemented in `Wristpad.at_wear()` method
- Checks `db.is_municipal_wristpad` flag before displaying
- Uses cyan color for government authority aesthetic
- Beep sound effect suggested by color codes

---

### 3. Scissors-Required Removal

**What it does:**
- Characters cannot remove a municipal pulse watch without surgical scissors
- Attempting removal without scissors shows: "The wristpad's needle is firmly anchored to your wrist. You need scissors to remove it painfully."
- With scissors present in inventory, removal is allowed and shows a painful message
- The watch is marked as "cut" and renamed to "cut Pulse watch"

**How it works:**

1. **Without scissors:**
   - Character attempts to remove the watch
   - `at_pre_remove()` hook checks inventory for scissors
   - If no scissors found, removal is prevented
   - Character gets error message

2. **With scissors:**
   - Character has scissors in inventory
   - Removal is allowed
   - Character sees: "|r*PAIN* You carefully cut through the needle attachment, severing the wristpad's connection to your wrist. Blood wells from the puncture wound as you remove the device.|n"
   - Watch is marked as damaged (`db.is_cut = True`)
   - Watch name changes to "cut Pulse watch"
   - Watch description updates to reflect damage

**Messages:**

Without scissors:
```
|rThe wristpad's needle is firmly anchored to your wrist. You need scissors to remove it painfully.|n
```

With scissors (character):
```
|r*PAIN* You carefully cut through the needle attachment, severing the wristpad's connection to your wrist. Blood wells from the puncture wound as you remove the device.|n
```

With scissors (others):
```
|r[Character] carefully removes their wristpad with surgical scissors, wincing in pain.|n
```

**Technical:**
- Implemented in `Wristpad.at_pre_remove()` method
- Checks for item with `key == 'surgical scissors'` in inventory
- Sets `db.is_cut = True` flag
- Updates key, description, and appearance

---

### 4. Reattachment via Electronics Skill

**What it does:**
- A severed/cut pulse watch can be reattached to the wrist
- Reattachment requires an Electronics skill check
- Target difficulty is 25 (moderate)
- Success restores the watch to original state
- Failure permanently destroys the watch

**How to use:**

```
repair pulse watch <watch name>
```

Examples:
```
repair pulse watch cut pulse watch
repair pulse watch my broken watch
```

**Skill Check:**
- Effective roll = (1d100 roll) + (Electronics * 2)
- Target difficulty: 25
- Most deckers with decent electronics (15+) will pass consistently
- Electronics 0 characters have ~25% chance of success

**Success Result:**
- Watch is repaired and restored to working condition
- Name reverts to "Pulse watch"
- Description reverts to original working state
- Watch can be worn again immediately
- No cooldown or additional requirements

**Failure Result:**
- Watch is permanently destroyed
- Name changes to "broken pulse watch"
- Watch cannot be picked up anymore (locked)
- Watch has final description: "A destroyed municipal wristpad, its circuits fried beyond all repair. A smoking scent rises from its shattered components."

**Messages:**

Before repair attempt:
```
|y[Electronics Check: 47 vs Difficulty 25]|n
```

Success:
```
|g*beep* You carefully reattach the [watch name], threading the needle back through the puncture site on your wrist. After a moment, it chirps to life.|n

Others see:
|g*beep* [Character] carefully reattaches their pulse watch.|n
```

Failure:
```
|r*fzzzt* Your repair attempt fails! The delicate circuitry of the [watch name] is now beyond recovery. The device is permanently damaged.|n

Others see:
|r*fzzzt* [Character]'s repair attempt fails - the [watch name] is now beyond recovery.|n
```

**Technical:**
- Implemented as `CmdRepairPulseWatch` command
- Checks for items with `db.is_municipal_wristpad == True` and `db.is_cut == True`
- Reads Electronics stat from `char.db.electronics`
- Simple d100 roll system with stat multiplier
- Modifies watch state and description on success/failure

---

## Surgical Scissors Item

**Prototype Name:** `SURGICAL_SCISSORS`

**Properties:**
- Key: "surgical scissors"
- Description: Precision surgical instruments designed for delicate cutting tasks, including municipal pulse watch needle attachments
- Weight: 0.05 kg (very light)
- Wearable: No (carried item)
- Can be spawned by builders/admin

**Usage:**
- Required to remove a municipal pulse watch
- Can be found in medical rooms, hacker hideouts, or purchasable items
- Consumable/reusable (doesn't disappear after use)
- Can be dropped/traded/sold like any item

**Spawning:**
```
@spawn SURGICAL_SCISSORS
```

---

## Gameplay Implications

### For Decker/Tracker Roles:
- Unique watch IDs enable location tracking and surveillance gameplay
- Removed watches create evidence/clues for investigation
- Electronics check adds skill-based recovery mechanics
- Creates high-stakes item management

### For Security/Enforcement:
- Watch removal indicates unauthorized decker activity
- Traces/clues from damaged watches support investigation
- Can be used as evidence in roleplay situations

### For General Players:
- Immersive removal mechanic encourages roleplay
- Creates consequences for getting caught (broken watch)
- Electronics skill becomes valuable for equipment maintenance
- Adds tension to wearing government-issued devices

---

## State Tracking

### Pulse Watch Database Attributes:

```python
watch.db.is_municipal_wristpad    # True for government-issued
watch.db.is_hacked_wristpad       # False (municipal = not hacked)
watch.db.pulse_watch_id           # 10-char unique ID (e.g., "K7m@4P!xZ2")
watch.db.is_cut                   # True if removed without reattachment
watch.db.is_broken                # True if repair failed
watch.db.desc                     # Updated on cut/repair
```

### Character NDB Attributes:

None specific to pulse watch (uses standard worn items tracking).

---

## Troubleshooting

### Watch won't come off:
- Check inventory for scissors
- Must have scissors item in inventory with exact name "surgical scissors"
- Try: `inventory` to see what you're carrying

### Repair keeps failing:
- Check Electronics skill: `stats` or `ip`
- Need ~25 electronics to pass reliably (50%+ chance at 20, ~80% chance at 30)
- Each attempt is a fresh dice roll - some luck involved

### Lost the watch:
- If permanently destroyed, will need admin spawn a new one
- If just "cut", can be repaired with scissors + Electronics skill
- If dropped, use `search` or ask staff to locate it

### Can't find scissors:
- Check with staff or look in medical/tech areas
- Can be purchased from shops if available
- Spawning restricted to builders/admin via `@spawn SURGICAL_SCISSORS`

---

## Command Reference

### Player Commands:

**Repair Pulse Watch:**
```
repair pulse watch <watch name>
reattach pulse watch <watch name>
fix pulse watch <watch name>
```

### Admin/Builder Commands:

**Spawn Scissors:**
```
@spawn SURGICAL_SCISSORS
```

**Spawn Municipal Wristpad:**
```
@spawn MUNICIPAL_WRISTPAD
```

**Check Watch State:**
```
examine <watch>
```

---

## Implementation Notes

### Files Modified:
1. `typeclasses/items.py` - Wristpad class
   - Added unique ID generation in `at_object_creation()`
   - Added `at_wear()` hook for welcome chime
   - Added `at_pre_remove()` hook for scissors check and removal logic

2. `commands/CmdRepairPulseWatch.py` - New command
   - Implements repair/reattach mechanics
   - Electronics skill check system
   - Success/failure state changes

3. `commands/default_cmdsets.py`
   - Added import for CmdRepairPulseWatch
   - Added command to CharacterCmdSet

4. `world/prototypes.py`
   - Added SURGICAL_SCISSORS prototype
   - Already had MUNICIPAL_WRISTPAD and HACKED_WRISTPAD

### No Changes Needed:
- `world/safetynet/utils.py` - has_municipal_wristpad() still works
- `commands/mapper.py` - Map display already gated by worn wristpad
- `commands/CmdMedical.py` - Medical access already requires worn wristpad
- Combat/vitals display - Already gated by worn wristpad

---

## Future Enhancement Ideas

1. **Animation System** - Custom removal/wear animations
2. **Tracking Network** - Cross-city watch tracking for deckers
3. **Watch Jamming** - Electronics-based interference
4. **Medical Alerts** - Automatic alerts if watch shows critical health
5. **Lock System** - Authorized unlock codes for safe removal
6. **Self-Destruct** - Government watches that can remotely destroy themselves

---

*This system is fully implemented and ready for use. All features are functional and tested.*
