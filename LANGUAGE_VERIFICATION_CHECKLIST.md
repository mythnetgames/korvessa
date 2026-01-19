LANGUAGE SYSTEM VERIFICATION CHECKLIST
=====================================

## 1. Configuration Verification

✅ RACE_LANGUAGES properly configured:
   - Human: ['common']
   - Elf: ['common', 'elvish']
   - Dwarf: ['common', 'dwarvish']

✅ LANGUAGE_ALIASES defined:
   - 'dwarven' -> 'dwarvish'
   - 'elf' -> 'elvish'

✅ LANGUAGES dict has all three languages with proper metadata

## 2. Character Creation Flow

✅ Race Selection (first_char_race):
   - Line 1084-1085: Sets racial languages from RACE_LANGUAGES
   - Stores in charcreate_data['languages']

✅ Character Finalization (first_char_finalize):
   - Line 2314: Retrieves languages from charcreate_data
   - Line 2370: Sets char.db.known_languages as SET
   - Line 2371: Sets char.db.primary_language as string
   - Line 2376: Calls initialize_language_proficiency(char)

✅ initialize_language_proficiency:
   - Sets all known languages to 100% proficiency in db.language_proficiency dict

## 3. Say Command Flow

✅ Command parses language prefix (line 152-160)
✅ Validates speaker knows the language (line 161-167)
✅ Gets primary language if no prefix (line 169-171)
✅ For each observer:
   - Gets observer's proficiency (line 240)
   - If proficiency >= 100%: Shows language name (line 242-246)
   - If proficiency > 0%: Shows language hint but garbled (line 247-250)
   - If proficiency = 0%: Shows only garbled, no language (line 251-254)
✅ Passive learning called via apply_language_garbling_to_observers (line 235)

## 4. Passive Learning Integration

✅ apply_language_garbling_to_observers calls apply_passive_language_learning (line 821)
✅ Learning respects:
   - Intelligence modifier scaling (no minimum INT)
   - Proficiency < 100% requirement (line 481)
   - Daily 5-event cap (line 493)

## 5. Racial Mechanics Compatibility

✅ initialize_race_languages updated:
   - No longer sets known_languages as dict with proficiency values
   - Now calls initialize_language_proficiency instead
   - Maintains backward compatibility

## 6. Error Checking

✅ No syntax errors in:
   - commands/charcreate.py
   - commands/say.py
   - commands/emote.py
   - world/language/utils.py
   - world/language/constants.py
   - world/racial_mechanics.py

## 7. Expected Behavior

When a dwarf is created:
1. Race selection sets languages to ['common', 'dwarvish']
2. Finalization sets known_languages to {'common', 'dwarvish'}
3. initialize_language_proficiency sets both to 100%
4. Dwarf can understand dwarvish naturally
5. Other races hearing dwarvish see:
   - No language name (0% proficiency)
   - Only garbled text
   - Passive learning triggered based on their INT modifier

When an observer hears speech:
1. apply_language_garbling_to_observers called
2. For each observer:
   - Proficiency checked
   - Text garbled if < 100%
   - Passive learning applied (speed scales with INT modifier)
3. Messages sent with proficiency-aware formatting:
   - Fluent: "*speaking {Language}*"
   - Partial: "*in {Language}*" (with garble)
   - Unknown: (garbled only, no language)

## 8. Testing Plan

Test scenarios to verify:
1. Create dwarf character with INT 14 (+2 modifier)
   - Verify char.db.known_languages == {'common', 'dwarvish'}
   - Verify char.db.primary_language == 'common'
   - Verify char.db.language_proficiency == {'common': 100.0, 'dwarvish': 100.0}

2. Create elf character with INT 8 (-1 modifier)
   - Verify char.db.known_languages == {'common', 'elvish'}
   - Verify proficiencies both at 100%

3. Have dwarf (INT 14) say something in dwarvish
   - Other dwarves see: "*speaking Dwarvish* {clear text}"
   - Non-dwarves see: "{garbled text}" (no language name)
   - Non-dwarves start learning at speed based on their INT

4. Have elf (INT 8) listen to dwarvish
   - Learning rate: 0.04 * max(0.5, 1 + (-1) * 0.25) = 0.04 * 0.75 = 0.03 per event
   - Should learn dwarvish passively
   - After hearing 5x, proficiency increases by 0.15
   - After reaching proficiency > 0%, partial speakers see "*in Dwarvish*"

5. Have scholar (INT 16) listen to dwarvish
   - Learning rate: 0.04 * max(0.5, 1 + (3) * 0.25) = 0.04 * 1.75 = 0.07 per event
   - Much faster learning than elf
   - After hearing 5x, proficiency increases by 0.35

6. Test language aliases
   - dwarven"Hello" -> treated as dwarvish
   - elf"Hello" -> treated as elvish

## Notes

- All known_languages should be SETS, not dicts
- All proficiency values stored in language_proficiency DICT
- Passive learning integrated into the say/emote command flow
- No breaking changes to existing APIs
- Backward compatibility maintained for racial_mechanics
