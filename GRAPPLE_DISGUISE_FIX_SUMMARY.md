GRAPPLE MESSAGE DISGUISE FIX - COMPLETION SUMMARY
==================================================

ISSUE:
Combat grapple messages were showing attacker's real name instead of disguised identity.
Example: "Dalao grapples Test Dummy!" instead of "a masked individual grapples Test Dummy!"

ROOT CAUSE:
Grapple messages were using char.key and target.key directly instead of using the disguise
system functions get_display_name_safe() and msg_contents_disguised().

FIXES APPLIED:
============

1. GRAPPLE INITIATE MESSAGES (world/combat/grappling.py, resolve_grapple_initiate)
   Lines 389-396:
   - Changed: char.msg(f"You successfully grapple {target.key}!")
   - To: char.msg(f"You successfully grapple {get_display_name_safe(target, char)}!")
   - Also fixed observer message to use msg_contents_disguised() with proper character list

2. GRAPPLE FAILURE MESSAGES (world/combat/grappling.py, lines 400-432)
   - Removed all |y, |n, |r, |g color codes
   - Changed to use get_display_name_safe() for participant messages
   - Changed observer messages to use msg_contents_disguised() with [attacker, target]

3. GRAPPLE JOIN MESSAGES (world/combat/grappling.py, resolve_grapple_join, lines 530-550)
   Success messages:
   - Now use get_display_name_safe() for all three character references
   - Observer message uses msg_contents_disguised() with [char, target, current_grappler]
   
   Failure messages:
   - Similar updates with proper disguise name handling

4. GRAPPLE TAKEOVER MESSAGES (world/combat/grappling.py, resolve_grapple_takeover, lines 673-700)
   Success messages:
   - Use get_display_name_safe() for all three character references
   - Observer message via msg_contents_disguised() with proper character list
   
   Failure messages:
   - Similar updates

5. COLOR CODE CLEANUP (all files)
   Removed all combat message color codes:
   - grappling.py: Removed |g, |y, |r, |n from lines 409, 419, 421, 424, 534, 540, 556, 564, 682, 684, 688, 700, 712
   - handler.py: Removed from lines 656, 660, 741
   - Color variable assignments (lines 1341, 1375 in handler.py) intentionally left for status bar display

TECHNICAL IMPLEMENTATION:
=======================

All grapple messages now follow this pattern:

For Direct Messages to Characters:
  char.msg(f"You {action} {get_display_name_safe(other, char)}!")
  other.msg(f"{get_display_name_safe(char, other)} {action}s you!")

For Observer Messages (via msg_contents_disguised):
  msg_contents_disguised(location, "{char0_name} {action}s {char1_name}!", 
                        [attacker, target], exclude=[attacker, target])

The get_display_name_safe() function:
- Takes the character to display and the observer
- Uses disguise system to show appropriate name
- Falls back to character.key if no disguise

The msg_contents_disguised() function:
- Sends per-observer messages
- Each observer sees character names formatted for them
- Automatically applies get_display_name_safe() internally

FUNCTIONS MODIFIED:
- resolve_grapple_initiate()
- resolve_grapple_join()
- resolve_grapple_takeover()
- Various local message calls in handler.py at_repeat()

IMPORT STRUCTURE:
- get_display_name_safe is imported at module level from utils
- msg_contents_disguised is imported locally within functions from .handler
- All imports are in place and functional

RESULT:
When a disguised character grapples another character:
- Attacker sees: "You successfully grapple [target's name]!"
- Target sees: "[Attacker's disguise] grapples you!"
- Observers see: "[Disguise] grapples [target name]!" (via msg_contents_disguised)

All color codes have been removed from combat messages (except status bar variables).

VERIFICATION:
Test file created: test_grapple_disguise.py
- Tests get_display_name_safe() function
- Tests msg_contents_disguised() function
- Verifies observer sees disguised names
