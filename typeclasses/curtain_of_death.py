"""
Curtain of Death - Death Animation System for Evennia

This module provides a "dripping blood" death animation that creates
a curtain effect by progressively removing characters from a message.
Based on the elegant design that centers text in a "sea" of characters
and creates a dripping effect by removing characters in sequence.
Compatible with Evennia's messaging and delay systems.
"""

import random
from evennia.utils import delay


def _get_terminal_width(session=None):
    """
    Get terminal width from session, defaulting to 78 for MUD compatibility.
    
    Args:
        session: Evennia session object to get width from
        
    Returns:
        int: Terminal width in characters
    """
    if session:
        # Use Evennia's built-in screen width detection
        try:
            detected_width = session.protocol_flags.get("SCREENWIDTH", [78])[0]
            return max(60, detected_width)  # Minimum 60 for readability
        except (IndexError, KeyError, TypeError):
            # Fallback if protocol flags aren't available or malformed
            pass
    return 78


def _colorize_evennia(text):
    """Apply Evennia color codes to text for a blood-red effect."""
    # Use Evennia's color system - random red variations for blood effect
    colors = ["|r", "|R"]  # Red variations for blood effect
    
    colored = ["|r"]  # Always start with red color code for filter detection
    for char in text:
        if char != " ":  # Don't colorize spaces
            colored.append(f"{random.choice(colors)}{char}")
        else:
            colored.append(char)
    
    colored.append("|n")  # Always reset color at the end
    return "".join(colored)


def _strip_color_codes(text):
    """
    Remove Evennia color codes to get the visible text length.
    
    Args:
        text (str): Text with color codes
        
    Returns:
        str: Text without color codes
    """
    import re
    # Remove all |x and |xx codes (where x is any character)
    return re.sub(r'\|.', '', text)


def curtain_of_death(text, width=None, session=None):
    """
    Create a fading death animation using punctuation.
    
    Args:
        text (str): The message to animate
        width (int, optional): Width of the display area
        session: Evennia session object for width detection
        
    Returns:
        List[str]: Animation frames
    """
    if width is None:
        width = _get_terminal_width(session)
    
    curtain_width = width - 1
    visible_text = _strip_color_codes(text)
    
    frames = []
    
    # Phase 1: Full message with punctuation border
    padding_needed = curtain_width - len(visible_text)
    if padding_needed > 0:
        left_padding = padding_needed // 2
        right_padding = padding_needed - left_padding
        left_border = _colorize_evennia("." * left_padding)
        right_border = _colorize_evennia("." * right_padding)
        frames.append(left_border + text + right_border)
    else:
        frames.append(text)
    
    # Phase 2: Message gradually fades by replacing characters with dots (12 frames)
    chars = list(visible_text)
    char_indices = [i for i in range(len(chars)) if chars[i] != " "]
    
    for fade_step in range(12):
        # Calculate how many characters to replace with dots this frame
        fade_ratio = (fade_step + 1) / 12
        chars_to_fade = int(len(char_indices) * fade_ratio)
        
        # Replace random characters with dots
        indices_to_remove = random.sample(char_indices, min(chars_to_fade, len(char_indices)))
        for idx in indices_to_remove:
            if idx in char_indices:
                chars[idx] = "."
                char_indices.remove(idx)
        
        # Build frame with remaining text and colored dots
        frame_text = "".join(chars)
        if padding_needed > 0:
            left_border = _colorize_evennia("." * left_padding)
            right_border = _colorize_evennia("." * right_padding)
            frame = left_border + _colorize_evennia(frame_text) + right_border
        else:
            frame = _colorize_evennia(frame_text)
        
        frames.append(frame)
    
    # Phase 3: Final fade to empty (5 frames of increasingly sparse text)
    for final_step in range(5):
        remaining = [i for i in range(len(chars)) if chars[i] != " " and chars[i] != "."]
        remove_count = max(1, len(remaining) // (5 - final_step))
        
        for idx in random.sample(remaining, min(remove_count, len(remaining))):
            chars[idx] = "."
        
        frame_text = "".join(chars)
        if padding_needed > 0:
            left_border = _colorize_evennia("." * left_padding)
            right_border = _colorize_evennia("." * right_padding)
            frame = left_border + _colorize_evennia(frame_text) + right_border
        else:
            frame = _colorize_evennia(frame_text)
        
        frames.append(frame)
    
    # Phase 4: Blank frame for transition (2 frames)
    for _ in range(2):
        frames.append(_colorize_evennia(" " * curtain_width))
    
    return frames


class DeathCurtainSender:
    """
    Simple sender object to identify death curtain messages in the msg filter.
    This allows the character.msg() filter to recognize and allow death curtain frames.
    """
    key = "death_curtain_animation"
    
    def __repr__(self):
        return "<DeathCurtainSender>"


class DeathCurtain:
    """
    Creates a "dripping blood" death animation by progressively removing
    characters from a death message to create a curtain effect.
    """
    
    def __init__(self, character, message=None):
        """
        Initialize the death curtain animation.
        
        Args:
            character: The character object to send the animation to
            message (str, optional): Custom death message
        """
        self.character = character
        self.location = character.location
        
        # Get session for width detection
        self.session = None
        if character and hasattr(character, 'sessions') and character.sessions.get():
            self.session = character.sessions.get()[0]
        
        # Get terminal width for this character's session
        self.width = _get_terminal_width(self.session)
        
        # Create informed death message based on cause
        if message is None:
            # Always use the beautiful mixed red message for the curtain
            message = "|rA |Rred |rhaze |Rblurs |ryour |Rvision |ras |Rthe |rworld |Rslips |raway|R...|n"
        
        self.message = message
        self.frames = curtain_of_death(message, session=self.session)
        self.current_frame = 0
        self.frame_delay = 0.05  # Start slower than before (was 0.015)
        self.delay_multiplier = 1.02  # More significant slowdown (was 1.005)
        # Create a sender object so message filter can identify death curtain messages
        self.sender = DeathCurtainSender()
        
    def start_animation(self):
        """Start the death curtain animation."""
        # Send initial death messages before the curtain starts
        if self.location:
            # Get death cause for both messages
            death_cause = None
            if hasattr(self.character, 'get_death_cause'):
                death_cause = self.character.get_death_cause()
            
            # Send victim's initial death message
            if self.character:
                if death_cause:
                    victim_msg = f"|rYour body succumbs to {death_cause}. The end draws near...|n"
                else:
                    victim_msg = f"|rYour body fails you. The end draws near...|n"
                self.character.msg(victim_msg, from_obj=self.sender)
            
            # Don't send initial "dying from" message to observers - 
            # we'll send a combined death message later
        
        self.current_frame = 0
        self._show_next_frame()
        
    def _show_next_frame(self):
        """Show the next frame of the animation."""
        if self.current_frame < len(self.frames):
            # Send current frame to the dying character with sender for filter identification
            if self.character:
                self.character.msg(self.frames[self.current_frame], from_obj=self.sender)
            
            self.current_frame += 1
            
            # Schedule next frame with increasing delay (like original)
            delay(self.frame_delay, self._show_next_frame)
            self.frame_delay *= self.delay_multiplier
        else:
            # Animation complete, trigger death
            self._on_animation_complete()
            
    def _on_animation_complete(self):
        """Called when the animation completes."""
        # Send a single, vivid death message that incorporates the cause
        if self.location:
            death_cause = getattr(self.character.db, 'death_cause', None)
            
            if death_cause:
                # Create vivid death descriptions based on cause
                if 'blood loss' in death_cause.lower():
                    death_msg = f"|R{self.character.key}'s lifeblood pools crimson around their still form.|n"
                elif 'heart failure' in death_cause.lower():
                    death_msg = f"|R{self.character.key} clutches their chest one last time before going still.|n"
                elif 'head' in death_cause.lower() or 'brain' in death_cause.lower():
                    death_msg = f"|R{self.character.key}'s eyes lose focus as they collapse, unmoving.|n"
                elif 'poison' in death_cause.lower():
                    death_msg = f"|R{self.character.key} convulses violently before falling silent.|n"
                elif 'fire' in death_cause.lower() or 'burn' in death_cause.lower():
                    death_msg = f"|R{self.character.key}'s charred form crumples to the ground.|n"
                elif 'stab' in death_cause.lower() or 'slash' in death_cause.lower():
                    death_msg = f"|R{self.character.key} gasps once, crimson flowing, then goes still.|n"
                else:
                    # Generic death message with cause hint
                    death_msg = f"|R{self.character.key} draws their final breath and grows still.|n"
            else:
                # No cause specified
                death_msg = f"|R{self.character.key} draws their final breath and grows still.|n"
                
            self.location.msg_contents(death_msg, exclude=[self.character])
        
        # Start death progression system after death curtain completes
        try:
            from .death_progression import start_death_progression
            script = start_death_progression(self.character)
            
            # Debug logging
            try:
                from evennia.comms.models import ChannelDB
                splattercast = ChannelDB.objects.get_channel("Splattercast")
                splattercast.msg(f"DEATH_CURTAIN: Death progression started for {self.character.key}, script: {script}")
            except:
                pass
                
        except Exception as e:
            # Debug logging for any errors
            try:
                from evennia.comms.models import ChannelDB
                splattercast = ChannelDB.objects.get_channel("Splattercast")
                splattercast.msg(f"DEATH_CURTAIN_ERROR: Failed to start death progression for {self.character.key}: {e}")
            except:
                pass


def show_death_curtain(character, message=None):
    """
    Convenience function to show the death curtain animation.
    
    Args:
        character: The character object to show the animation to
        message (str, optional): Custom death message
    """
    curtain = DeathCurtain(character, message)
    curtain.start_animation()