# PULSE WATCH QUICK REFERENCE CARD

## Commands

### Player Commands
```
wear pulse watch              - Put on the watch (see welcome chime + ID)
remove pulse watch            - Remove watch (blocked without scissors)
repair pulse watch <watch>    - Attempt to fix a cut watch
reattach pulse watch <watch>  - Alternative: repair command
fix pulse watch <watch>       - Alternative: repair command
```

### Admin Commands
```
@spawn MUNICIPAL_WRISTPAD     - Create a municipal pulse watch
@spawn SURGICAL_SCISSORS      - Create surgical scissors
examine pulse watch           - Check watch attributes and unique ID
```

---

## Messages You'll See

### Wearing the Watch
```
*beep* Welcome, K7m@4P!xZ2! Glory be to China!
```

### Trying to Remove Without Scissors
```
The wristpad's needle is firmly anchored to your wrist. 
You need scissors to remove it painfully.
```

### Removing With Scissors (You)
```
*PAIN* You carefully cut through the needle attachment, 
severing the wristpad's connection to your wrist. 
Blood wells from the puncture wound as you remove the device.
```

### Removing With Scissors (Others See)
```
[PlayerName] carefully removes their wristpad with 
surgical scissors, wincing in pain.
```

### Repair Success
```
*beep* You carefully reattach the cut Pulse watch, 
threading the needle back through the puncture site on 
your wrist. After a moment, it chirps to life.
```

### Repair Failure
```
*fzzzt* Your repair attempt fails! The delicate circuitry 
of the cut Pulse watch is now beyond recovery. The device 
is permanently damaged.
```

---

## Watch States

| State | Name | Can Wear? | Can Repair? | Looks Like |
|-------|------|-----------|-------------|-----------|
| Working | Pulse watch | YES | N/A | Normal wristpad |
| Cut | cut Pulse watch | NO | YES | Severed with dangling cables |
| Broken | broken pulse watch | NO | NO | Destroyed circuits |

---

## Skills & Difficulty

```
REPAIR SKILL CHECK:
- Stat Used: Electronics
- Target Difficulty: 25
- Calculation: 1d100 + (Electronics * 2)

EXPECTED SUCCESS RATES:
- Electronics 0-5: 25-50% (risky)
- Electronics 10-15: 75-95% (likely)
- Electronics 20+: 100% (guaranteed)
```

---

## Getting Started

### 1. Get a Watch
```
@spawn MUNICIPAL_WRISTPAD
```

### 2. Wear It
```
wear pulse watch
```
You'll see: `*beep* Welcome, K7m@4P!xZ2! Glory be to China!`

### 3. Try to Remove (No Scissors)
```
remove pulse watch
```
You'll see: Error about needle being anchored

### 4. Get Scissors
```
@spawn SURGICAL_SCISSORS
```

### 5. Remove It (With Scissors)
```
remove pulse watch
```
You'll see: Pain message, watch becomes "cut Pulse watch"

### 6. Repair It (If Electronics Skill > 0)
```
repair pulse watch cut pulse watch
```
You'll see: Skill check, then success/failure message

---

## Unique Identifier Examples

Each watch gets a different random 10-character ID:
```
K7m@4P!xZ2
9xR#nL$wQ4
pA!2bC@3dE
4fG@5hI$6j
7kL!8mN@9o
```

Check it with: `examine pulse watch`

---

## System Benefits

**For Deckers/Trackers:**
- Unique IDs enable location tracking
- Can identify specific watches
- Removal creates evidence trails

**For Players:**
- Immersive RP of painful removal
- Consequence-based gameplay
- Skill-based item recovery

**For Staff:**
- Supports investigation gameplay
- Adds depth to item mechanics
- Creates RP opportunities

---

## Troubleshooting

**Q: Welcome message doesn't show?**
A: Make sure you're wearing a MUNICIPAL wristpad (not hacked).

**Q: Can't remove without scissors?**
A: This is intentional. Get scissors: `@spawn SURGICAL_SCISSORS`

**Q: Repair keeps failing?**
A: Electronics skill affects chance. Low skill = risky attempts.

**Q: Lost the watch?**
A: If destroyed, ask admin to spawn a new one. If cut, repair it.

**Q: Scissors don't work?**
A: Check name: `examine surgical scissors` - must be exact match.

---

## Developer Notes

### File Locations
```
typeclasses/items.py              - Wristpad class with hooks
commands/CmdRepairPulseWatch.py   - Repair command
commands/default_cmdsets.py       - Command registration
world/prototypes.py               - Item definitions
```

### Key Attributes
```
watch.db.pulse_watch_id          - Unique 10-char identifier
watch.db.is_cut                  - Needle removed flag
watch.db.is_municipal_wristpad   - Municipal vs hacked
```

### Key Methods
```
Wristpad.at_wear()               - Welcome chime display
Wristpad.at_pre_remove()         - Scissors check + pain
CmdRepairPulseWatch.func()       - Repair with skill check
```

---

## Easter Eggs

The unique ID system can support:
- Hidden tracking of specific watches
- Identification during RP investigations
- Cross-city watch network (future)
- Decker gameplay mechanics

---

*Last Updated: Implementation Complete*
*Status: Production Ready*
