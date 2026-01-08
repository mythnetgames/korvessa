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
            # Insert accent for 'says' patterns
            speech_pattern = r'(says,?\s*["\'])(.*?)(["\'])'
            def replace_speech(match):
                prefix = match.group(1)
                speech = match.group(2)
                quote = match.group(3)
                return f'{prefix}*in a {voice}* {speech}{quote}'
            emote_text = re.sub(speech_pattern, replace_speech, emote_text)

            # Insert accent for emotes that are just quoted speech (e.g., "Test")
            # Only if the whole emote is a quoted string
            quote_only_pattern = r'^(["\'])(.*?)(["\'])$'
            def replace_quote_only(match):
                open_quote = match.group(1)
                speech = match.group(2)
                close_quote = match.group(3)
                return f'{open_quote}*in a {voice}* {speech}{close_quote}'
            emote_text = re.sub(quote_only_pattern, replace_quote_only, emote_text)
        
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
