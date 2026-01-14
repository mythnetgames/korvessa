"""
Custom Say command that integrates voice descriptions and language garbling.
"""

import re
from evennia.commands.default.general import CmdSay as DefaultCmdSay
from world.language.utils import (
    get_primary_language,
    apply_language_garbling_to_observers,
)


def fix_speech_grammar(text):
    """
    Fix common speech grammar issues:
    - Fix common contractions (Ive -> I've, Thats -> That's, etc.)
    - Capitalize standalone "i" to "I"
    
    Args:
        text (str): Speech text to fix
        
    Returns:
        str: Grammar-fixed text
    """
    # Fix contractions - map common bad spellings to correct contractions
    contractions = {
        r'\bIve\b': "I've",
        r'\bive\b': "I've",
        r'\bHes\b': "He's",
        r'\bShe?s\b': "She's",
        r'\bIts\b': "It's",
        r'\bThats\b': "That's",
        r'\bWhats\b': "What's",
        r'\bWhos\b': "Who's",
        r'\bWheres\b': "Where's",
        r'\bWhens\b': "When's",
        r'\bHows\b': "How's",
        r'\bIsnt\b': "Isn't",
        r'\bArent\b': "Aren't",
        r'\bWasnt\b': "Wasn't",
        r'\bWerent\b': "Weren't",
        r'\bHasnt\b': "Hasn't",
        r'\bHavent\b': "Haven't",
        r'\bDidnt\b': "Didn't",
        r'\bDont\b': "Don't",
        r'\bCant\b': "Can't",
        r'\bWont\b': "Won't",
        r'\bCouldnt\b': "Couldn't",
        r'\bShouldnt\b': "Shouldn't",
        r'\bWouldnt\b': "Wouldn't",
        r'\bYoure\b': "You're",
        r'\bTheyre\b': "They're",
        r'\bWeve\b': "We've",
        r'\bTheyve\b': "They've",
    }
    
    for bad, good in contractions.items():
        text = re.sub(bad, good, text)
    
    # Capitalize standalone "i" to "I"
    # Match 'i' that is either:
    # - at the start of string, or after space/punctuation
    # - followed by space, punctuation, or end of string
    text = re.sub(r'(?<![a-zA-Z])i(?![a-zA-Z])', 'I', text)
    
    return text


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
        
        # Fix grammar - contractions and capitalize standalone "i"
        speech = fix_speech_grammar(speech)
        
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
                
                # Send passive learning notification after the speech
                from world.language.utils import get_language_proficiency
                from world.language.constants import LANGUAGES
                proficiency = get_language_proficiency(observer, primary_language)
                if proficiency < 100.0 and primary_language not in ['cantonese', 'english']:  # Don't notify for common starting languages
                    lang_name = LANGUAGES[primary_language]['name']
                    if proficiency > 0:
                        observer.msg(f"|x(You pick up a few words of {lang_name}... {proficiency:.2f}% proficiency)|n")
