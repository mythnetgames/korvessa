"""
Death Progression System

A simple, reliable death progression that sends messages to dying characters
and eventually completes the death process.

Uses Evennia's delay() for timing instead of a repeating script, which is
more reliable and easier to debug.
"""

from evennia.utils import delay
from evennia.comms.models import ChannelDB
from evennia import DefaultScript
import time


# Configuration - can be adjusted for testing
TOTAL_DURATION = 90  # seconds until permanent death
MESSAGE_COUNT = 10   # number of progression messages


def _log(msg):
    """Log to Splattercast channel."""
    try:
        ch = ChannelDB.objects.get_channel("Splattercast")
        ch.msg(msg)
    except:
        pass


def start_death_progression(character):
    """
    Start death progression for a character.
    
    Uses delay-based messaging instead of a script timer for reliability.
    """
    if not character:
        _log("DEATH_PROG: No character provided")
        return None
    
    _log(f"DEATH_PROG: Starting for {character.key}")
    
    # Check for existing progression
    if getattr(character.ndb, '_death_progression_active', False):
        _log(f"DEATH_PROG: Already active for {character.key}")
        return None
    
    # Mark as active
    character.ndb._death_progression_active = True
    character.ndb._death_progression_start = time.time()
    character.ndb._death_progression_message_index = 0
    
    # Send initial message immediately
    _send_initial_message(character)
    
    # Schedule all progression messages using delay()
    message_interval = TOTAL_DURATION / MESSAGE_COUNT
    
    for i in range(MESSAGE_COUNT):
        delay_time = message_interval * (i + 1)
        delay(delay_time, _send_progression_message, character, i)
    
    # Schedule final death
    delay(TOTAL_DURATION + 2, _complete_death, character)
    
    _log(f"DEATH_PROG: Scheduled {MESSAGE_COUNT} messages over {TOTAL_DURATION}s for {character.key}")
    
    return True


def _send_to_character(character, text):
    """
    Send a message to a dead/dying character, bypassing filters.
    
    Uses ndb._death_curtain_active flag which the character's msg() method
    checks to allow messages through during death progression.
    """
    if not character:
        return
    
    # Set the flag that allows messages through the filter
    # Keep it active throughout death progression
    character.ndb._death_curtain_active = True
    
    try:
        character.msg(text)
    except Exception as e:
        _log(f"DEATH_PROG_ERROR: Send failed: {e}")


def _send_initial_message(character):
    """Send the initial dying message."""
    if not character:
        return
    
    _log(f"DEATH_PROG: Sending initial message to {character.key}")
    
    msg = (
        "\n|R" + "=" * 60 + "|n\n"
        "|RYou hover at the threshold between life and death.|n\n"
        "|rYour essence flickers like a candle in the wind...|n\n"
        "|RThere may still be time for intervention.|n\n"
        "|R" + "=" * 60 + "|n\n"
    )
    
    _send_to_character(character, msg)


def _send_progression_message(character, index):
    """Send a specific progression message."""
    if not character:
        return
    
    # Check if progression was cancelled (e.g., by revival)
    if not getattr(character.ndb, '_death_progression_active', False):
        _log(f"DEATH_PROG: Cancelled, skipping message {index} for {character.key}")
        return
    
    messages = _get_messages()
    
    if index >= len(messages):
        index = len(messages) - 1
    
    msg_data = messages[index]
    
    _log(f"DEATH_PROG: Message {index + 1}/{len(messages)} for {character.key}")
    
    # Send the dying message
    _send_to_character(character, msg_data["dying"])
    
    # Send observer message if in a location
    if character.location and "observer" in msg_data:
        obs_msg = msg_data["observer"].format(name=character.key)
        character.location.msg_contents(obs_msg, exclude=[character])


def _complete_death(character):
    """Complete the death process and present the CLONE/DIE choice."""
    if not character:
        return
    
    # Check if already completed or cancelled
    if not getattr(character.ndb, '_death_progression_active', False):
        _log(f"DEATH_PROG: Already completed/cancelled for {character.key}")
        return
    
    _log(f"DEATH_PROG: Completing death for {character.key}")
    
    # Clear the progression flag
    character.ndb._death_progression_active = False
    
    # Send final message (flag still allows messages through)
    final_msg = (
        "\n|m" + "=" * 60 + "|n\n"
        "|mThe Watcher's gaze falls upon you...|n\n"
        "|mYour fate is sealed in the eternal silence.|n\n"
        "|m" + "=" * 60 + "|n\n"
    )
    _send_to_character(character, final_msg)
    
    # Now clear the curtain flag - no more messages needed
    character.ndb._death_curtain_active = False
    
    # STORE THE DEATH LOCATION BEFORE ANY MOVEMENTS
    death_location = character.location
    
    # Send observer message
    if character.location:
        character.location.msg_contents(
            f"|#5f005f{character.key}'s form fades from sight, becoming one with The Watcher's realm.|n",
            exclude=[character]
        )
    
    # Get account and session
    account = character.account
    session = None
    if account and account.sessions.all():
        session = account.sessions.all()[0]
    
    if not account or not session:
        _log(f"DEATH_PROG: No account/session for {character.key}")
        return
    
    # Store death location for later use if player chooses DIE
    account.ndb._death_location = death_location
    
    # Present the choice (no backup data anymore - just ask LIVE or DIE)
    _present_death_choice(character, account, session)


def _present_death_choice(character, account, session):
    """Present the LIVE or DIE choice to the player."""
    from evennia.utils import delay
    
    # Store state for the choice
    account.ndb._death_choice_pending = True
    account.ndb._death_choice_character = character
    
    # Add the death choice cmdset to the account AND session
    # (session is the actual command receiver when unpuppeted)
    from commands.death_choice import DeathChoiceCmdSet
    account.cmdset.add(DeathChoiceCmdSet, persistent=False)
    if session:
        session.cmdset.add(DeathChoiceCmdSet, persistent=False)
    
    # Small delay then show the choice
    delay(2.0, _show_death_choice_menu, account, session)


def _show_death_choice_menu(account, session):
    """Display the death choice menu in Watcher's Domain theme."""
    account.msg("")
    account.msg("=" * 70)
    account.msg("")
    account.msg("    THE WATCHER OBSERVES. YOUR CHOICE AWAITS.")
    account.msg("")
    account.msg("    Your essence teeters at the threshold between breath and silence.")
    account.msg("    The Watcher's gaze presses upon your soul, appraising, measuring.")
    account.msg("")
    account.msg("    You stand in the Watcher's Domain - a space between worlds.")
    account.msg("    Here, in this moment, only one choice matters.")
    account.msg("")
    account.msg("    " + "-" * 66)
    account.msg("")
    account.msg("    |cLIVE|n    - Return to the mortal world. Face the consequences.")
    account.msg("           The Watcher will speak with those who tend the world.")
    account.msg("           You will answer for what transpired.")
    account.msg("")
    account.msg("    |rDIE|n     - Accept the void. Let your story end here.")
    account.msg("           The Watcher releases you into eternal silence.")
    account.msg("           Your name fades from the world's memory.")
    account.msg("")
    account.msg("    " + "-" * 66)
    account.msg("")
    account.msg("=" * 70)
    account.msg("")
    account.msg("Type |cLIVE|n or |rDIE|n to choose your fate.")
    account.msg("")
    
    # Death choice cmdset is added in _present_death_choice


def _process_death_choice(account, choice):
    """Process the player's death choice."""
    # Get session first
    session = account.sessions.all()[0] if account.sessions.count() else None
    
    # Remove the death choice cmdset from both account and session
    try:
        account.cmdset.remove("death_choice_cmdset")
    except Exception:
        pass
    if session:
        try:
            session.cmdset.remove("death_choice_cmdset")
        except Exception:
            pass
    
    # Get stored state
    character = getattr(account.ndb, '_death_choice_character', None)
    death_location = getattr(account.ndb, '_death_location', None)
    
    # Clear the state
    if hasattr(account.ndb, '_death_choice_pending'):
        del account.ndb._death_choice_pending
    if hasattr(account.ndb, '_death_choice_character'):
        del account.ndb._death_choice_character
    if hasattr(account.ndb, '_death_location'):
        del account.ndb._death_location
    
    _log(f"DEATH_CHOICE: {account.key} chose {choice}")
    
    if choice == "live":
        # Player chose to live - teleport to room #5 for admin intervention
        _handle_live_path(account, character, session)
    else:
        # Chose to die - show permanent death sequence with corpse creation
        _handle_permanent_death_path(account, character, session, death_location)


def _handle_live_path(account, character, session):
    """Handle the LIVE choice - teleport to room #5 for admin intervention."""
    from evennia.utils import delay
    from evennia import search_object
    from world.medical.utils import full_heal
    
    account.msg("\n" * 2)
    account.msg("=" * 70)
    account.msg("")
    account.msg("The Watcher observes your choice.")
    account.msg("")
    
    # Revive the character and teleport to room #5
    def _revive_and_teleport():
        if not character:
            _log("LIVE_PATH: No character found")
            return
        
        # First, fully heal the character
        try:
            full_heal(character)
            _log(f"LIVE_PATH: Revived {character.key}")
        except Exception as e:
            _log(f"LIVE_PATH: Error reviving {character.key}: {e}")
        
        # Clear any death flags
        if hasattr(character.ndb, 'death_curtain_pending'):
            del character.ndb.death_curtain_pending
        if hasattr(character.ndb, '_death_curtain_active'):
            del character.ndb._death_curtain_active
        if hasattr(character.ndb, '_death_progression_active'):
            del character.ndb._death_progression_active
        if hasattr(character.db, 'death_processed'):
            del character.db.death_processed
        
        # Try to find room #5 by dbref
        try:
            admin_room = search_object("#5")
            if admin_room and len(admin_room) > 0:
                old_loc = character.location
                character.move_to(admin_room[0], quiet=True)
                _log(f"LIVE_PATH: Moved {character.key} from {old_loc} to {admin_room[0].key}")
                
                # Puppet the character back so they can see the room
                if session and account:
                    account.puppet_object(session, character)
                    _log(f"LIVE_PATH: Puppeted {character.key}")
                
                account.msg("You are drawn through the veil of The Watcher's Domain.")
                account.msg("When vision returns, you find yourself in an unfamiliar place.")
                account.msg("A figure awaits, ready to speak about your fate.")
                account.msg("")
                
                # Force a look command so they see the room
                delay(0.5, lambda: character.execute_cmd("look"))
            else:
                _log("LIVE_PATH: Room #5 not found, using limbo")
                # Fallback to limbo if room #5 doesn't exist
                _move_to_limbo(character)
                account.msg("You are drawn into the void, waiting for judgment.")
        except Exception as e:
            _log(f"LIVE_PATH: Error teleporting {character.key}: {e}")
            import traceback
            _log(traceback.format_exc())
            _move_to_limbo(character)
    
    delay(2.0, _revive_and_teleport)
    delay(5.0, account.msg, "")
    delay(6.0, account.msg, "=" * 70)


def _handle_permanent_death_path(account, character, session, death_location):
    """Handle the permanent death path (player chose DIE)."""
    from evennia.utils import delay
    
    # Store the character name in deceased names list BEFORE any deletion
    # This prevents the name from being reused
    char_name = character.key if character else None
    if char_name and account:
        # Strip any Roman numerals from the name to get base name
        import re
        roman_pattern = r'\s+(M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3}))$'
        base_name = re.sub(roman_pattern, '', char_name, flags=re.IGNORECASE).strip()
        
        # Add to deceased names list
        if not account.db.deceased_character_names:
            account.db.deceased_character_names = []
        if base_name not in account.db.deceased_character_names:
            account.db.deceased_character_names.append(base_name)
            _log(f"PERMANENT_DEATH: Added '{base_name}' to deceased names for {account.key}")
    
    # Store character reference and death location for deletion after cutscene
    account.ndb._character_to_delete = character
    account.ndb._corpse_location = death_location
    
    # Create corpse NOW in the death location BEFORE moving character
    if death_location and character:
        try:
            corpse = _create_corpse(character, death_location)
            _log(f"PERMANENT_DEATH: Corpse created in {death_location.key} for {character.key}")
        except Exception as e:
            _log(f"PERMANENT_DEATH: Error creating corpse: {e}")
    
    # Move character to limbo
    _move_to_limbo(character)
    
    # Unpuppet
    if session:
        account.unpuppet_object(session)
    
    # Remove character from account's character list (allows new char creation)
    if character and account and character in account.characters:
        account.characters.remove(character)
        _log(f"PERMANENT_DEATH: Removed {character.key} from {account.key}'s character list")
    
    # Lock commands during the death sequence
    account.ndb._clone_awakening_locked = True
    if session:
        session.ndb._clone_awakening_locked = True
    
    # Play the permanent death sequence
    _play_permanent_death(account, character, session)


def _play_permanent_death(account, character, session):
    """Play the permanent death sequence in Watcher's Domain with divine theme."""
    from evennia.utils import delay
    
    # Clear screen
    account.msg("\n" * 3)
    
    # Color codes for Watcher's Domain gradient
    # Deep purple -> Dark magenta -> Magenta -> Bright magenta -> Pink
    
    # The dissolution begins
    delay(0.5, account.msg, "|m" + "=" * 70 + "|n")
    delay(1.0, account.msg, "")
    delay(1.5, account.msg, "|5You release your grip on the mortal world.|n")
    delay(3.0, account.msg, "")
    delay(4.0, account.msg, "|5The breath leaves your body.|n")
    delay(5.5, account.msg, "|5The pain becomes memory becomes nothing.|n")
    delay(7.0, account.msg, "|5Everything... dissolves...|n")
    delay(9.0, account.msg, "")
    delay(10.5, account.msg, "|1Darkness wraps around you, soft and inevitable.|n")
    delay(12.5, account.msg, "")
    delay(14.0, account.msg, "|1No light. No sound. No self.|n")
    delay(16.0, account.msg, "")
    delay(18.0, account.msg, "|1Only the vast, knowing silence.|n")
    delay(20.0, account.msg, "")
    delay(22.0, account.msg, "|m" + "=" * 70 + "|n")
    delay(24.0, account.msg, "")
    delay(26.0, account.msg, "|3    And then...|n")
    delay(28.0, account.msg, "")
    delay(30.0, account.msg, "|m    Eyes open.|n")
    delay(32.0, account.msg, "")
    delay(33.5, account.msg, "|m" + "-" * 70 + "|n")
    delay(35.0, account.msg, "")
    delay(36.5, account.msg, "|m[THE WATCHER SPEAKS - A voice like starlight and stone]|n")
    delay(38.0, account.msg, "")
    
    # Character name handling
    char_name = 'Departed One'
    if character:
        char_name = getattr(character.db, 'real_full_name', None)
        if not char_name:
            first = getattr(character.db, 'real_first_name', '')
            last = getattr(character.db, 'real_last_name', '')
            if first or last:
                char_name = f"{first} {last}".strip()
            else:
                char_name = character.key
    
    delay(40.0, account.msg, f"|m    \"I have seen your thread, {char_name}.|n")
    delay(43.0, account.msg, f"|m    I have measured its weight.|n")
    delay(46.0, account.msg, "|m    I have appraised its worth.|n")
    delay(49.0, account.msg, "")
    delay(51.5, account.msg, "|m    You sought to write more pages.|n")
    delay(54.5, account.msg, "|m    Your story ended here instead.|n")
    delay(57.5, account.msg, "")
    delay(60.0, account.msg, "|m    Your name fades from the world.|n")
    delay(63.0, account.msg, "|m    Your deeds become whispers.|n")
    delay(66.0, account.msg, "|m    Your thread unravels into the eternal silence.|n")
    delay(69.0, account.msg, "|m    You are released.\"|n")
    delay(72.0, account.msg, "")
    
    delay(74.5, account.msg, "|m" + "-" * 70 + "|n")
    delay(76.0, account.msg, "")
    delay(78.0, account.msg, "|m" + "=" * 70 + "|n")
    
    # Start character creation after sequence
    delay(80.0, _begin_character_creation, account, character, session)


def _handle_death_completion(character):
    """Handle corpse creation and character transition to limbo.
    
    NOTE: This is now only called as a fallback. Main flow goes through
    _complete_death -> _present_death_choice -> _process_death_choice
    """
    try:
        # Check if character has a clone backup
        from typeclasses.cloning_pod import has_clone_backup, get_clone_backup
        has_backup = has_clone_backup(character)
        backup_data = get_clone_backup(character) if has_backup else None
        
        _log(f"DEATH_PROG: {character.key} has clone backup: {has_backup}")
        
        # Create corpse
        corpse = _create_corpse(character)
        
        # Get account before unpuppeting
        account = character.account
        session = None
        if account and account.sessions.all():
            session = account.sessions.all()[0]
        
        # Move character to limbo
        _move_to_limbo(character)
        
        # Unpuppet and start character creation/restoration
        if account and session:
            account.unpuppet_object(session)
            
            if has_backup and backup_data:
                # Has clone backup - restore from it
                _start_clone_restoration(account, character, session, backup_data)
            else:
                # No clone backup - full character creation
                _start_new_character(account, character, session)
        
        # Archive the character
        if hasattr(character, 'archive_character'):
            character.archive_character(reason="death")
        
        _log(f"DEATH_PROG: Death completion done for {character.key}")
        
    except Exception as e:
        _log(f"DEATH_PROG_ERROR: Death completion failed: {e}")
        import traceback
        _log(f"DEATH_PROG_TRACE: {traceback.format_exc()}")


def _create_corpse(character, location=None):
    """Create a corpse object from the dead character.
    
    Args:
        character: The character object to create a corpse from
        location: Optional specific location for corpse. If None, uses character.location
    
    Returns:
        Corpse object or None if creation failed
    """
    from evennia import create_object
    
    # Use provided location or character's current location
    corpse_location = location or character.location
    
    if not corpse_location:
        _log(f"DEATH_PROG_ERROR: No location for corpse of {character.key}")
        return None
    
    try:
        corpse = create_object(
            typeclass="typeclasses.corpse.Corpse",
            key="fresh corpse",
            location=corpse_location
        )
        
        # Transfer data
        corpse.db.original_character_name = character.key
        corpse.db.original_character_dbref = character.dbref
        corpse.db.death_time = time.time()
        corpse.db.physical_description = getattr(character.db, 'desc', 'A person.')
        
        # Preserve worn items data before transferring
        worn_items_data = {}
        if hasattr(character.db, 'worn_items') and character.db.worn_items:
            # Copy worn items structure, mapping item dbrefs
            for location_key, items in character.db.worn_items.items():
                worn_items_data[location_key] = [item.dbref for item in items if item]
        corpse.db.worn_items_data = worn_items_data
        
        # Preserve hands/wielded items data
        hands_data = {}
        if hasattr(character, 'hands') and character.hands:
            for hand, item in character.hands.items():
                if item:
                    hands_data[hand] = item.dbref
        corpse.db.hands_data = hands_data
        
        # Transfer inventory (all items in character contents)
        for item in list(character.contents):
            item.move_to(corpse, quiet=True)
        
        # Clear character's worn_items and hands since items are now on corpse
        if hasattr(character.db, 'worn_items'):
            character.db.worn_items = {}
        if hasattr(character, 'hands'):
            character.hands = {"left": None, "right": None}
        
        _log(f"DEATH_PROG: Corpse created for {character.key} in {corpse_location.key} with {len(list(corpse.contents))} items")
        return corpse
        
    except Exception as e:
        _log(f"DEATH_PROG_ERROR: Corpse creation failed for {character.key}: {e}")
        import traceback
        _log(f"DEATH_PROG_TRACE: {traceback.format_exc()}")
        return None


def _move_to_limbo(character):
    """Move character to limbo."""
    from evennia import search_object
    
    try:
        limbo = search_object("#2")[0]
        character.move_to(limbo, quiet=True, move_hooks=False)
        _log(f"DEATH_PROG: Moved {character.key} to limbo")
    except Exception as e:
        _log(f"DEATH_PROG_ERROR: Move to limbo failed: {e}")


def _begin_character_creation(account, old_character, session):
    """Start new character creation after death."""
    # Delete the old character if marked for deletion (permanent death path)
    char_to_delete = getattr(account.ndb, '_character_to_delete', None)
    if char_to_delete:
        char_name = char_to_delete.key
        try:
            # Actually delete the character object
            char_to_delete.delete()
            _log(f"PERMANENT_DEATH: Deleted character {char_name}")
        except Exception as e:
            _log(f"PERMANENT_DEATH: Error deleting character {char_name}: {e}")
        
        # Clear the reference
        if hasattr(account.ndb, '_character_to_delete'):
            del account.ndb._character_to_delete
    
    account.msg("")
    account.msg("|m[Your character has passed into The Watcher's Domain.|n")
    account.msg("|m Your story has ended. A new one awaits.]|n")
    account.msg("")
    
    try:
        from commands.charcreate import start_character_creation
        start_character_creation(account, is_respawn=False, old_character=None)
    except ImportError:
        account.msg("|mCharacter creation is under development.|n")
        account.msg("|mPlease contact staff for a new character.|n")


def cancel_death_progression(character):
    """
    Cancel death progression (e.g., if character is revived).
    Clears ALL death-related flags on the character and their account.
    """
    if not character:
        return
    
    _log(f"DEATH_PROG: Cancelling death progression for {character.key}")
    
    # Clear character flags
    if hasattr(character.ndb, '_death_progression_active'):
        del character.ndb._death_progression_active
    if hasattr(character.ndb, '_death_curtain_active'):
        del character.ndb._death_curtain_active
    if hasattr(character.ndb, '_death_progression_start'):
        del character.ndb._death_progression_start
    
    # Clear account flags if account exists
    account = character.account
    if account:
        # Clear awakening lock
        if hasattr(account.ndb, '_clone_awakening_locked'):
            del account.ndb._clone_awakening_locked
        
        # Clear death choice state
        if hasattr(account.ndb, '_death_choice_pending'):
            del account.ndb._death_choice_pending
        if hasattr(account.ndb, '_death_choice_character'):
            del account.ndb._death_choice_character
        if hasattr(account.ndb, '_death_choice_backup_data'):
            del account.ndb._death_choice_backup_data
        if hasattr(account.ndb, '_death_choice_has_backup'):
            del account.ndb._death_choice_has_backup
        
        # Clear session flags and cmdsets
        for session in account.sessions.all():
            if hasattr(session.ndb, '_clone_awakening_locked'):
                del session.ndb._clone_awakening_locked
            # Remove cmdset from session
            try:
                session.cmdset.remove("death_choice_cmdset")
            except Exception:
                pass
        
        # Remove the death choice cmdset from account if it exists
        try:
            account.cmdset.remove("death_choice_cmdset")
        except Exception:
            pass
    
    _log(f"DEATH_PROG: Cancelled all death state for {character.key}")


def get_death_progression_status(character):
    """Get status of death progression for a character."""
    if not character:
        return {"in_progression": False}
    
    if not getattr(character.ndb, '_death_progression_active', False):
        return {"in_progression": False}
    
    start_time = getattr(character.ndb, '_death_progression_start', time.time())
    elapsed = time.time() - start_time
    remaining = max(0, TOTAL_DURATION - elapsed)
    
    return {
        "in_progression": True,
        "time_elapsed": elapsed,
        "time_remaining": remaining,
        "total_duration": TOTAL_DURATION,
        "can_be_revived": remaining > 0
    }


def _get_messages():
    """Get the list of death progression messages."""
    return [
        {
            "dying": "|#5f005fYou feel The Watcher's attention settle upon you like a weight. Its gaze is cold, searching, dissecting every memory, every choice, every lie.|n\n",
            "observer": "|n{name}'s eyes go wide, then vacant, as if looking into something vast and unknowable.|n"
        },
        {
            "dying": "|#5f005fThe Watcher weighs your actions on scales you cannot see. Each moment of your life is lifted, examined, turned over in that terrible judgment. Nothing is hidden.|n\n",
            "observer": "|n{name}'s body goes rigid, every muscle taut with invisible tension.|n"
        },
        {
            "dying": "|#5f0087You are being analyzed. Dissected. Your very soul laid bare before an intelligence that has watched ten thousand like you die, and will watch ten thousand more. You are neither unique nor memorable.|n\n",
            "observer": "|n{name}'s breath comes in shallow, panicked gasps.|n"
        },
        {
            "dying": "|#5f0087The Watcher catalogs your failures. It sees the cruelty you hid. It sees the kindness you never offered. It sees exactly what you were beneath the flesh. There is no appeal. There is no mercy.|n\n",
            "observer": "|n{name}'s skin pales to ashen gray as beads of cold sweat form on their brow.|n"
        },
        {
            "dying": "|#5f00afYour consciousness fractures under that scrutiny. Piece by piece, moment by moment, you are reduced to component parts. Everything you were is being sorted into the cosmic ledger.|n\n",
            "observer": "|n{name}'s muscles twitch involuntarily, as if struck by invisible forces.|n"
        },
        {
            "dying": "|#5f00afYou realize, with terrible clarity, that The Watcher knows you. Truly knows you. Every petty thought, every selfish act, every prayer that was never sincere. Nothing escapes that gaze.|n\n",
            "observer": "|n{name}'s body convulses, a final spasm of resistance against the inevitable.|n"
        },
        {
            "dying": "|#5f00d7The weight of The Watcher's judgment presses down like gravity itself. Your mind becomes smaller, narrower, until there is nothing left but the crushing awareness of what you were and what you have failed to be.|n\n",
            "observer": "|n{name} lies nearly still, only the faintest rise and fall of their chest remaining.|n"
        },
        {
            "dying": "|#5f00d7The Watcher's assessment is complete. You have been weighed, measured, and found... as all things are found. Your thread has been observed from first breath to last. Now comes the reckoning.|n\n",
            "observer": "|n{name}'s breathing becomes barely perceptible, a whisper of life fading away.|n"
        },
        {
            "dying": "|#5f00ffIn the silence of The Watcher's presence, you understand finally: you were never in control. You were always just a story it was reading. And now that story is ending exactly as it was meant to.|n\n",
            "observer": "|n{name}'s lips have gone pale, all color draining away like sand through an hourglass.|n"
        },
        {
            "dying": "|#5f00ffYou surrender to The Watcher's gaze. There is nothing left to resist with. Only the final silence remains, and in that silence, The Watcher continues to watch.|n\n",
            "observer": "|n{name} lies motionless, no longer struggling against what cannot be escaped.|n"
        }
    ]
