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
    """Complete the death process."""
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
    
    # Handle corpse creation and character transition
    _handle_death_completion(character)


def _handle_death_completion(character):
    """Handle corpse creation and character transition to limbo."""
    try:
        # Create corpse
        corpse = _create_corpse(character)
        
        # Get account before unpuppeting
        account = character.account
        session = None
        if account and account.sessions.all():
            session = account.sessions.all()[0]
        
        # Move character to limbo
        _move_to_limbo(character)
        
        # Unpuppet and start character creation
        if account and session:
            account.unpuppet_object(session)
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


def _start_new_character(account, old_character, session):
    """Start character creation for the account."""
    account.msg("|r" + "=" * 60 + "|n")
    account.msg("|rYour character has died and cannot be revived.|n")
    account.msg("|rA corpse has been left behind for investigation.|n")
    account.msg("|r" + "=" * 60 + "|n")
    account.msg("")
    
    try:
        from commands.charcreate import start_character_creation
        start_character_creation(account, is_respawn=True, old_character=old_character)
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
