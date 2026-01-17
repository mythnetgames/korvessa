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
    
    # Send observer message
    if character.location:
        character.location.msg_contents(
            f"|m{character.key}'s form fades from sight, becoming one with The Watcher's realm.|n",
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
    account.msg("|m" + "=" * 70 + "|n")
    account.msg("")
    account.msg("|m    THE WATCHER OBSERVES. YOUR CHOICE AWAITS.|n")
    account.msg("")
    account.msg("|m    Your essence teeters at the threshold between breath and silence.|n")
    account.msg("|m    The Watcher's gaze presses upon your soul, appraising, measuring.|n")
    account.msg("")
    account.msg("|m    You stand in the Watcher's Domain - a space between worlds.|n")
    account.msg("|m    Here, in this moment, only one choice matters.|n")
    account.msg("")
    account.msg("|m    " + "-" * 66 + "|n")
    account.msg("")
    account.msg("|m    |cLIVE|m    - Return to the mortal world. Face the consequences.|n")
    account.msg("|m           The Watcher will speak with those who tend the world.|n")
    account.msg("|m           You will answer for what transpired.|n")
    account.msg("")
    account.msg("|m    |rDIE|m     - Accept the void. Let your story end here.|n")
    account.msg("|m           The Watcher releases you into eternal silence.|n")
    account.msg("|m           Your name fades from the world's memory.|n")
    account.msg("")
    account.msg("|m    " + "-" * 66 + "|n")
    account.msg("")
    account.msg("|m" + "=" * 70 + "|n")
    account.msg("")
    account.msg("|mType |cLIVE|m or |rDIE|m to choose your fate.|n")
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
    
    # Clear the state
    if hasattr(account.ndb, '_death_choice_pending'):
        del account.ndb._death_choice_pending
    if hasattr(account.ndb, '_death_choice_character'):
        del account.ndb._death_choice_character
    
    _log(f"DEATH_CHOICE: {account.key} chose {choice}")
    
    if choice == "live":
        # Player chose to live - teleport to room #5 for admin intervention
        _handle_live_path(account, character, session)
    else:
        # Chose to die - show permanent death sequence
        _handle_permanent_death_path(account, character, session)


def _handle_live_path(account, character, session):
    """Handle the LIVE choice - teleport to room #5 for admin intervention."""
    from evennia.utils import delay
    from evennia.search_index import search_object
    
    account.msg("\n" * 2)
    account.msg("|m" + "=" * 70 + "|n")
    account.msg("")
    account.msg("|mThe Watcher observes your choice.|n")
    account.msg("")
    
    # Teleport character to room #5
    def _teleport_to_admin_room():
        if character and character.location:
            # Try to find room #5 by dbref
            try:
                admin_room = search_object("#5")
                if admin_room:
                    character.move_to(admin_room[0], quiet=True)
                    account.msg("|mYou are drawn through the veil of The Watcher's Domain.|n")
                    account.msg("|mWhen vision returns, you find yourself in an unfamiliar place.|n")
                    account.msg("|mA figure awaits, ready to speak about your fate.|n")
                else:
                    # Fallback to limbo if room #5 doesn't exist
                    _move_to_limbo(character)
                    account.msg("|mYou are drawn into the void, waiting for judgment.|n")
            except Exception as e:
                _log(f"LIVE_PATH: Error teleporting {character.key}: {e}")
                _move_to_limbo(character)
    
    delay(2.0, _teleport_to_admin_room)
    delay(5.0, account.msg, "")
    delay(6.0, account.msg, "|m" + "=" * 70 + "|n")


def _handle_permanent_death_path(account, character, session):
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
    
    # Store character reference for deletion after cutscene
    account.ndb._character_to_delete = character
    
    # Create corpse first
    corpse = _create_corpse(character)
    
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


def _create_corpse(character):
    """Create a corpse object from the dead character."""
    from evennia import create_object
    
    if not character.location:
        return None
    
    try:
        corpse = create_object(
            typeclass="typeclasses.corpse.Corpse",
            key="fresh corpse",
            location=character.location
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
            for location, items in character.db.worn_items.items():
                worn_items_data[location] = [item.dbref for item in items if item]
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
        
        _log(f"DEATH_PROG: Corpse created for {character.key} with {len(list(corpse.contents))} items")
        return corpse
        
    except Exception as e:
        _log(f"DEATH_PROG_ERROR: Corpse creation failed: {e}")
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
            "dying": "|nTime becomes elastic, stretched like chewing gum between your teeth. The edges of everything are soft now, melting like crayons left in a hot car. You're floating in warm red soup that tastes like copper pennies. The clock on the wall ticks backwards and each second is a small death, a tiny funeral for the person you were just a moment ago.|n\n",
            "observer": "|n{name}'s eyes roll back, showing only whites.|n"
        },
        {
            "dying": "|nYou're sinking through the floor now, through layers of concrete and earth and forgotten promises. The voices above sound like they're speaking underwater. Everything tastes like iron and regret. Your body feels like it belongs to someone else, some stranger whose story you heard in a bar once but never really believed.|n\n",
            "observer": "|n{name}'s breathing becomes shallow and erratic.|n"
        },
        {
            "dying": "|nThe world is a television with bad reception and someone keeps changing the channels. Static. Your grandmother's kitchen. Static. That time you nearly drowned. Static. The taste of blood and birthday cake and the sound of someone crying who might be you but probably isn't.|n\n",
            "observer": "|n{name} makes a low, rattling sound in their throat.|n"
        },
        {
            "dying": "|nYou're watching yourself from the ceiling corner like a security camera recording the most boring crime ever committed. That body down there, that meat puppet with your face, is leaking life like a punctured water balloon. And you're thinking, this is it? This is the grand finale?|n\n",
            "observer": "|n{name}'s skin takes on a waxy, gray pallor.|n"
        },
        {
            "dying": "|nMemory becomes a kaleidoscope where every piece is broken glass and every turn cuts deeper. You taste the last cigarette you ever smoked, feel the first hand you ever held, hear the last lie you ever told, and it's all happening simultaneously in this carnival of consciousness.|n\n",
            "observer": "|n{name}'s fingers twitch spasmodically.|n"
        },
        {
            "dying": "|nThe darkness isn't dark anymore; it's every color that doesn't have a name, every sound that was never made, every word that was never spoken. You're dissolving into the spaces between seconds, becoming the pause between heartbeats, the silence between screams.|n\n",
            "observer": "|n{name}'s body convulses once, violently.|n"
        },
        {
            "dying": "|nYou're a radio losing signal, static eating away at the song of yourself until there's nothing left but the spaces between the notes. The pain is gone now, replaced by this vast emptiness that feels like Sunday afternoons and unfinished conversations.|n\n",
            "observer": "|n{name} lies perfectly still except for barely perceptible breathing.|n"
        },
        {
            "dying": "|nYou're becoming weather now, becoming the wind that carries other people's secrets, the rain that washes away their sins. You're evaporating into stories that will never be told, jokes that will never be finished, dreams that will never be dreamed.|n\n",
            "observer": "|n{name}'s breathing has become so faint it's almost imperceptible.|n"
        },
        {
            "dying": "|nThe last thoughts are like photographs burning in a fire, curling at the edges before disappearing into ash. You remember everything and nothing. You are everyone and no one. The boundary between self and not-self becomes as meaningless as the difference between Tuesday and the color blue.|n\n",
            "observer": "|n{name}'s lips have turned blue.|n"
        },
        {
            "dying": "|n...so tired... ...so very... ...tired... ...the light is... ...warm... ...like being... ...held... ...you can hear... ...laughter... ...from somewhere... ...safe... ...you're not... ...scared anymore... ...just... ...tired...|n\n",
            "observer": "|n{name} lies motionless, their body completely still.|n"
        }
    ]
