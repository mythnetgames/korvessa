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
    known = getattr(character.db, DB_LANGUAGES, {DEFAULT_LANGUAGE})
    
    # Ensure primary is in known
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
