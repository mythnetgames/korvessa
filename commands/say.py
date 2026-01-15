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
    # Capitalize standalone "i" to "I" first
    # Match 'i' that is not surrounded by letters
    text = re.sub(r'(?<![a-zA-Z])i(?![a-zA-Z])', 'I', text)
    
    # Fix contractions - case-insensitive matching
    # Format: (pattern, replacement)
    contractions = [
        (r'\bim\b', "I'm"),
        (r'\bIm\b', "I'm"),
        (r'\bive\b', "I've"),
        (r'\bIve\b', "I've"),
        (r'\bhes\b', "he's"),
        (r'\bHes\b', "He's"),
        (r'\bshes\b', "she's"),
        (r'\bShes\b', "She's"),
        (r'\bits\b', "it's"),
        (r'\bIts\b', "It's"),
        (r'\bthats\b', "that's"),
        (r'\bThats\b', "That's"),
        (r'\bwhats\b', "what's"),
        (r'\bWhats\b', "What's"),
        (r'\bwhos\b', "who's"),
        (r'\bWhos\b', "Who's"),
        (r'\bwheres\b', "where's"),
        (r'\bWheres\b', "Where's"),
        (r'\bwhens\b', "when's"),
        (r'\bWhens\b', "When's"),
        (r'\bhows\b', "how's"),
        (r'\bHows\b', "How's"),
        (r'\bisnt\b', "isn't"),
        (r'\bIsnt\b', "Isn't"),
        (r'\barent\b', "aren't"),
        (r'\bArent\b', "Aren't"),
        (r'\bwasnt\b', "wasn't"),
        (r'\bWasnt\b', "Wasn't"),
        (r'\bwerent\b', "weren't"),
        (r'\bWerent\b', "Weren't"),
        (r'\bhasnt\b', "hasn't"),
        (r'\bHasnt\b', "Hasn't"),
        (r'\bhavent\b', "haven't"),
        (r'\bHavent\b', "Haven't"),
        (r'\bdidnt\b', "didn't"),
        (r'\bDidnt\b', "Didn't"),
        (r'\bdont\b', "don't"),
        (r'\bDont\b', "Don't"),
        (r'\bcant\b', "can't"),
        (r'\bCant\b', "Can't"),
        (r'\bwont\b', "won't"),
        (r'\bWont\b', "Won't"),
        (r'\bcouldnt\b', "couldn't"),
        (r'\bCouldnt\b', "Couldn't"),
        (r'\bshouldnt\b', "shouldn't"),
        (r'\bShouldnt\b', "Shouldn't"),
        (r'\bwouldnt\b', "wouldn't"),
        (r'\bWouldnt\b', "Wouldn't"),
        (r'\byoure\b', "you're"),
        (r'\bYoure\b', "You're"),
        (r'\byouve\b', "you've"),
        (r'\bYouve\b', "You've"),
        (r'\btheyre\b', "they're"),
        (r'\bTheyre\b', "They're"),
        (r'\bweve\b', "we've"),
        (r'\bWeve\b', "We've"),
        (r'\btheyve\b', "they've"),
        (r'\bTheyve\b', "They've"),
    ]
    
    for pattern, replacement in contractions:
        text = re.sub(pattern, replacement, text)
    
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
