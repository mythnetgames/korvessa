# Death System Overhaul - Watcher's Domain

## Overview

The death system has been completely overhauled to replace the cyberpunk cloning/consciousness backup system with a divine fantasy-themed Watcher's Domain system. Players now face a simple LIVE or DIE choice when they die, with appropriate Watcher-themed messaging.

## Key Changes

### 1. Death Choice Commands (commands/death_choice.py)

**Removed:**
- `CmdDeathClone` - Consciousness backup restoration command
- References to consciousness backup and sleeve allocation

**Added:**
- `CmdDeathLive` - Simple command to choose LIVE path
- Direct integration with Watcher's Domain theme

### 2. Death Progression Flow (typeclasses/death_progression.py)

#### Removed Functions:
- `_start_clone_restoration()` - Matrix-style pod awakening sequence
- `_play_clone_awakening()` - 64-second clone pod extraction cutscene
- `_create_restored_clone()` - Clone character restoration from backup
- `_start_new_character()` - Clone malfunction sequence
- `_play_clone_malfunction()` - Failed clone cutscene
- `_handle_clone_path()` - Clone restoration path handler
- `_handle_failed_clone_path()` - Failed clone path handler

#### Updated Functions:
- `_complete_death()` - Now presents LIVE/DIE choice without backup checks
- `_present_death_choice()` - Simplified to handle LIVE/DIE only
- `_show_death_choice_menu()` - New Watcher's Domain theme messaging
- `_process_death_choice()` - Routes to LIVE or DIE paths

#### New Functions:
- `_handle_live_path()` - Teleports character to room #5 for admin intervention
- Updated `_play_permanent_death()` - Watcher's Domain cutscene with color palette

### 3. Death Choice Menu

**Old Theme (Cyberpunk):**
```
NEURAL PATTERN DETECTED - CONSCIOUSNESS TRANSFER INITIATED
[CONSCIOUSNESS BACKUP FOUND]
RESTORE or DIE
```

**New Theme (Divine/Watcher):**
```
THE WATCHER OBSERVES. YOUR CHOICE AWAITS.
Your essence teeters at the threshold between breath and silence.
The Watcher's gaze presses upon your soul, appraising, measuring.

LIVE    - Return to the mortal world. Face the consequences.
         The Watcher will speak with those who tend the world.
         You will answer for what transpired.

DIE     - Accept the void. Let your story end here.
         The Watcher releases you into eternal silence.
         Your name fades from the world's memory.
```

### 4. Death Cutscene (DIE Path)

**New Watcher's Domain Sequence:**
Uses color codes |m (magenta), |5 (dark purple), |1 (dark magenta), |3 (red)

Messages emphasize:
- Dissolution into darkness
- Watcher's observation and appraisal
- Release into eternal silence
- Thread unraveling
- Imminent character deletion

### 5. Life Choice (LIVE Path)

When a player chooses LIVE:
1. The Watcher approves the choice
2. Player is drawn through the veil of Watcher's Domain
3. Character is teleported to room #5
4. Admin staff speaks with them about their fate
5. Story outcome determined by admin

### 6. Permanent Death (DIE Path)

When a player chooses DIE:
1. 80-second Watcher's Domain cutscene plays
2. Character is permanently deleted
3. Player begins new character creation
4. Character name added to deceased names list

## Color Palette Used

```
|m - Magenta (primary Watcher's Domain color)
|5 - Dark purple (#5f005f)
|1 - Dark magenta (#af005f)
|3 - Red (#ff0000)
```

These colors progressively convey the mystical, unsettling nature of The Watcher observing all souls.

## File Changes Summary

| File | Changes |
|------|---------|
| commands/death_choice.py | Renamed CmdDeathClone to CmdDeathLive, updated docstrings |
| typeclasses/death_progression.py | Major refactor: removed ~400 lines of clone code, added LIVE path, updated messages |

## Testing Notes

- Death system triggers when character health reaches 0
- Players see LIVE/DIE choice menu after death progression
- LIVE choice: check room #5 exists and admin handling works
- DIE choice: verify character is deleted and new char creation starts
- No remnants of consciousness backup terminology in system

## Next Steps for Staff

1. Ensure room #5 exists and is configured for admin intervention
2. Brief staff on new LIVE choice handling (discuss story outcomes with player)
3. Monitor death scenarios to verify smooth flow
4. Consider roleplay prompts for players choosing LIVE

## Backward Compatibility

This change removes all cloning/consciousness backup mechanics. Any existing:
- Cloning pods should be removed or repurposed
- Backup data fields are ignored
- References to consciousness/sleeves are gone from character displays

Players understand they have permanent character death now.
