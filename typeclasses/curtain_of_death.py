"""
Curtain of Death - Death Animation System for Evennia

A simple, reliable death animation that shows a fading message to the dying character.
"""

from evennia.utils import delay


def show_death_curtain(character, message=None):
    """
    Show a death animation to a character.
    
    This is the main entry point for the death curtain system.
    It displays a fading death message to the character and then
    starts the death progression system.
    
    Args:
        character: The character who is dying
        message (str, optional): Custom death message
    """
    from evennia.comms.models import ChannelDB
    
    try:
        splattercast = ChannelDB.objects.get_channel("Splattercast")
        splattercast.msg(f"DEATH_CURTAIN: Starting for {character.key}")
    except:
        pass
    
    # Mark character as receiving death curtain so msg filter allows our messages
    character.ndb._death_curtain_active = True
    
    # Default death message
    if message is None:
        message = "A red haze blurs your vision as the world slips away..."
    
    # Get location for observer message
    location = character.location
    
    # Send the death sequence with delays
    _send_death_sequence(character, message, location)


def _send_death_sequence(character, message, location):
    """Send the death message sequence with timing."""
    import random
    
    # Frame 1: Initial message (immediate)
    _send_death_msg(character, f"\n|r{message}|n\n")
    
    # Frames 2-5: Progressive fade with delays
    delay(0.4, _send_death_msg, character, f"|r{_fade_text(message, 0.15)}|n")
    delay(0.8, _send_death_msg, character, f"|r{_fade_text(message, 0.35)}|n")
    delay(1.2, _send_death_msg, character, f"|r{_fade_text(message, 0.60)}|n")
    delay(1.6, _send_death_msg, character, f"|r{_fade_text(message, 0.85)}|n")
    delay(2.0, _send_death_msg, character, f"|r{_fade_text(message, 1.0)}|n\n")
    
    # Complete the animation after all frames
    delay(2.5, _complete_death_animation, character, location)


def _fade_text(text, fade_amount):
    """
    Fade text by replacing characters with dots.
    
    Args:
        text: Original text
        fade_amount: 0.0 = no fade, 1.0 = fully faded
        
    Returns:
        str: Faded text
    """
    import random
    
    chars = list(text)
    num_to_fade = int(len(chars) * fade_amount)
    
    # Get indices of non-space, non-dot characters
    indices = [i for i, c in enumerate(chars) if c not in ' .']
    
    # Randomly select characters to fade
    if indices:
        fade_count = min(num_to_fade, len(indices))
        fade_indices = random.sample(indices, fade_count)
        for i in fade_indices:
            chars[i] = '.'
    
    return ''.join(chars)


def _send_death_msg(character, text):
    """
    Send a death curtain message to a character.
    Bypasses the msg filter by using the ndb flag.
    """
    if not character:
        return
    
    # Ensure death curtain flag is set
    character.ndb._death_curtain_active = True
    
    # Send the message - the character's msg() method will check the flag
    character.msg(text)


def _complete_death_animation(character, location):
    """Called when death animation completes."""
    from evennia.comms.models import ChannelDB
    
    try:
        splattercast = ChannelDB.objects.get_channel("Splattercast")
        splattercast.msg(f"DEATH_CURTAIN_COMPLETE: Animation finished for {character.key}")
    except:
        pass
    
    # Clear the death curtain flag
    if hasattr(character, 'ndb'):
        character.ndb._death_curtain_active = False
    
    # Send observer message
    if location:
        death_cause = getattr(character.db, 'death_cause', None) if hasattr(character, 'db') else None
        
        if death_cause:
            if 'blood' in death_cause.lower():
                death_msg = f"|R{character.key}'s lifeblood pools crimson around their still form.|n"
            elif 'heart' in death_cause.lower():
                death_msg = f"|R{character.key} clutches their chest one last time before going still.|n"
            elif 'head' in death_cause.lower() or 'brain' in death_cause.lower():
                death_msg = f"|R{character.key}'s eyes lose focus as they collapse, unmoving.|n"
            else:
                death_msg = f"|R{character.key} draws their final breath and grows still.|n"
        else:
            death_msg = f"|R{character.key} draws their final breath and grows still.|n"
        
        location.msg_contents(death_msg, exclude=[character])
    
    # Start death progression
    try:
        from .death_progression import start_death_progression
        script = start_death_progression(character)
        
        try:
            splattercast = ChannelDB.objects.get_channel("Splattercast")
            splattercast.msg(f"DEATH_CURTAIN: Death progression started for {character.key}")
        except:
            pass
    except Exception as e:
        try:
            splattercast = ChannelDB.objects.get_channel("Splattercast")
            splattercast.msg(f"DEATH_CURTAIN_ERROR: Failed to start death progression: {e}")
        except:
            pass
