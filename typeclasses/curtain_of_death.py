"""
Veil of the Watcher - Death Animation System

Divine, thematic death animation that displays to the dying character
and then triggers death progression into the Watcher's Domain.
"""

from evennia.utils import delay
from evennia.comms.models import ChannelDB


def _log(msg):
    """Log to Splattercast channel."""
    try:
        ch = ChannelDB.objects.get_channel("Splattercast")
        ch.msg(msg)
    except:
        pass


def show_death_curtain(character, message=None):
    """
    Main entry point - show death animation to character.
    
    Displays the Veil descending as consciousness fades.
    
    Args:
        character: The dying character
        message: Optional custom death message
    """
    if not character:
        return
        
    _log(f"VEIL: Starting for {character.key}")
    
    # Set flag so messages bypass the dead character filter
    character.ndb._death_curtain_active = True
    
    # Default message - thematic and mystical
    if not message:
        message = "The world grows distant. You feel yourself slipping into shadow..."
    
    location = character.location
    
    # Send animation frames with delays
    _send_frame(character, 0, message, 0.0)    # Full awareness
    _send_frame(character, 1, message, 0.4)    # Slipping
    _send_frame(character, 2, message, 0.8)    # Fading
    _send_frame(character, 3, message, 1.2)    # Dimming
    _send_frame(character, 4, message, 1.6)    # Almost gone
    _send_frame(character, 5, message, 2.0)    # Into darkness
    
    # Complete animation and start progression
    delay(2.5, _complete_animation, character, location)


def _send_frame(character, frame_num, message, delay_time):
    """Send a single animation frame."""
    fade_amounts = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    fade = fade_amounts[min(frame_num, len(fade_amounts) - 1)]
    
    if delay_time == 0:
        _do_send_frame(character, message, fade, frame_num == 0)
    else:
        delay(delay_time, _do_send_frame, character, message, fade, False)


def _do_send_frame(character, message, fade_amount, is_first):
    """Actually send the frame message."""
    if not character:
        return
        
    # Keep flag active
    character.ndb._death_curtain_active = True
    
    # Fade the text
    faded = _fade_text(message, fade_amount)
    
    # Format with newlines for first and last
    if is_first:
        text = f"\n|r{faded}|n\n"
    elif fade_amount >= 1.0:
        text = f"|r{faded}|n\n\n"
    else:
        text = f"|r{faded}|n"
    
    # Send directly to character - bypass any filtering
    try:
        # Use the lowest level msg possible
        character.msg(text)
    except Exception as e:
        _log(f"CURTAIN_ERROR: Frame send failed: {e}")


def _fade_text(text, fade_amount):
    """Replace characters with shadowy symbols based on fade amount (mystical fading)."""
    import random
    
    if fade_amount <= 0:
        return text
    if fade_amount >= 1.0:
        # Fully faded into void - use mystical symbol
        return ' ' * len(text)
    
    chars = list(text)
    # Get non-space indices
    indices = [i for i, c in enumerate(chars) if c not in ' ']
    
    if indices:
        num_to_fade = int(len(indices) * fade_amount)
        to_fade = random.sample(indices, min(num_to_fade, len(indices)))
        # Use mystical fade characters instead of dots
        fade_chars = ['~', '-', '`', "'", '.']
        for i in to_fade:
            chars[i] = random.choice(fade_chars)
    
    return ''.join(chars)


def _complete_animation(character, location):
    """Called when animation finishes - start death progression."""
    if not character:
        return
        
    _log(f"CURTAIN_COMPLETE: Animation done for {character.key}")
    
    # DON'T clear curtain flag here - death progression needs it to stay active
    # It will be cleared when death progression completes
    
    # Send observer message
    if location:
        cause = getattr(character.db, 'death_cause', None)
        if cause and 'blood' in str(cause).lower():
            msg = f"|R{character.key}'s lifeblood pools crimson around their still form.|n"
        elif cause and 'heart' in str(cause).lower():
            msg = f"|R{character.key} clutches their chest one last time before going still.|n"
        elif cause and ('head' in str(cause).lower() or 'brain' in str(cause).lower()):
            msg = f"|R{character.key}'s eyes lose focus as they collapse, unmoving.|n"
        else:
            msg = f"|R{character.key} draws their final breath and grows still.|n"
        
        location.msg_contents(msg, exclude=[character])
    
    # Start death progression - this is the key part
    _start_progression(character)


def _start_progression(character):
    """Start the death progression system."""
    try:
        from typeclasses.death_progression import start_death_progression
        script = start_death_progression(character)
        _log(f"CURTAIN: Death progression started: {script}")
    except Exception as e:
        _log(f"CURTAIN_ERROR: Failed to start progression: {e}")
        import traceback
        _log(f"CURTAIN_TRACE: {traceback.format_exc()}")
