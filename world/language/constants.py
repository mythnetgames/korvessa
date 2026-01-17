"""
Language System Constants

Centralized language definitions for Korvessa fantasy MUD language system.

LANGUAGE HIERARCHY:

Common Languages:
- Common: The universal trade language spoken by all civilized races.
  Default language for most interactions.

Racial Languages:
- Elvish: The flowing, melodic language of the elven people. Known for its
  poetry and magical terminology.
- Dwarvish: The harsh, guttural language of the dwarves. Rich in terms for
  crafting, mining, and stonework.

Builder+ Permission:
- Builders with Builder+ permission gain access to all languages for NPC creation.
- Standard builders see a curated set of common languages.
"""

# ===================================================================
# LANGUAGE DEFINITIONS
# ===================================================================

LANGUAGES = {
    'common': {
        'name': 'Common',
        'description': 'The universal trade language spoken by all civilized races.',
        'native': False,
        'common': True,  # Default language
    },
    'elvish': {
        'name': 'Elvish',
        'description': 'The flowing, melodic language of the elven people.',
        'native': False,
        'common': False,
    },
    'dwarvish': {
        'name': 'Dwarvish',
        'description': 'The harsh, guttural language of the dwarves.',
        'native': False,
        'common': False,
    },
}

# ===================================================================
# LANGUAGE SYSTEM CONSTANTS
# ===================================================================

DEFAULT_LANGUAGE = 'common'
MAX_LANGUAGES = 10
# Removed SMARTS_THRESHOLD - language selection is now race-based

# Common languages available to all builders
COMMON_LANGUAGES = [code for code, info in LANGUAGES.items() if info.get('common', False)]

# All languages available only to Builder+ users
ALL_LANGUAGES = list(LANGUAGES.keys())

# Race-based language bonuses
RACE_LANGUAGES = {
    'human': ['common'],  # Humans know Common, can pick one additional
    'elf': ['common', 'elvish'],  # Elves know Common and Elvish
    'dwarf': ['common', 'dwarvish'],  # Dwarves know Common and Dwarvish
}


# ===================================================================
# DATABASE AND NDB FIELD NAMES
# ===================================================================

DB_PRIMARY_LANGUAGE = 'primary_language'
DB_LANGUAGES = 'known_languages'
NDB_LAST_SPOKEN = 'last_spoken_language'

# ===================================================================
# MESSAGE TEMPLATES
# ===================================================================

MSG_LANGUAGE_SET = "|g{char_name}'s primary language is now set to {language}.|n"
MSG_LANGUAGE_ADDED = "|g{language} added to {char_name}'s known languages.|n"
MSG_LANGUAGE_REMOVED = "|g{language} removed from {char_name}'s known languages.|n"
MSG_LANGUAGE_ALREADY_KNOWN = "|y{char_name} already speaks {language}.|n"
MSG_LANGUAGE_NOT_KNOWN = "|r{char_name} does not speak {language}.|n"
MSG_LANGUAGE_INVALID = "|rInvalid language: {language}|n"
MSG_LANGUAGE_LIST = "|yKnown Languages:|n {languages}"
MSG_PRIMARY_LANGUAGE = "|yPrimary Language:|n {language}"
MSG_SPEAK_IN = "speaks in {language}"
MSG_LANGUAGE_CANNOT_REMOVE_PRIMARY = "|rCannot remove primary language. Set a new primary language first.|n"
