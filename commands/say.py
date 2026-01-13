"""
Custom Say command that integrates voice descriptions and language garbling.
"""

from evennia.commands.default.general import CmdSay as DefaultCmdSay
from world.language.utils import (
    get_primary_language,
    apply_language_garbling_to_observers,
)


class CmdSay(DefaultCmdSay):
    """
    Speak as your character with optional voice description and language garbling.
    
    Usage:
        say <message>
        "<message>
    
    If you have set a @voice, others will hear your speech as:
    *in a [voice description]* <message>
    
    The language you speak is determined by your primary language.
    Others will hear your speech garbled based on their proficiency in that language.
    
    Examples:
        say Hello there!
        "How are you?
    """
    
    def func(self):
        """Override say to include voice description and language garbling."""
        caller = self.caller
        
        if not self.args:
            caller.msg("Say what?")
            return
        
        speech = self.args.strip()
        
        # Capitalize first letter
        if speech:
            speech = speech[0].upper() + speech[1:] if len(speech) > 1 else speech.upper()
        
        # Add period if no ending punctuation
        if speech and speech[-1] not in '.!?':
            speech = speech + '.'
        
        # Get speaker's primary language
        primary_language = get_primary_language(caller)
        
        # Get language name
        from world.language.constants import LANGUAGES
        language_name = LANGUAGES[primary_language]['name']
        
        # Check if character has a voice set
        voice = getattr(caller.db, 'voice', None)
        
        if voice:
            # Format message with voice and language for speaker (no garbling for themselves)
            message = f'{caller.name} says, "*speaking {language_name} in a {voice}* {speech}"|n'
            
            # Send to caller (ungarbled)
            caller.msg(message)
        else:
            # No voice - format simple message with language
            message = f'{caller.name} says, "*speaking {language_name}* {speech}"|n'
            caller.msg(message)
        
        # Apply language garbling for observers
        if caller.location:
            observer_messages = apply_language_garbling_to_observers(
                caller, speech, primary_language
            )
            
            # Send garbled messages to each observer
            for observer, garbled_speech in observer_messages.items():
                if voice:
                    observer_msg = f'{caller.name} says, "*speaking {language_name} in a {voice}* {garbled_speech}"|n'
                else:
                    observer_msg = f'{caller.name} says, "*speaking {language_name}* {garbled_speech}"|n'
                observer.msg(observer_msg)
