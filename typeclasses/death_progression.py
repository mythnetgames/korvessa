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
        "\n|R" + "=" * 60 + "|n\n"
        "|RThe darkness claims you completely...|n\n"
        "|rYour consciousness fades into the void.|n\n"
        "|R" + "=" * 60 + "|n\n"
    )
    _send_to_character(character, final_msg)
    
    # Now clear the curtain flag - no more messages needed
    character.ndb._death_curtain_active = False
    
    # Send observer message
    if character.location:
        character.location.msg_contents(
            f"|r{character.key}'s form grows utterly still, life's final spark extinguished forever.|n",
            exclude=[character]
        )
    
    # Check if character has a clone backup
    from typeclasses.cloning_pod import has_clone_backup, get_clone_backup
    has_backup = has_clone_backup(character)
    backup_data = get_clone_backup(character) if has_backup else None
    
    # Get account and session
    account = character.account
    session = None
    if account and account.sessions.all():
        session = account.sessions.all()[0]
    
    if not account or not session:
        _log(f"DEATH_PROG: No account/session for {character.key}")
        return
    
    # Present the choice
    _present_death_choice(character, account, session, has_backup, backup_data)


def _present_death_choice(character, account, session, has_backup, backup_data):
    """Present the CLONE or DIE choice to the player."""
    from evennia.utils import delay
    
    # Store state for the choice
    account.ndb._death_choice_pending = True
    account.ndb._death_choice_character = character
    account.ndb._death_choice_backup_data = backup_data
    account.ndb._death_choice_has_backup = has_backup
    
    # Small delay then show the choice
    delay(2.0, _show_death_choice_menu, account, session, has_backup)


def _show_death_choice_menu(account, session, has_backup):
    """Display the death choice menu."""
    account.msg("")
    account.msg("|X" + "=" * 70 + "|n")
    account.msg("")
    account.msg("|W    NEURAL PATTERN DETECTED - CONSCIOUSNESS TRANSFER INITIATED|n")
    account.msg("")
    
    if has_backup:
        account.msg("|g    [CLONE BACKUP FOUND]|n")
        account.msg("")
        account.msg("|W    Your consciousness hovers between this world and the next.|n")
        account.msg("|W    A backup of your neural pattern exists in the system.|n")
        account.msg("")
        account.msg("|W    You have a choice:|n")
        account.msg("")
        account.msg("|c    CLONE|n - Transfer to your backup body. You will awaken")
        account.msg("            with your memories and identity intact.")
        account.msg("")
        account.msg("|r    DIE|n   - Refuse the transfer. Your consciousness will")
        account.msg("            dissipate. You will cease to exist.")
        account.msg("")
    else:
        account.msg("|r    [NO CLONE BACKUP FOUND]|n")
        account.msg("")
        account.msg("|W    Your consciousness hovers between this world and the next.|n")
        account.msg("|r    No backup of your neural pattern exists in the system.|n")
        account.msg("")
        account.msg("|W    You have a choice:|n")
        account.msg("")
        account.msg("|y    CLONE|n - Attempt emergency neural transfer. Without a backup,")
        account.msg("            the process will fail. A blank slate may be generated.")
        account.msg("")
        account.msg("|r    DIE|n   - Accept the void. Your consciousness will")
        account.msg("            dissipate. You will cease to exist.")
        account.msg("")
    
    account.msg("|X" + "=" * 70 + "|n")
    account.msg("")
    account.msg("|WType |cCLONE|W or |rDIE|W to make your choice.|n")
    account.msg("")
    
    # Add the death choice command set
    from evennia import CmdSet
    from evennia import Command
    
    class CmdDeathClone(Command):
        """Choose to clone."""
        key = "clone"
        locks = "cmd:all()"
        
        def func(self):
            account = self.caller
            _process_death_choice(account, "clone")
    
    class CmdDeathDie(Command):
        """Choose to die."""
        key = "die"
        locks = "cmd:all()"
        
        def func(self):
            account = self.caller
            _process_death_choice(account, "die")
    
    class DeathChoiceCmdSet(CmdSet):
        key = "death_choice"
        priority = 200
        mergetype = "Replace"
        
        def at_cmdset_creation(self):
            self.add(CmdDeathClone())
            self.add(CmdDeathDie())
    
    # Add the command set
    account.cmdset.add(DeathChoiceCmdSet)


def _process_death_choice(account, choice):
    """Process the player's death choice."""
    # Remove the choice command set
    account.cmdset.remove("death_choice")
    
    # Get stored state
    character = getattr(account.ndb, '_death_choice_character', None)
    backup_data = getattr(account.ndb, '_death_choice_backup_data', None)
    has_backup = getattr(account.ndb, '_death_choice_has_backup', False)
    
    # Clear the state
    if hasattr(account.ndb, '_death_choice_pending'):
        del account.ndb._death_choice_pending
    if hasattr(account.ndb, '_death_choice_character'):
        del account.ndb._death_choice_character
    if hasattr(account.ndb, '_death_choice_backup_data'):
        del account.ndb._death_choice_backup_data
    if hasattr(account.ndb, '_death_choice_has_backup'):
        del account.ndb._death_choice_has_backup
    
    session = account.sessions.all()[0] if account.sessions.count() else None
    
    _log(f"DEATH_CHOICE: {account.key} chose {choice} (has_backup={has_backup})")
    
    if choice == "clone":
        if has_backup and backup_data:
            # Has backup - proceed with clone restoration
            _handle_clone_path(account, character, session, backup_data)
        else:
            # No backup - clone fails, show malfunction
            _handle_failed_clone_path(account, character, session)
    else:
        # Chose to die - show permanent death sequence
        _handle_permanent_death_path(account, character, session)


def _handle_clone_path(account, character, session, backup_data):
    """Handle the clone restoration path."""
    # Create corpse first
    corpse = _create_corpse(character)
    
    # Move character to limbo
    _move_to_limbo(character)
    
    # Unpuppet
    if session:
        account.unpuppet_object(session)
    
    # Archive the character
    if hasattr(character, 'archive_character'):
        character.archive_character(reason="death")
    
    # Start clone restoration
    _start_clone_restoration(account, character, session, backup_data)


def _handle_failed_clone_path(account, character, session):
    """Handle the failed clone path (no backup)."""
    # Create corpse first
    corpse = _create_corpse(character)
    
    # Move character to limbo
    _move_to_limbo(character)
    
    # Unpuppet
    if session:
        account.unpuppet_object(session)
    
    # Archive the character
    if hasattr(character, 'archive_character'):
        character.archive_character(reason="death")
    
    # Start the failed clone sequence (similar to clone but ends in failure)
    _start_new_character(account, character, session)


def _handle_permanent_death_path(account, character, session):
    """Handle the permanent death path (player chose DIE)."""
    from evennia.utils import delay
    
    # Create corpse first
    corpse = _create_corpse(character)
    
    # Move character to limbo
    _move_to_limbo(character)
    
    # Unpuppet
    if session:
        account.unpuppet_object(session)
    
    # Archive the character
    if hasattr(character, 'archive_character'):
        character.archive_character(reason="death_permanent")
    
    # Lock commands during the death sequence
    account.ndb._clone_awakening_locked = True
    if session:
        session.ndb._clone_awakening_locked = True
    
    # Play the permanent death sequence
    _play_permanent_death(account, character, session)


def _play_permanent_death(account, character, session):
    """Play the permanent death sequence."""
    from evennia.utils import delay
    
    # Clear screen
    account.msg("\n" * 3)
    
    # The void
    delay(0.5, account.msg, "|X" + "=" * 70 + "|n")
    delay(1.0, account.msg, "")
    delay(1.5, account.msg, "|xYou let go.|n")
    delay(3.0, account.msg, "")
    delay(4.0, account.msg, "|xThe light fades.|n")
    delay(5.5, account.msg, "|xThe pain fades.|n")
    delay(7.0, account.msg, "|xEverything... fades.|n")
    delay(9.0, account.msg, "")
    delay(10.5, account.msg, "|XThere is nothing.|n")
    delay(12.5, account.msg, "")
    delay(14.0, account.msg, "|XNo sensation. No thought. No self.|n")
    delay(16.0, account.msg, "")
    delay(18.0, account.msg, "|XJust... nothing.|n")
    delay(20.0, account.msg, "")
    delay(22.0, account.msg, "|X" + "=" * 70 + "|n")
    delay(24.0, account.msg, "")
    delay(26.0, account.msg, "|r    And then...|n")
    delay(28.0, account.msg, "")
    delay(30.0, account.msg, "|W    Something.|n")
    delay(32.0, account.msg, "")
    delay(33.5, account.msg, "|X" + "-" * 70 + "|n")
    delay(35.0, account.msg, "")
    delay(36.5, account.msg, "|c[SYSTEM VOICE - Cold, distant, indifferent]|n")
    delay(38.0, account.msg, "")
    delay(40.0, account.msg, "|W    \"Consciousness termination confirmed.\"|n")
    delay(42.5, account.msg, "|W    \"Neural pattern: dissolved.\"|n")
    delay(45.0, account.msg, "|W    \"Identity file: closed.\"|n")
    delay(47.5, account.msg, "")
    delay(49.5, account.msg, f"|W    \"{character.key if character else 'Subject'}: Deceased.\"|n")
    delay(52.0, account.msg, "")
    delay(54.0, account.msg, "|W    \"Sleeve allocation for account in progress.\"|n")
    delay(56.5, account.msg, "|W    \"Please stand by for neural imprinting.\"|n")
    delay(58.5, account.msg, "")
    delay(60.0, account.msg, "|X" + "-" * 70 + "|n")
    delay(61.5, account.msg, "")
    delay(63.0, account.msg, "|X" + "=" * 70 + "|n")
    
    # Start character creation after sequence
    delay(65.0, _begin_character_creation, account, character, session)


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
        
        # Transfer inventory
        for item in list(character.contents):
            item.move_to(corpse, quiet=True)
        
        _log(f"DEATH_PROG: Corpse created for {character.key}")
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


def _start_clone_restoration(account, old_character, session, backup_data):
    """
    Restore character from clone backup - the unnerving Matrix-style awakening.
    
    This is only called when the character HAS a clone backup.
    They are pulled from a pod with their backed-up stats/skills/appearance.
    Chrome and inventory are LOST.
    """
    from evennia.utils import delay
    
    # Lock commands during the cutscene by setting flag on account and session
    account.ndb._clone_awakening_locked = True
    if session:
        session.ndb._clone_awakening_locked = True
    
    # Play the unnerving awakening sequence
    _play_clone_awakening(account, old_character, session, backup_data)


def _play_clone_awakening(account, old_character, session, backup_data):
    """Play the unnerving Matrix-style pod extraction sequence."""
    from datetime import datetime
    from evennia.utils import delay
    
    # Get the backup timestamp for the voice to read
    backup_timestamp = backup_data.get('timestamp', 0)
    backup_datetime = datetime.fromtimestamp(backup_timestamp)
    last_backup_str = backup_datetime.strftime("%B %d, %Y at %H:%M")
    
    # Current time for the voice to announce
    current_datetime = datetime.now()
    current_time_str = current_datetime.strftime("%B %d, %Y. %H:%M hours")
    
    # Clear screen and start the unnerving sequence
    account.msg("\n" * 5)
    
    # Darkness and sensory confusion
    delay(0.5, account.msg, "|X" + "=" * 70 + "|n")
    delay(1.0, account.msg, "")
    delay(1.5, account.msg, "|xYou can't move.|n")
    delay(2.5, account.msg, "|xYou can't see.|n")
    delay(3.5, account.msg, "|xYou can't breathe.|n")
    delay(5.0, account.msg, "")
    delay(5.5, account.msg, "|xThere is pressure. All around you. Thick. Viscous.|n")
    delay(7.0, account.msg, "|xYou are suspended in something warm and wet.|n")
    delay(8.5, account.msg, "")
    
    # The drainage
    delay(9.5, account.msg, "|rA loud THUNK echoes through your skull.|n")
    delay(11.0, account.msg, "|xThe liquid begins to drain.|n")
    delay(12.5, account.msg, "|xSlowly at first. Then rushing.|n")
    delay(14.0, account.msg, "|xYou feel yourself... settling. Heavy.|n")
    delay(15.5, account.msg, "")
    
    # The opening
    delay(16.5, account.msg, "|xA seam of light. Blinding.|n")
    delay(18.0, account.msg, "|xGlass parts with a hydraulic hiss.|n")
    delay(19.5, account.msg, "|xCold air hits wet skin.|n")
    delay(21.0, account.msg, "")
    delay(21.5, account.msg, "|xYou fall forward.|n")
    delay(23.0, account.msg, "|xHands catch you. Mechanical. Precise.|n")
    delay(24.5, account.msg, "")
    
    # The voice
    delay(26.0, account.msg, "|X" + "-" * 70 + "|n")
    delay(27.0, account.msg, "")
    delay(28.0, account.msg, "|c[SYSTEM VOICE - Pleasant, synthetic, wrong]|n")
    delay(29.5, account.msg, "")
    delay(30.5, account.msg, f"|W    \"Good morning. The current date and time is:|n")
    delay(32.0, account.msg, f"|W     {current_time_str}.\"|n")
    delay(34.0, account.msg, "")
    delay(35.5, account.msg, f"|W    \"Your last consciousness backup was recorded:|n")
    delay(37.0, account.msg, f"|W     {last_backup_str}.\"|n")
    delay(39.0, account.msg, "")
    delay(40.5, account.msg, "|W    \"Your previous body has been... discontinued.\"|n")
    delay(42.5, account.msg, "|W    \"This is your new sleeve. Please take a moment.\"|n")
    delay(44.5, account.msg, "|W    \"Motor functions will normalize shortly.\"|n")
    delay(46.5, account.msg, "")
    delay(47.5, account.msg, "|W    \"Welcome back.\"|n")
    delay(49.0, account.msg, "")
    delay(50.0, account.msg, "|X" + "-" * 70 + "|n")
    delay(51.0, account.msg, "")
    
    # Coming to
    delay(52.5, account.msg, "|xYour vision clears.|n")
    delay(54.0, account.msg, "|xYou are kneeling on cold tile. Naked. Shivering.|n")
    delay(55.5, account.msg, "|xBiosynthetic amniotic fluid drips from your body.|n")
    delay(57.0, account.msg, "")
    delay(58.0, account.msg, "|yThe memories of your death are... |rfragmented|y. Distant.|n")
    delay(59.5, account.msg, "|yLike something that happened to someone else.|n")
    delay(61.0, account.msg, "")
    delay(62.0, account.msg, "|X" + "=" * 70 + "|n")
    
    # Actually create the new character after the sequence
    delay(64.0, _create_restored_clone, account, old_character, session, backup_data)


def _create_restored_clone(account, old_character, session, backup_data):
    """Create the actual restored clone character."""
    from typeclasses.cloning_pod import restore_from_clone
    from evennia import search_object
    
    _log(f"CLONE_CREATE: Starting clone creation for {account.key}")
    _log(f"CLONE_CREATE: backup_data keys: {list(backup_data.keys()) if backup_data else 'None'}")
    
    try:
        # Get current session - the one passed in may be stale after 64 second delay
        current_session = session
        if account.sessions.count():
            current_session = account.sessions.all()[0]
        
        _log(f"CLONE_CREATE: Session valid: {current_session is not None}")
        
        # Get clone spawn location - room #53 (clone decanting room)
        try:
            start_location = search_object("#53")[0]
            _log(f"CLONE_CREATE: Using clone room #53")
        except (IndexError, AttributeError):
            # Fallback to regular start location
            from commands.charcreate import get_start_location
            start_location = get_start_location()
            _log(f"CLONE_CREATE: Using fallback start location")
        
        # Use base_name directly - NO Roman numerals (death count is private meta info)
        char_name = backup_data.get('base_name') if backup_data else None
        if not char_name:
            char_name = old_character.key if old_character else "Clone"
        
        # Strip any existing Roman numerals just in case
        import re
        roman_pattern = r'\s+(M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3}))$'
        char_name = re.sub(roman_pattern, '', char_name, flags=re.IGNORECASE).strip()
        
        _log(f"CLONE_CREATE: Using name '{char_name}'")
        
        # Remove old character from account (MAX_NR_CHARACTERS=1)
        # Check by key name since the object reference might be stale
        chars_to_remove = [c for c in account.characters if c.key == old_character.key or c == old_character]
        for c in chars_to_remove:
            account.characters.remove(c)
            _log(f"CLONE_CREATE: Removed {c.key} from account.characters")
        
        _log(f"CLONE_CREATE: Account characters after removal: {[c.key for c in account.characters]}")
        
        # Create new character with same name
        char, errors = account.create_character(
            key=char_name,
            location=start_location,
            home=start_location,
            typeclass="typeclasses.characters.Character"
        )
        
        if errors:
            _log(f"CLONE_CREATE: Creation errors: {errors}")
            raise Exception(f"Clone restoration failed: {errors}")
        
        _log(f"CLONE_CREATE: Character created: {char.key} ({char.dbref})")
        
        # Restore from backup (stats, skills, appearance)
        restore_from_clone(char, backup_data)
        
        # Unlock commands and OOC menu - awakening sequence is complete
        if hasattr(account.ndb, '_clone_awakening_locked'):
            del account.ndb._clone_awakening_locked
        if current_session and hasattr(current_session.ndb, '_clone_awakening_locked'):
            del current_session.ndb._clone_awakening_locked
        
        # Note: Chrome and inventory are NOT restored - they were lost
        account.msg("|y[Note: Cybernetic implants and inventory were not backed up.|n")
        account.msg("|y Your belongings remain with your previous body.]|n")
        account.msg("")
        
        # Puppet the new character
        account.puppet_object(current_session, char)
        
        # Final release message
        char.msg("|xYou feel control returning to your limbs.|n")
        char.msg("|xYour fingers twitch. Then curl. Then grip.|n")
        char.msg("")
        char.msg("|W\"Motor functions restored. You are free to proceed.\"|n")
        char.msg("")
        
        if char.location:
            char.location.msg_contents(
                f"|x{char.key} stirs on the cold tile, biosynthetic fluid pooling beneath them, eyes slowly focusing.|n",
                exclude=[char]
            )
        
        _log(f"CLONE_RESTORE: {char_name} restored from backup for {account.key}")
        
    except Exception as e:
        _log(f"CLONE_RESTORE_ERROR: {e}")
        import traceback
        _log(f"CLONE_RESTORE_TRACE: {traceback.format_exc()}")
        
        # Get current session for unlock
        current_session = session
        if account.sessions.count():
            current_session = account.sessions.all()[0]
        
        # Unlock on failure
        if hasattr(account.ndb, '_clone_awakening_locked'):
            del account.ndb._clone_awakening_locked
        if current_session and hasattr(current_session.ndb, '_clone_awakening_locked'):
            del current_session.ndb._clone_awakening_locked
        
        # Show error and let them try again
        account.msg("|rCLONE RESTORATION CRITICAL FAILURE.|n")
        account.msg("|rPlease contact staff for assistance.|n")


def _start_new_character(account, old_character, session):
    """
    Start character creation for the account (no clone backup).
    Shows an unnerving clone malfunction cutscene before character creation.
    """
    from evennia.utils import delay
    
    # Lock commands during the cutscene
    account.ndb._clone_awakening_locked = True
    if session:
        session.ndb._clone_awakening_locked = True
    
    # Play the clone malfunction cutscene
    _play_clone_malfunction(account, old_character, session)


def _play_clone_malfunction(account, old_character, session):
    """Play the unnerving clone malfunction sequence before character creation."""
    from evennia.utils import delay
    
    # Clear screen
    account.msg("\n" * 5)
    
    # Start sequence - same initial pod experience
    delay(0.5, account.msg, "|X" + "=" * 70 + "|n")
    delay(1.0, account.msg, "")
    delay(1.5, account.msg, "|xYou can't move.|n")
    delay(2.5, account.msg, "|xYou can't see.|n")
    delay(3.5, account.msg, "|xYou can't breathe.|n")
    delay(5.0, account.msg, "")
    delay(5.5, account.msg, "|xThere is pressure. All around you. Thick. Viscous.|n")
    delay(7.0, account.msg, "|xYou are suspended in something warm and wet.|n")
    delay(8.5, account.msg, "")
    
    # Something goes wrong
    delay(9.5, account.msg, "|rA loud THUNK echoes through your skull.|n")
    delay(11.0, account.msg, "|xThe liquid begins to drain.|n")
    delay(12.5, account.msg, "|rBut something is... wrong.|n")
    delay(14.0, account.msg, "")
    
    # Error state
    delay(15.5, account.msg, "|R[ERROR KLAXON - Harsh, repeating]|n")
    delay(17.0, account.msg, "")
    delay(18.0, account.msg, "|r    \"CRITICAL ERROR. CRITICAL ERROR.\"|n")
    delay(19.5, account.msg, "|r    \"CONSCIOUSNESS BACKUP NOT FOUND.\"|n")
    delay(21.0, account.msg, "|r    \"NEURAL PATTERN INTEGRITY: 0%\"|n")
    delay(22.5, account.msg, "")
    delay(24.0, account.msg, "|xThe liquid drains completely.|n")
    delay(25.5, account.msg, "|xYou gasp. Choke. Breathe.|n")
    delay(27.0, account.msg, "")
    delay(28.5, account.msg, "|xThe pod opens. Light floods in.|n")
    delay(30.0, account.msg, "|xYou collapse onto cold tile.|n")
    delay(31.5, account.msg, "")
    
    # The voice - cold, clinical
    delay(33.0, account.msg, "|X" + "-" * 70 + "|n")
    delay(34.0, account.msg, "")
    delay(35.0, account.msg, "|c[SYSTEM VOICE - Cold, clinical]|n")
    delay(36.5, account.msg, "")
    delay(38.0, account.msg, "|W    \"Clone activation failed.\"|n")
    delay(40.0, account.msg, "|W    \"No consciousness backup on file for this identity.\"|n")
    delay(42.0, account.msg, "|W    \"Sleeve resources have been... reallocated.\"|n")
    delay(44.0, account.msg, "")
    delay(45.5, account.msg, "|W    \"A fresh identity will be assigned.\"|n")
    delay(47.5, account.msg, "|W    \"Please stand by for neural imprinting.\"|n")
    delay(49.5, account.msg, "")
    delay(51.0, account.msg, "|X" + "-" * 70 + "|n")
    delay(52.0, account.msg, "")
    
    # Final state
    delay(53.5, account.msg, "|xYou lie there. Naked. Shivering. Empty.|n")
    delay(55.0, account.msg, "|xYou don't remember who you were.|n")
    delay(56.5, account.msg, "|xYou don't remember anything at all.|n")
    delay(58.0, account.msg, "")
    delay(59.0, account.msg, "|X" + "=" * 70 + "|n")
    
    # Start character creation after the cutscene
    delay(61.0, _begin_character_creation, account, old_character, session)


def _begin_character_creation(account, old_character, session):
    """Actually begin character creation after the malfunction cutscene."""
    # Unlock commands
    if hasattr(account.ndb, '_clone_awakening_locked'):
        del account.ndb._clone_awakening_locked
    if session and hasattr(session.ndb, '_clone_awakening_locked'):
        del session.ndb._clone_awakening_locked
    
    account.msg("")
    account.msg("|y[Your previous character has died without a consciousness backup.|n")
    account.msg("|y You must create a new character.]|n")
    account.msg("")
    
    try:
        from commands.charcreate import start_character_creation
        start_character_creation(account, is_respawn=False, old_character=None)
    except ImportError:
        account.msg("|yCharacter creation is under development.|n")
        account.msg("|yPlease contact staff for a new character.|n")


def cancel_death_progression(character):
    """
    Cancel death progression (e.g., if character is revived).
    """
    if not character:
        return
    
    if getattr(character.ndb, '_death_progression_active', False):
        character.ndb._death_progression_active = False
        _log(f"DEATH_PROG: Cancelled for {character.key}")


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
