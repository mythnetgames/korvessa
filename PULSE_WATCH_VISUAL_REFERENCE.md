# PULSE WATCH SYSTEM - VISUAL REFERENCE & FLOWCHARTS

## State Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                   PULSE WATCH LIFECYCLE                         │
└─────────────────────────────────────────────────────────────────┘

1. CREATION STATE
   ├─ @spawn MUNICIPAL_WRISTPAD
   ├─ Generates unique ID: pulse_watch_id = "K7m@4P!xZ2"
   ├─ Sets: is_municipal_wristpad = True
   ├─ Sets: is_cut = False
   ├─ Sets: is_broken = False
   └─ Ready to be picked up

2. WORN STATE
   ├─ player: wear pulse watch
   ├─ TRIGGER: at_wear() hook
   ├─ Display: "*beep* Welcome, K7m@4P!xZ2! Glory be to China!"
   ├─ Store: watch in character.db.worn_items["arm"]
   ├─ Grant: map display access
   ├─ Grant: combat system access
   └─ Grant: medical command access

3. REMOVAL ATTEMPT STATE (no scissors)
   ├─ player: remove pulse watch
   ├─ TRIGGER: at_pre_remove() hook
   ├─ Check: "surgical scissors" in inventory?
   ├─ Result: FALSE - remove blocked
   ├─ Message: "The wristpad's needle is firmly anchored..."
   └─ State: UNCHANGED - watch still worn

4. REMOVAL ATTEMPT STATE (with scissors)
   ├─ player: remove pulse watch
   ├─ TRIGGER: at_pre_remove() hook
   ├─ Check: "surgical scissors" in inventory?
   ├─ Result: TRUE - proceed with removal
   ├─ Display pain message to character
   ├─ Display action to room
   ├─ TRANSITION: is_cut = True
   ├─ Update: key = "cut Pulse watch"
   ├─ Update: description shows damage
   └─ Final: watch removed from body

5. CUT STATE
   ├─ watch: "cut Pulse watch"
   ├─ Status: Not wearable/functional
   ├─ Can be: carried, dropped, traded
   ├─ Options: Repair via Electronics check
   │           OR wait for destruction
   └─ Timeout: Can be destroyed after long period

6. REPAIR ATTEMPT STATE
   ├─ player: repair pulse watch cut pulse watch
   ├─ Check: target is_cut = True?
   ├─ Read: character.db.electronics
   ├─ Calculate: effective_roll = 1d100 + (electronics * 2)
   ├─ Compare: effective_roll vs difficulty 25
   │
   ├─ SUCCESS (roll >= 25):
   │  ├─ Restore: key = "Pulse watch"
   │  ├─ Restore: is_cut = False
   │  ├─ Restore: description to original
   │  ├─ Message: "*beep* You carefully reattach..."
   │  └─ Result: Watch fully functional again
   │
   └─ FAILURE (roll < 25):
      ├─ Destroy: is_broken = True
      ├─ Rename: key = "broken pulse watch"
      ├─ Lock: cannot pick up (locked)
      ├─ Message: "*fzzzt* Your repair attempt fails..."
      └─ Result: Permanently destroyed
```

---

## Access Control Flowchart

```
┌────────────────────────────────────────────────────────┐
│  CHARACTER ENTERS ROOM / MOVES / LOOKS                  │
└────────────────────────────────────────────────────────┘
                         │
                         ▼
        ┌─────────────────────────────────┐
        │ has_municipal_wristpad()        │
        │ (world/safetynet/utils.py)      │
        └─────────────────────────────────┘
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
         TRUE                      FALSE
         ┌──────────┐              ┌──────────────┐
         │ GRANT    │              │ DENY         │
         │ ACCESS   │              │ ACCESS       │
         └──────────┘              └──────────────┘
             │                         │
    ┌────────┴────────┐               │
    │                 │               │
    ▼                 ▼               ▼
  MAP             COMBAT         NO MAP
 DISPLAY          PROMPTS       NO COMBAT
              Medical Access     NO MEDICAL


INTERNAL CHECK (has_municipal_wristpad):
    1. Check: character.db.worn_items exists?
    2. Loop: For each body location (arm, leg, etc)
    3. Check: For each item in worn_items[location]
    4. Verify: item.db.is_municipal_wristpad == True
    5. Return: True if found, False otherwise
```

---

## Command Flow - Repair Example

```
┌──────────────────────────────────┐
│ player: repair pulse watch cut   │
└──────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────┐
│ CmdRepairPulseWatch.func()       │
└──────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────┐
│ Validate syntax:                  │
│ - "repair pulse watch <name>"    │
│ - Parse and search inventory     │
└──────────────────────────────────┘
         │                 │
         ▼ FOUND           ▼ NOT FOUND
       PASS              FAIL
         │                 │
         ▼                 ▼
      Continue         "Target not found"
                           │
                           ▼
                        RETURN
              │
              ▼
┌──────────────────────────────────┐
│ Validate watch type:              │
│ - has is_municipal_wristpad?     │
│ - has is_cut = True?             │
└──────────────────────────────────┘
         │                 │
      PASS              FAIL
         │                 │
         ▼                 ▼
      Continue        Error: "Not damaged"
                           │
                           ▼
                        RETURN
              │
              ▼
┌──────────────────────────────────┐
│ Get Electronics Skill:            │
│ electronics = char.db.electronics│
│    or 0 (default)                │
└──────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────┐
│ Roll Check:                       │
│ roll = random(1-100)             │
│ effective = roll + (skill * 2)   │
│ difficulty = 25                  │
└──────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────┐
│ Compare:                          │
│ effective >= difficulty?          │
└──────────────────────────────────┘
      │                 │
   TRUE            FALSE
      │                 │
      ▼                 ▼
   SUCCESS            FAILURE
      │                 │
      ▼                 ▼
   SUCCESS_REPAIR    FAILURE_REPAIR
      │                 │
      ├─ Restore       ├─ Destroy
      │  watch name    │  watch
      ├─ Restore       ├─ Rename to
      │  is_cut        │  "broken"
      ├─ Restore       ├─ Lock item
      │  description   ├─ Message
      ├─ Message       └─ RETURN
      └─ RETURN
```

---

## Scissors Requirement Flowchart

```
┌─────────────────────────────────────────┐
│ Player: remove pulse watch              │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│ Evennia: at_pre_remove() called         │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│ Wristpad.at_pre_remove() (items.py)    │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│ Check: is_municipal_wristpad?           │
└─────────────────────────────────────────┘
         │              │
        YES             NO
         │              │
         ▼              ▼
     Continue        Return TRUE
                    (removal allowed)
         │
         ▼
┌─────────────────────────────────────────┐
│ Check: is_cut?                          │
│ (Previously severed)                    │
└─────────────────────────────────────────┘
         │              │
        YES             NO
         │              │
         ▼              ▼
    Return TRUE    Continue
    (removal       (check scissors)
     allowed)           │
                        ▼
                ┌─────────────────────┐
                │ Loop inventory:     │
                │ for item in content │
                │   if key ==         │
                │   "surgical scissors"
                │      has = True     │
                └─────────────────────┘
                        │
              ┌─────────┴─────────┐
              │                   │
            TRUE                FALSE
              │                   │
              ▼                   ▼
        Continue            Return FALSE
        (removal ok)     + send error msg
              │
              ▼
    ┌────────────────────┐
    │ Apply Pain Message │
    │ Mark: is_cut=True  │
    │ Rename watch       │
    │ Update description │
    │ Return TRUE        │
    └────────────────────┘
              │
              ▼
         Removal allowed
```

---

## Message Timeline - Full Wear to Removal Cycle

```
TIME    EVENT                           MESSAGE

T=0     Player: wear pulse watch        (nothing yet)
        ├─ Trigger: at_wear()
        └─ Display chime

T=0+    CHARACTER SEES:
        "*beep* Welcome, K7m@4P!xZ2! Glory be to China!"
        
        OTHERS SEE:
        "*beep* [PlayerName]'s wristpad chirps and activates."

        SYSTEM STATE:
        ├─ watch in worn_items["arm"]
        ├─ map access enabled
        ├─ combat access enabled
        └─ medical access enabled

---

TIME    Player: remove pulse watch (no scissors)

T=X     Character attempts removal
        ├─ Trigger: at_pre_remove()
        ├─ Check: scissors in inventory?
        └─ Result: NO

        CHARACTER SEES:
        "|rThe wristpad's needle is firmly anchored to your wrist. 
         You need scissors to remove it painfully.|n"

        SYSTEM STATE:
        ├─ watch STILL worn
        ├─ access STILL granted
        └─ removal BLOCKED

---

TIME    Player: get scissors, remove pulse watch

T=Y     Character picks up scissors
        └─ (no special message)

T=Y+    Character attempts removal
        ├─ Trigger: at_pre_remove()
        ├─ Check: scissors in inventory?
        └─ Result: YES - proceed

        CHARACTER SEES:
        "|r*PAIN* You carefully cut through the needle attachment,
         severing the wristpad's connection to your wrist.
         Blood wells from the puncture wound as you remove
         the device.|n"

        OTHERS SEE:
        "|r[PlayerName] carefully removes their wristpad with
         surgical scissors, wincing in pain.|n"

        SYSTEM STATE:
        ├─ watch.db.is_cut = True
        ├─ watch.key = "cut Pulse watch"
        ├─ watch description updated
        ├─ watch removed from worn_items
        ├─ map access REVOKED
        ├─ combat access REVOKED
        └─ medical access REVOKED

---

TIME    Player: repair pulse watch (success)

T=Z     Character: repair pulse watch cut pulse watch
        ├─ Check: watch is_cut?
        └─ Electronics check rolls

        DISPLAY:
        "|y[Electronics Check: 52 vs Difficulty 25]|n"

        SUCCESS RESULT:
        CHARACTER SEES:
        "|g*beep* You carefully reattach the cut Pulse watch,
         threading the needle back through the puncture site
         on your wrist. After a moment, it chirps to life.|n"

        OTHERS SEE:
        "|g*beep* [PlayerName] carefully reattaches their
         pulse watch.|n"

        SYSTEM STATE:
        ├─ watch.db.is_cut = False
        ├─ watch.key = "Pulse watch"
        ├─ watch description restored
        ├─ watch ready to be worn again
        └─ repair successful
```

---

## Skill Check Probability Table

```
ELECTRONICS SKILL vs REPAIR SUCCESS RATE

Skill   | Effective Roll Range | Probability of Success
        | (roll + skill*2)     | (>= 25)
--------|----------------------|----------------------
  0     | 1 - 100              | 0%  (need 25+: can't happen)
  5     | 11 - 110             | 45% (need 25+)
 10     | 21 - 120             | 75% (need 25+)
 12     | 25 - 124             | 88% (need 25+)
 15     | 31 - 130             | 96% (need 25+)
 20     | 41 - 140             | 100% (automatic pass)
 25     | 51 - 150             | 100% (automatic pass)

INTERPRETATION:
- Electronics 0: ~50% chance (need lucky roll)
- Electronics 5-10: 45-75% chance
- Electronics 12+: ~88%+ chance (fairly reliable)
- Electronics 20+: Automatic success
```

---

## Integration Points with Other Systems

```
┌─────────────────────────────────────────────────────────┐
│ PULSE WATCH SYSTEM - INTEGRATION MAP                    │
└─────────────────────────────────────────────────────────┘

CALLS TO OTHER SYSTEMS:
┌──────────────────┐
│ Pulse Watch      │
└──────────────────┘
        │
        ├─→ has_municipal_wristpad()
        │   (world/safetynet/utils.py)
        │   └─→ Used by:
        │       - CmdMap (commands/mapper.py)
        │       - Combat system (_append_combat_prompt)
        │       - Medical commands (CmdMedical.py)
        │       - Character at_look/at_post_move
        │
        ├─→ character.db.electronics
        │   └─→ Standard stat system
        │       (used for repair check)
        │
        └─→ character.db.worn_items
            └─→ Clothing system
                (tracks what's worn)

CALLED BY OTHER SYSTEMS:
┌──────────────────┐
│ Pulse Watch      │
└──────────────────┘
        │
        ├─← at_spawn()
        │   └─ MUNICIPAL_WRISTPAD prototype
        │
        ├─← at_wear() / at_remove()
        │   └─ Clothing/wear system
        │
        └─← CmdRepairPulseWatch
            └─ Player command
```

---

## Database Schema - Pulse Watch Attributes

```
MUNICIPAL WRISTPAD OBJECT

object.db:
├─ is_municipal_wristpad: bool = True
├─ is_hacked_wristpad: bool = False
├─ pulse_watch_id: str = "K7m@4P!xZ2" (10 chars, generated)
├─ is_cut: bool = False (True if needle removed)
├─ is_broken: bool = False (True if repair failed)
├─ desc: str = "(full description text)"
├─ is_removable: bool = False (can't drop while worn)
└─ is_wristpad: bool = False (not hacked variant)

CHARACTER worn_items DURING WEAR:
char.db.worn_items:
└─ "left_arm" / "right_arm":
   └─ [wristpad_object_ref]

CHARACTER NDB DURING COMBAT:
char.ndb:
└─ combat_handler: CombatHandler (if in combat)
```

---

## Error Handling Flowchart

```
┌──────────────────────────────────────────┐
│ All Operations Have Error Paths          │
└──────────────────────────────────────────┘

REPAIR COMMAND ERRORS:
├─ No arguments provided
│  └─ "Usage: repair pulse watch <object>"
│
├─ Wrong syntax
│  └─ "Usage: repair pulse watch <object name or number>"
│
├─ Watch not found
│  └─ "[Searching]" then "Not found."
│
├─ Not a municipal wristpad
│  └─ "[object name] is not a municipal pulse watch."
│
├─ Watch not damaged
│  └─ "The [watch] doesn't appear to be damaged."
│
└─ Repair check results:
   ├─ SUCCESS: Watch repaired
   └─ FAILURE: Watch destroyed

REMOVAL ERRORS:
├─ No scissors in inventory
│  └─ "The wristpad's needle is firmly anchored..."
│
└─ With scissors:
   └─ Removal succeeds (no error)

WEAR ERRORS:
└─ None (at_wear can't fail)
```

---

*This reference guide provides complete visual documentation of the pulse watch system architecture and flows.*
