"""
Language System Utilities

Helper functions for the language system.
"""

from .constants import (
    LANGUAGES,
    DEFAULT_LANGUAGE,
    MAX_LANGUAGES,
    DB_PRIMARY_LANGUAGE,
    DB_LANGUAGES,
    NDB_LAST_SPOKEN,
)


def initialize_character_languages(character, primary_language=None, additional_languages=None):
    """
    Initialize a character's language system.
    
    Cantonese is the default spoken language of Kowloon.
    
    Args:
        character: The character to initialize
        primary_language (str): Primary language code (defaults to Cantonese)
        additional_languages (list): List of additional language codes
    """
    if primary_language is None:
        primary_language = DEFAULT_LANGUAGE
    
    if primary_language not in LANGUAGES:
        primary_language = DEFAULT_LANGUAGE
    
    # Set primary language
    character.db.primary_language = primary_language
    
    # Initialize known languages set
    known_languages = {primary_language}
    
    # Add additional languages if provided
    if additional_languages:
        for lang in additional_languages:
            if lang in LANGUAGES and len(known_languages) < MAX_LANGUAGES:
                known_languages.add(lang)
    
    character.db.known_languages = known_languages
    
    # Initialize proficiency tracking - don't reset if already exists
    existing_prof = character.db.language_proficiency
    if existing_prof is None or not isinstance(existing_prof, dict):
        character.db.language_proficiency = {}
    
    # Set proficiency for all known languages to 100% only if not already set
    prof_dict = character.db.language_proficiency
    for lang in known_languages:
        if lang not in prof_dict:
            prof_dict[lang] = 100.0
    character.db.language_proficiency = prof_dict


def get_character_languages(character):
    """
    Get a character's known languages.
    
    Args:
        character: The character object
        
    Returns:
        dict: Contains 'primary' and 'known' keys
    """
    # Ensure initialized
    if not hasattr(character.db, DB_PRIMARY_LANGUAGE):
        initialize_character_languages(character)
    
    if not hasattr(character.db, DB_LANGUAGES):
        initialize_character_languages(character)
    
    primary = getattr(character.db, DB_PRIMARY_LANGUAGE, DEFAULT_LANGUAGE)
    known = getattr(character.db, DB_LANGUAGES, None)
    
    # Handle None or invalid known_languages
    if known is None or not isinstance(known, (set, list)):
        known = {DEFAULT_LANGUAGE}
        character.db.known_languages = known
    
    # Convert to set if it's a list
    if isinstance(known, list):
        known = set(known)
        character.db.known_languages = known
    
    # Ensure primary is valid (but don't reset it if it's valid)
    if primary is None or primary not in LANGUAGES:
        primary = DEFAULT_LANGUAGE
        character.db.primary_language = primary
    
    # Ensure primary is in known languages (add it if missing)
    if primary not in known:
        known.add(primary)
        character.db.known_languages = known
    
    return {
        'primary': primary,
        'known': known,
    }


def get_primary_language(character):
    """
    Get a character's primary language.
    
    Args:
        character: The character object
        
    Returns:
        str: Primary language code
    """
    languages = get_character_languages(character)
    return languages['primary']


def get_all_known_languages(character):
    """
    Get all languages a character knows.
    
    Args:
        character: The character object
        
    Returns:
        list: List of language codes
    """
    languages = get_character_languages(character)
    return sorted(list(languages['known']))


def add_language(character, language_code):
    """
    Add a language to a character's known languages.
    
    Args:
        character: The character object
        language_code (str): Language code to add
        
    Returns:
        tuple: (success: bool, message: str)
    """
    if language_code not in LANGUAGES:
        return (False, f"Invalid language: {language_code}")
    
    languages = get_character_languages(character)
    known = languages['known']
    
    if language_code in known:
        return (False, f"{character.key} already speaks {LANGUAGES[language_code]['name']}")
    
    if len(known) >= MAX_LANGUAGES:
        return (False, f"Cannot learn more than {MAX_LANGUAGES} languages")
    
    known.add(language_code)
    character.db.known_languages = known
    return (True, f"{LANGUAGES[language_code]['name']} added to {character.key}'s known languages")


def remove_language(character, language_code):
    """
    Remove a language from a character's known languages.
    
    Args:
        character: The character object
        language_code (str): Language code to remove
        
    Returns:
        tuple: (success: bool, message: str)
    """
    if language_code not in LANGUAGES:
        return (False, f"Invalid language: {language_code}")
    
    languages = get_character_languages(character)
    primary = languages['primary']
    known = languages['known']
    
    if language_code == primary:
        return (False, f"Cannot remove primary language. Set a new primary language first")
    
    if language_code not in known:
        return (False, f"{character.key} does not speak {LANGUAGES[language_code]['name']}")
    
    known.discard(language_code)
    character.db.known_languages = known
    return (True, f"{LANGUAGES[language_code]['name']} removed from {character.key}'s known languages")


def set_primary_language(character, language_code):
    """
    Set a character's primary language.
    
    Args:
        character: The character object
        language_code (str): Language code to set as primary
        
    Returns:
        tuple: (success: bool, message: str)
    """
    if language_code not in LANGUAGES:
        return (False, f"Invalid language: {language_code}")
    
    languages = get_character_languages(character)
    known = languages['known']
    
    # Add to known if not already
    if language_code not in known:
        if len(known) >= MAX_LANGUAGES:
            return (False, f"Cannot learn more than {MAX_LANGUAGES} languages")
        known.add(language_code)
        character.db.known_languages = known
    
    character.db.primary_language = language_code
    return (True, f"{character.key}'s primary language is now set to {LANGUAGES[language_code]['name']}")


def get_language_flavor_text(character, verb="says"):
    """
    Get flavor text for how a character is speaking in the format:
    *speaking Language in a [character's voice]*
    
    Uses the character's db.voice attribute if set, otherwise uses a generic form.
    
    Args:
        character: The character object
        verb (str): The speech verb (not used in current format but kept for compatibility)
        
    Returns:
        str: Formatted flavor text
    """
    primary = get_primary_language(character)
    language_info = LANGUAGES.get(primary, {})
    language_name = language_info.get('name', 'Unknown')
    
    # Get character's voice if set
    voice = getattr(character.db, 'voice', None)
    
    if voice:
        return f"*speaking {language_name} in a {voice}*"
    else:
        return f"*speaking {language_name}*"


def list_languages_for_display(character):
    """
    Get a formatted list of a character's languages for display.
    
    Args:
        character: The character object
        
    Returns:
        str: Formatted language list
    """
    languages = get_character_languages(character)
    known = sorted(list(languages['known']))
    primary = languages['primary']
    
    lang_names = []
    for lang_code in known:
        lang_name = LANGUAGES[lang_code]['name']
        if lang_code == primary:
            lang_names.append(f"|c{lang_name}|n (primary)")
        else:
            lang_names.append(lang_name)
    
    return ", ".join(lang_names)


def check_can_speak_language(character, language_code):
    """
    Check if a character can speak a specific language.
    
    Args:
        character: The character object
        language_code (str): Language code to check
        
    Returns:
        bool: True if character can speak the language
    """
    if language_code not in LANGUAGES:
        return False
    
    languages = get_character_languages(character)
    return language_code in languages['known']


# ===================================================================
# LANGUAGE PROFICIENCY SYSTEM
# ===================================================================

def initialize_language_proficiency(character):
    """
    Initialize proficiency tracking for all known languages.
    
    Args:
        character: The character object
    """
    # Use direct access instead of getattr for Evennia db attributes
    try:
        proficiency = character.db.language_proficiency
    except AttributeError:
        proficiency = None
    
    if proficiency is None or not isinstance(proficiency, dict):
        proficiency = {}
        
        # Initialize known languages with 100% proficiency
        known = get_character_languages(character)['known']
        for lang in known:
            proficiency[lang] = 100.0
        
        character.db.language_proficiency = proficiency


def get_language_proficiency(character, language_code):
    """
    Get proficiency percentage (0-100) for a language.
    
    Args:
        character: The character object
        language_code (str): Language code
        
    Returns:
        float: Proficiency percentage (0-100)
    """
    from evennia.comms.models import ChannelDB
    try:
        splattercast = ChannelDB.objects.get_channel("Splattercast")
    except:
        splattercast = None
    
    # Use Evennia's attributes API directly
    proficiency_dict = character.attributes.get("language_proficiency", default={})
    
    if splattercast:
        splattercast.msg(f"GET_PROF: {character.key} {language_code} dict={proficiency_dict} id={id(proficiency_dict)}")
    
    if not isinstance(proficiency_dict, dict):
        proficiency_dict = {}
    
    # Check if value exists in dict first
    value = proficiency_dict.get(language_code)
    if value is not None:
        if splattercast:
            splattercast.msg(f"GET_PROF: returning {value} from dict")
        return float(value)
    
    # If not in dict, check if it's a known language (should be 100%)
    known = character.attributes.get("known_languages", default=set())
    if known and language_code in known:
        if splattercast:
            splattercast.msg(f"GET_PROF: returning 100.0 (known language)")
        return 100.0
    
    # Unknown languages default to 0.0
    if splattercast:
        splattercast.msg(f"GET_PROF: returning 0.0 (unknown)")
    return 0.0


def set_language_proficiency(character, language_code, proficiency):
    """
    Set proficiency for a language (0-100).
    
    Args:
        character: The character object
        language_code (str): Language code
        proficiency (float): Proficiency percentage
    """
    from evennia.comms.models import ChannelDB
    try:
        splattercast = ChannelDB.objects.get_channel("Splattercast")
    except:
        splattercast = None
    
    proficiency = max(0.0, min(100.0, proficiency))
    
    # Use Evennia's attributes API directly for persistence
    existing = character.attributes.get("language_proficiency", default={})
    if splattercast:
        splattercast.msg(f"SET_PROF existing via attributes.get: {existing}")
    
    if not isinstance(existing, dict):
        existing = {}
    
    # Create new dict with updated value
    new_dict = dict(existing)
    new_dict[language_code] = proficiency
    
    # Use attributes.add to force persistence
    character.attributes.add("language_proficiency", new_dict)
    
    if splattercast:
        verify = character.attributes.get("language_proficiency")
        splattercast.msg(f"SET_PROF after attributes.add: {verify}")


def increase_language_proficiency(character, language_code, amount):
    """
    Increase proficiency for a language.
    
    Args:
        character: The character object
        language_code (str): Language code
        amount (float): Amount to increase (capped at 100)
    """
    from evennia.comms.models import ChannelDB
    try:
        splattercast = ChannelDB.objects.get_channel("Splattercast")
        if splattercast:
            splattercast.msg(f"INCREASE_PROF CALLED: {character.key} {language_code} +{amount}")
    except:
        pass
    
    current = get_language_proficiency(character, language_code)
    new_proficiency = min(100.0, current + amount)
    set_language_proficiency(character, language_code, new_proficiency)


def get_language_learning_speed(character):
    """
    Calculate learning speed multiplier based on Smarts stat.
    
    Smarts stat ranges 1-10, with 1 being baseline (1x speed).
    Each point of Smarts above 1 gives 0.15x multiplier.
    
    Args:
        character: The character object
        
    Returns:
        float: Learning speed multiplier (minimum 1.0)
    """
    try:
        # Stats are accessed directly on character, not character.db
        smarts = getattr(character, 'smrt', 1)
        if not isinstance(smarts, (int, float)) or smarts is None:
            smarts = 1
        multiplier = 1.0 + (max(0, smarts - 1) * 0.15)
        return max(1.0, multiplier)
    except:
        return 1.0


def apply_passive_language_learning(character, heard_language_code):
    """
    Apply passive learning when hearing a language.
    
    Hearing a language you don't know increases proficiency by 0.04 per event.
    Daily cap: 5 events = 0.2 proficiency per day.
    
    Args:
        character: The character object
        heard_language_code (str): Language code heard
    """
    from evennia.comms.models import ChannelDB
    try:
        splattercast = ChannelDB.objects.get_channel("Splattercast")
    except:
        splattercast = None
    
    if heard_language_code not in LANGUAGES:
        if splattercast:
            splattercast.msg(f"PASSIVE: {character.key} {heard_language_code} not in LANGUAGES")
        return
    
    # Only passive learning for languages not already at 100%
    current_proficiency = get_language_proficiency(character, heard_language_code)
    if splattercast:
        splattercast.msg(f"PASSIVE: {character.key} checking {heard_language_code}, current={current_proficiency}")
    
    if current_proficiency >= 100.0:
        if splattercast:
            splattercast.msg(f"PASSIVE: {character.key} {heard_language_code} already at 100%")
        return
    
    # Check daily passive learning cap (max 5 events = 0.2 proficiency per day)
    if not hasattr(character.ndb, 'daily_passive_learning'):
        character.ndb.daily_passive_learning = {}
    
    today = str(__import__('datetime').datetime.now().date())
    if not hasattr(character.ndb, 'passive_learning_date'):
        character.ndb.passive_learning_date = today
    
    # Reset if it's a new day
    if character.ndb.passive_learning_date != today:
        character.ndb.daily_passive_learning = {}
        character.ndb.passive_learning_date = today
    
    # Track passive learning count
    count = character.ndb.daily_passive_learning.get(heard_language_code, 0)
    if splattercast:
        splattercast.msg(f"PASSIVE: {character.key} {heard_language_code} count={count}/5")
    
    if count < 5:  # Max 5 passive learning events per language per day
        increase_language_proficiency(character, heard_language_code, 0.04)
        character.ndb.daily_passive_learning[heard_language_code] = count + 1
    else:
        if splattercast:
            splattercast.msg(f"PASSIVE: {character.key} {heard_language_code} CAPPED at 5")


def calculate_ip_cost_for_proficiency(target_proficiency):
    """
    Calculate IP cost to reach a target proficiency level.
    
    System: 50 IP per 1% proficiency. Total cost to reach 100%: 5000 IP.
    
    Args:
        target_proficiency (float): Target proficiency (0-100)
        
    Returns:
        int: IP cost
    """
    return int(target_proficiency * 50)


def get_ip_spent_today_on_language(character, language_code):
    """
    Get total IP spent today on a specific language.
    
    Args:
        character: The character object
        language_code (str): Language code
        
    Returns:
        int: IP spent today
    """
    if not hasattr(character.ndb, 'daily_ip_spent'):
        character.ndb.daily_ip_spent = {}
    
    today = str(__import__('datetime').datetime.now().date())
    if not hasattr(character.ndb, 'ip_spending_date'):
        character.ndb.ip_spending_date = today
    
    # Reset if new day
    if character.ndb.ip_spending_date != today:
        character.ndb.daily_ip_spent = {}
        character.ndb.ip_spending_date = today
    
    return character.ndb.daily_ip_spent.get(language_code, 0)


def get_daily_ip_cap_for_language(character, language_code):
    """
    Get daily IP spending cap for learning a language.
    
    Cap based on Smarts stat. Max 50 IP/day at Smarts 1, +5 per point.
    
    Args:
        character: The character object
        language_code (str): Language code
        
    Returns:
        int: Daily IP cap
    """
    try:
        # Stats are accessed directly on character, not character.db
        smarts = getattr(character, 'smrt', 1)
        if not isinstance(smarts, (int, float)) or smarts is None:
            smarts = 1
        cap = 50 + (max(0, smarts - 1) * 5)
        return int(cap)
    except:
        return 50


def spend_ip_on_language(character, language_code, ip_amount):
    """
    Spend IP to learn a language.
    
    Returns proficiency gained and any excess IP.
    
    Args:
        character: The character object
        language_code (str): Language code to learn
        ip_amount (int): IP to spend
        
    Returns:
        tuple: (success: bool, proficiency_gained: float, message: str)
    """
    if language_code not in LANGUAGES:
        return (False, 0, f"Invalid language: {language_code}")
    
    if ip_amount <= 0:
        return (False, 0, "IP amount must be positive")
    
    # Check daily IP cap
    spent_today = get_ip_spent_today_on_language(character, language_code)
    daily_cap = get_daily_ip_cap_for_language(character, language_code)
    
    if spent_today >= daily_cap:
        return (False, 0, f"Daily IP spending cap for {LANGUAGES[language_code]['name']} ({daily_cap} IP) reached. Try again tomorrow.")
    
    # Limit IP spending to daily cap
    ip_to_spend = min(ip_amount, daily_cap - spent_today)
    
    # Check character has enough IP
    if character.db.IP < ip_to_spend:
        return (False, 0, f"Not enough IP. You have {character.db.IP} IP.")
    
    # Calculate proficiency gain
    # 50 IP = 1% proficiency (0.02% per IP)
    proficiency_gain = ip_to_spend * 0.02
    
    # Apply learning speed multiplier based on Smarts
    learning_speed = get_language_learning_speed(character)
    proficiency_gain *= learning_speed
    
    # Update character
    character.db.IP -= ip_to_spend
    increase_language_proficiency(character, language_code, proficiency_gain)
    
    # Track daily spending
    if not hasattr(character.ndb, 'daily_ip_spent'):
        character.ndb.daily_ip_spent = {}
    character.ndb.daily_ip_spent[language_code] = spent_today + ip_to_spend
    
    # If language is unknown, add it to known languages
    if not check_can_speak_language(character, language_code):
        add_language(character, language_code)
    
    proficiency = get_language_proficiency(character, language_code)
    
    return (True, proficiency_gain, f"Spent {ip_to_spend} IP on {LANGUAGES[language_code]['name']}. Proficiency: {proficiency:.1f}%")


# ===================================================================
# LANGUAGE GARBLING SYSTEM
# ===================================================================

def garble_text_by_proficiency(text, proficiency):
    """
    Garble text based on language proficiency.
    
    At 0% proficiency: Almost all words are garbled
    At 50% proficiency: About half the words are garbled
    At 100% proficiency: No words are garbled
    
    Garbled words are replaced with random character sequences of similar length.
    The process is randomized so patterns cannot be extracted algorithmically.
    
    Args:
        text (str): The text to garble
        proficiency (float): Proficiency percentage (0-100)
        
    Returns:
        str: Garbled text appropriate to proficiency level
    """
    import random
    import re
    
    if proficiency >= 99.0:
        # Nearly perfect understanding - minimal garbling
        return text
    
    if proficiency <= 0.1:
        # No understanding - garble everything
        return _garble_all_text(text)
    
    # Split into words (preserve spacing and punctuation)
    words = text.split()
    garbled_words = []
    
    # Calculate garble probability (inverse of proficiency)
    # At 80% proficiency, garble 20% of words
    garble_chance = (100.0 - proficiency) / 100.0
    
    for word in words:
        # Separate word from trailing punctuation
        trailing_punct = ''
        clean_word = word
        
        while clean_word and not clean_word[-1].isalnum():
            trailing_punct = clean_word[-1] + trailing_punct
            clean_word = clean_word[:-1]
        
        # Randomly decide whether to garble this word
        if random.random() < garble_chance and clean_word:
            # Sometimes garble the whole word, sometimes just parts
            if random.random() < 0.6:
                # Garble entire word
                garbled = _generate_random_word(len(clean_word))
            else:
                # Garble parts of word - leave some letters for recognition
                garbled = _garble_word_partially(clean_word)
            
            garbled_words.append(garbled + trailing_punct)
        else:
            # Keep word as-is
            garbled_words.append(word)
    
    return ' '.join(garbled_words)


def _garble_all_text(text):
    """Garble all words in text (0% proficiency)."""
    import random
    import re
    
    words = text.split()
    garbled = []
    
    for word in words:
        # Separate punctuation
        trailing_punct = ''
        clean_word = word
        while clean_word and not clean_word[-1].isalnum():
            trailing_punct = clean_word[-1] + trailing_punct
            clean_word = clean_word[:-1]
        
        if clean_word:
            garbled.append(_generate_random_word(len(clean_word)) + trailing_punct)
        else:
            garbled.append(word)
    
    return ' '.join(garbled)


def _garble_word_partially(word):
    """
    Garble parts of a word to allow some recognition.
    Randomly replaces 50-80% of letters with random characters.
    """
    import random
    
    word_list = list(word)
    garble_count = random.randint(
        int(len(word_list) * 0.5),
        int(len(word_list) * 0.8)
    )
    
    # Randomly select positions to garble
    positions = random.sample(range(len(word_list)), min(garble_count, len(word_list)))
    
    for pos in positions:
        word_list[pos] = _random_character()
    
    return ''.join(word_list)


def _generate_random_word(length):
    """Generate a random garbled word of given length."""
    import random
    return ''.join(_random_character() for _ in range(length))


def _random_character():
    """
    Generate a random character for garbling.
    Uses mix of consonants, vowels, and symbols for natural-looking gibberish.
    """
    import random
    
    # Mix different character types for variety
    choice = random.random()
    
    if choice < 0.4:
        # Consonants
        chars = 'bcdfghjklmnpqrstvwxyz'
    elif choice < 0.7:
        # Vowels
        chars = 'aeiou'
    elif choice < 0.85:
        # Numbers
        chars = '0123456789'
    else:
        # Symbol-like chars
        chars = '&@#%$!?'
    
    return random.choice(chars)


def apply_language_garbling_to_observers(speaker, message, language_code):
    """
    Apply language garbling to message for all observers except speaker.
    
    This function should be called after a character speaks.
    Each observer sees the message garbled to their proficiency level.
    
    Args:
        speaker: The character speaking
        message (str): The message spoken
        language_code (str): Language code being spoken
        
    Returns:
        dict: Mapping of character to their garbled message
    """
    observer_messages = {}
    
    # Get all characters in the room except the speaker
    location = speaker.location
    if not location:
        return observer_messages
    
    # Debug
    from evennia.comms.models import ChannelDB
    try:
        splattercast = ChannelDB.objects.get_channel("Splattercast")
    except:
        splattercast = None
    
    for obj in location.contents:
        # Skip the speaker
        if obj == speaker:
            continue
        
        # Debug: show typeclass for each object
        try:
            typeclass = obj.typeclass_path.lower()
            if splattercast:
                splattercast.msg(f"DEBUG: {obj.key} typeclass={typeclass}")
            if 'character' not in typeclass:
                continue
        except (AttributeError, TypeError) as e:
            if splattercast:
                splattercast.msg(f"DEBUG: {obj.key} no typeclass - {e}")
            continue
        
        if splattercast:
            splattercast.msg(f"DEBUG: Processing {obj.key} for {language_code}")
        
        # Get observer's proficiency in this language
        proficiency = get_language_proficiency(obj, language_code)
        
        # Apply garbling
        if proficiency < 100.0:
            garbled = garble_text_by_proficiency(message, proficiency)
        else:
            garbled = message
        
        observer_messages[obj] = garbled
        
        # Apply passive learning
        apply_passive_language_learning(obj, language_code)
        
        if splattercast:
            new_prof = get_language_proficiency(obj, language_code)
            splattercast.msg(f"DEBUG: After learning {obj.key} proficiency={new_prof}")
    
    return observer_messages
    
    return observer_messages
