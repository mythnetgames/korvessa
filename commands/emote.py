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
        """Override emote to include voice description in speech."""
        caller = self.caller
        
        if not self.args:
            caller.msg("Emote what?")
            return
        
        emote_text = self.args
        
        # Check if character has a voice set
        voice = getattr(caller.db, 'voice', None)
        
        if voice:
            # Look for speech patterns in the emote
            # Match patterns like: says, "text" or says 'text' or says, "text"
            speech_pattern = r'(says,?\s*["\'])(.*?)(["\'])'
            
            def replace_speech(match):
                prefix = match.group(1)  # 'says, "' or 'says "'
                speech = match.group(2)   # The actual speech
                quote = match.group(3)    # The closing quote
                return f'{prefix}*in a {voice}* {speech}{quote}'
            
            # Replace all speech instances with voice-enhanced versions
            emote_text = re.sub(speech_pattern, replace_speech, emote_text)
        
        # Use the parent emote command with the processed text
        self.args = emote_text
        super().func()
