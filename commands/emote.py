"""
Custom Emote command that integrates voice descriptions into speech and language garbling.
Also supports sdesc-based target parsing with /word syntax for characters and *word for objects.
"""

import re
from evennia.commands.default.general import CmdPose as DefaultCmdPose
from world.language.utils import (
    get_primary_language,
    garble_text_by_proficiency,
    get_language_proficiency,
    apply_passive_language_learning,
)
from world.sdesc_system import (
    get_sdesc_with_pose, parse_targets_in_string, personalize_text
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
    
    You can reference other characters in the room by partial sdesc match:
        emote smiles at /tall and waves.
        (becomes: "A short woman smiles at a tall man and waves.")
    
    You can also reference objects with *:
        emote picks up *sword and examines it.
        (becomes: "A tall man picks up a steel sword and examines it.")
    
    If your emote contains speech (like "says,"), your @voice will be inserted
    around the speech text. Speech text will also be garbled for observers based
    on their language proficiency.
    
    Examples:
        emote passes the boof to /test and says, "Hit this shit."
        : waves hello to everyone.
        :nods to /hooded and /scarred
        emote picks up *dagger and looks at /elf
    """
    
    def func(self):
        """Override emote to include voice description, sdesc targets, and language garbling."""
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
        
        # Parse /target references for characters and *target for objects
        # Returns (parsed_text, char_targets, obj_targets) where:
        # - char_targets is list of (search_term, matched_character, possessive) tuples
        # - obj_targets is list of (search_term, matched_object, possessive) tuples
        parsed_text, char_targets, obj_targets = parse_targets_in_string(emote_text, caller.location, caller)
        
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
        
        # Get speaker's primary language (default if not specified per-speech)
        primary_language = get_primary_language(caller)
        
        # Extract speech from emote for language processing
        # Supports language prefix syntax: dwarven"Hello" or just "Hello" (uses primary)
        # Language-prefixed speech: language"speech"
        lang_speech_pattern = r'(\w+)"([^"]*)"'
        # Simple quoted speech: "speech" or 'speech'
        simple_quote_pattern = r'(["\'])([^"\']*)\1'
        
        # Track speech segments with their languages for garbling
        # First, find language-prefixed speech and replace with processed version
        def process_lang_speech(match):
            language = match.group(1).lower()
            speech = match.group(2)
            
            # Check if it's actually a language or just a word before quotes
            from world.language.constants import LANGUAGES
            if language not in LANGUAGES:
                # Not a valid language, treat as regular quote
                return match.group(0)
            
            # Validate caller knows this language
            lang_proficiency = get_language_proficiency(caller, language)
            if lang_proficiency < 10.0:
                # Don't know language well enough - will be handled at render time
                pass
            
            # Process the speech
            speech = fix_speech_grammar(speech)
            if speech:
                speech = speech[0].upper() + speech[1:] if len(speech) > 1 else speech.upper()
            if speech and speech[-1] not in '.!?':
                speech = speech + '.'
            
            # Apply intoxication slurring
            try:
                from world.survival.core import slur_speech
                speech = slur_speech(caller, speech)
            except Exception:
                pass
            
            lang_name = LANGUAGES[language]['name']
            if voice:
                return f'"*speaking {lang_name} in a {voice}* {speech}"'
            else:
                return f'"*speaking {lang_name}* {speech}"'
        
        # Process language-prefixed speech first
        emote_text_processed = re.sub(lang_speech_pattern, process_lang_speech, parsed_text)
        
        # Now handle remaining simple quotes (no language prefix = use primary)
        def process_simple_speech(match):
            quote = match.group(1)
            speech = match.group(2)
            
            # Skip if already processed (contains *speaking)
            if '*speaking' in speech:
                return match.group(0)
            
            speech = fix_speech_grammar(speech)
            if speech:
                speech = speech[0].upper() + speech[1:] if len(speech) > 1 else speech.upper()
            if speech and speech[-1] not in '.!?':
                speech = speech + '.'
            
            # Apply intoxication slurring
            try:
                from world.survival.core import slur_speech
                speech = slur_speech(caller, speech)
            except Exception:
                pass
            
            # Use speaker's primary language
            from world.language.constants import LANGUAGES
            lang_name = LANGUAGES.get(primary_language, {}).get('name', primary_language.title())
            
            if voice:
                return f'{quote}*speaking {lang_name} in a {voice}* {speech}{quote}'
            else:
                return f'{quote}*speaking {lang_name}* {speech}{quote}'
        
        emote_text = re.sub(simple_quote_pattern, process_simple_speech, emote_text_processed)
        
        # Re-extract speech matches for garbling (now with language tags)
        speech_matches = list(re.finditer(simple_quote_pattern, emote_text))
        
        # Get caller's sdesc for the pose (uses sdesc system which respects disguises)
        from world.sdesc_system import get_sdesc
        caller_sdesc = get_sdesc(caller, caller)  # Self-view - shows real sdesc
        
        # Format the pose with placeholders for targets and caller's sdesc
        pose_template = f"{{caller}} {emote_text}"
        
        # Send to the caller (ungarbled, personalized)
        # For self, capitalize the sdesc for sentence start
        caller_pose = pose_template.replace("{caller}", caller_sdesc.capitalize() if caller_sdesc else caller.key)
        caller_pose = personalize_text(caller_pose, char_targets, obj_targets, caller, caller)
        caller.msg(caller_pose)
        
        # Send to others in the location
        if caller.location:
            for char in caller.location.contents:
                if char == caller:
                    continue
                if not hasattr(char, 'msg'):
                    continue
                
                # Get how this viewer sees the caller
                viewer_sees_caller = get_sdesc(caller, char)
                
                # Create perspective-adjusted message for this character
                message = pose_template.replace("{caller}", viewer_sees_caller.capitalize() if viewer_sees_caller else caller.key)
                message = personalize_text(message, char_targets, obj_targets, char, caller)
                
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
                
                char.msg(message)
