# Racial Mechanics System

## Overview

Each playable race has distinct perks that affect survival, social interaction, and character mechanics.

## Race Descriptions & Perks

### Human
**Description:** Brief-lived and ever-changing, humans survive by adapting when things go wrong. They stumble, recover, and try again, often succeeding not through perfection, but persistence.

**Perks:**
- **Hourly Reroll**: Once per hour, silently reroll a failed non-combat roll and accept the new result
- **Native Language**: Common

**Mechanics:**
- Stored in `character.ndb.human_reroll_data`
- Reroll timer resets after each use
- Only applies to non-combat rolls
- Automatic (staff just record when it's used)

### Elf
**Description:** Deliberate and restrained, elves prefer quiet paths and indirect solutions. They act with patience, favoring misdirection and subtle influence over force or haste.

**Perks:**
- **Subterfuge Advantage**: Gain advantage on non-combat Subterfuge rolls (roll twice, take higher)
- **Native Languages**: Common and Elvish

**Mechanics:**
- Automatically applied to qualifying rolls
- Must be tracked/called by skill system
- Language fluency set to 100 (native speaker) on creation

### Dwarf
**Description:** Stone-bred and enduring, dwarves are shaped by long labor and scarce provision. They move steadily through hardship, sustained by habit and discipline.

**Perks:**
- **Slow Metabolism**: Hunger and thirst advance more slowly (2x longer between meals/drinks)
- **Slow Intoxication**: Get drunk slower (2x longer to sober up)
- **Native Languages**: Common and Dwarvish

**Mechanics:**
- Hunger timer multiplier: `0.5x` (multiplied against CON modifier)
- Intoxication decay multiplier: `0.5x` (sobering takes 2x as long)
- Language fluency set to 100 (native speaker) on creation

## Implementation

### Files Modified
- [commands/charcreate.py](commands/charcreate.py) - Updated race descriptions, added `apply_racial_mechanics()` call
- [world/racial_mechanics.py](world/racial_mechanics.py) - New file with human reroll, elf advantage, language init
- [world/survival/core.py](world/survival/core.py) - Added dwarf modifiers for hunger/thirst/intoxication
- [typeclasses/characters.py](typeclasses/characters.py) - Added racial mechanics initialization on puppet

### Key Functions

**In `world/racial_mechanics.py`:**
- `can_use_human_reroll(character)` - Check if reroll is available
- `use_human_reroll(character)` - Use a reroll, return timestamp
- `has_elf_subterfuge_advantage(character)` - Check if elf
- `apply_elf_subterfuge_advantage(roll_result)` - Apply advantage to roll
- `initialize_race_languages(character)` - Set native language fluency
- `apply_racial_mechanics(character)` - Initialize all racial systems

**In `world/survival/core.py`:**
- `_get_constitution_modifier(character)` - Returns CON modifier (includes dwarf 0.5x)
- `_get_intoxication_decay_multiplier(character)` - Returns decay modifier (dwarf 0.5x)

## Testing

Use admin commands:
```
@survivaltest set_con 50 - Set CON for testing
@survivaltest status - Check survival state with modifiers
```

## Notes

- All races get Common as native language
- Racial language proficiency is 100 (fluent/native)
- Dwarf mechanics are integrated into survival system calculations
- Human reroll is noiseless (staff must narrate if using it)
- Elf advantage integrates with skill system (needs to be called by roll mechanics)
