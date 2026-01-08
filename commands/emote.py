"""
Custom Emote command that integrates voice descriptions into speech.
"""

import re
from evennia.commands.default.general import CmdPose as DefaultCmdPose


class CmdEmote(DefaultCmdPose):
    """
    Perform an action (emote) with optional voice description in speech.
    
    Usage:
        emote <action>
        :<action>
    
    If your emote contains speech (like "says,"), your @voice will be inserted
    around the speech text.
    
    Examples:
        emote passes the boof to Test Dummy and says, "Hit this shit."
        : waves hello to everyone.
    """
    
    def func(self):
        """Override emote to include voice description in speech and perspective replacement."""
        caller = self.caller
        
        if not self.args:
            caller.msg("Emote what?")
            return
        
        emote_text = self.args.lstrip()  # Remove leading whitespace
        
        # Check if character has a voice set
        voice = getattr(caller.db, 'voice', None)
        
        if voice:
            # Look for any quoted speech in the emote and insert accent
            # Match patterns like: says "text", exclaiming to you, "text", etc.
            quote_pattern = r'(["\'])(.*?)\1'
            
            def replace_quotes(match):
                quote = match.group(1)  # The quote character (" or ')
                speech = match.group(2)  # The actual speech
                return f'{quote}*in a {voice}* {speech}{quote}'
            
            # Replace all quoted speech instances with voice-enhanced versions
            emote_text = re.sub(quote_pattern, replace_quotes, emote_text)
        
        # Format the pose with caller's name (ensure single space)
        pose_text = f"{caller.name} {emote_text}"
        
        # Send to the caller
        caller.msg(pose_text)
        
        # Send to others in the location, replacing their name with "you" if present
        if caller.location:
            for char in caller.location.contents:
                if char == caller:
                    continue
                
                # Create perspective-adjusted message for this character
                message = pose_text
                
                # Replace character's name with "you" (case-insensitive but preserve original capitalization context)
                # Match whole word boundaries
                message = re.sub(
                    rf'\b{re.escape(char.name)}\b',
                    'you',
                    message,
                    flags=re.IGNORECASE
                )
                
                if hasattr(char, 'msg'):
                    char.msg(message)
