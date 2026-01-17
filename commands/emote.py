"""
Custom Emote command that integrates voice descriptions into speech and language garbling.
"""

import re
from evennia.commands.default.general import CmdPose as DefaultCmdPose
from world.language.utils import (
    get_primary_language,
    garble_text_by_proficiency,
    get_language_proficiency,
    apply_passive_language_learning,
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
    # Capitalize standalone "i" to "I" - match 'i' surrounded by spaces or punctuation
    text = re.sub(r'(?<![a-zA-Z])\bi\b(?![a-zA-Z])', 'I', text)
    
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
        (r'\bwouldve\b', "would've"),
        (r'\bWouldve\b', "Would've"),
        (r'\bwoulda\b', "would'a"),
        (r'\bWoulda\b', "Would'a"),
        (r'\bcouldve\b', "could've"),
        (r'\bCouldve\b', "Could've"),
        (r'\bcouldda\b', "could'a"),
        (r'\bCouldda\b', "Could'a"),
        (r'\bshouldve\b', "should've"),
        (r'\bShouldve\b', "Should've"),
        (r'\bshouldda\b', "should'a"),
        (r'\bShouldda\b', "Should'a"),
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


class CmdEmote(DefaultCmdPose):
    """
    Perform an action (emote) with optional voice description in speech and language garbling.
    
    Usage:
        emote <action>
        :<action>
    
    If your emote contains speech (like "says,"), your @voice will be inserted
    around the speech text. Speech text will also be garbled for observers based
    on their language proficiency.
    
    Examples:
        emote passes the boof to Test Dummy and says, "Hit this shit."
        : waves hello to everyone.
    """
    
    def func(self):
        """Override emote to include voice description and language garbling."""
        caller = self.caller
        
        # Debug: Check if func is being called multiple times
        try:
            from evennia.comms.models import ChannelDB
            splattercast = ChannelDB.objects.get_channel("Splattercast")
            splattercast.msg(f"EMOTE_FUNC_START: {caller.key} args={self.args[:30]}")
        except Exception:
            pass
        
        if not self.args:
            caller.msg("Emote what?")
            return
        
        emote_text = self.args.lstrip()  # Remove leading whitespace
        
        # Fix grammar in the emote text - contractions and capitalize standalone "i"
        emote_text = fix_speech_grammar(emote_text)
        
        # Check for disguise slip on emote
        try:
            from world.disguise.core import (
                check_disguise_slip, trigger_slip_event, get_anonymity_item
            )
            slipped, slip_type = check_disguise_slip(caller, "emote")
            if slipped:
                item, _ = get_anonymity_item(caller)
                trigger_slip_event(caller, slip_type, item=item)
        except ImportError:
            pass  # Disguise system not available
        
        # Check if character has a voice set
        voice = getattr(caller.db, 'voice', None)
        
        # Get speaker's primary language
        primary_language = get_primary_language(caller)
        
        # Extract speech from emote for language processing
        quote_pattern = r'(["\'])(.*?)\1'
        speech_matches = list(re.finditer(quote_pattern, emote_text))
        
        if voice:
            # Look for any quoted speech in the emote and insert accent
            def replace_quotes(match):
                quote = match.group(1)  # The quote character (" or ')
                speech = match.group(2)  # The actual speech
                # Fix speech grammar (contractions, capitalize I, etc.)
                speech = fix_speech_grammar(speech)
                # Capitalize first letter
                if speech:
                    speech = speech[0].upper() + speech[1:] if len(speech) > 1 else speech.upper()
                # Add period if no ending punctuation
                if speech and speech[-1] not in '.!?':
                    speech = speech + '.'
                # Apply intoxication slurring if drunk
                try:
                    from world.survival.core import slur_speech
                    speech = slur_speech(caller, speech)
                except Exception:
                    pass  # Survival system not loaded
                return f'{quote}*in a {voice}* {speech}{quote}'
            
            # Replace all quoted speech instances with voice-enhanced versions
            emote_text = re.sub(quote_pattern, replace_quotes, emote_text)
        else:
            # Even without voice, fix grammar in quoted speech
            def fix_quotes(match):
                quote = match.group(1)
                speech = match.group(2)
                speech = fix_speech_grammar(speech)
                # Capitalize first letter
                if speech:
                    speech = speech[0].upper() + speech[1:] if len(speech) > 1 else speech.upper()
                # Add period if no ending punctuation
                if speech and speech[-1] not in '.!?':
                    speech = speech + '.'
                # Apply intoxication slurring if drunk
                try:
                    from world.survival.core import slur_speech
                    speech = slur_speech(caller, speech)
                except Exception:
                    pass  # Survival system not loaded
                return f'{quote}{speech}{quote}'
            
            emote_text = re.sub(quote_pattern, fix_quotes, emote_text)
        
        # Format the pose with caller's display name (respects disguises)
        pose_text = f"{caller.get_display_name(caller)} {emote_text}"
        
        # Send to the caller (ungarbled)
        caller.msg(pose_text)
        
        # Send to others in the location
        if caller.location:
            for char in caller.location.contents:
                if char == caller:
                    continue
                
                # Create perspective-adjusted message for this character
                # Just use the original pose_text - display_name is already correct
                message = pose_text
                
                # Apply language garbling to speech if present
                if speech_matches:
                    proficiency = get_language_proficiency(char, primary_language)
                    
                    if proficiency < 100.0:
                        # Process each quoted section with garbling
                        for match in reversed(speech_matches):  # Reverse to maintain positions
                            quote_char = match.group(1)
                            speech_text = match.group(2)
                            start, end = match.span()
                            
                            # Garble the speech
                            garbled_speech = garble_text_by_proficiency(speech_text, proficiency)
                            
                            # Replace in message
                            message = message[:start] + quote_char + f'*in a {voice}* {garbled_speech}' + quote_char + message[end:] if voice else message[:start] + quote_char + garbled_speech + quote_char + message[end:]
                        
                        # Apply passive learning
                        apply_passive_language_learning(char, primary_language)
                
                if hasattr(char, 'msg'):
                    char.msg(message)
