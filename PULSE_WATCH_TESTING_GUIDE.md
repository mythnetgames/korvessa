# PULSE WATCH FEATURES - TESTING GUIDE

## Quick Test Workflow

### Prerequisites
Before testing, make sure you have:
- Administrative or builder access
- Access to spawn commands

---

## Test 1: Basic Unique ID Generation and Welcome Chime

### Steps:

1. **Spawn a municipal wristpad:**
   ```
   @spawn MUNICIPAL_WRISTPAD
   ```

2. **Examine the watch to see the unique ID:**
   ```
   examine pulse watch
   ```
   Look for the output showing the watch object details

3. **Put on the watch:**
   ```
   wear pulse watch
   ```

4. **Expected Result:**
   You should see a message like:
   ```
   *beep* Welcome, K7m@4P!xZ2! Glory be to China!
   ```
   (The alphanumeric string will be different each time)

5. **Others see:**
   ```
   *beep* [Your Name]'s wristpad chirps and activates.
   ```

**Status:** ✓ PASS (if you see welcome message with unique ID)

---

## Test 2: Scissors-Required Removal

### Steps:

1. **Try to remove the watch WITHOUT scissors:**
   ```
   remove pulse watch
   ```

2. **Expected Result:**
   ```
   |rThe wristpad's needle is firmly anchored to your wrist. You need scissors to remove it painfully.|n
   ```
   (Should prevent removal with error message)

3. **Spawn surgical scissors:**
   ```
   @spawn SURGICAL_SCISSORS
   ```

4. **Remove the watch WITH scissors present:**
   ```
   remove pulse watch
   ```

5. **Expected Result - Character sees:**
   ```
   |r*PAIN* You carefully cut through the needle attachment, severing the wristpad's connection to your wrist. Blood wells from the puncture wound as you remove the device.|n
   ```

6. **Expected Result - Others see:**
   ```
   |r[Your Name] carefully removes their wristpad with surgical scissors, wincing in pain.|n
   ```

7. **Check the watch name changed:**
   ```
   inventory
   ```
   Should show "cut Pulse watch" instead of "Pulse watch"

8. **Examine the watch:**
   ```
   examine cut pulse watch
   ```
   Description should mention "severed" and "broken needle attachment"

**Status:** ✓ PASS (if removal blocked without scissors, allowed with scissors, and watch renamed to "cut Pulse watch")

---

## Test 3: Reattachment via Electronics Skill Check

### Steps:

1. **Make sure you have the cut pulse watch in inventory:**
   ```
   inventory
   ```
   Should show "cut Pulse watch"

2. **Make sure you have surgical scissors:**
   ```
   inventory
   ```
   Should show "surgical scissors"

3. **Check your current Electronics skill:**
   ```
   stats
   ```
   or
   ```
   ip
   ```
   Note your Electronics value

4. **Attempt to repair the watch:**
   ```
   repair pulse watch cut pulse watch
   ```

5. **Expected Result:**
   - You'll see a skill check display showing your roll vs difficulty 25
   ```
   |y[Electronics Check: 47 vs Difficulty 25]|n
   ```

6. **If you PASS (roll >= 25):**
   - Character message:
     ```
     |g*beep* You carefully reattach the cut Pulse watch, threading the needle back through the puncture site on your wrist. After a moment, it chirps to life.|n
     ```
   - Others see:
     ```
     |g*beep* [Your Name] carefully reattaches their pulse watch.|n
     ```
   - Watch name should revert to "Pulse watch" (without "cut")
   - Watch description should revert to original working state

7. **If you FAIL (roll < 25):**
   - Character message:
     ```
     |r*fzzzt* Your repair attempt fails! The delicate circuitry of the cut Pulse watch is now beyond recovery. The device is permanently damaged.|n
     ```
   - Watch becomes "broken pulse watch" (permanently destroyed)
   - Watch can no longer be picked up

**Status:** ✓ PASS (if skill check triggers, success repairs and renames watch, failure destroys watch)

---

## Test 4: Full Workflow Integration

### Complete Testing Scenario:

1. **Start fresh:**
   ```
   inventory
   ```
   Drop/remove any extra items

2. **Spawn fresh watch and scissors:**
   ```
   @spawn MUNICIPAL_WRISTPAD
   @spawn SURGICAL_SCISSORS
   ```

3. **Put on the watch:**
   ```
   wear pulse watch
   ```
   See: Welcome message with unique ID

4. **Try to remove without scissors (scissors still in inventory):**
   ```
   drop surgical scissors
   remove pulse watch
   ```
   See: Error message about needle being anchored

5. **Pick up scissors and remove:**
   ```
   get surgical scissors
   remove pulse watch
   ```
   See: Pain message, watch renamed to "cut Pulse watch"

6. **Attempt repair:**
   ```
   repair pulse watch cut pulse watch
   ```
   See: Skill check and result (success or failure)

7. **Verify final state:**
   ```
   examine <watch>
   inventory
   ```

---

## Debugging Commands

### If Welcome Chime Doesn't Show:

1. Check watch attributes:
   ```
   examine pulse watch
   ```
   Look for database attributes showing:
   - is_municipal_wristpad = True
   - pulse_watch_id = [10-character string]

2. Try wearing again:
   ```
   remove pulse watch
   wear pulse watch
   ```

### If Scissors Check Doesn't Work:

1. Verify scissors name:
   ```
   inventory
   examine surgical scissors
   ```
   Item key must be exactly "surgical scissors"

2. Try removal again:
   ```
   remove pulse watch
   ```

### If Repair Command Not Found:

1. Check available commands:
   ```
   help repair
   ```

2. Try alternative aliases:
   ```
   reattach pulse watch <watch>
   fix pulse watch <watch>
   ```

---

## Expected Behavior Summary

| Action | Without Scissors | With Scissors |
|--------|------------------|---------------|
| Remove Watch | BLOCKED - error message | ALLOWED - pain message, watch cut |
| Watch Name | "Pulse watch" | Changes to "cut Pulse watch" |
| Watch Description | Original working state | Shows as severed/damaged |
| Repair Possible | N/A | Yes (Electronics check 25+) |

---

## Troubleshooting

### Issue: Welcome message shows but without unique ID
**Solution:** Make sure at_wear() hook is running. Try: remove/wear again

### Issue: Scissors check doesn't prevent removal
**Solution:** Verify scissors item name is exactly "surgical scissors" (case-insensitive in code)

### Issue: Repair command returns "Usage" error
**Solution:** Syntax is: `repair pulse watch <watchname>` - make sure "pulse watch" is exact

### Issue: Repair always fails
**Solution:** Check Electronics skill is 25+ for reliable pass. Each attempt is a fresh 1d100 roll, so some variance is expected

### Issue: Repaired watch still shows as "cut"
**Solution:** Repair was successful - check inventory again. Name should have reverted to "Pulse watch"

---

## Admin Verification Commands

To verify the system is working:

```
# Check handler is loaded
@py from commands.CmdRepairPulseWatch import CmdRepairPulseWatch; print("Command loaded successfully")

# Check prototypes exist
@py from world import prototypes; print(hasattr(prototypes, 'MUNICIPAL_WRISTPAD')); print(hasattr(prototypes, 'SURGICAL_SCISSORS'))

# Check character has required methods
@py from typeclasses.items import Wristpad; print(hasattr(Wristpad, 'at_wear')); print(hasattr(Wristpad, 'at_pre_remove'))
```

---

## Feature Checklist

- [ ] Unique ID generated on watch creation (10 characters with letters, numbers, symbols)
- [ ] Welcome chime displays ID when watch is worn
- [ ] Watch cannot be removed without scissors in inventory
- [ ] Scissors present allows removal with pain message
- [ ] Removed watch is renamed to "cut Pulse watch"
- [ ] Removed watch description updated to show damage
- [ ] Repair command exists and accepts syntax: `repair pulse watch <name>`
- [ ] Electronics skill check triggers with difficulty 25
- [ ] Successful repair restores watch to original state and name
- [ ] Failed repair permanently destroys watch and locks it

---

## Performance Notes

- Unique ID generation: O(1) - just random string creation
- Wear/remove/repair: All O(1) operations
- No database queries in hot paths
- Safe for production use

---

*All features implemented and ready for testing. Report any issues to development team.*
